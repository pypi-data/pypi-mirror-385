"""
# -----------------------------------------------------------------------------
# ConnectedFilterLayerByThresholds (grupos de ≥1 atributos por saída)
# -----------------------------------------------------------------------------
# Objetivo
#   Aprender **um limiar normalizado por atributo** (vários por grupo) e combinar
#   os atributos de cada grupo via **mínimo das margens** (AND lógico):
#       m_k = a_k(normalizado) − τ_k   e   m_min = min_k m_k
#   Em seguida aplica-se σ(β_f · m_min) e o **filtering conectado** (C++).
#   O backward usa β_b na estimativa do gradiente para os limiares τ_k.
# Destaques
#   • Suporta grupos com K≥1 atributos (AND) por canal de entrada
#   • Normalização por **estatísticas do dataset** (minmax ou z-score)
#   • Cache de árvore/atributos por **hash SHA-256 do conteúdo**
#   • Auto-init de τ_k pelo **quantil do atributo normalizado** (1ª vez)
#   • Filtering em C++ **diferenciável** (árvore/atributos não são)
#   • Par de ganhos da sigmoide: **β_f** (forward) endurece/amassa a curva e
#     **β_b** (backward) controla a suavidade do gradiente dos limiares
# Boas práticas
#   • Empírico: β_f alto (e.g., 100–1000) acelera a convergência (forward ~hard);
#     manter β_b≈1 dá um backward soft e estável
#   • Use `predict(x, beta_f=1000)` para avaliação com forward ~hard sem autograd
# Exemplo rápido
#   layer = ConnectedFilterLayerByThresholds(
#       in_channels=1,
#       attributes_spec=[(mmcfilters.Type.AREA, mmcfilters.Type.GRAY_HEIGHT)],
#       tree_type="max-tree", scale_mode="minmax01", beta_f=1000.0, beta_b=1.0
#   )
#   y = layer(x)  # x: (B,1,H,W)
# -----------------------------------------------------------------------------
"""
import struct, hashlib
import torch
import numpy as np
import mmcfilters
import mtlearn


