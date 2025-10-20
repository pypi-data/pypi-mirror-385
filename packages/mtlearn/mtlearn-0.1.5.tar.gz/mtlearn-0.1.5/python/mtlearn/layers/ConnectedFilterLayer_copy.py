import hashlib
import torch
import numpy as np
import mmcfilters
import mtlearn

# -----------------------------------------------------------------------------
# Função autograd responsável por aplicar o operador conexo com parâmetros
# aprendíveis (weight, bias) sobre atributos calculados na árvore morfológica.
# -----------------------------------------------------------------------------
class ConnectedFilterFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, tree, attributes, weight, bias):
        """
        Parâmetros
        ----------
        tree : objeto de árvore (mmcfilters.MorphologicalTree)
            Árvore morfológica construída sobre a imagem do canal.
        attributes : torch.Tensor (numNodes, numFeatures)
            Atributos por nó da árvore; podem ser concatenados (grupos).
        weight : torch.Tensor (numFeatures,)  ou (numFeatures, 1)
            Pesos para combinar as features do grupo em um escalar por nó.
        bias : torch.Tensor (1,)
            Viés escalar do grupo.

        Retorna
        -------
        y_pred : torch.Tensor (H, W)
            Resultado no domínio da imagem após aplicar o filtro conectado
            guiado pelos scores sigmoid(attributes @ weight + bias).
        """
        logits = attributes @ weight + bias            # (numNodes,) se weight=(F,), (numNodes,1) se (F,1)
        sigmoid = torch.sigmoid(logits).squeeze(-1)    # garante (numNodes,)
        # Aplica o operador conectado no backend, que espera os scores por nó:
        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filter(tree, sigmoid)

        # Guardamos no contexto o que é necessário para o backward
        ctx.tree = tree
        # Salvar tensores (apenas tensores) para o backward:
        ctx.save_for_backward(attributes, sigmoid)
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        """
        grad_output : torch.Tensor (H, W)
            Gradiente do loss w.r.t. y_pred no domínio da imagem.

        Retorna
        -------
        (None, None, grad_weight, grad_bias)
            Gradientes alinhados aos argumentos de entrada (tree, attributes, weight, bias).
            'tree' e 'attributes' não recebem gradiente aqui (None).
        """
        # Recupera tensores salvos no forward:
        attributes, sigmoid = ctx.saved_tensors   # (numNodes, numFeatures), (numNodes,)
        tree = ctx.tree

        # O backend 'gradients' deve internamente converter grad_output (H,W)
        # para gradientes por nó (numNodes,) via agregação pixel->nó.
        grad_weight, grad_bias = mtlearn.ConnectedFilterByMorphologicalTree.gradients(
            tree, attributes, sigmoid, grad_output
        )

        # A API do autograd exige retornar gradientes na mesma ordem dos inputs:
        # (tree, attributes, weight, bias)
        # 'tree' e 'attributes' não são parâmetros treináveis aqui -> None
        return None, None, grad_weight, grad_bias


