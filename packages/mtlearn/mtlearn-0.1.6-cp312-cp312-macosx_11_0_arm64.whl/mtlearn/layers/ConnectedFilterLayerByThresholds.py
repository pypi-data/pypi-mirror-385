"""
# -----------------------------------------------------------------------------
# ConnectedFilterLayerBySingleThreshold
# -----------------------------------------------------------------------------
# Objetivo:
#   Camada PyTorch que aprende um ÚNICO limiar normalizado por atributo
#   (um por grupo) e aplica um filtro conectado em árvores morfológicas
#   (max-tree, min-tree ou ToS). Oferece opção de saída top-hat.
# Destaques:
#   • Normalização por ESTATÍSTICAS DO DATASET (minmax ou z-score)
#   • Cache por conteúdo (árvore/atributos) com hash SHA-256
#   • Limiar autoinicializado por quantil do atributo NORMALIZADO
#   • Par de ganhos da sigmoide: `beta_f` (forward) e `beta_b` (backward)
#       - < 1: mais suave; = 1: sigmoide padrão; > 1: mais “degrau”
#       - Recomendado p/ STE: beta_f=1000 (forward ~hard), beta_b=1 (backward soft)
#   • A **filtragem conectada** em C++ expõe gradientes (é diferenciável). Já a
#     construção da árvore e o cálculo de atributos não são; assim, o gradiente flui
#     principalmente para o **limiar normalizado** (`thr_norm`).
# -----------------------------------------------------------------------------

# Resumo de alto nível
#   • Esta camada aprende **um limiar normalizado** por atributo (um por grupo)
#     e aplica um **filtro conectado** usando árvores morfológicas.
#   • Os atributos são **normalizados por estatísticas do dataset** (minmax ou z-score),
#     armazenadas e atualizadas ao longo do treino. Quando mudam, a camada re-normaliza
#     automaticamente os atributos em cache.
#   • A computação da árvore/atributos ocorre em **CPU (C++)** e não é diferenciável; o
#     gradiente flui apenas para o **limiar normalizado** (`thr_norm`).
#   • Com os **defaults** `beta_f=1000` e `beta_b=1`, o comportamento é o clássico
#     **forward hard / backward soft** (tipo STE): forward ~degrau e backward com
#     gradiente suave.
#   • A camada também suporta **top-hat** opcional após o filtering.
#
#   • Observação empírica: uma sigmoide muito "soft" (beta_f baixo) tende a tornar o
#     treinamento lento; endurecer a curva (beta_f alto, e.g., 1000) costuma acelerar
#     a convergência — mantendo beta_b=1 para um backward mais estável (soft).
#   • Estabilidade numérica: com `clamp_logits=True` (default), clampamos beta_f*logits em ±12
#     apenas na hora da sigmoide, evitando NaNs sem alterar o restante do fluxo.
#
# Exemplo de uso (PyTorch)
# -----------------------------------------------------------------------------
# import torch
# import mmcfilters
# from mtlearn.layers.ConnectedFilterLayerBySingleThreshold import (
#     ConnectedFilterLayerBySingleThreshold,
# )
#
# # 1) Construa a camada: 1 canal de entrada, 1 atributo por grupo
# layer = ConnectedFilterLayerBySingleThreshold(
#     in_channels=1,
#     attributes_spec=[(mmcfilters.Type.AREA,)],   # escolha o atributo do mmcfilters
#     tree_type="max-tree",                       # "max-tree" | "min-tree" | ToS
#     device="cpu",                               # CPU obrigatória p/ a árvore atual
#     scale_mode="minmax01",                      # ou "zscore_tree" | "none"
#     top_hat=False,                               # True para top-hat
#     #     clamp_logits=True,                       # clamp ±12 só na sigmoide (default)
#     # beta_f=1000.0, beta_b=1.0                  # defaults já são 1000/1
# )
#
# # 2) Crie um batch (B=1, C=1, H, W) em [0,255]
# img = torch.randint(0, 256, (128, 128), dtype=torch.uint8)
# x = img.float().unsqueeze(0).unsqueeze(0)  # (1,1,H,W)
#
# # 3) Forward + backward
# y = layer(x)                       # (1, out_channels=1, H, W)
# loss = y.mean()
# loss.backward()                    # gradiente vai para `thr_norm`
#
# # 4) Inspecione o limiar no domínio bruto do atributo
# print(layer.get_descaled_threshold())
#
# # 5) (Opcional) Salve os thresholds normalizados
# layer.save_params("thr_norm.pt")
"""
import torch
import numpy as np
import mmcfilters
import mtlearn
from ._helpers import (
    hash_tensor_sha256,
    to_numpy_u8,
    build_tree,
    update_ds_stats,
    normalize_with_ds_stats,
    maybe_refresh_norm_for_key,
)
# ============================
#  Versão GENERALIZADA p/ grupos com ≥1 atributos
#  Combinação: produto de distâncias absolutas  prod_j |a_j - t_j|
#  STE: forward usa beta_f, backward usa beta_b
#  Backward dos limiares: usa C++ gradientsOfThreshold(..., sigmoid_soft2D, ...)
# ============================
import torch
import numpy as np
import mmcfilters
import mtlearn
import hashlib, struct
from ._helpers import (
    hash_tensor_sha256,
    to_numpy_u8,
    build_tree,
    update_ds_stats,
    normalize_with_ds_stats,
    maybe_refresh_norm_for_key,
)

