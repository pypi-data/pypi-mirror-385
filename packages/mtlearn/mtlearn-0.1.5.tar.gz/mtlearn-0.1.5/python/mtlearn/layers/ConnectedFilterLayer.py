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
)


# ============================================================================
#  Modelo geral: σ( attr_norm @ weight + bias ) por grupo (K≥1 atributos)
#  - Forward: usa the same C++ filtering
#  - Backward: usa C++ gradients(tree, attrs, sigmoid, gradLoss) -> (dW, dB)
# ============================================================================
class ConnectedFilterFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, tree, attrs2d: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, beta_f: float = 1000.0, clamp_logits: bool = True):
        """
        Args:
            tree: ponteiro/handle da árvore morfológica (C++)
            attrs2d: (numNodes, K) atributos **normalizados** do grupo
            weight: (K,) pesos aprendíveis do grupo
            bias: () ou (1,) bias aprendível do grupo
            beta_f: ganho da sigmoide no FORWARD (endurece/soften a curva)
            clamp_logits: se True, faz clamp de beta_f*logits em ±12 antes da sigmoide
        Returns:
            y_pred: imagem filtrada (H, W)
        """
        assert attrs2d.dim() == 2, "attrs2d deve ter shape (numNodes, K)"
        assert weight.dim() == 1, "weight deve ter shape (K,)"
        logits = attrs2d @ weight.view(-1) + bias.view(())   # (numNodes,)
        s = beta_f * logits
        if clamp_logits:
            s = torch.clamp(s, -12.0, 12.0)
        sigmoid = torch.sigmoid(s)  # (numNodes,)
        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filtering(tree, sigmoid)

        # Guarda para o backward (gradientes de w e b vêm do C++)
        ctx.tree = tree
        ctx.beta_f = beta_f
        ctx.save_for_backward(attrs2d.to(torch.float32), sigmoid.to(torch.float32))
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        """Backward em (weight, bias) via C++: returns (None, None, dW, dB, None, None)."""
        attrs2d, sigmoid = ctx.saved_tensors
        tree = ctx.tree
        beta_f = ctx.beta_f

        # C++: gradients(treePtr, attrs, sigmoid, dL/dY) -> (dW, dB)
        dW, dB = mtlearn.ConnectedFilterByMorphologicalTree.gradients(tree, attrs2d, sigmoid, beta_f, grad_output)
        
        # Match forward args: (tree, attrs2d, weight, bias, beta_f, clamp_logits)
        return None, None, dW, dB, None, None