# -----------------------------------------------------------------------------
# Camada PyTorch que organiza o uso de árvores, atributos e grupos de atributos
# por canal, com cache por CONTEÚDO (hash da imagem) criado on-the-fly.
# Parâmetros (W,b) inicializados no __init__, assumindo cada atributo ESCALAR.
# -----------------------------------------------------------------------------
class ConnectedFilterLayer(torch.nn.Module):
    def __init__(self, in_channels, attributes_spec, tree_type="max-tree",
                 device="cpu", assume_static_inputs=True):
        """
        Parâmetros
        ----------
        in_channels : int
            Número de canais da entrada (C).
        attributes_spec : lista
            Especificação de grupos. Cada item pode ser:
              - Type.XYZ                     (grupo unitário; F_group=1)
              - (Type.A, Type.B, ...)        (grupo multivariado; F_group = nº de attrs no grupo)
            Ex.: [AREA, GRAY_HEIGHT, VARIANCE_LEVEL]
                 [AREA, (GRAY_HEIGHT, VARIANCE_LEVEL), GRAY_HEIGHT]
        tree_type : str
            "max-tree" | "min-tree" | "tos"
        device : str ou torch.device
            Dispositivo dos parâmetros e tensores gerados.
        assume_static_inputs : bool
            Mantido por compatibilidade; agora o cache é por conteúdo e criado on-the-fly.
        """
        super().__init__()
        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        self.device      = torch.device(device)
        self.assume_static_inputs = bool(assume_static_inputs)

        # Normaliza attributes_spec para uma lista de tuplas de Types (grupos)
        self.group_defs = []
        for item in attributes_spec:
            self.group_defs.append(tuple(item) if isinstance(item, (list, tuple)) else (item,))
        self.num_groups   = len(self.group_defs)
        # Saída padrão Conv2d: (B, out_channels, H, W)
        self.out_channels = self.in_channels * self.num_groups

        # Dimensão por grupo (F_group = nº de atributos no grupo, já que F_attr=1)
        self._group_F = {}
        for group in self.group_defs:
            gname = self._group_name(group)
            self._group_F[gname] = len(group)

        # ---------------- CACHES por CONTEÚDO ----------------
        # key = sha256(shape + dtype + canal + bytes)
        self._trees = {}            # key -> mmcfilters.MorphologicalTree
        self._base_attrs = {}       # key -> { Type -> Tensor (numNodes, 1) }
        self._group_feats = {}      # key -> { group_name -> Tensor (numNodes, F_group) }

        # ---------------- PARÂMETROS ----------------
        # Parâmetros por grupo (independentes da entrada):
        # - W_g em (F_group,)  [vetor]
        # - b_g em (1,)
        self._W = torch.nn.ParameterDict()  # group_name -> (F_group,)
        self._b = torch.nn.ParameterDict()  # group_name -> (1,)
        for group in self.group_defs:
            gname = self._group_name(group)
            Fg = self._group_F[gname]
            W = torch.empty(Fg, dtype=torch.float32, device=self.device)  # vetor
            torch.nn.init.uniform_(W, -1e-5, 1e-5)
            b = torch.empty(1, dtype=torch.float32, device=self.device)
            torch.nn.init.constant_(b, 1.0)
            self._W[gname] = torch.nn.Parameter(W, requires_grad=True)
            self._b[gname] = torch.nn.Parameter(b, requires_grad=True)

    # ---------------- HELPERs / UTILs ----------------
    def _group_name(self, group):
        """Gera um nome estável para o grupo (ex.: 'AREA' ou 'GRAY_HEIGHT+VARIANCE_LEVEL')."""
        return "+".join([t.name for t in group])

    @staticmethod
    def _hash_numpy(img_np: np.ndarray, chan_idx: int) -> str:
        """
        Cria uma hash estável a partir de shape, dtype, índice do canal e bytes da imagem.
        Usada para identificar unicamente (imagem, canal) no cache (content-addressable).
        """
        h = hashlib.sha256()
        h.update(np.int64(img_np.shape).tobytes())
        h.update(str(img_np.dtype).encode())
        h.update(np.int64(chan_idx).tobytes())
        h.update(img_np.tobytes())
        return h.hexdigest()

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        """
        Converte tensor (H,W) para numpy uint8 SEM reescalonar caso já esteja em [0,255]:
          - torch.uint8     -> retorna direto os bytes como np.uint8
          - float em [0,1]  -> escala ×255 e converte p/ np.uint8
          - float em [0,255]-> apenas converte p/ np.uint8 (não clipa nem reescala)
        """
        t = img2d_t.detach().to("cpu")

        # Caso 1: já é uint8
        if t.dtype == torch.uint8:
            return t.contiguous().numpy()

        # Caso 2: float
        arr = t.float().contiguous().numpy()
        mx = float(arr.max()) if arr.size > 0 else 1.0

        # Se parece estar em [0,1], escala para [0,255]; caso contrário, só converte:
        if mx <= 1.5:                      # heurística prática
            arr = arr * 255.0

        return arr.astype(np.uint8, copy=False)

    def _build_tree(self, img_np: np.ndarray):
        """Constrói a árvore morfológica segundo 'tree_type'."""
        if self.tree_type == "max-tree":
            return mmcfilters.MorphologicalTree(img_np, True)
        elif self.tree_type == "min-tree":
            return mmcfilters.MorphologicalTree(img_np, False)
        else:
            return mmcfilters.MorphologicalTree(img_np)  # ToS

    def _ensure_tree_and_base_attrs(self, key: str, img_np: np.ndarray):
        """
        Garante (cria se necessário) a árvore e os atributos-base por Type no cache da 'key'.
        Executado apenas uma vez por (imagem, canal).
        """
        if key in self._trees:
            return

        # Constrói árvore e registra:
        tree = self._build_tree(img_np)
        self._trees[key] = tree

        # Calcula cada atributo base UMA vez por key e guarda (F_attr=1 -> coluna única):
        per_attr = {}
        for group in self.group_defs:
            for attr_type in group:
                if attr_type in per_attr:
                    continue
                attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]  # (numNodes, 1)
                per_attr[attr_type] = torch.as_tensor(
                    attr_np, dtype=torch.float32, device=self.device
                ).contiguous()
        self._base_attrs[key] = per_attr

        # Inicializa dict para features de grupos (concatenações) que serão criadas sob demanda:
        self._group_feats[key] = {}

    def _ensure_group_feats(self, key: str, group):
        """
        Garante (concatena se necessário) as features do 'group' para a 'key'.
        Concatena as colunas dos atributos base: (numNodes, F_group).
        Como cada atributo é escalar, F_group = nº de atributos no grupo.
        """
        gname = self._group_name(group)
        if gname in self._group_feats[key]:
            return
        feats = [self._base_attrs[key][t] for t in group]  # lista de (numNodes, 1)
        self._group_feats[key][gname] = torch.cat(feats, dim=1).contiguous()  # (numNodes, F_group)

    # ---------------- FORWARD (cache on-the-fly por conteúdo) ----------------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x : torch.Tensor (B, C, H, W)
        return : torch.Tensor (B, out_channels, H, W)
        """
        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, mas input C={C}"

        # Aloca tensor de saída no device da camada:
        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        # Processa por (b, c) e por grupo, cacheando por CONTEÚDO (hash):
        for b in range(B):
            for c in range(C):
                # Gera key por conteúdo (hash da imagem + canal)
                img_np = self._to_numpy_u8(x[b, c])
                key = self._hash_numpy(img_np, c)

                # Garante que árvore/atributos estão no cache (se não, cria 1x)
                self._ensure_tree_and_base_attrs(key, img_np)
                tree = self._trees[key]

                # Garante features por grupo no cache (se não, concatena 1x)
                for group in self.group_defs:
                    self._ensure_group_feats(key, group)

                # Aplica por grupo
                for g, group in enumerate(self.group_defs):
                    gname = self._group_name(group)
                    feats = self._group_feats[key][gname]   # (numNodes, F_group)
                    Wg    = self._W[gname]                  # (F_group,)  vetor
                    bg    = self._b[gname]                  # (1,)

                    # Checagem defensiva: F_group do cache deve bater com Wg
                    if feats.shape[1] != Wg.numel():
                        raise RuntimeError(
                            f"Dimensão do grupo '{gname}' diverge: feats={feats.shape}, W={Wg.shape}"
                        )

                    y_ch = ConnectedFilterFunction.apply(tree, feats, Wg, bg)  # (H, W)
                    out[b, c * self.num_groups + g] = y_ch.to(self.device, dtype=torch.float32).contiguous()

        return out

    # ---------------- I/O DE PARÂMETROS ----------------
    def save_params(self, path: str):
        """
        Salva pesos e bias da camada em um arquivo .pt (PyTorch).
        Útil quando deseja congelar/inspecionar os parâmetros de grupos.
        """
        params = {}
        # Salva pesos por group_name:
        for gname in self._W.keys():
            params[f"W_{gname}"] = self._W[gname].detach().cpu()
        # Salva bias por group_name:
        for gname in self._b.keys():
            params[f"b_{gname}"] = self._b[gname].detach().cpu()
        torch.save(params, path)
        print(f"[ConnectedFilterLayer] parâmetros salvos em {path}")




# ============================
#  Versão com parâmetro threshold
# ============================
# --- acrescente estes imports se ainda não tiver ---
import hashlib
import torch
import numpy as np
import mmcfilters
import mtlearn

# ============================
#  Versão com parâmetro threshold BRUTO + normalização por árvore
# ============================
class ConnectedThresholdFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, tree, attr_scaled_1d, threshold_norm):
        """
        attr_scaled_1d: (numNodes,)  atributo já normalizado por-árvore
        threshold_norm: ()           limiar normalizado na MESMA escala de attr_scaled_1d
        """
        logits = attr_scaled_1d - threshold_norm.view(())
        sigmoid_soft = torch.sigmoid(logits).contiguous()   # (numNodes,)

        # ---------- STE: forward duro, backward mole ----------
        gate_hard = (sigmoid_soft >= 0.5).to(sigmoid_soft.dtype).contiguous()
        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filter(tree, gate_hard)

        # Para o backward usamos a sigmoide suave (derivada não-zero)
        ctx.tree = tree
        ctx.save_for_backward(sigmoid_soft)
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        (sigmoid_soft,) = ctx.saved_tensors
        tree = ctx.tree
        # Gradiente em relação ao threshold_norm usando a sigmoide suave
        grad_threshold_norm = mtlearn.ConnectedFilterByMorphologicalTree.gradients(
            tree,
            sigmoid_soft,                 # σ suave -> dσ/dthr = -σ(1-σ)
            grad_output.contiguous()
        )
        return None, None, grad_threshold_norm

class ConnectedThresholdLayer(torch.nn.Module):
    """
    Camada com um único parâmetro BRUTO 'thr_raw' por grupo.
    No forward, para CADA árvore:
      - escala o atributo bruto -> attr_scaled
      - escala o thr_raw        -> threshold_norm   (usando as MESMAS estatísticas da árvore)
      - aplica σ(attr_scaled - threshold_norm) e o filtering.
    """
    def __init__(self, in_channels, attributes_spec, tree_type="max-tree",
                 device="cpu", scale_mode: str = "minmax01", eps: float = 1e-6):
        super().__init__()
        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)
        self.eps         = float(eps)

        # grupos unitários (um atributo por grupo)
        self.group_defs = []
        for item in attributes_spec:
            group = tuple(item) if isinstance(item, (list, tuple)) else (item,)
            if len(group) != 1:
                raise ValueError("Cada grupo deve conter exatamente 1 atributo para o threshold.")
            self.group_defs.append(group)

        self.num_groups   = len(self.group_defs)
        self.out_channels = self.in_channels * self.num_groups

        # caches por conteúdo
        self._trees = {}      # key -> tree
        self._base_attrs = {} # key -> { Type -> Tensor (numNodes,1) }

        # parâmetro BRUTO: 1 thr_raw por grupo (compartilhado entre canais)
        # dica: se seu alvo original era AREA > 100, inicie com 100.0
        self._thr_raw = torch.nn.ParameterDict()
        for (attr_type,) in self.group_defs:
            name = attr_type.name
            p = torch.empty(1, dtype=torch.float32, device=self.device)
            torch.nn.init.constant_(p, 0.0)  # ajuste se souber um bom chute bruto (ex.: 100.0)
            self._thr_raw[name] = torch.nn.Parameter(p, requires_grad=True)

        # auto-init 1x do thr_raw a partir da primeira árvore (opcional)
        self._thr_raw_initialized = set()

    # ---------- util: normalização por árvore + conversão do thr_raw ----------
    def _scale_attr_and_threshold(self, a_1d: torch.Tensor, thr_raw: torch.Tensor):
        """
        Retorna:
          a_scaled (numNodes,)     atributo normalizado por-árvore
          thr_norm  ()             thr_raw convertido para a MESMA escala de a_scaled
        """
        mode, eps = self.scale_mode, self.eps
        thr_raw = thr_raw.view(())

        if mode == "none":
            return a_1d, thr_raw

        if mode == "log1p":
            a_scaled = torch.log1p(torch.clamp_min(a_1d, 0.0))
            thr_norm = torch.log1p(torch.clamp_min(thr_raw, 0.0))
            return a_scaled, thr_norm

        if mode == "minmax01":
            amin, amax = torch.min(a_1d), torch.max(a_1d)
            denom = torch.clamp(amax - amin, min=eps)
            a_scaled = (a_1d - amin) / denom
            thr_norm = (thr_raw - amin) / denom
            return a_scaled, thr_norm

        if mode == "log1p_minmax01":
            a = torch.log1p(torch.clamp_min(a_1d, 0.0))
            amin, amax = torch.min(a), torch.max(a)
            denom = torch.clamp(amax - amin, min=eps)
            a_scaled = (a - amin) / denom
            thr_norm = (torch.log1p(torch.clamp_min(thr_raw, 0.0)) - amin) / denom
            return a_scaled, thr_norm

        if mode == "zscore_tree":
            mean = torch.mean(a_1d)
            std  = torch.std(a_1d).clamp_min(eps)
            a_scaled = (a_1d - mean) / std
            thr_norm = (thr_raw - mean) / std
            return a_scaled, thr_norm

        if mode == "rank01":
            # NÃO recomendado para um único limiar global (não diferenciável em thr_raw).
            # Se realmente quiser, teria de aproximar a CDF com uma função suave.
            raise ValueError("scale_mode='rank01' não é adequado com thr_global bruto. Use 'none'/'minmax01'/'zscore_tree'/etc.")

        raise ValueError(f"scale_mode desconhecido: {mode}")

    # ---------- helpers de árvore/atributo ----------
    def _group_name(self, group): return "+".join([t.name for t in group])

    @staticmethod
    def _hash_numpy(img_np: np.ndarray, chan_idx: int) -> str:
        h = hashlib.sha256()
        h.update(np.int64(img_np.shape).tobytes())
        h.update(str(img_np.dtype).encode())
        h.update(np.int64(chan_idx).tobytes())
        h.update(img_np.tobytes())
        return h.hexdigest()

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        t = img2d_t.detach().to("cpu")
        if t.dtype == torch.uint8:
            return t.contiguous().numpy()
        arr = t.float().contiguous().numpy()
        mx = float(arr.max()) if arr.size > 0 else 1.0
        if mx <= 1.5: arr = arr * 255.0
        return arr.astype(np.uint8, copy=False)

    def _build_tree(self, img_np: np.ndarray):
        if self.tree_type == "max-tree":
            return mmcfilters.MorphologicalTree(img_np, True)
        elif self.tree_type == "min-tree":
            return mmcfilters.MorphologicalTree(img_np, False)
        else:
            return mmcfilters.MorphologicalTree(img_np)

    def _ensure_tree_and_attr(self, key: str, img_np: np.ndarray):
        if key in self._trees: return
        tree = self._build_tree(img_np)
        self._trees[key] = tree
        per_attr = {}
        for (attr_type,) in self.group_defs:
            if attr_type in per_attr: continue
            attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]  # (numNodes,1)
            per_attr[attr_type] = torch.as_tensor(attr_np, dtype=torch.float32, device=self.device).contiguous()
        self._base_attrs[key] = per_attr

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, mas input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                img_np = self._to_numpy_u8(x[b, c])
                key = self._hash_numpy(img_np, c)
                self._ensure_tree_and_attr(key, img_np)
                tree = self._trees[key]

                for g, (attr_type,) in enumerate(self.group_defs):
                    # atributo bruto por nó -> 1D
                    a1   = self._base_attrs[key][attr_type].squeeze(1).contiguous()   # (numNodes,)
                    name = attr_type.name
                    thr_raw = self._thr_raw[name]                                     # (1,) bruto

                    # auto-init 1x do thr_raw com percentil/mediana da PRIMEIRA árvore (opcional)
                    if name not in self._thr_raw_initialized:
                        with torch.no_grad():
                            # escolha sua estratégia: mediana (0.5) ou p75, etc.
                            init_val = torch.quantile(a1, 0.5)
                            self._thr_raw[name].copy_(init_val)
                        self._thr_raw_initialized.add(name)

                    # escala atributo E threshold para a MESMA escala por-árvore
                    a_scaled, thr_norm = self._scale_attr_and_threshold(a1, thr_raw)  # (numNodes,), ()

                    # forward via Function (grad do threshold_norm vem da sobrecarga C++)
                    y_ch = ConnectedThresholdFunction.apply(tree, a_scaled, thr_norm)  # (H,W)
                    out[b, c * self.num_groups + g] = y_ch.to(self.device, dtype=torch.float32).contiguous()

        return out

    # ---------- salvar / inspecionar ----------
    def save_params(self, path: str):
        """Salva SOMENTE os thresholds brutos (um por grupo)."""
        params = { f"thr_raw_{name}": p.detach().cpu() for name, p in self._thr_raw.items() }
        torch.save(params, path)
        print(f"[ConnectedThresholdLayer] thresholds BRUTOS salvos em {path}")

    def get_descaled_threshold(self, x: torch.Tensor = None, channel: int = 0):
        """
        Devolve o limiar NO DOMÍNIO BRUTO do atributo, por grupo.
        Não depende de imagem quando usamos thr_raw como parâmetro aprendível.
        Mantém assinatura compatível; 'x' é opcional aqui.
        """
        return { name: float(p.item()) for name, p in self._thr_raw.items() }
      
      
      
# Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterLayer',
    'ConnectedFilterFunction',
    'ConnectedThresholdLayer',
    'ConnectedThresholdFunction',
]