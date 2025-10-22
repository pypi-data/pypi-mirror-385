import struct, hashlib
import torch
import numpy as np
import mmcfilters
import mtlearn

# ============================
#  Versão com parâmetro threshold NORMALIZADO + normalização por árvore
# ============================
class ConnectedFilterFunctionBySingleThreshold(torch.autograd.Function):
    @staticmethod
    def forward(ctx, tree, attr_scaled_1d, threshold_norm, beta_f: float=1.0, beta_b: float=1.0 ):
        """
        attr_scaled_1d: (numNodes,)  atributo já normalizado por-árvore
        threshold_norm: ()           limiar normalizado na MESMA escala de attr_scaled_1d
        """
        logits = attr_scaled_1d - threshold_norm.view(())
        sigmoid_soft1D = torch.sigmoid(beta_f*logits)   # (numNodes,)
        #sigmoid_soft2D = torch.sigmoid(beta*logits).unsqueeze(1) # (numNodes,1)

        # ---------- STE: forward duro, backward mole ----------
        #gate_hard = (sigmoid_soft1D >= 0.5).to(sigmoid_soft1D.dtype)
        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filtering(tree, sigmoid_soft1D)

        ctx.tree = tree
        ctx.beta_b = beta_b
        ctx.save_for_backward(sigmoid_soft1D)
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        (sigmoid_soft1D,) = ctx.saved_tensors
        tree = ctx.tree
        beta_b = ctx.beta_b
        grad_threshold_norm = mtlearn.ConnectedFilterByMorphologicalTree.gradientsOfThreshold(tree, sigmoid_soft1D, beta_b, grad_output)
        return None, None, grad_threshold_norm, None, None


class ConnectedFilterLayerBySingleThreshold(torch.nn.Module):
    """
    Agora o parâmetro aprendível é o limiar **normalizado** `thr_norm` (um por grupo).
    No forward, para CADA árvore:
      - usa o atributo **normalizado** cacheado (por árvore)
      - aplica σ(attr_scaled - thr_norm) e o filtering.
    Se `top_hat=True`, aplica:
      • max-tree:  imagem - filtrado  
      • min-tree:  filtrado - imagem  
      • ToS:       abs(filtrado - imagem)  (subdiferenciável)
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
        self._trees      = {}  # key -> tree
        self._base_attrs = {}  # key -> { Type -> Tensor (numNodes,1) }
        self._norm_attrs = {}  # key -> { Type -> Tensor (numNodes,) }
        # versioning/invalidations for dataset-wide normalization
        self._stats_epoch = 0                   # increments whenever ds stats change
        self._norm_epoch_by_key = {}            # key -> epoch when normalization was computed
        # parâmetro NORMALIZADO: 1 thr_norm por grupo (compartilhado entre canais)
        self._thr_norm = torch.nn.ParameterDict()
        for (attr_type,) in self.group_defs:
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
        """Update dataset-level stats for normalization, using raw (non-normalized) attribute.
        If stats change, bump the epoch to invalidate cached normalized attributes.
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
        """Normalize a_raw_1d using dataset-level stats accumulated in self._ds_stats."""
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
        """Recompute normalized attributes for a cached tree when dataset stats epoch advanced."""
        last_epoch = self._norm_epoch_by_key.get(key, -1)
        if last_epoch == self._stats_epoch:
            return
        # Re-normalize all attributes for this key from cached RAW attributes
        per_attr_raw = self._base_attrs[key]          # {attr_type: (numNodes,1)}
        per_attr_norm = {}
        for (attr_type,) in self.group_defs:
            a_raw_1d = per_attr_raw[attr_type].squeeze(1)
            a_norm   = self._normalize_with_ds_stats(attr_type, a_raw_1d)
            per_attr_norm[attr_type] = a_norm
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- helpers de árvore/atributo ----------
    def _group_name(self, group): return "+".join([t.name for t in group])

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

    def _build_tree(self, img_np: np.ndarray):
        if self.tree_type == "max-tree":
            return mmcfilters.MorphologicalTree(img_np, True)
        elif self.tree_type == "min-tree":
            return mmcfilters.MorphologicalTree(img_np, False)
        else:
            return mmcfilters.MorphologicalTree(img_np)

    def _ensure_tree_and_attr(self, key: str, img_np: np.ndarray):
        if key in self._trees:
            return
        tree = self._build_tree(img_np)
        self._trees[key] = tree

        per_attr_raw, per_attr_norm = {}, {}
        for (attr_type,) in self.group_defs:
            attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)

            # Update dataset-level stats on first-seen trees and every new tree
            self._update_ds_stats(attr_type, a_raw_1d)

            # Normalize using dataset-level stats (not per-tree)
            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)

            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)  # debug/compat
            per_attr_norm[attr_type] = a_norm

        self._base_attrs[key] = per_attr_raw
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
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

                for g, (attr_type,) in enumerate(self.group_defs):
                    name      = attr_type.name
                    a_scaled  = self._norm_attrs[key][attr_type]  # (numNodes,)

                    thr_norm  = self._thr_norm[name]              # (1,)

                    # auto-init 1x do thr_norm com o quantil do atributo NORMALIZADO
                    if name not in self._thr_norm_initialized:
                        with torch.no_grad():
                            init_val = torch.quantile(a_scaled, self.initial_quantile_threshold)
                            self._thr_norm[name].copy_(init_val)
                        self._thr_norm_initialized.add(name)

                    # forward usa thr_norm diretamente (mesma escala de a_scaled)
                    y_ch = ConnectedFilterFunctionBySingleThreshold.apply(tree, a_scaled, thr_norm, self.beta_f, self.beta_b)  # (H,W)
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

    # ---------- salvar / inspecionar ----------
    def save_params(self, path: str):
        """Salva os thresholds **normalizados** (um por grupo)."""
        params = { f"thr_norm_{name}": p.detach().cpu() for name, p in self._thr_norm.items() }
        torch.save(params, path)
        print(f"[ConnectedThresholdLayer] thresholds NORMALIZADOS salvos em {path}")

    def get_descaled_threshold(self, channel: int = 0):
        """
        Converte cada `thr_norm` para o domínio BRUTO usando as stats GLOBAIS do dataset
        acumuladas até o momento (dataset-wide normalization).
        """
        if not self._ds_stats:
            raise RuntimeError("Sem stats de dataset. Rode um forward ao menos uma vez para acumular estatísticas.")

        out = {}
        for (attr_type,) in self.group_defs:
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
        """Re-normaliza os atributos de TODAS as árvores cacheadas com as stats de dataset atuais."""
        for key in list(self._base_attrs.keys()):
            self._maybe_refresh_norm_for_key(key)

# Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterLayerBySingleThreshold',
    'ConnectedFilterFunctionBySingleThreshold',
]