class ConnectedFilterLayer(torch.nn.Module):
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

    def _build_tree(self, img_np: np.ndarray):
        return build_tree(img_np, self.tree_type)

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
    def _ensure_tree_and_attr(self, key: str, img_np: np.ndarray):
        # Copiado do modelo anterior: computa e normaliza atributos por-árvore
        if key in self._trees:
            return
        tree = self._build_tree(img_np)
        self._trees[key] = tree
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
    def inspect_training_sample(self, img: torch.Tensor, channel: int = 0, build_if_missing: bool = True):
        """
        Retorna um pacote de inspeção para UMA imagem:

        1) tree: ponteiro/handle da árvore morfológica;
        2) base_attrs_by_group: atributos brutos empilhados por grupo (dict[gname] -> (numNodes, K));
        3) norm_attrs_by_group: atributos normalizados empilhados por grupo (dict[gname] -> (numNodes, K));
        4) weights_by_group: pesos atuais por grupo (dict[gname] -> (K,));
        5) bias_by_group: bias atual por grupo (dict[gname] -> (1,)).

        Args:
            img: Tensor (H,W) ou (C,H,W). Se (C,H,W), usa `channel`.
            channel: índice do canal a usar quando C>1.
            build_if_missing: se True, constrói e cacheia árvore/atributos se ainda não existir.

        Raises:
            KeyError: se `build_if_missing=False` e a imagem não estiver no cache.

        Obs.: pesos/bias são retornados como referências aos Parameters; use
            `.detach().cpu().clone()` se desejar cópias imutáveis.
        """
        # Normaliza formato da imagem
        if img.dim() == 2:
            imgCHW = img.unsqueeze(0)  # (1,H,W)
        elif img.dim() == 3:
            imgCHW = img               # (C,H,W)
        else:
            raise ValueError(f"img deve ser (H,W) ou (C,H,W); veio {tuple(img.shape)}")

        C, H, W = imgCHW.shape
        if C != self.in_channels:
            # Se o usuário passou apenas um canal, aceitamos C==1
            if C != 1:
                raise AssertionError(f"in_channels={self.in_channels}, input C={C}")

        c = channel if C > 1 else 0
        img_np = self._to_numpy_u8(imgCHW[c])
        t_u8   = torch.from_numpy(img_np)
        key    = self._hash_tensor_sha256(t_u8, c)

        # Garante árvore/atributos no cache
        if (key not in self._trees) and build_if_missing:
            self._ensure_tree_and_attr(key, img_np)
        elif key not in self._trees:
            raise KeyError("Árvore/atributos não encontrados no cache. Use build_if_missing=True.")

        # Atualiza normalização se necessário
        self._maybe_refresh_norm_for_key(key)

        tree = self._trees[key]
        base_attrs_by_group = {}
        norm_attrs_by_group = {}
        weights_by_group    = {}
        bias_by_group       = {}

        for group in self.group_defs:
            gname = self._group_name(group)

            # Empilha colunas (numNodes, K)
            cols_raw  = [self._base_attrs[key][attr_type].view(-1, 1) for attr_type in group]
            cols_norm = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
            A_raw  = torch.cat(cols_raw,  dim=1)
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
        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                img_np = self._to_numpy_u8(x[b, c])
                t_u8   = torch.from_numpy(img_np)
                key    = self._hash_tensor_sha256(t_u8, c)
                self._ensure_tree_and_attr(key, img_np)
                tree = self._trees[key]
                self._maybe_refresh_norm_for_key(key)

                for g, group in enumerate(self.group_defs):
                    gname = self._group_name(group)
                    # Monta A_norm (numNodes, K) empilhando colunas dos atributos do grupo
                    cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                    A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                    y_ch = ConnectedFilterFunction.apply(
                        tree, A_norm, self._weights[gname], self._biases[gname],
                        self.beta_f, self.clamp_logits
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
            B, C, H, W = x.shape
            out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)
            for b in range(B):
                for c in range(C):
                    img_np = self._to_numpy_u8(x[b, c])
                    t_u8   = torch.from_numpy(img_np)
                    key    = self._hash_tensor_sha256(t_u8, c)
                    self._ensure_tree_and_attr(key, img_np)
                    tree = self._trees[key]
                    self._maybe_refresh_norm_for_key(key)
                    for g, group in enumerate(self.group_defs):
                        gname = self._group_name(group)
                        cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                        A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterFunction.apply(
                            tree, A_norm, self._weights[gname], self._biases[gname],
                            beta_f, self.clamp_logits  # usa β_f passado
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

    # ---------- coleta de stats ----------
    def collect_dataset_stats(self, x, channel: int = 0, cache: bool = True) -> dict:
        """Coleta/atualiza estatísticas de normalização percorrendo um **dataset**.

        Aceita:
          • `x` como **Tensor** (B,C,H,W) — compatível com a versão anterior;
          • um **iterável** (ex.: DataLoader) que produza tensores (B,C,H,W) ou (C,H,W);
          • um **Dataset** iterável.

        Não realiza forward; apenas constrói a árvore, computa atributos **brutos** e
        atualiza `_ds_stats`. Com `cache=True`, guarda árvore/atributos normalizados
        para reutilização posterior.

        Args:
            x: Tensor (B,C,H,W) **ou** iterável de tensores (B,C,H,W) / (C,H,W)
            channel (int): índice do canal a usar quando C>1 (padrão: 0)
            cache (bool): se True, armazena árvore/atributos no cache interno

        Returns:
            dict: resumo por atributo. Para `minmax01`: {amin, amax};
                  para `zscore_tree`/`hybrid`: {count, mean, std}; para `none`: {}.
        """
        def _consume_batch(batch_t: torch.Tensor):
            assert batch_t.dim() in (3,4), f"Esperado (B,C,H,W) ou (C,H,W), veio {tuple(batch_t.shape)}"
            if batch_t.dim() == 3:
                batch_t = batch_t.unsqueeze(0)  # (1,C,H,W)
            B, C, H, W = batch_t.shape
            assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"
            with torch.no_grad():
                for b in range(B):
                    c = channel if C > 1 else 0
                    img_np = self._to_numpy_u8(batch_t[b, c])
                    t_u8   = torch.from_numpy(img_np)
                    key    = self._hash_tensor_sha256(t_u8, c)
                    tree = self._build_tree(img_np)
                    if cache:
                        self._trees[key] = tree
                    per_attr_raw = {}
                    per_attr_norm = {}
                    for attr_type in self._all_attr_types:
                        attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                        a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                        self._update_ds_stats(attr_type, a_raw_1d)
                        if cache:
                            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)
                            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                            per_attr_norm[attr_type] = a_norm
                    if cache:
                        self._base_attrs[key] = per_attr_raw
                        self._norm_attrs[key] = per_attr_norm
                        self._norm_epoch_by_key[key] = self._stats_epoch

        # Detecta tipo de `x` e consome iterativamente
        if isinstance(x, torch.Tensor):
            _consume_batch(x)
        else:
            # iterável/loader/dataset
            for it in x:
                # Suporta pares (inputs, target) vindos de DataLoader
                if isinstance(it, (list, tuple)) and len(it) >= 1:
                    batch_t = it[0]
                else:
                    batch_t = it
                if not isinstance(batch_t, torch.Tensor):
                    raise TypeError("Iterável do dataset deve produzir tensores")
                _consume_batch(batch_t)

        # monta resumo
        summary = {}
        for attr_type in self._all_attr_types:
            st = self._ds_stats.get(attr_type, None)
            name = attr_type.name
            if st is None:
                summary[name] = {}
                continue
            if self.scale_mode == "minmax01":
                summary[name] = {"amin": float(st["amin"].item()), "amax": float(st["amax"].item())}
            elif self.scale_mode in ("zscore_tree", "hybrid"):
                count = st["count"].to(torch.float32)
                mean  = (st["sum"] / count) if count.item() > 0 else torch.tensor(0.0)
                var   = (st["sumsq"] / count - mean * mean) if count.item() > 0 else torch.tensor(0.0)
                std   = torch.sqrt(torch.clamp(var, min=self.eps))
                summary[name] = {"count": int(count.item()), "mean": float(mean.item()), "std": float(std.item())}
            else:
                summary[name] = {}
        return summary

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


# Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterLayer',
    'ConnectedFilterFunction',
]