#
# --- Função customizada de autograd: grupos (K≥1) combinados por min-margin (AND) ---
class ConnectedFilterFunctionByThresholds(torch.autograd.Function):
    @staticmethod
    def forward(ctx, tree, *args):
        """
        Args:
            tree: Morphological tree (opaque handle)
            *args: a_scaled_1, ..., a_scaled_K, thr_1, ..., thr_K, beta_f, beta_b
                a_scaled_k: (numNodes,) float tensor (já **normalizado** por dataset)
                thr_k: () float tensor (limiar **normalizado** de A_k)
                beta_f: float (ganho da sigmoide **no forward**)
                beta_b: float (ganho usado **no backward**)
        Returns:
            y_pred: saída filtrada (H, W)

        Notas:
        • Combinação de grupo: m_k = a_k − τ_k  e  m_min = min_k m_k (AND lógico)
        • Forward: aplica σ(β_f · m_min). β_f grande ≈ limiar duro (STE prático)
        • Filtering C++ é diferenciável; árvore/atributos não: o gradiente afeta τ_k
        """
        total_args = len(args)
        if total_args < 4:
            raise RuntimeError("ConnectedFilterFunctionByGroupMinAND: argumentos insuficientes.")
        beta_f = float(args[-2])
        beta_b = float(args[-1])
        K = (total_args - 2) // 2
        if 2*K + 2 != total_args or K < 1:
            raise RuntimeError("ConnectedFilterFunctionByGroupMinAND: número de argumentos inconsistente.")

        a_scaled_k = list(args[:K])
        thr_k      = list(args[K:2*K])

        # Garantir dtypes/shapes
        margins_k = []
        for i in range(K):
            ai = a_scaled_k[i]
            ti = thr_k[i]
            if ai.dim() != 1:
                raise RuntimeError("a_scaled_k deve ter shape (numNodes,).")
            if ti.dim() != 0:
                raise RuntimeError("thr_k deve ser escalar 0-D.")
            ai = ai.to(dtype=torch.float32)
            ti = ti.to(dtype=torch.float32)
            margins_k.append(ai - ti.view(()))
        # Empilha margens (K, numNodes) e toma o mínimo por nó (AND entre atributos)
        m_stack = torch.stack(margins_k, dim=0)            # (K, numNodes)
        m_min, _ = torch.min(m_stack, dim=0)               # (numNodes,)
        # Sigmoide com ganho β_f no FORWARD (β_f alto ≈ passo/"hard").
        s = torch.sigmoid(torch.as_tensor(beta_f, dtype=torch.float32, device=m_min.device) * m_min)  # (numNodes,)
        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filtering(tree, s)

        # Guardamos {a_scaled_k} e {thr_k} para o backward (grad em τ_k)
        ctx.K = K
        ctx.beta_b = beta_b
        ctx.tree = tree
        # salve tensores necessários
        ctx.save_for_backward(*[t.to(torch.float32) for t in a_scaled_k],
                              *[t.to(torch.float32) for t in thr_k])
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        """Backward em τ_k usando β_b (ganho da sigmoide no estimador de gradiente)."""
        K = ctx.K
        beta_b = float(ctx.beta_b)
        tree = ctx.tree
        saved = ctx.saved_tensors
        a_scaled_k = saved[:K]
        thr_k      = saved[K:2*K]

        # Para cada atributo do grupo, calcula σ(β_b · (a_k − τ_k)) (colunas de sigmoids2d)
        sigmoids_k = []
        for k in range(K):
            logits_k = a_scaled_k[k] - thr_k[k].view(())
            s_k = torch.sigmoid(torch.as_tensor(beta_b, dtype=torch.float32, device=logits_k.device) * logits_k)
            sigmoids_k.append(s_k.to(torch.float32))
        sigmoids2d = torch.stack(sigmoids_k, dim=1).contiguous()  # (numNodes, K) float32

        # Gradiente w.r.t. os limiares por atributo (shape esperado: K)
        gradThresholds = mtlearn.ConnectedFilterByMorphologicalTree.gradientsOfThresholds(
            tree,
            sigmoids2d,
            float(beta_b),
            grad_output
        )

        # Monta lista de grads alinhada aos inputs: [None (tree), None... (a_scaled_k), grads τ_k..., None, None]
        grad_list = [None]
        grad_list += [None for _ in range(K)]  # a_scaled_k não requerem grad
        # gradThresholds esperado como (K,)
        for i in range(K):
            gi = gradThresholds[i] if isinstance(gradThresholds, torch.Tensor) else gradThresholds[i]
            grad_list.append(gi)
        grad_list += [None, None]  # beta_f, beta_b
        return tuple(grad_list)
    