# ---------------------------------------------------------------------
# Function custom — grupos com múltiplos atributos
# ---------------------------------------------------------------------
class ConnectedFilterFunctionByThresholds(torch.autograd.Function):
    """
    forward(tree, attrs_scaled_stack, thr_norm_vec, beta_f=1000.0, beta_b=1.0, clamp_logits=True)

    Parâmetros:
      - attrs_scaled_stack: (Gg, N)  # Gg = nº de atributos do grupo; N = numNodes
      - thr_norm_vec:       (Gg,)    # thresholds normalizados (mesma escala de attrs)
      - beta_f / beta_b: ganhos da sigmoide p/ forward/backward (STE)
      - clamp_logits: limita beta*logits em ±12 na sigmoide (evita NaNs)

    Forward:
      • d = prod_j |a_j - t_j|  -> logits1D = -d
      • sigmoid1D = sigmoid(beta_f * logits1D)  -> filtering(tree, sigmoid1D)
      • sigmoid2D[j,:] = sigmoid(beta_b * (a_j - t_j))  (salva para o backward)

    Backward:
      • Usa sigmoid2D salva e chama:
        grad_thresholds2D_norm = gradientsOfThreshold(tree, sigmoid2D, beta_b, grad_output)
      • Retorna dL/d thr_norm_vec (shape (Gg,))
    """
    @staticmethod
    def forward(ctx, tree, attrs_scaled_stack, thr_norm_vec,
                beta_f: float = 1000.0, beta_b: float = 1.0, clamp_logits: bool = True):
        # --- checagens básicas ---
        if attrs_scaled_stack.dim() != 2:
            raise ValueError("attrs_scaled_stack deve ser 2D (Gg, N).")
        Gg, N = attrs_scaled_stack.shape
        if thr_norm_vec.dim() != 1 or thr_norm_vec.numel() != Gg:
            raise ValueError("thr_norm_vec deve ser (Gg,) com Gg = attrs_scaled_stack.size(0).")

        # ----- (A) Máscara 1D para o filtering (via produto de distâncias) -----
        diffs  = torch.abs(attrs_scaled_stack - thr_norm_vec.view(-1, 1))  # (Gg, N)
        d_prod = diffs.prod(dim=0)                                         # (N,)
        logits1D = -d_prod
        s1 = beta_f * logits1D
        if clamp_logits:
            s1 = torch.clamp(s1, -12.0, 12.0)
        sigmoid1D = torch.sigmoid(s1)                                      # (N,)

        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filtering(tree, sigmoid1D)  # (H,W)

        # ----- (B) Versão 2D (uma linha por atributo) salva para o backward -----
        #        sigmoid2D[j,:] = sigmoid(beta_b * (a_j - t_j))
        s2 = beta_b * (attrs_scaled_stack - thr_norm_vec.view(-1, 1))      # (Gg, N)
        if clamp_logits:
            s2 = torch.clamp(s2, -12.0, 12.0)
        sigmoid2D = torch.sigmoid(s2)                                      # (Gg, N)

        # Guarda tudo que o backward precisa
        ctx.tree = tree
        ctx.beta_b = float(beta_b)
        ctx.clamp_logits = bool(clamp_logits)
        # Salva diretamente a sigmoid2D (evita recomputar e garante consistência)
        ctx.save_for_backward(sigmoid2D)

        # Nada além de y_pred precisa grad daqui
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        (sigmoid2D,) = ctx.saved_tensors  # (Gg, N)
        tree   = ctx.tree
        beta_b = ctx.beta_b

        # Nota: grad_output vem com shape (H, W). A função C++ sabe projetar isso
        # para o espaço dos nós (N) internamente, usando a árvore.
        # Retorna dL/d t_j para cada atributo do grupo (shape (Gg,))
        grad_thresholds2D_norm = mtlearn.ConnectedFilterByMorphologicalTree.gradientsOfThreshold(
            tree, sigmoid2D, beta_b, grad_output
        )

        # Retornos alinhados com os args do forward:
        # (grad_tree, grad_attrs_scaled_stack, grad_thr_norm_vec, grad_beta_f, grad_beta_b, grad_clamp)
        return (None, None, grad_thresholds2D_norm, None, None, None)

