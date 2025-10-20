
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
    def forward(ctx, tree, attrs2d: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor,
                beta_f: float = 1000.0, clamp_logits: bool = True):
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
        ctx.save_for_backward(attrs2d.to(torch.float32), sigmoid.to(torch.float32))
        return y_pred

    @staticmethod
    def backward(ctx, grad_output):
        """Backward em (weight, bias) via C++: returns (None, None, dW, dB, None, None)."""
        attrs2d, sigmoid = ctx.saved_tensors
        tree = ctx.tree
        # C++: gradients(treePtr, attrs, sigmoid, dL/dY) -> (dW, dB)
        dW, dB = mtlearn.ConnectedFilterByMorphologicalTree.gradients(tree, attrs2d, sigmoid, grad_output)
        
        # Match forward args: (tree, attrs2d, weight, bias, beta_f, clamp_logits)
        return None, None, dW, dB, None, None


class ConnectedFilterLayer(torch.nn.Module):
    def collect_and_init_from_quantiles(self,
                                        x,
                                        q: float = 0.5,
                                        alpha: float = 1.0,
                                        channel: int = 0,
                                        cache: bool = True,
                                        freeze_stats: bool = True) -> dict:
        """Pipeline único: coleta stats do *dataset* e inicializa (w,b) via quantis dos atributos.

        Faz duas etapas:
          (1) `collect_dataset_stats(x, channel, cache)` para garantir stats e (opcional) cache;
          (2) Agrega os atributos **normalizados** sobre `x`, calcula o quantil `q` por atributo
              e inicializa os grupos com `w=alpha` e `b=-Σ w·t`.

        Aceita `x` como Tensor (B,C,H,W) ou como **iterável/DataLoader** que produza tensores
        (B,C,H,W) ou (C,H,W). É análogo a `init_linear_boundary_from_quantiles`, mas operando
        num *dataset* completo em vez de um único batch.

        Args:
            x: Tensor 4D ou iterável/dataloader/dataset que produza tensores
            q (float): quantil em [0,1] a ser usado como "threshold" por atributo
            alpha (float): valor inicial comum dos pesos `w`
            channel (int): canal a usar quando C>1
            cache (bool): se True, armazena árvores/atributos no cache interno durante a coleta
            freeze_stats (bool): se True, congela as stats após a coleta para estabilidade

        Returns:
            dict: {attr_name: t_k_norm} com os quantis usados (em espaço normalizado)
        """
        assert 0.0 <= float(q) <= 1.0, "q deve estar em [0,1]"
        # 1) Coleta/atualiza stats do dataset (e opcionalmente cacheia)
        _ = self.collect_dataset_stats(x, channel=channel, cache=cache)
        if freeze_stats:
            self.freeze_ds_stats()

        # 2) Varre `x` novamente para agregar atributos **normalizados** e calcular os quantis
        def _consume_batch_for_pool(batch_t: torch.Tensor, pool: dict):
            assert batch_t.dim() in (3,4), f"Esperado (B,C,H,W) ou (C,H,W), veio {tuple(batch_t.shape)}"
            if batch_t.dim() == 3:
                batch_t = batch_t.unsqueeze(0)
            B, C, H, W = batch_t.shape
            assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"
            with torch.no_grad():
                for b in range(B):
                    c = channel if C > 1 else 0
                    img_np = self._to_numpy_u8(batch_t[b, c])
                    t_u8   = torch.from_numpy(img_np)
                    key    = self._hash_tensor_sha256(t_u8, c)
                    # garante presença no cache (se já estava, não recalcula)
                    self._ensure_tree_and_attr(key, img_np)
                    self._maybe_refresh_norm_for_key(key)
                    for attr_type in self._all_attr_types:
                        a_norm_1d = self._norm_attrs[key][attr_type].view(-1)
                        pool[attr_type].append(a_norm_1d)

        pool = {attr_type: [] for attr_type in self._all_attr_types}
        if isinstance(x, torch.Tensor):
            _consume_batch_for_pool(x, pool)
        else:
            for it in x:
                batch_t = it[0] if (isinstance(it, (list, tuple)) and len(it) >= 1) else it
                if not isinstance(batch_t, torch.Tensor):
                    raise TypeError("Iterável do dataset deve produzir tensores")
                _consume_batch_for_pool(batch_t, pool)

        # concat por atributo e calcula quantil
        t_norm = {}
        for attr_type in self._all_attr_types:
            name = attr_type.name
            if len(pool[attr_type]) == 0:
                t_norm[name] = 0.0
                continue
            vec = torch.cat(pool[attr_type], dim=0).to(torch.float32)
            t = torch.quantile(vec, float(q))
            t_norm[name] = float(t.item())

        # 3) Inicializa w=alpha e b=-Σ w·t por grupo
        with torch.no_grad():
            for g, group in enumerate(self.group_defs):
                gname = self._group_name(group)
                w = self._weights[gname]
                b = self._biases[gname]
                w.fill_(float(alpha))
                s = 0.0
                for attr_type in group:
                    s += float(alpha) * float(t_norm[attr_type.name])
                b.fill_(-s)

        return t_norm
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
        scale_mode (str): "minmax01" | "zscore_tree" | "none"
        eps (float): proteção numérica
        initial_weight (float): valor inicial para pesos (default 0.0)
        initial_bias (float): valor inicial para bias (default 0.0)
        beta_f (float): ganho da sigmoide no FORWARD (default 1000.0)
        top_hat (bool): aplica top-hat ao final (como nas outras camadas)
        clamp_logits (bool): se True, clamp de β_f·logits em ±12 antes da sigmoide
    """
    def __init__(self,
                 in_channels,
                 attributes_spec,
                 tree_type="max-tree",
                 device="cpu",
                 scale_mode: str = "minmax01",
                 eps: float = 1e-6,
                 beta_f: float = 100.0,
                 top_hat: bool = False,
                 clamp_logits: bool = True):
        super().__init__()
        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)
        self.eps         = float(eps)
        self.beta_f      = float(beta_f)
        self.top_hat     = bool(top_hat)
        self.clamp_logits = bool(clamp_logits)

        # Training stability options
        self.enforce_positive_weights = True  # force w_k >= w_floor via softplus reparam
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

        # Caches/normalização (compatível com as camadas anteriores)
        self._trees      = {}
        self._base_attrs = {}
        self._norm_attrs = {}
        self._stats_epoch = 0
        self._norm_epoch_by_key = {}
        self._ds_stats = {}
        # controle de atualização online das estatísticas do dataset
        self._stats_frozen = False

        # Parâmetros: para cada grupo g, (w_g, b_g)
        # Usamos ParameterDicts indexados pelo nome do grupo
        self._weights = torch.nn.ParameterDict()
        self._biases  = torch.nn.ParameterDict()
        for g, group in enumerate(self.group_defs):
            k = len(group)
            gname = "+".join([t.name for t in group])
            w = torch.empty(k, dtype=torch.float32, device=self.device)
            b = torch.empty(1, dtype=torch.float32, device=self.device)
            # Xavier-like init for 1D vector weights (fan_out=1, fan_in=k)
            fan_in, fan_out = k, 1
            gain = 1.0  # linear activation
            std = gain * math.sqrt(2.0 / float(fan_in + fan_out))
            a = math.sqrt(3.0) * std  # bounds for uniform from std
            torch.nn.init.uniform_(w, -a, a)
            torch.nn.init.constant_(b, 0.0)
            self._weights[gname] = torch.nn.Parameter(w, requires_grad=True)
            self._biases[gname]  = torch.nn.Parameter(b, requires_grad=True)


    # ---------- helpers de normalização/árvore/cache (independentes) ----------
    def _group_name(self, group):
        return group_name(group)

    def _hash_tensor_sha256(self, t_u8: torch.Tensor, chan_idx: int):
        return hash_tensor_sha256(t_u8, chan_idx)

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        return to_numpy_u8(img2d_t)

    def _build_tree(self, img_np: np.ndarray):
        return build_tree(img_np, self.tree_type)

    def _update_ds_stats(self, attr_type, a_raw_1d: torch.Tensor):
        if getattr(self, "_stats_frozen", False):
            return
        changed = update_ds_stats(self._ds_stats, self.scale_mode, attr_type, a_raw_1d)
        if changed:
            self._stats_epoch += 1

    def _normalize_with_ds_stats(self, attr_type, a_raw_1d: torch.Tensor) -> torch.Tensor:
        return normalize_with_ds_stats(self._ds_stats, self.scale_mode, self.eps, attr_type, a_raw_1d)

    def _maybe_refresh_norm_for_key(self, key: str):
        maybe_refresh_norm_for_key(key, self._base_attrs, self._norm_attrs, self._all_attr_types, self._ds_stats, self.scale_mode, self.eps, self._norm_epoch_by_key, self._stats_epoch)

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
                    A = torch.cat(cols, dim=1)  # (numNodes, K)
                    w = self._weights[gname]
                    bpar = self._biases[gname]
                    # enforce non-negativity and a small floor to avoid near-zero divisions in analysis
                    w_eff = F.softplus(w) + self.weight_floor if self.enforce_positive_weights else w

                    y_ch = ConnectedFilterFunction.apply(tree, A, w_eff, bpar, self.beta_f, self.clamp_logits)
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
                        A = torch.cat(cols, dim=1)
                        w = self._weights[gname]
                        bpar = self._biases[gname]
                        w_eff = F.softplus(w) + self.weight_floor if self.enforce_positive_weights else w
                        y_ch = ConnectedFilterFunction.apply(tree, A, w_eff, bpar, float(beta_f), self.clamp_logits)
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

    # ---------- init data-driven: fronteira a partir de quantis por atributo ----------
    def init_linear_boundary_from_quantiles(self,
                                            x: torch.Tensor,
                                            q: float = 0.5,
                                            alpha: float = 1.0,
                                            channel: int = 0) -> dict:
        """Inicializa (w,b) usando **quantis** dos atributos normalizados (data-driven).

        Ideia: para cada atributo k, compute o quantil q de a_k (em espaço **normalizado**)
        a partir dos nós das árvores no batch `x`. Em seguida, para cada grupo g:

            w_{gk} = α  (constante positiva)
            b_g    = - Σ_k w_{gk} · t_k,   onde t_k = quantile(a_k, q)

        Assim, a fronteira linear Aw+b=0 passa pelo ponto de "thresholds por atributo"
        definido pelos quantis dos próprios dados (analogia direta ao modelo de thresholds).

        Args:
            x (torch.Tensor): batch (B,C,H,W)
            q (float): quantil em [0,1] para cada atributo (padrão 0.5)
            alpha (float): valor comum dos pesos na inicialização (padrão 1.0)
            channel (int): canal a usar quando C>1 (padrão 0)

        Returns:
            dict: mapeamento {attr_name: t_k_norm} dos quantis usados por atributo.
        """
        assert 0.0 <= float(q) <= 1.0, "q deve estar em [0,1]"
        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"

        # 1) Garante árvores/atributos e agrega valores normalizados por atributo em todo o batch
        pool = {attr_type: [] for attr_type in self._all_attr_types}
        for b in range(B):
            c = channel if C > 1 else 0
            img_np = self._to_numpy_u8(x[b, c])
            t_u8   = torch.from_numpy(img_np)
            key    = self._hash_tensor_sha256(t_u8, c)
            self._ensure_tree_and_attr(key, img_np)
            self._maybe_refresh_norm_for_key(key)
            for attr_type in self._all_attr_types:
                a = self._norm_attrs[key][attr_type].view(-1)
                pool[attr_type].append(a)
        # concat por atributo
        for attr_type in self._all_attr_types:
            pool[attr_type] = torch.cat(pool[attr_type], dim=0)

        # 2) Calcula quantis por atributo (em espaço normalizado)
        t_norm = {}
        for attr_type in self._all_attr_types:
            name = attr_type.name
            vec = pool[attr_type]
            # robustez: se todos NaN/vazio, usa 0.0
            if vec.numel() == 0:
                t = torch.tensor(0.0, dtype=torch.float32, device=self.device)
            else:
                t = torch.quantile(vec.to(torch.float32), float(q))
            t_norm[name] = float(t.item())

        # 3) Define w=alpha e b=-Σ w*t no alinhamento de cada grupo
        with torch.no_grad():
            for g, group in enumerate(self.group_defs):
                gname = self._group_name(group)
                w = self._weights[gname]
                b = self._biases[gname]
                w.fill_(float(alpha))
                s = 0.0
                for attr_type in group:
                    s += float(alpha) * float(t_norm[attr_type.name])
                b.fill_(-s)

        return t_norm

    # ---------- regularizador: equalização de pesos por grupo (soft-soft) ----------
    def equalization_loss(self, alpha: float = 1.0, weight: float = 1.0) -> torch.Tensor:
        """Promove pesos próximos de um valor comum α (evita dominância de um atributo).

        L_equal = weight * Σ_g mean( (w_g − α)^2 )
        Útil no regime soft-soft (β_f≈1), para manter contribuição balanceada entre atributos.
        """
        total = torch.zeros((), dtype=torch.float32, device=self.device)
        a = float(alpha)
        for gname, w in self._weights.items():
            total = total + (w - a).pow(2).mean()
        return total * float(weight)

    # ---------- estimativa de thresholds efetivos por peso (w_k) ----------
    def estimate_effective_thresholds(self,
                                      x: torch.Tensor,
                                      agg: str = "median",
                                      channel: int = 0) -> dict:
        """
        Estima, para cada grupo g e atributo k, um **limiar efetivo** a_k* tal que
        σ( A_norm @ w + b ) = 0.5 ⇒ (A_norm @ w + b) = 0.

        Usa os pesos efetivos (w_eff), incluindo floor de positividade, para maior estabilidade.
        Para pesos |w_k| < eps_w_est, retorna NaN para aquele atributo.

        Modos de estimação:
          • mode="nodewise" (padrão): mantém os demais atributos fixos **nos valores do próprio nó**
            e agrega sobre nós via `agg` ou `quantile`.
          • mode="typical": fixa os demais atributos no **valor típico** do grupo
            (mediana ou média por atributo no conjunto de nós) e calcula um único limiar por k.

        Args:
            x (torch.Tensor): batch de entrada (B, C, H, W). Usado para construir/cachear
                a árvore e extrair os atributos normalizados A_norm por (b,c).
            agg (str): "median" (padrão) ou "mean" para agregação quando `quantile` for None.
            channel (int): canal de entrada a considerar quando C>1 (padrão 0).
            mode (str): "nodewise" | "typical".
            quantile (float|None): se definido (0..1), usa quantil em vez de `agg`.

        Returns:
            dict: dicionário aninhado { (b,c,gname): { attr_name: {"norm": v, "raw": v_raw } } }
        """
        # parâmetros opcionais adicionais (mantém compatibilidade com chamadas antigas)
        import math as _math  # local import para evitar poluir namespace do módulo
        def _nanquantile(t: torch.Tensor, q: float) -> torch.Tensor:
            # torch.nanquantile existe em versões recentes; fallback manual
            if hasattr(torch, 'nanquantile'):
                return torch.nanquantile(t, q)
            # fallback: filtra NaN e usa quantile
            mask = ~torch.isnan(t)
            if mask.any():
                return torch.quantile(t[mask], q)
            return torch.tensor(float('nan'), device=t.device)

        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"
        assert agg in ("median", "mean"), "agg deve ser 'median' ou 'mean'"
        # valores padrão para novos argumentos
        mode = locals().get('mode', 'nodewise')
        quantile = locals().get('quantile', None)
        assert mode in ("nodewise", "typical"), "mode deve ser 'nodewise' ou 'typical'"

        results = {}
        for b in range(B):
            c = channel if C > 1 else 0
            # Garante árvore/atributos no cache
            img_np = self._to_numpy_u8(x[b, c])
            t_u8   = torch.from_numpy(img_np)
            key    = self._hash_tensor_sha256(t_u8, c)
            self._ensure_tree_and_attr(key, img_np)
            self._maybe_refresh_norm_for_key(key)

            for g, group in enumerate(self.group_defs):
                gname = self._group_name(group)
                # A: (N,K) com atributos normalizados do grupo
                cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                A = torch.cat(cols, dim=1).to(dtype=torch.float32, device=self.device)
                N, K = A.shape
                w = self._weights[gname].to(dtype=torch.float32)
                bpar = self._biases[gname].view(())

                # use effective weights for analysis (respecting positivity floor)
                if self.enforce_positive_weights:
                    w = F.softplus(w) + self.weight_floor

                # Trata pesos ~0 (evita divisão explosiva)
                w_abs = torch.abs(w)
                small = w_abs < self.eps_w_est

                eff = {}

                if mode == "nodewise":
                    # Vectorized: a_k*(i) = -(b + sum_j w_j a_j(i) - w_k a_k(i)) / w_k
                    wk = w.view(1, -1)              # (1,K)
                    sum_all = (A * wk).sum(dim=1, keepdim=True)  # (N,1)
                    thr_nodes_all = -(bpar + sum_all - A * wk) / wk  # (N,K)
                    # Mascara pesos pequenos como NaN
                    if small.any():
                        thr_nodes_all[:, small] = float('nan')

                    # Agregação por coluna (k)
                    if quantile is not None:
                        vals = [_nanquantile(thr_nodes_all[:, k], float(quantile)).item() for k in range(K)]
                    elif agg == "median":
                        vals = [torch.nanmedian(thr_nodes_all[:, k]).item() for k in range(K)]
                    else:
                        vals = [torch.nanmean(thr_nodes_all[:, k]).item() for k in range(K)]

                else:  # mode == "typical"
                    # Usa valor típico por atributo (mediana/média nos nós)
                    if agg == "median":
                        typical = torch.nanmedian(A, dim=0).values  # (K,)
                    else:
                        typical = torch.nanmean(A, dim=0)           # (K,)
                    vals = []
                    for k in range(K):
                        if small[k]:
                            vals.append(float('nan'))
                            continue
                        # soma dos j≠k com valores típicos
                        sum_except = (w * typical).sum() - w[k] * typical[k]
                        thr_k = -(bpar + sum_except) / w[k]
                        vals.append(float(thr_k.item()))

                # Desscala para o domínio bruto (por atributo)
                for k, attr_type in enumerate(group):
                    v = float(vals[k])
                    if _math.isnan(v):
                        v_raw = float('nan')
                    else:
                        if self.scale_mode == "minmax01":
                            stats = self._ds_stats.get(attr_type, None)
                            if stats is not None:
                                amin = float(stats["amin"].item())
                                amax = float(stats["amax"].item())
                                v_raw = v * (amax - amin) + amin
                            else:
                                v_raw = float('nan')
                        elif self.scale_mode == "zscore_tree":
                            stats = self._ds_stats.get(attr_type, None)
                            if stats is not None and stats["count"].item() > 0:
                                count = stats["count"].to(torch.float32)
                                mean  = float((stats["sum"] / count).item())
                                var   = float((stats["sumsq"] / count - (stats["sum"] / count) ** 2).item())
                                std   = float(np.sqrt(max(var, self.eps)))
                                v_raw = v * std + mean
                            else:
                                v_raw = float('nan')
                        elif self.scale_mode == "none":
                            v_raw = v
                        else:
                            v_raw = float('nan')

                    name = attr_type.name
                    eff[name] = {"norm": v, "raw": v_raw}

                results[(b, c, gname)] = eff

        return results


    # ---------- análise de proximidade à fronteira σ=0.5 (margens por atributo) ----------
    def estimate_margins_to_boundary(self,
                                     x: torch.Tensor,
                                     channel: int = 0,
                                     agg: str = "median",
                                     quantiles: tuple = (0.5, 0.9)) -> dict:
        """
        Estima, para cada grupo g e atributo k, **quão perto** cada nó positivo (logit>0)
        está da fronteira de decisão σ=0.5 ao longo do eixo de `a_k`.

        Ideia técnica (comentário explicativo):
            Seja o logit do nó i:  ℓ_i = (A w + b)_i. A fronteira σ=0.5 equivale a ℓ=0.
            Fixando todos os atributos exceto k, o passo necessário em a_k para zerar o logit é:

                Δ_k(i) = a_k(i) - a_k*(i) = ℓ_i / w_k

            (deriva de a_k* = -( b + Σ_{j≠k} w_j a_j(i) ) / w_k ).
            Logo, a **distância** até a fronteira ao longo do atributo k é |Δ_k(i)| = |ℓ_i / w_k|.
            Para ℓ_i ≤ 0 (nós já no lado negativo), descartamos o nó pois ele não está “pressionando”
            a fronteira do lado positivo. Para w_k ≈ 0, Δ_k(i) fica indefinido → ignoramos (∞/NaN).

        O que o método retorna:
            • Para cada (b,c,g), estatísticas por atributo k:
                - dist["agg"]: estatística agregada (mediana/média) de |Δ_k| em nós positivos (ℓ>0)
                - dist["q"]: quantis de |Δ_k| conforme `quantiles`
                - prop_nearest: proporção de nós positivos em que k é o atributo mais “crítico” (menor |Δ_k|)
              E também o total de nós positivos considerados: `count_pos_nodes`.

        Args:
            x (torch.Tensor): batch de entrada (B, C, H, W)
            channel (int): canal a usar quando C>1 (default 0)
            agg (str): "median" ou "mean" para a estatística agregada
            quantiles (tuple): lista/tupla de quantis em [0,1] (ex.: (0.5, 0.9))

        Returns:
            dict: {(b,c,gname): { 'count_pos_nodes': int,
                                  attr_name: { 'dist': { 'agg': float,
                                                          'q': {q: float, ...} },
                                               'prop_nearest': float } }}
        """
        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        assert agg in ("median", "mean"), "agg deve ser 'median' ou 'mean'"
        # normaliza quantiles
        q_list = [float(q) for q in (quantiles if isinstance(quantiles, (list, tuple)) else [quantiles])]
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"

        results = {}
        eps_w = self.eps

        for b in range(B):
            c = channel if C > 1 else 0
            img_np = self._to_numpy_u8(x[b, c])
            t_u8   = torch.from_numpy(img_np)
            key    = self._hash_tensor_sha256(t_u8, c)
            self._ensure_tree_and_attr(key, img_np)
            self._maybe_refresh_norm_for_key(key)

            for g, group in enumerate(self.group_defs):
                gname = self._group_name(group)
                cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                A = torch.cat(cols, dim=1).to(dtype=torch.float32, device=self.device)  # (N,K)
                N, K = A.shape
                w = self._weights[gname].to(dtype=torch.float32)
                bpar = self._biases[gname].view(())

                # logit por nó e máscara de nós positivos (ℓ>0)
                logit = (A @ w.view(-1)) + bpar  # (N,)
                mask_pos = logit > 0
                count_pos = int(mask_pos.sum().item())

                out_g = { 'count_pos_nodes': count_pos }
                if count_pos == 0:
                    # sem nós positivos: popula com NaNs/zeros
                    for k, attr_type in enumerate(group):
                        name = attr_type.name
                        out_g[name] = {
                            'dist': { 'agg': float('nan'), 'q': {q: float('nan') for q in q_list} },
                            'prop_nearest': 0.0,
                        }
                    results[(b, c, gname)] = out_g
                    continue

                Apos = A[mask_pos]          # (N_pos,K)
                ell  = logit[mask_pos]      # (N_pos,)

                # Distâncias |Δ_k| = |ℓ / w_k| (broadcast), com proteção para w≈0
                W = w.view(1, -1).expand_as(Apos)  # (N_pos,K)
                absW = W.abs()
                # usa +inf onde |w_k|<eps para excluir do argmin/estatística
                D = torch.where(absW >= eps_w, ell.view(-1,1).abs() / absW, torch.tensor(float('inf'), device=self.device))

                # atributo mais próximo por nó (menor |Δ_k|)
                k_star = torch.argmin(D, dim=1)  # (N_pos,)

                # proporção de vezes em que cada k é o “gargalo”
                prop = {}
                for k in range(K):
                    prop_k = float((k_star == k).float().mean().item())
                    prop[k] = prop_k

                # estatísticas por atributo (ignorando inf)
                for k, attr_type in enumerate(group):
                    name = attr_type.name
                    d_k = D[:, k]
                    finite_mask = torch.isfinite(d_k)
                    if finite_mask.any():
                        d_vals = d_k[finite_mask]
                        agg_val = (torch.median(d_vals) if agg == 'median' else torch.mean(d_vals)).item()
                        q_vals = {q: (torch.quantile(d_vals, q).item() if 0.0 <= q <= 1.0 else float('nan')) for q in q_list}
                    else:
                        agg_val = float('nan')
                        q_vals = {q: float('nan') for q in q_list}

                    out_g[name] = {
                        'dist': { 'agg': float(agg_val), 'q': {float(q): float(v) for q, v in q_vals.items()} },
                        'prop_nearest': float(prop[k]),
                    }

                results[(b, c, gname)] = out_g

        return results
    
    def collect_dataset_stats(self, x, channel: int = 0, cache: bool = False) -> dict:
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
                  para `zscore_tree`: {count, mean, std}; para `none`: {}.
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
            elif self.scale_mode == "zscore_tree":
                count = st["count"].to(torch.float32)
                mean  = (st["sum"] / count) if count.item() > 0 else torch.tensor(0.0)
                var   = (st["sumsq"] / count - mean * mean) if count.item() > 0 else torch.tensor(0.0)
                std   = torch.sqrt(torch.clamp(var, min=self.eps))
                summary[name] = {"count": int(count.item()), "mean": float(mean.item()), "std": float(std.item())}
            else:
                summary[name] = {}
        return summary



    
    def feasibility_loss(self, x: torch.Tensor, k_sigma: float = 3.0, weight: float = 0.01, channel: int = 0) -> torch.Tensor:
        """Penaliza thresholds efetivos (em RAW) que saem de uma faixa plausível.

        Para cada atributo, define um intervalo: minmax (se scale_mode=minmax01) ou μ±kσ (se zscore_tree).
        Calcula limiares efetivos via `estimate_effective_thresholds(x, agg="median")` e adiciona penalidade
        proporcional à distância para dentro da faixa.
        """
        eff = self.estimate_effective_thresholds(x, agg="median", channel=channel)
        # pega o primeiro item (b,c,g)
        if not eff:
            return torch.zeros((), device=self.device)
        _, vals = next(iter(eff.items()))
        pen = 0.0
        for attr_type in self._all_attr_types:
            name = attr_type.name
            v_raw = vals.get(name, {}).get("raw", float("nan"))
            stats = self._ds_stats.get(attr_type, None)
            if stats is None:
                continue
            if self.scale_mode == "minmax01":
                lo, hi = float(stats["amin"].item()), float(stats["amax"].item())
            elif self.scale_mode == "zscore_tree":
                cnt = stats["count"].to(torch.float32)
                if cnt.item() <= 0:
                    continue
                mu = (stats["sum"]/cnt).item()
                var = (stats["sumsq"]/cnt - (stats["sum"]/cnt)**2).item()
                std = max(var, self.eps) ** 0.5
                lo, hi = mu - k_sigma*std, mu + k_sigma*std
            else:
                continue
            if not np.isnan(v_raw):
                if v_raw < lo:
                    pen += (lo - v_raw)
                elif v_raw > hi:
                    pen += (v_raw - hi)
        return float(weight) * torch.as_tensor(pen, dtype=torch.float32, device=self.device)

    def weight_stability_summary(self) -> dict:
        """Retorna |w|, flags de pequeno-módulo, e se positivity está ativa."""
        out = {}
        for g, group in enumerate(self.group_defs):
            gname = self._group_name(group)
            w = self._weights[gname].detach().float().cpu()
            if self.enforce_positive_weights:
                w_eff = F.softplus(self._weights[gname].detach()).cpu() + self.weight_floor
            else:
                w_eff = w
            out[gname] = {
                "w": w.tolist(),
                "w_eff": w_eff.tolist(),
                "small_mask": (torch.abs(w_eff) < self.eps_w_est).tolist(),
            }
        return out
    
    
    # Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterLayer',
    'ConnectedFilterFunction',
]