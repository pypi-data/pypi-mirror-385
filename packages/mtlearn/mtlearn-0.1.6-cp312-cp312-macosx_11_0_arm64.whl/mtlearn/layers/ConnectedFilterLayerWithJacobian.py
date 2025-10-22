# ConnectedFilterLayer.py — MorphologicalTreeLearning

import struct, hashlib
import math
import torch
import numpy as np
import mmcfilters
import mtlearn
import torch.nn.functional as F
from ._helpers import (
    group_name,
    hash_tensor_sha256,
    to_numpy_u8,
    build_tree,
    update_ds_stats,
    normalize_with_ds_stats,
    maybe_refresh_norm_for_key,
    IndexedDatasetWrapper
)

class ConnectedFilterWithJacobianFunction(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        jacobian: torch.Tensor,
        residues: torch.Tensor,
        numRows: int,
        numCols: int,
        attrs2d: torch.Tensor,
        weight: torch.Tensor,
        bias: torch.Tensor,
        beta_f: float = 1.0,
        clamp_logits: bool = False
    ):
        assert attrs2d.dim() == 2, "attrs2d deve ter shape (numNodes, K)"
        assert weight.dim() == 1, "weight deve ter shape (K,)"

        logits = attrs2d @ weight.view(-1) + bias.view(())
        s = beta_f * logits
        if clamp_logits:
            s = torch.clamp(s, -12.0, 12.0)

        sigmoid = torch.sigmoid(s)

        y_pred = (jacobian.T @ (residues * sigmoid)).reshape(numRows, numCols)

        ctx.jacobian = jacobian
        ctx.residues = residues
        ctx.beta_f = beta_f

        ctx.save_for_backward(attrs2d, sigmoid)
        return y_pred


    @staticmethod
    def backward(ctx, grad_output):
        attrs2d, sigmoid = ctx.saved_tensors

        jacobian = ctx.jacobian
        residues = ctx.residues
        beta_f = ctx.beta_f

        grad_output = grad_output.flatten()

        d_sigmoid = sigmoid * (1 - sigmoid)

        d_rec_W = jacobian.T @ (residues.unsqueeze(1) * beta_f * d_sigmoid.unsqueeze(1) * attrs2d)
        d_rec_B = jacobian.T @ (residues.unsqueeze(1) * beta_f * d_sigmoid.unsqueeze(1))

        dW = (grad_output @ d_rec_W)
        dB = (grad_output @ d_rec_B)

        return None, None, None, None, None, dW, dB, None, None