# ---------------------------------------------------------------------
# Camada PyTorch — GENERALIZADA
# ---------------------------------------------------------------------
class ConnectedFilterLayerByThresholds(torch.nn.Module):
    """
    Suporta GRUPOS com ≥1 atributos. Para o grupo g com atributos {a_{g,j}} e thresholds {t_{g,j}}:

        d_g(n)      =  Π_j | a_{g,j}(n) - t_{g,j} |
        logits_g(n) = - d_g(n)
        s_f         = sigmoid(beta_f * logits_g)    # forward
        s_b         = sigmoid(beta_b * logits_g)    # só para intuição do STE (grad via C++)
        s2D[j,:]    = sigmoid(beta_b * (a_{g,j} - t_{g,j}))  # passa ao C++ p/ grad dos thresholds

    A camada chama a Function acima, que usa o `gradientsOfThreshold(...)` no backward.
    Mantém: predict, save_params, get_descaled_threshold, refresh_cached_normalization.
    """
    def __init__(
        self,
        in_channels,
        attributes_spec,               # Iterable[Type | Iterable[Type]]
        tree_type="max-tree",
        device="cpu",
        scale_mode: str = "minmax01",
        eps: float = 1e-6,
        initial_quantile_threshold: float = 0.5,
        beta_f: float = 1000.0,
        beta_b: float = 1.0,
        top_hat: bool = False,
        clamp_logits: bool = True,
    ):
        super().__init__()
        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        if device != "cpu":
            raise ValueError("O modelo só está implementado para CPU.")
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)
        self.eps         = float(eps)
        self.initial_quantile_threshold = float(initial_quantile_threshold)
        self.beta_f = float(beta_f)
        self.beta_b = float(beta_b)
        self.top_hat = bool(top_hat)
        self.clamp_logits = bool(clamp_logits)

        # -------- grupos com ≥1 atributos --------
        self.group_defs = []
        for item in attributes_spec:
            group = tuple(item) if isinstance(item, (list, tuple)) else (item,)
            if len(group) < 1:
                raise ValueError("Cada grupo deve conter pelo menos 1 atributo.")
            self.group_defs.append(group)

        self.num_groups   = len(self.group_defs)
        self.out_channels = self.in_channels * self.num_groups

        # Conjunto de TODOS os tipos de atributo necessários (para cache/normalização)
        self._attr_types = []
        seen = set()
        for group in self.group_defs:
            for attr_type in group:
                if attr_type not in seen:
                    seen.add(attr_type)
                    self._attr_types.append(attr_type)

        # caches
        self._trees      = {}   # key -> tree
        self._base_attrs = {}   # key -> { Type -> Tensor (numNodes,1) }
        self._norm_attrs = {}   # key -> { Type -> Tensor (numNodes,)   }
        self._stats_epoch = 0
        self._norm_epoch_by_key = {}

        # ---------- parâmetros aprendíveis (thresholds normalizados) ----------
        # um threshold por (grupo g, atributo j): nome "G{g}:{ATTR}"
        self._thr_norm = torch.nn.ParameterDict()
        for g, group in enumerate(self.group_defs):
            for attr_type in group:
                name = f"G{g}:{attr_type.name}"
                p = torch.empty(1, dtype=torch.float32, device=self.device)
                torch.nn.init.constant_(p, 0.5)
                self._thr_norm[name] = torch.nn.Parameter(p, requires_grad=True)

        # autoinit 1x por (g, attr) com quantil do atributo normalizado
        self._thr_norm_initialized = set()

        # dataset-level normalization stats
        self._ds_stats = {}

    # ---------- dataset-wide normalization helpers ----------
    def _update_ds_stats(self, attr_type, a_raw_1d: torch.Tensor):
        changed = update_ds_stats(self._ds_stats, self.scale_mode, attr_type, a_raw_1d)
        if changed:
            self._stats_epoch += 1

    def _normalize_with_ds_stats(self, attr_type, a_raw_1d: torch.Tensor) -> torch.Tensor:
        return normalize_with_ds_stats(self._ds_stats, self.scale_mode, self.eps, attr_type, a_raw_1d)

    def _maybe_refresh_norm_for_key(self, key: str):
        maybe_refresh_norm_for_key(
            key, self._base_attrs, self._norm_attrs, self._attr_types,
            self._ds_stats, self.scale_mode, self.eps,
            self._norm_epoch_by_key, self._stats_epoch
        )

    # ---------- helpers de árvore/atributo ----------
    def _hash_tensor_sha256(self, t_u8: torch.Tensor, chan_idx: int):
        return hash_tensor_sha256(t_u8, chan_idx)

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        return to_numpy_u8(img2d_t)

    def _build_tree(self, img_np: np.ndarray):
        return build_tree(img_np, self.tree_type)

    def _ensure_tree_and_attr(self, key: str, img_np: np.ndarray):
        if key in self._trees:
            return
        tree = self._build_tree(img_np)
        self._trees[key] = tree

        per_attr_raw, per_attr_norm = {}, {}
        for attr_type in self._attr_types:
            attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
            self._update_ds_stats(attr_type, a_raw_1d)
            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)
            per_attr_norm[attr_type] = a_norm

        self._base_attrs[key] = per_attr_raw
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Para cada (b,c) e grupo g:
          • attrs_stack = stack_j a_{g,j} (normalizados)           -> (Gg, N)
          • thr_vec     = stack_j t_{g,j} (aprendidos, normalizados)-> (Gg,)
          • y = Function.apply(tree, attrs_stack, thr_vec, beta_f, beta_b, clamp)
          • (opcional) top-hat sobre y
        """
        assert x.dim() == 4, f"Esperado (B, C, H, W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, mas input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                img_np = self._to_numpy_u8(x[b, c])
                t_u8   = torch.from_numpy(img_np)
                key    = self._hash_tensor_sha256(t_u8, c)

                self._ensure_tree_and_attr(key, img_np)
                self._maybe_refresh_norm_for_key(key)
                tree = self._trees[key]

                for g, group in enumerate(self.group_defs):
                    # Empilha atributos normalizados e thresholds do grupo
                    a_list, thr_list = [], []
                    for attr_type in group:
                        a_scaled = self._norm_attrs[key][attr_type]          # (N,)
                        pname    = f"G{g}:{attr_type.name}"
                        thr      = self._thr_norm[pname]                      # (1,)

                        # autoinit 1x
                        if pname not in self._thr_norm_initialized:
                            with torch.no_grad():
                                init_val = torch.quantile(a_scaled, self.initial_quantile_threshold)
                                self._thr_norm[pname].copy_(init_val)
                            self._thr_norm_initialized.add(pname)

                        a_list.append(a_scaled)
                        thr_list.append(thr.view(()))

                    attrs_stack = torch.stack(a_list, dim=0)   # (Gg, N)
                    thr_vec     = torch.stack(thr_list, dim=0) # (Gg,)

                    y_ch = ConnectedFilterFunctionByThresholds.apply(tree, attrs_stack, thr_vec, self.beta_f, self.beta_b, self.clamp_logits)  # (H,W)

                    x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                    if self.top_hat:
                        tt = self.tree_type
                        if tt == "max-tree":
                            y_out = x_bc - y_ch
                        elif tt == "min-tree":
                            y_out = y_ch - x_bc
                        else:
                            y_out = torch.abs(y_ch - x_bc)
                    else:
                        y_out = y_ch

                    out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)

        return out

    # ---------- predição / inferência ----------
    def predict(self, x: torch.Tensor, beta_f: float = 1000.0) -> torch.Tensor:
        was_training = self.training
        self.eval()
        with torch.no_grad():
            B, C, H, W = x.shape
            out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)
            for b in range(B):
                for c in range(C):
                    img_np = self._to_numpy_u8(x[b, c])
                    t_u8   = torch.from_numpy(img_np)
                    key    = self._hash_tensor_sha256(t_u8, c)

                    self._ensure_tree_and_attr(key, img_np)
                    self._maybe_refresh_norm_for_key(key)
                    tree = self._trees[key]

                    for g, group in enumerate(self.group_defs):
                        a_list, thr_list = [], []
                        for attr_type in group:
                            a_scaled = self._norm_attrs[key][attr_type]
                            pname    = f"G{g}:{attr_type.name}"
                            thr      = self._thr_norm[pname]
                            a_list.append(a_scaled)
                            thr_list.append(thr.view(()))

                        attrs_stack = torch.stack(a_list, dim=0)
                        thr_vec     = torch.stack(thr_list, dim=0)

                        # usa beta_f escolhido p/ inferência (backward não é usado)
                        y_ch = ConnectedFilterFunctionByThresholds.apply(tree, attrs_stack, thr_vec, beta_f, self.beta_b, self.clamp_logits)
                        x_bc = x[b, c].to(dtype=torch.float32, device=self.device)

                        if self.top_hat:
                            tt = self.tree_type
                            if tt == "max-tree":
                                y_out = x_bc - y_ch
                            elif tt == "min-tree":
                                y_out = y_ch - x_bc
                            else:
                                y_out = torch.abs(y_ch - x_bc)
                        else:
                            y_out = y_ch

                        out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)
        self.train(was_training)
        return out

    # ---------- salvar / inspecionar ----------
    def save_params(self, path: str):
        payload = {
            "thresholds_norm": { name: p.detach().cpu() for name, p in self._thr_norm.items() },
            "ds_stats": self._ds_stats,
            "scale_mode": self.scale_mode,
        }
        for name, p in self._thr_norm.items():
            payload[f"thr_norm_{name}"] = p.detach().cpu()
        torch.save(payload, path)
        print(f"[ConnectedThresholdLayer] thresholds NORMALIZADOS + ds_stats salvos em {path}")

    def get_descaled_threshold(self):
        """
        Retorna dict: { grupo_index: { attr_name: thr_raw } }
        desscalado para o domínio bruto de cada atributo (stats globais).
        """
        if not self._ds_stats:
            raise RuntimeError("Sem stats de dataset. Rode um forward ao menos uma vez.")
        out = {}
        for g, group in enumerate(self.group_defs):
            out_g = {}
            for attr_type in group:
                pname = f"G{g}:{attr_type.name}"
                thrn  = float(self._thr_norm[pname].item())
                if self.scale_mode == "minmax01":
                    st = self._ds_stats.get(attr_type, None)
                    if st is None:
                        raise RuntimeError("Stats minmax inexistentes; rode um forward primeiro.")
                    amin = float(st["amin"].item()); amax = float(st["amax"].item())
                    thr_raw = thrn * (amax - amin) + amin
                elif self.scale_mode == "zscore_tree":
                    st = self._ds_stats.get(attr_type, None)
                    if st is None or st["count"].item() == 0:
                        raise RuntimeError("Stats zscore inexistentes; rode um forward primeiro.")
                    count = st["count"].to(torch.float32)
                    mean  = float((st["sum"] / count).item())
                    var   = float((st["sumsq"] / count - (st["sum"] / count) ** 2).item())
                    std   = float(np.sqrt(max(var, self.eps)))
                    thr_raw = thrn * std + mean
                elif self.scale_mode == "none":
                    thr_raw = thrn
                else:
                    raise ValueError(f"scale_mode desconhecido: {self.scale_mode}")
                out_g[attr_type.name] = float(thr_raw)
            out[g] = out_g
        return out

    def refresh_cached_normalization(self):
        for key in list(self._base_attrs.keys()):
            self._maybe_refresh_norm_for_key(key)


__all__ = [
    'ConnectedFilterLayerByThresholds',
    'ConnectedFilterFunctionByThresholds',
]