# --- Camada PyTorch: grupos por min-margin (AND), normalização por dataset, cache ---
class ConnectedFilterLayerByThresholds(torch.nn.Module):
    """
    Agora o parâmetro aprendível é o(s) limiar(es) **normalizado(s)** `thr_norm` (um por **atributo**).
    Grupos podem ter **um ou mais atributos**. No forward, para CADA árvore e para CADA grupo:
      - para cada atributo `A_k` do grupo, computa a margem `m_k = a_k_normalizado - thr_norm_k`;
      - combina o grupo pelo **mínimo das margens**: `m_min = min_k m_k` (equivale a AND lógico: todos > threshold);
      - aplica σ(β_f · m_min) e faz o filtering.
    Se `top_hat=True`, aplica:
      • max-tree:  imagem - filtrado  
      • min-tree:  filtrado - imagem  
      • ToS:       abs(filtrado - imagem)  (subdiferenciável)
    Observação: com β_f grande (p.ex. ≥100), o forward se aproxima de um step (hard); com β_b≈1, o backward permanece suave.

    Parâmetros de forma da sigmoide:
    • β_f (forward): <1 suaviza; =1 padrão; >1 endurece (≈degrau para valores altos).
      Em prática, β_f≈100–1000 acelera a convergência.
    • β_b (backward): controla a suavidade da estimativa do gradiente em τ_k; 1 é um bom padrão.
    """
    def __init__(self, in_channels, attributes_spec, tree_type="max-tree", device="cpu", scale_mode: str = "minmax01", eps: float = 1e-6, initial_quantile_threshold: float = 0.5, beta_f: float = 1.0, beta_b: float = 1.0, top_hat: bool = False):
        super().__init__()
        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)   # 'minmax01' | 'zscore_tree' | 'none'
        self.eps         = float(eps)
        self.initial_quantile_threshold = float(initial_quantile_threshold)
        self.beta_f = float(beta_f)
        self.beta_b = float(beta_b)
        self.top_hat = bool(top_hat)
        
        # `attributes_spec` pode ter grupos com >=1 atributos. Cada τ_k é criado por atributo
        # único (compartilhado onde o atributo aparece em múltiplos grupos/canais).
        # grupos com >=1 atributos
        self.group_defs = []
        all_attr_types_set = set()
        for item in attributes_spec:
            group = tuple(item) if isinstance(item, (list, tuple)) else (item,)
            if len(group) < 1:
                raise ValueError("Cada grupo deve conter pelo menos 1 atributo.")
            self.group_defs.append(group)
            for at in group:
                all_attr_types_set.add(at)
        # lista estável de todos os atributos usados (para cache/stats)
        self._all_attr_types = list(all_attr_types_set)

        self.num_groups   = len(self.group_defs)
        self.out_channels = self.in_channels * self.num_groups

        # Caches por-chave de conteúdo: reutilizam árvore/atributos para imagens idênticas.
        # `_stats_epoch` força re-normalização quando as estatísticas do dataset mudam.
        self._trees      = {}  # key -> tree
        self._base_attrs = {}  # key -> { Type -> Tensor (numNodes,1) }
        self._norm_attrs = {}  # key -> { Type -> Tensor (numNodes,) }
        # versioning/invalidations for dataset-wide normalization
        self._stats_epoch = 0
        self._norm_epoch_by_key = {}
        # parâmetro NORMALIZADO: 1 thr_norm por **atributo** (compartilhado entre canais/grupos onde aparece)
        self._thr_norm = torch.nn.ParameterDict()
        for attr_type in self._all_attr_types:
            name = attr_type.name
            p = torch.empty(1, dtype=torch.float32, device=self.device)
            torch.nn.init.constant_(p, 0.5)  # meio da faixa normalizada é um bom ponto de partida
            self._thr_norm[name] = torch.nn.Parameter(p, requires_grad=True)

        # auto-init 1x do thr_norm a partir da primeira árvore (na escala normalizada)
        self._thr_norm_initialized = set()

        # dataset-level normalization stats
        self._ds_stats = {}

    # ---------- dataset-wide normalization helpers ----------
    def _update_ds_stats(self, attr_type, a_raw_1d: torch.Tensor):
        """Atualiza estatísticas de normalização do **dataset** (não por-árvore).
        • minmax01: expande [amin, amax] conforme chegam novas amostras
        • zscore_tree: mantém contagem/soma/soma² para média/variância contínuas
        • none: não faz nada
        Ao alterar stats, incrementa `_stats_epoch` para invalidar normalizações cacheadas.
        """
        if self.scale_mode == "minmax01":
            amin_new = torch.min(a_raw_1d.detach())
            amax_new = torch.max(a_raw_1d.detach())
            changed = False
            if attr_type not in self._ds_stats:
                self._ds_stats[attr_type] = {"amin": amin_new, "amax": amax_new}
                changed = True
            else:
                st = self._ds_stats[attr_type]
                # expand range only when needed
                if amin_new < st["amin"]:
                    st["amin"] = amin_new
                    changed = True
                if amax_new > st["amax"]:
                    st["amax"] = amax_new
                    changed = True
            if changed:
                self._stats_epoch += 1
        elif self.scale_mode == "zscore_tree":
            # Keep running aggregates: count, sum, sumsq
            v = a_raw_1d.detach().to(torch.float32)
            cnt = torch.tensor(v.numel(), dtype=torch.long)
            sm = torch.sum(v)
            sq = torch.sum(v * v)
            if attr_type not in self._ds_stats:
                self._ds_stats[attr_type] = {"count": cnt, "sum": sm, "sumsq": sq}
            else:
                self._ds_stats[attr_type]["count"] = self._ds_stats[attr_type]["count"] + cnt
                self._ds_stats[attr_type]["sum"]   = self._ds_stats[attr_type]["sum"] + sm
                self._ds_stats[attr_type]["sumsq"] = self._ds_stats[attr_type]["sumsq"] + sq
            # New samples always change mean/std -> bump epoch
            self._stats_epoch += 1
        elif self.scale_mode == "none":
            # No normalization needed
            pass
        else:
            raise ValueError(f"scale_mode desconhecido: {self.scale_mode}")

    def _normalize_with_ds_stats(self, attr_type, a_raw_1d: torch.Tensor) -> torch.Tensor:
        """Normaliza `a_raw_1d` usando stats globais acumuladas em `_ds_stats`.
        • minmax01: (x−amin)/(amax−amin);  • zscore_tree: (x−μ)/σ;  • none: identidade.
        Em caso de ausência de stats (primeiro batch), recorre a estatística do batch.
        """
        if self.scale_mode == "minmax01":
            stats = self._ds_stats.get(attr_type, None)
            if stats is None:
                # If no stats yet (first batch), fallback to per-batch minmax but also safe-clamp
                amin = torch.min(a_raw_1d)
                amax = torch.max(a_raw_1d)
            else:
                amin = stats["amin"]
                amax = stats["amax"]
            denom = torch.clamp(amax - amin, min=self.eps)
            return (a_raw_1d - amin) / denom
        elif self.scale_mode == "zscore_tree":
            stats = self._ds_stats.get(attr_type, None)
            if stats is None or stats["count"].item() == 0:
                mean = torch.mean(a_raw_1d)
                std  = torch.std(a_raw_1d).clamp_min(self.eps)
            else:
                count = stats["count"].to(torch.float32)
                mean  = stats["sum"] / count
                var   = stats["sumsq"] / count - mean * mean
                std   = torch.sqrt(torch.clamp(var, min=self.eps))
            return (a_raw_1d - mean) / std
        elif self.scale_mode == "none":
            return a_raw_1d
        else:
            raise ValueError(f"scale_mode desconhecido: {self.scale_mode}")

    def _maybe_refresh_norm_for_key(self, key: str):
        """Re-normaliza atributos cacheados da `key` quando `_stats_epoch` avança."""
        last_epoch = self._norm_epoch_by_key.get(key, -1)
        if last_epoch == self._stats_epoch:
            return
        # Re-normalize all attributes for this key from cached RAW attributes
        per_attr_raw = self._base_attrs[key]          # {attr_type: (numNodes,1)}
        per_attr_norm = {}
        for attr_type in self._all_attr_types:
            a_raw_1d = per_attr_raw[attr_type].squeeze(1)
            a_norm   = self._normalize_with_ds_stats(attr_type, a_raw_1d)
            per_attr_norm[attr_type] = a_norm
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- helpers de árvore/atributo ----------
    def _group_name(self, group): return "+".join([t.name for t in group])

    # Gera chave estável por (canal, shape, dtype, bytes) para o cache
    def _hash_tensor_sha256(self, t_u8: torch.Tensor, chan_idx: int):
        assert t_u8.device.type == "cpu", "hash só suporta tensor em CPU"
        if not t_u8.is_contiguous():
            t_u8 = t_u8.contiguous()
        assert t_u8.dtype == torch.uint8, "esperado uint8"
        h = hashlib.sha256()
        h.update(struct.pack("=I", chan_idx))
        h.update(struct.pack("=I", t_u8.ndimension()))
        for s in t_u8.shape:
            h.update(struct.pack("=I", int(s)))
        h.update(str(t_u8.dtype).encode())
        arr = t_u8.numpy()  # view sem cópia
        h.update(memoryview(arr))
        return h.hexdigest()

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        # Converte (H,W) para uint8:
        #   • se max≤1.5 assume [0,1] e escala x255; senão apenas faz cast p/ uint8
        #   • cuidado com truncamentos se a entrada já estiver >255
        t = img2d_t.detach().to("cpu")
        if t.dtype == torch.uint8:
            return (t if t.is_contiguous() else t.contiguous()).numpy()
        if t.numel() == 0:
            return t.to(torch.uint8).numpy()
        mx = float(t.max())
        if mx <= 1.5:
            u8 = (t * 255.0).to(torch.uint8)
        else:
            u8 = t.to(torch.uint8)
        return (u8 if u8.is_contiguous() else u8.contiguous()).numpy()

    # Constrói árvore morfológica conforme `tree_type` (max/min/ToS)
    def _build_tree(self, img_np: np.ndarray):
        if self.tree_type == "max-tree":
            return mmcfilters.MorphologicalTree(img_np, True)
        elif self.tree_type == "min-tree":
            return mmcfilters.MorphologicalTree(img_np, False)
        else:
            return mmcfilters.MorphologicalTree(img_np)

    def _ensure_tree_and_attr(self, key: str, img_np: np.ndarray):
        # Garante construção da árvore e cálculo de atributos brutos/normalizados
        if key in self._trees:
            return
        tree = self._build_tree(img_np)
        self._trees[key] = tree

        per_attr_raw, per_attr_norm = {}, {}
        for attr_type in self._all_attr_types:
            attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)

            # Atualiza stats globais do dataset (pode invalidar normalizações anteriores)
            self._update_ds_stats(attr_type, a_raw_1d)

            # Normaliza com as stats globais atuais do dataset
            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)

            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)  # debug/compat
            per_attr_norm[attr_type] = a_norm

        self._base_attrs[key] = per_attr_raw
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Aplica o filtro por grupo (min-margin AND) canal-a-canal.
        Passos por (b,c): hash→cache→(re)normaliza→σ(β_f·m_min)→filtering→(top-hat opcional).
        """
        assert x.dim() == 4, f"Esperado (B, C, H, W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, mas input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                img_np = self._to_numpy_u8(x[b, c])   # np.uint8 (CPU)
                t_u8   = torch.from_numpy(img_np)     # tensor CPU uint8 (view)
                key    = self._hash_tensor_sha256(t_u8, c)
                self._ensure_tree_and_attr(key, img_np)
                tree = self._trees[key]
                # If dataset-wide stats changed since this tree was cached, re-normalize on the fly
                self._maybe_refresh_norm_for_key(key)

                for g, group in enumerate(self.group_defs):
                    # Prepara listas {a_k} e {τ_k} do grupo g; auto-init 1x de τ_k por quantil
                    a_scaled_list = []
                    thr_list = []
                    for attr_type in group:
                        name     = attr_type.name
                        a_scaled = self._norm_attrs[key][attr_type]      # (numNodes,)
                        thr_norm = self._thr_norm[name].view(())          # ()
                        # auto-init 1x do thr_norm com o quantil do atributo NORMALIZADO
                        if name not in self._thr_norm_initialized:
                            with torch.no_grad():
                                init_val = torch.quantile(a_scaled, self.initial_quantile_threshold)
                                self._thr_norm[name].copy_(init_val)
                            self._thr_norm_initialized.add(name)
                        a_scaled_list.append(a_scaled)
                        thr_list.append(thr_norm)

                    # Chama a função robusta de grupo (K>=1) com β_f (forward) e β_b (backward)
                    y_ch = ConnectedFilterFunctionByThresholds.apply(
                        tree,
                        *a_scaled_list,   # tensors (numNodes,)
                        *thr_list,        # tensors ()
                        float(self.beta_f),
                        float(self.beta_b)
                    )
                    x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                    if self.top_hat:
                        tt = self.tree_type
                        if tt == "max-tree":
                            y_out = x_bc - y_ch
                        elif tt == "min-tree":
                            y_out = y_ch - x_bc
                        else:
                            # ToS (ou outros): top-hat absoluto
                            y_out = torch.abs(y_ch - x_bc)
                    else:
                        y_out = y_ch
                    out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)

        return out


    # ---------- predição / inferência ----------
    def predict(self, x: torch.Tensor, beta_f: float = 1000.0) -> torch.Tensor:
        """
        Realiza predição (inferência) sem gradiente usando um `beta_f` fixo (por padrão 1000).
        Essa função é equivalente ao forward, mas forçando o modo hard (~degrau)
        e desabilitando o cálculo de gradientes. Usa internamente β_f fixo para endurecer a sigmoide (forward ~hard).

        Após a execução, o modo de treino/avaliação do modelo é restaurado automaticamente ao estado anterior.

        Args:
            x (torch.Tensor): imagem de entrada (B, C, H, W)
            beta_f (float): ganho da sigmoide no forward (default: 1000)

        Returns:
            torch.Tensor: saída filtrada (mesmas dimensões do forward)
        """
        was_training = self.training  # guarda o estado atual (train ou eval)
        self.eval()  # muda temporariamente para modo avaliação
        with torch.no_grad():
            B, C, H, W = x.shape
            out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

            for b in range(B):
                for c in range(C):
                    img_np = self._to_numpy_u8(x[b, c])   # np.uint8 (CPU)
                    t_u8   = torch.from_numpy(img_np)     # tensor CPU uint8 (view)
                    key    = self._hash_tensor_sha256(t_u8, c)
                    self._ensure_tree_and_attr(key, img_np)
                    tree = self._trees[key]
                    # If dataset-wide stats changed since this tree was cached, re-normalize on the fly
                    self._maybe_refresh_norm_for_key(key)

                    for g, group in enumerate(self.group_defs):
                        # -- Grupo g pode ter >=1 atributos: compute min-margin (AND) --
                        a_scaled_list = []
                        thr_list = []
                        for attr_type in group:
                            name     = attr_type.name
                            a_scaled = self._norm_attrs[key][attr_type]      # (numNodes,)
                            thr_norm = self._thr_norm[name].view(())          # ()
                            a_scaled_list.append(a_scaled)
                            thr_list.append(thr_norm)

                        # Call robust group-min-AND function (handles K>=1):
                        y_ch = ConnectedFilterFunctionByThresholds.apply(
                            tree,
                            *a_scaled_list,   # tensors (numNodes,)
                            *thr_list,        # tensors ()
                            float(beta_f),
                            float(self.beta_b)
                        )
                        x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                        if self.top_hat:
                            tt = self.tree_type
                            if tt == "max-tree":
                                y_out = x_bc - y_ch
                            elif tt == "min-tree":
                                y_out = y_ch - x_bc
                            else:
                                # ToS (ou outros): top-hat absoluto
                                y_out = torch.abs(y_ch - x_bc)
                        else:
                            y_out = y_ch
                        out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)
            

        # Restaura o modo anterior (train/eval)
        if was_training:
            self.train()
        else:
            self.eval()
        return out

    # ---------- salvar / inspecionar ----------
    def save_params(self, path: str):
        """Salva os thresholds **normalizados** (um por atributo)."""
        params = { f"thr_norm_{name}": p.detach().cpu() for name, p in self._thr_norm.items() }
        torch.save(params, path)
        print(f"[ConnectedThresholdLayer] thresholds NORMALIZADOS salvos em {path}")

    def get_descaled_threshold(self, channel: int = 0):
        """
        Converte cada `thr_norm` para o domínio BRUTO usando as stats GLOBAIS do dataset
        acumuladas até o momento (dataset-wide normalization).
        Independente de β_f/β_b, a desscala reflete as stats globais correntes.
        """
        if not self._ds_stats:
            raise RuntimeError("Sem stats de dataset. Rode um forward ao menos uma vez para acumular estatísticas.")

        out = {}
        for attr_type in self._all_attr_types:
            name = attr_type.name
            thrn = float(self._thr_norm[name].item())

            if self.scale_mode == "minmax01":
                stats = self._ds_stats.get(attr_type, None)
                if stats is None:
                    raise RuntimeError("Stats minmax do dataset inexistentes. Rode um forward primeiro.")
                amin = float(stats["amin"].item())
                amax = float(stats["amax"].item())
                thr_raw = thrn * (amax - amin) + amin
            elif self.scale_mode == "zscore_tree":
                stats = self._ds_stats.get(attr_type, None)
                if stats is None or stats["count"].item() == 0:
                    raise RuntimeError("Stats zscore do dataset inexistentes. Rode um forward primeiro.")
                count = stats["count"].to(torch.float32)
                mean  = float((stats["sum"] / count).item())
                var   = float((stats["sumsq"] / count - (stats["sum"] / count) ** 2).item())
                std   = float(np.sqrt(max(var, self.eps)))
                thr_raw = thrn * std + mean
            elif self.scale_mode == "none":
                thr_raw = thrn
            else:
                raise ValueError(f"scale_mode desconhecido: {self.scale_mode}")

            out[name] = float(thr_raw)

        return out

    def refresh_cached_normalization(self):
        """Re-normaliza os atributos de TODAS as árvores cacheadas com as stats de dataset atuais.
        Não altera β_f/β_b; apenas re-normaliza os atributos em cache."""
        for key in list(self._base_attrs.keys()):
            self._maybe_refresh_norm_for_key(key)


# Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterLayerByThresholds',
    'ConnectedFilterFunctionByThresholds',
]