class ConnectedFilterLayerWithJacobian(torch.nn.Module):
    """
    Camada geral por grupo: σ( A_norm @ w + b ) com filtering conectado.

    • Para cada grupo g com K atributos normalizados A_g ∈ R^{numNodes×K},
      aplica-se logits = A_g @ w_g + b_g e s = σ(β_f · logits).
    • O filtering conectado (C++) é aplicado sobre s.
    • O backward de (w_g, b_g) é calculado por C++ via `gradients(tree, attrs, sigmoid, dL/dY)`.

    Args:
        in_channels (int): canais de entrada
        attributes_spec (Iterable[Iterable[Type]]): lista de grupos (K≥1 atributos)
        tree_type (str): "max-tree" | "min-tree" | outro (ToS)
        device (str): dispositivo para tensores de saída e parâmetros
        scale_mode (str): "minmax01" | "zscore_tree" | "hybrid" | "none"
        eps (float): proteção numérica
        initial_weight (float): valor inicial para pesos (default 0.0)
        initial_bias (float): valor inicial para bias (default 0.0)
        beta_f (float): ganho da sigmoide no FORWARD (default 1000.0)
        top_hat (bool): aplica top-hat ao final (como nas outras camadas)
        clamp_logits (bool): se True, clamp de β_f·logits em ±12 antes da sigmoide
        hybrid_k (float): clipping em ±kσ para o modo híbrido
        hybrid_floor_a (float): remapeamento para [a,1] no modo híbrido
    """
    def __init__(self,
                 in_channels,
                 attributes_spec,
                 tree_type="max-tree",
                 device="cpu",
                 scale_mode: str = "hybrid",
                 eps: float = 1e-6,
                 beta_f: float = 1.0,
                 top_hat: bool = False,
                 clamp_logits: bool = False,
                 hybrid_k: float = 3.0,
                 hybrid_floor_a: float = 0.05,
                 ):
        super().__init__()
    
        # --- parâmetros do modo híbrido ---
        self.hybrid_k = float(hybrid_k)
        self.hybrid_floor_a = float(hybrid_floor_a)

        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)
        self.eps         = float(eps)
        self.beta_f      = float(beta_f)
        self.top_hat     = bool(top_hat)
        self.clamp_logits = bool(clamp_logits)

        # Training stability options
        self.enforce_positive_weights = True  # force w_k >= w_floor via softplus reparam (placeholder)
        self.weight_floor = 5e-2             # minimal magnitude for stable threshold estimates
        self.eps_w_est = 5e-2                # epsilon used in threshold estimation

        # Definição de grupos (K≥1) e conjunto de atributos usados
        self.group_defs = []
        all_attr_types_set = set()
        for item in attributes_spec:
            group = tuple(item) if isinstance(item, (list, tuple)) else (item,)
            if len(group) < 1:
                raise ValueError("Cada grupo deve conter pelo menos 1 atributo.")
            self.group_defs.append(group)
            for at in group:
                all_attr_types_set.add(at)
        self._all_attr_types = list(all_attr_types_set)

        self.num_groups   = len(self.group_defs)
        self.out_channels = self.in_channels * self.num_groups

        # Caches/normalização
        self._trees      = {}
        self._jacobians  = {}
        self._residues   = {}
        self._base_attrs = {}
        self._norm_attrs = {}
        self._stats_epoch = 0
        self._norm_epoch_by_key = {}
        self._ds_stats = {}
        self._stats_frozen = False

        # Parâmetros: para cada grupo g, (w_g, b_g)
        self._weights = torch.nn.ParameterDict()
        self._biases  = torch.nn.ParameterDict()
        for g, group in enumerate(self.group_defs):
            k = len(group)
            gname = "+".join([t.name for t in group])
            w = torch.empty(k, dtype=torch.float32, device=self.device)
            b = torch.empty(1, dtype=torch.float32, device=self.device)
            # Xavier-like init para vetor 1D
            fan_in, fan_out = k, 1
            gain = 1.0
            std = gain * math.sqrt(2.0 / float(fan_in + fan_out))
            a = math.sqrt(3.0) * std
            torch.nn.init.uniform_(w, -a, a)
            torch.nn.init.constant_(b, 0.0)
            self._weights[gname] = torch.nn.Parameter(w, requires_grad=True)
            self._biases[gname]  = torch.nn.Parameter(b, requires_grad=True)

    # ---------- helpers ----------
    def _group_name(self, group):
        return group_name(group)

    def _hash_tensor_sha256(self, t_u8: torch.Tensor, chan_idx: int):
        return hash_tensor_sha256(t_u8, chan_idx)

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        return to_numpy_u8(img2d_t)

    def _build_tree_jacobian_and_residues(self, img_np: np.ndarray):
        tree = build_tree(img_np, self.tree_type)
        jacobian = mtlearn.InfoTree.get_jacobian(tree).to(self.device)
        residues = mtlearn.InfoTree.get_residues(tree).to(self.device)
        return tree, jacobian, residues

    # ---------- normalização com suporte a 'hybrid' ----------
    def _update_ds_stats(self, attr_type, a_raw_1d: torch.Tensor):
        """
        Coleta estatísticas do dataset. Para o modo 'hybrid', usamos as mesmas
        estatísticas do 'zscore_tree' (count, sum, sumsq).
        """
        if getattr(self, "_stats_frozen", False):
            return
        smode = self.scale_mode
        if smode == "hybrid":
            smode = "zscore_tree"
        changed = update_ds_stats(self._ds_stats, smode, attr_type, a_raw_1d)
        if changed:
            self._stats_epoch += 1

    def _normalize_with_ds_stats(self, attr_type, a_raw_1d: torch.Tensor) -> torch.Tensor:
        """
        Normaliza conforme self.scale_mode. No caso 'hybrid', aplica:
          1) z-score com mean/std do dataset
          2) clipping em [-k, +k]
          3) remapeamento para [a, 1]:  a + (1-a) * ( (x+k)/(2k) )
        """
        if self.scale_mode != "hybrid":
            return normalize_with_ds_stats(self._ds_stats, self.scale_mode, self.eps, attr_type, a_raw_1d)

        # --- modo híbrido ---
        st = self._ds_stats.get(attr_type, None)
        if st is None:
            # fallback: retorna o tensor original (evita crash em primeiros passos)
            return a_raw_1d

        # estatísticas em estilo z-score
        count = st["count"].to(torch.float32)
        mean  = (st["sum"] / torch.clamp(count, min=1.0)) if count.item() > 0 else torch.tensor(0.0, device=a_raw_1d.device)
        var   = (st["sumsq"] / torch.clamp(count, min=1.0) - mean * mean) if count.item() > 0 else torch.tensor(0.0, device=a_raw_1d.device)
        std   = torch.sqrt(torch.clamp(var, min=self.eps))

        # 1) z-score
        x = (a_raw_1d - mean) / std
        # 2) clip em [-k, +k]
        k = torch.tensor(self.hybrid_k, dtype=x.dtype, device=x.device)
        x = torch.clamp(x, -k, k)
        # 3) reescala para [a, 1]
        a = torch.tensor(self.hybrid_floor_a, dtype=x.dtype, device=x.device)
        x01 = a + (1.0 - a) * ((x + k) / (2.0 * k))
        return x01

    def _maybe_refresh_norm_for_key(self, key: str):
        """
        Atualiza as normalizações em cache para a imagem/árvore identificada por `key`
        caso _stats_epoch tenha mudado. Para o modo 'hybrid', aplicamos a nossa
        própria rotina (_normalize_with_ds_stats). Para os demais modos, delegamos
        ao helper externo.
        """
        # Se não há atributos brutos cacheados, nada a fazer
        if key not in self._base_attrs:
            return

        # Já está atualizado para este epoch?
        if self._norm_epoch_by_key.get(key, -1) == self._stats_epoch:
            return

        if self.scale_mode == "hybrid":
            # Reaplica normalização híbrida atributo a atributo
            per_attr_raw = self._base_attrs[key]           # dict[attr_type] -> (numNodes,1)
            per_attr_norm = {}
            for attr_type, a_raw_2d in per_attr_raw.items():
                a_raw_1d = a_raw_2d.view(-1)              # (numNodes,)
                a_norm   = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                per_attr_norm[attr_type] = a_norm
            self._norm_attrs[key] = per_attr_norm
            self._norm_epoch_by_key[key] = self._stats_epoch
        else:
            # Modos já suportados pelo helper (_helpers.normalize_with_ds_stats)
            maybe_refresh_norm_for_key(
                key,
                self._base_attrs,
                self._norm_attrs,
                self._all_attr_types,
                self._ds_stats,
                self.scale_mode,
                self.eps,
                self._norm_epoch_by_key,
                self._stats_epoch
            )
            
    def freeze_ds_stats(self):
        """Congela a atualização de `_ds_stats` (não coleta mais nem avança `_stats_epoch`)."""
        self._stats_frozen = True

    def unfreeze_ds_stats(self):
        """Descongela a atualização de `_ds_stats` e permite voltar a coletar stats."""
        self._stats_frozen = False

    def save_stats(self, path: str):
        """Salva `_ds_stats` e `scale_mode` para reprodutibilidade."""
        payload = {"ds_stats": self._ds_stats, "scale_mode": self.scale_mode}
        torch.save(payload, path)
        print(f"[ConnectedLinearUnit] stats salvas em {path}")

    def load_stats(self, path: str, refresh_cache: bool = True):
        """Carrega `_ds_stats` e, opcionalmente, re-normaliza o cache existente."""
        payload = torch.load(path, map_location=self.device)
        self._ds_stats = payload.get("ds_stats", {})
        # invalida normalizações antigas
        self._stats_epoch += 1
        if refresh_cache:
            self.refresh_cached_normalization()

    # ---------- construção de árvore e atributos ----------
    def _ensure_tree_and_attr(self, key: str, img_t: torch.Tensor):
        # Aceita tensor PyTorch, converte internamente para np.ndarray
        if key in self._trees:
            return

        img_np = self._to_numpy_u8(img_t.detach())
        tree, jacobian, residues = self._build_tree_jacobian_and_residues(img_np)
        self._trees[key] = tree
        self._jacobians[key] = jacobian
        self._residues[key] = residues
        
        per_attr_raw, per_attr_norm = {}, {}
        for attr_type in self._all_attr_types:
            attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
            self._update_ds_stats(attr_type, a_raw_1d)
            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)
            per_attr_norm[attr_type] = a_norm

        self._base_attrs[key] = per_attr_raw
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch
        

    # ---------- inspeção ----------
    def inspect_training_sample(self, img: torch.Tensor, channel: int = 0, idx: int | None = None, build_if_missing: bool = True):
        """
        Retorna árvore, atributos, pesos e bias de uma amostra específica.

        Se 'idx' for fornecido, usa o cache (key = f"{idx}_{c}").
        Caso contrário, computa árvore e atributos on-the-fly, sem cache.
        """
        # Normaliza formato da imagem
        if img.dim() == 2:
            imgCHW = img.unsqueeze(0)
        elif img.dim() == 3:
            imgCHW = img
        else:
            raise ValueError(f"img deve ser (H,W) ou (C,H,W); veio {tuple(img.shape)}")

        C, H, W = imgCHW.shape
        if C != self.in_channels:
            if C != 1:
                raise AssertionError(f"in_channels={self.in_channels}, input C={C}")

        c = channel if C > 1 else 0

        if idx is not None:
            key = f"{idx}_{c}"
            use_cache = True
        else:
            use_cache = False

        if use_cache:
            if (key not in self._trees) and build_if_missing:
                self._ensure_tree_and_attr(key, imgCHW[c])
            elif key not in self._trees:
                raise KeyError("Árvore/atributos não encontrados no cache. Use build_if_missing=True.")
            self._maybe_refresh_norm_for_key(key)
            tree = self._trees[key]
            base_attrs_by_group = {}
            norm_attrs_by_group = {}
            weights_by_group    = {}
            bias_by_group       = {}
            for group in self.group_defs:
                gname = self._group_name(group)
                cols_raw  = [self._base_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                cols_norm = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                A_raw  = torch.cat(cols_raw,  dim=1)
                A_norm = torch.cat(cols_norm, dim=1)
                base_attrs_by_group[gname] = A_raw
                norm_attrs_by_group[gname] = A_norm
                weights_by_group[gname]    = self._weights[gname]
                bias_by_group[gname]       = self._biases[gname]
        else:
            print("[inspect_training_sample] Executando sem cache — computando árvore e atributos diretamente.")
            img_np = self._to_numpy_u8(imgCHW[c].detach())
            tree, jacobian, residues = self._build_tree_jacobian_and_residues(img_np)
            base_attrs_by_group = {}
            norm_attrs_by_group = {}
            weights_by_group    = {}
            bias_by_group       = {}
            for group in self.group_defs:
                gname = self._group_name(group)
                cols_raw, cols_norm = [], []
                for attr_type in group:
                    attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                    a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                    a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                    cols_raw.append(a_raw_1d.unsqueeze(1))
                    cols_norm.append(a_norm.view(-1, 1))
                A_raw = torch.cat(cols_raw, dim=1)
                A_norm = torch.cat(cols_norm, dim=1)
                base_attrs_by_group[gname] = A_raw
                norm_attrs_by_group[gname] = A_norm
                weights_by_group[gname]    = self._weights[gname]
                bias_by_group[gname]       = self._biases[gname]

        return {
            "tree": tree,
            "base_attrs_by_group": base_attrs_by_group,
            "norm_attrs_by_group": norm_attrs_by_group,
            "weights_by_group": weights_by_group,
            "bias_by_group": bias_by_group,
        }

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Aplica σ( A_norm @ w + b ) por grupo, seguido do filtering conectado."""
        # Lógica de entrada igual ao ConnectedFilterLayer
        if isinstance(x, tuple) and len(x) == 2:
            x, idx = x
            use_cache = True
        elif isinstance(x, list) and len(x) == 2 and isinstance(x[1], torch.Tensor) and x[1].dim() == 1:
            x, idx = x[0], x[1]
            use_cache = True
        else:
            if isinstance(x, list):
                x = torch.stack(x, dim=0)
            idx = torch.arange(x.size(0), device=x.device)
            use_cache = False

        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                if use_cache:
                    # Use idx como parte da chave para persistência de cache
                    key = f"{int(idx[b])}_{c}"
                    self._ensure_tree_and_attr(key, x[b, c])
                    tree = self._trees[key]
                    self._maybe_refresh_norm_for_key(key)
                    for g, group in enumerate(self.group_defs):
                        gname = self._group_name(group)
                        # Monta A_norm (numNodes, K) empilhando colunas dos atributos do grupo
                        cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                        A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterWithJacobianFunction.apply(
                            self._jacobians[key],
                            self._residues[key],
                            tree.numRows,
                            tree.numCols,
                            A_norm,
                            self._weights[gname],
                            self._biases[gname],
                            self.beta_f,
                            self.clamp_logits
                        )
                        if self.top_hat:
                            x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
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
                else:
                    # Não usar cache, construir árvore e atributos diretamente
                    #print("[ConnectedFilterLayerWithJacobian] Cache não está sendo usado (índice não fornecido).")
                    img_np = self._to_numpy_u8(x[b, c].detach())
                    tree, jacobian, residues = self._build_tree_jacobian_and_residues(img_np)
                    # Calcula atributos e normaliza direto, sem cache
                    per_attr_norm = {}
                    for attr_type in self._all_attr_types:
                        attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                        a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                        a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                        per_attr_norm[attr_type] = a_norm
                    for g, group in enumerate(self.group_defs):
                        gname = self._group_name(group)
                        cols = [per_attr_norm[attr_type].view(-1, 1) for attr_type in group]
                        A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterWithJacobianFunction.apply(
                            jacobian,
                            residues,
                            tree.numRows,
                            tree.numCols,
                            A_norm,
                            self._weights[gname],
                            self._biases[gname],
                            self.beta_f,
                            self.clamp_logits
                        )
                        if self.top_hat:
                            x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
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
        """Predição com β_f fixo (forward ~hard); restaura modo train/eval ao final."""
        was_training = self.training
        self.eval()
        with torch.no_grad():
            # Lógica de entrada igual ao forward
            if isinstance(x, tuple) and len(x) == 2:
                x, idx = x
                use_cache = True
            elif isinstance(x, list) and len(x) == 2 and isinstance(x[1], torch.Tensor) and x[1].dim() == 1:
                x, idx = x[0], x[1]
                use_cache = True
            else:
                if isinstance(x, list):
                    x = torch.stack(x, dim=0)
                idx = torch.arange(x.size(0), device=x.device)
                use_cache = False
            B, C, H, W = x.shape
            out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)
            for b in range(B):
                for c in range(C):
                    if use_cache:
                        key = f"{int(idx[b])}_{c}"
                        self._ensure_tree_and_attr(key, x[b, c])
                        tree = self._trees[key]
                        self._maybe_refresh_norm_for_key(key)
                        for g, group in enumerate(self.group_defs):
                            gname = self._group_name(group)
                            cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                            A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                            y_ch = ConnectedFilterWithJacobianFunction.apply(
                                self._jacobians[key],
                                self._residues[key],
                                tree.numRows,
                                tree.numCols,
                                A_norm,
                                self._weights[gname],
                                self._biases[gname],
                                beta_f,  # usa β_f passado
                                self.clamp_logits
                            )
                            if self.top_hat:
                                x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
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
                    else:
                        #print("[ConnectedFilterLayerWithJacobian] Cache não está sendo usado (índice não fornecido) na predição.")
                        img_np = self._to_numpy_u8(x[b, c].detach())
                        tree, jacobian, residues = self._build_tree_jacobian_and_residues(img_np)
                        per_attr_norm = {}
                        for attr_type in self._all_attr_types:
                            attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                            per_attr_norm[attr_type] = a_norm
                        for g, group in enumerate(self.group_defs):
                            gname = self._group_name(group)
                            cols = [per_attr_norm[attr_type].view(-1, 1) for attr_type in group]
                            A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                            y_ch = ConnectedFilterWithJacobianFunction.apply(
                                jacobian,
                                residues,
                                tree.numRows,
                                tree.numCols,
                                A_norm,
                                self._weights[gname],
                                self._biases[gname],
                                beta_f,  # usa β_f passado
                                self.clamp_logits
                            )
                            if self.top_hat:
                                x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
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
        if was_training:
            self.train()
        else:
            self.eval()
        return out

    # ---------- salvar / carregar ----------
    def save_params(self, path: str):
        """Salva pesos e bias de todos os grupos."""
        payload = {
            "weights": { name: p.detach().cpu() for name, p in self._weights.items() },
            "biases":  { name: p.detach().cpu() for name, p in self._biases.items()  },
            "scale_mode": self.scale_mode,
        }
        torch.save(payload, path)
        print(f"[ConnectedLinearUnit] pesos e bias salvos em {path}")

    def get_params(self):
        """Retorna dicionários {weights}, {biases} (tensores clonados em CPU)."""
        return (
            { name: p.detach().cpu().clone() for name, p in self._weights.items() },
            { name: p.detach().cpu().clone() for name, p in self._biases.items()  },
        )


    # ---------- utilidades: normalização em cache ----------
    def refresh_cached_normalization(self):
        """Reaplica normalização aos atributos no cache conforme _ds_stats atual."""
        for key, per_attr_raw in self._base_attrs.items():
            per_attr_norm = {}
            for attr_type, a_raw_2d in per_attr_raw.items():
                a_raw_1d = a_raw_2d.view(-1)
                a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                per_attr_norm[attr_type] = a_norm
            self._norm_attrs[key] = per_attr_norm
            self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- inicializadores (Opção A e C) ----------
    @staticmethod
    def _logit(p: float) -> float:
        p = max(min(float(p), 1.0 - 1e-6), 1e-6)
        return math.log(p / (1.0 - p))

    @torch.no_grad()
    def init_identity_with_bias(self, p0: float = 0.995):
        """
        (Opção C) Inicializa para 'identidade' com viés:
          - w_g <- 0
          - b_g <- logit(p0)/beta_f
        Mantém a imagem (p≈p0) e permite treinar saindo dessa condição.
        """
        L = self._logit(p0) / float(self.beta_f)
        for group in self.group_defs:
            gname = self._group_name(group)
            self._weights[gname].zero_()
            self._biases[gname].fill_(L)

    @torch.no_grad()
    def init_identity_bias_zero(self, p0: float = 0.99):
        """
        (Opção A) Inicializa para 'identidade' com bias=0, assumindo 'scale_mode=="hybrid"':
          - atributos normalizados ∈ [a, 1], com 'a=self.hybrid_floor_a'
          - define w_g = c * 1, com c = logit(p0)/(beta_f * K * a)
          - define b_g = 0
        Garante p>=p0 para todos os nós (limiar inferior pela soma mínima K*a*c).
        """
        if self.scale_mode != "hybrid":
            print("[init_identity_bias_zero] Aviso: esta inicialização supõe 'scale_mode==\"hybrid\"'.")
        a = max(min(self.hybrid_floor_a, 1.0), 1e-6)
        L = self._logit(p0) / float(self.beta_f)
        for group in self.group_defs:
            gname = self._group_name(group)
            K = len(group)
            c = L / (K * a)
            self._weights[gname].fill_(c)
            self._biases[gname].zero_()

    # ---------- utilitário: converter jacobianas para denso ----------
    def jacobian_to_dense(self):
        """
        Converte todas as matrizes jacobianas no cache para formato denso.
        Substitui as versões esparsas pelo formato denso.
        """
        for key, J in list(self._jacobians.items()):
            if getattr(J, "is_sparse", False):
                J_dense = J.to_dense()
                self._jacobians[key] = J_dense
                print(f"[jacobian_to_dense] Jacobian '{key}' convertida para formato denso.")
            else:
                print(f"[jacobian_to_dense] Jacobian '{key}' já está em formato denso.")

    def move_cache_to_device(self, device: str | torch.device):
        """
        Transfere todos os tensores do cache para o dispositivo especificado.
        """
        device = torch.device(device)
        self.device = device
        for cache_name in ["_jacobians", "_residues", "_base_attrs", "_norm_attrs"]:
            cache = getattr(self, cache_name)
            for key, value in cache.items():
                if isinstance(value, dict):
                    for subkey, tensor in value.items():
                        cache[key][subkey] = tensor.to(device)
                elif torch.is_tensor(value):
                    cache[key] = value.to(device)
        print(f"[move_cache_to_device] Cache transferido para {device}.")


    def build_dataloader_cached(self, dataloader):
        """
        Pré-processa e cacheia árvores/atributos para um DataLoader, usando o cache persistente por idx+c.
        O DataLoader retornado produz batches ((x, idx), y), onde idx é o índice do dataset original.
        """
        from torch.utils.data import DataLoader

        dataset_wrapped = IndexedDatasetWrapper(dataloader.dataset)
        new_loader = DataLoader(
            dataset_wrapped,
            batch_size=dataloader.batch_size,
            shuffle=False,
            num_workers=dataloader.num_workers,
            pin_memory=dataloader.pin_memory,
            drop_last=False,
            collate_fn=dataloader.collate_fn,
            persistent_workers=getattr(dataloader, "persistent_workers", False),
        )

        print(f"[ConnectedFilterLayerWithJacobian] Preprocessing dataset using mode '{self.scale_mode}'...")
        self._stats_frozen = False
        total_batches = len(new_loader)

        with torch.no_grad():
            for batch_i, ((x, idx), y) in enumerate(new_loader):
                B, C, H, W = x.shape
                for b in range(B):
                    for c in range(C):
                        key = f"{int(idx[b])}_{c}"
                        self._ensure_tree_and_attr(key, x[b, c])
                if (batch_i + 1) % 10 == 0 or batch_i == total_batches - 1:
                    print(f"  [{batch_i+1}/{total_batches}] batches processed.")

        self.freeze_ds_stats()
        self.refresh_cached_normalization()
        print(f"[ConnectedFilterLayerWithJacobian] Full and normalized cache with '{self.scale_mode}'.")
        return new_loader
    

# Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterLayerWithJacobian',
    'ConnectedFilterWithJacobianFunction'
]
