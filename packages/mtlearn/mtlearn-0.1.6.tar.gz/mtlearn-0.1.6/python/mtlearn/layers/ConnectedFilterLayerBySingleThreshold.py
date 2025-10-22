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
#  Versão com parâmetro threshold NORMALIZADO + normalização por árvore
# ============================
# --- Função customizada de autograd para propagar gradiente do limiar ---
class ConnectedFilterFunctionBySingleThreshold(torch.autograd.Function):
    @staticmethod
    def forward(ctx, tree, attr_scaled_1d, threshold_norm, beta_f: float=1000.0, beta_b: float=1.0, clamp_logits: bool=True ):
        """
        attr_scaled_1d: (numNodes,)  atributo já normalizado por-árvore (na prática,
            aqui usamos normalização por dataset; ver camada abaixo)
        threshold_norm: ()           limiar normalizado NA MESMA escala de attr_scaled_1d
        Parâmetros de forma da sigmoide:
        - beta_f (forward): controla a "inclinação" da sigmoide usada no FORWARD.
            * < 1 → curva mais suave; = 1 → sigmoide padrão; > 1 → mais degrau
            * Recomenda-se beta_f=1000 para um forward praticamente "hard".
        - beta_b (backward): controla a inclinação usada no CÁLCULO DO GRADIENTE
          (estimador). Tipicamente mantemos beta_b=1 para um backward "soft".
        """
        logits = attr_scaled_1d - threshold_norm.view(())
        # Máscara soft (sigmóide). Para um STE "hard", poderia-se usar algo como:
        #   hard = (beta_f*logits >= 0).float()
        #   sigmoid_soft1D = hard.detach() - (torch.sigmoid(beta_f*logits)).detach() + torch.sigmoid(beta_f*logits)
        # Assim, o valor que segue no forward é binário, mas o gradiente
        # continua sendo o do sigmoide (straight-through estimator).
        #   Quando beta_f >> 1 (e.g., 1000), o forward se aproxima de um limiar duro.
        s = beta_f * logits
        if clamp_logits:
            s = torch.clamp(s, min=-12.0, max=12.0)
        sigmoid_soft1D = torch.sigmoid(s)   # (numNodes,)

        # Aplica o filtering conectado (regra substrativa) na árvore com criterio definido pela sigmoid
        # Nota: a operação de filtering em C++ é diferenciável (autograd disponível).
        # Em prática, usar beta_f elevado endurece a sigmoide e tem mostrado acelerar a convergência.
        y_pred = mtlearn.ConnectedFilterByMorphologicalTree.filtering(tree, sigmoid_soft1D)

        ctx.tree = tree
        ctx.beta_b = beta_b
        ctx.clamp_logits = clamp_logits
        ctx.save_for_backward(sigmoid_soft1D)
        return y_pred

    @staticmethod
    # No backward, propagamos gradiente APENAS para o limiar normalizado
    # via rotina específica `gradientsOfThreshold`. Atributos/árvore não
    # recebem gradiente (são None).
    def backward(ctx, grad_output):
        """
        Backprop do limiar normalizado. Usa `beta_b` para ajustar a inclinação
        da sigmoide NO GRADIENTE (estimador). Valores usuais:
          - beta_b < 1 → gradiente mais suave
          - beta_b = 1 → sigmoide padrão (recomendado)
          - beta_b > 1 → gradiente mais "duro"
        Em conjunto com beta_f=1000 no forward, fornece o padrão "forward hard,
        backward soft" (STE).
        """
        (sigmoid_soft1D,) = ctx.saved_tensors
        tree = ctx.tree
        beta_b = ctx.beta_b
        grad_threshold_norm = mtlearn.ConnectedFilterByMorphologicalTree.gradientsOfThreshold(tree, sigmoid_soft1D, beta_b, grad_output)
        return None, None, grad_threshold_norm, None, None, None


# --- Camada PyTorch: gerencia caches, normalização e thresholds ---
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
    
    Notas de implementação:
    • As estatísticas de normalização são mantidas em `_ds_stats` e um
      contador `_stats_epoch` invalida normalizações cacheadas sempre que
      mudam.
    • O cache `_trees/_base_attrs/_norm_attrs` é indexado por uma chave
      SHA-256 do conteúdo da imagem (por canal), garantindo reuso seguro.
    • Autoinicialização de `thr_norm` por quantil do atributo normalizado
      torna o treinamento mais estável do que iniciar aleatoriamente.

    Parâmetros importantes:
    • beta_f (float): ganho da sigmoide no FORWARD. <1 suaviza; =1 padrão; >1 deixa
      mais "degrau". Para um efeito quase hard no forward, use ~1000.
    • beta_b (float): ganho da sigmoide no BACKWARD (apenas no estimador de gradiente).
      Recomenda-se 1 para um backward "soft". Combinar beta_f=1000 e beta_b=1 produz
      o comportamento típico de STE (forward hard / backward soft).
    """
    def __init__(self, in_channels, attributes_spec, tree_type="max-tree", device="cpu", scale_mode: str = "minmax01", eps: float = 1e-6, initial_quantile_threshold: float = 0.5, beta_f: float = 1000.0, beta_b: float = 1.0, top_hat: bool = False, clamp_logits: bool = True):
        """
        Args:
            in_channels (int): # de canais de entrada.
            attributes_spec (Iterable[Type|Iterable[Type]]): lista de grupos (deve ser
                unitário por grupo), cada qual com um atributo.
            tree_type (str): "max-tree" | "min-tree" | outro (ToS).
            device (str): dispositivo para tensores de saída e parâmetros.
            scale_mode (str): "minmax01" | "zscore_tree" | "none".
            eps (float): proteção numérica para divisões/raiz.
            initial_quantile_threshold (float): quantil para auto-init de `thr_norm`.
            beta_f (float): ganho da sigmoide no FORWARD. <1 suaviza; =1 padrão; >1 degrau.
                Recomenda-se beta_f=1000 para um forward praticamente hard.
            beta_b (float): ganho da sigmoide no BACKWARD (gradiente). Recomenda-se 1
                para um backward soft.
            top_hat (bool): se True, aplica top-hat após o filtering.
            clamp_logits (bool): se True, aplica clamp em beta_f*logits em ±12 somente na hora da sigmoide (estabilidade numérica).
        """
        super().__init__()
        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        if device != "cpu":
                raise ValueError("O modelo só está implementado para CPU.")
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)   # 'minmax01' | 'zscore_tree' | 'none'
        self.eps         = float(eps)
        self.initial_quantile_threshold = float(initial_quantile_threshold)
        self.beta_f = float(beta_f)
        self.beta_b = float(beta_b)
        self.top_hat = bool(top_hat)
        self.clamp_logits = bool(clamp_logits)

        
        # Cada entrada de `attributes_spec` deve ser unitária (1 atributo por grupo),
        # pois esta camada aprende um limiar por grupo. Aqui normalizamos
        # a entrada para tuplas do tipo (attr_type,), e rejeitamos grupos maiores.
        # grupos unitários (um atributo por grupo)
        self.group_defs = []
        for item in attributes_spec:
            group = tuple(item) if isinstance(item, (list, tuple)) else (item,)
            if len(group) != 1:
                raise ValueError("Cada grupo deve conter exatamente 1 atributo para o threshold.")
            self.group_defs.append(group)

        self.num_groups   = len(self.group_defs)
        self.out_channels = self.in_channels * self.num_groups
        # Lista plana de atributos (útil para helpers compartilhados).
        self._attr_types = [attr_type for (attr_type,) in self.group_defs]

        # caches por conteúdo
        self._trees      = {}  # key -> tree
        self._base_attrs = {}  # key -> { Type -> Tensor (numNodes,1) }
        self._norm_attrs = {}  # key -> { Type -> Tensor (numNodes,) }
        # versioning/invalidations for dataset-wide normalization
        self._stats_epoch = 0                   # increments whenever ds stats change
        self._norm_epoch_by_key = {}            # key -> epoch when normalization was computed

        # Parâmetros aprendíveis: um `thr_norm` (escala normalizada) por atributo.
        # Usamos um ParameterDict indexado pelo `attr_type.name`.
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
        """Atualiza stats globais via helper compartilhado; avança _stats_epoch quando necessário."""
        changed = update_ds_stats(self._ds_stats, self.scale_mode, attr_type, a_raw_1d)
        if changed:
            self._stats_epoch += 1

    def _normalize_with_ds_stats(self, attr_type, a_raw_1d: torch.Tensor) -> torch.Tensor:
        """Wrapper thin sobre o helper de normalização para manter API da camada."""
        return normalize_with_ds_stats(self._ds_stats, self.scale_mode, self.eps, attr_type, a_raw_1d)

    def _maybe_refresh_norm_for_key(self, key: str):
        """Delegado ao helper para manter caches sincronizados quando _stats_epoch avançar."""
        maybe_refresh_norm_for_key(key, self._base_attrs, self._norm_attrs, self._attr_types, self._ds_stats, self.scale_mode, self.eps, self._norm_epoch_by_key, self._stats_epoch)

    # ---------- helpers de árvore/atributo ----------
    def _hash_tensor_sha256(self, t_u8: torch.Tensor, chan_idx: int):
        return hash_tensor_sha256(t_u8, chan_idx)

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        return to_numpy_u8(img2d_t)

    def _build_tree(self, img_np: np.ndarray):
        return build_tree(img_np, self.tree_type)

    def _ensure_tree_and_attr(self, key: str, img_np: np.ndarray):
        # Garante que a árvore e os atributos (bruto e normalizado) estejam
        # cacheados para a chave `key`. Se ainda não existem, computa e salva.
        if key in self._trees:
            return
        tree = self._build_tree(img_np)
        self._trees[key] = tree

        per_attr_raw, per_attr_norm = {}, {}
        for (attr_type,) in self.group_defs:
            attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
            # Atualiza estatísticas do dataset com os atributos BRUTOS desta árvore
            # (efeito-colateral: pode invalidar normalizações antigas via `_stats_epoch`).
            self._update_ds_stats(attr_type, a_raw_1d)

            # Normaliza usando as estatísticas GLOBAIS do dataset atuais.
            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)

            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)  # debug/compat
            per_attr_norm[attr_type] = a_norm

        self._base_attrs[key] = per_attr_raw
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Aplica o filtro conectado por (b,c) com máscara sigmoide do atributo
        normalizado. `beta_f` (forward) e `beta_b` (backward) controlam a dureza
        da sigmoide: beta_f grande (~1000) ≈ forward hard; beta_b=1 → backward soft.
        Na prática, uma sigmoide 'soft' (beta_f baixo) atrasa a convergência; endurecer (beta_f alto) acelera.
        """
        # Espera input (B, C, H, W). Para cada (b,c):
        #   1) Converte imagem 2D para uint8 (CPU) e calcula chave SHA-256
        #   2) Constrói/recupera árvore e atributos do cache
        #   3) (Re)normaliza atributos se as estatísticas do dataset mudaram
        #   4) Aplica filtro conectado com máscara sigmoide do atributo normalizado
        #   5) (Opcional) aplica top-hat conforme o tipo de árvore
        assert x.dim() == 4, f"Esperado (B, C, H, W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, mas input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                # 1) Conversão para uint8 (CPU) e hash por conteúdo (canal c)
                img_np = self._to_numpy_u8(x[b, c])   # np.uint8 (CPU)
                t_u8   = torch.from_numpy(img_np)     # tensor CPU uint8 (view)
                key    = self._hash_tensor_sha256(t_u8, c)
                # 2) Garante árvore/atributos cacheados para esta chave
                self._ensure_tree_and_attr(key, img_np)
                tree = self._trees[key]
                # 3) Se `_stats_epoch` mudou, re-normaliza atributos cacheados
                self._maybe_refresh_norm_for_key(key)

                # 4) Para cada atributo do grupo unitário, aplica Filtering conectado
                for g, (attr_type,) in enumerate(self.group_defs):
                    name      = attr_type.name
                    a_scaled  = self._norm_attrs[key][attr_type]  # (numNodes,)

                    thr_norm  = self._thr_norm[name]              # (1,)

                    # Autoinit 1x: define `thr_norm` como o quantil do atributo
                    # NORMALIZADO desta chave. Melhora a estabilidade do treinamento.
                    if name not in self._thr_norm_initialized:
                        with torch.no_grad():
                            init_val = torch.quantile(a_scaled, self.initial_quantile_threshold)
                            self._thr_norm[name].copy_(init_val)
                        self._thr_norm_initialized.add(name)

                    # forward usa thr_norm diretamente (mesma escala de a_scaled)
                    y_ch = ConnectedFilterFunctionBySingleThreshold.apply(tree, a_scaled, thr_norm, self.beta_f, self.beta_b, self.clamp_logits)  # (H,W)
                    
                    # (Opcional) Top-hat na saída do canal filtrado:
                    #   • max-tree:  img − filtrado
                    #   • min-tree:  filtrado − img
                    #   • ToS/default: |filtrado − img|
                    #   • Dureza da sigmoide: `beta_f` (forward) e `beta_b` (backward). Sugerido: 1000/1.
                    if self.top_hat:
                        x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
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
        e desabilitando o cálculo de gradientes.

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
                    img_np = self._to_numpy_u8(x[b, c])
                    t_u8 = torch.from_numpy(img_np)
                    key = self._hash_tensor_sha256(t_u8, c)
                    self._ensure_tree_and_attr(key, img_np)
                    self._maybe_refresh_norm_for_key(key)
                    tree = self._trees[key]

                    for g, (attr_type,) in enumerate(self.group_defs):
                        name = attr_type.name
                        a_scaled = self._norm_attrs[key][attr_type]
                        thr_norm = self._thr_norm[name]

                        # forward (sem gradiente) com beta_f fixo
                        y_ch = ConnectedFilterFunctionBySingleThreshold.apply(tree, a_scaled, thr_norm, beta_f, self.beta_b, self.clamp_logits)
                        

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

        # Restaura o modo anterior (train/eval)
        if was_training:
            self.train()
        else:
            self.eval()
        return out

    # ---------- salvar / inspecionar ----------
    def save_params(self, path: str):
        # Salva thresholds NORMALIZADOS + stats do dataset para reprodutibilidade.
        """Salva os thresholds **normalizados** (um por grupo) E as estatísticas do dataset (`_ds_stats`).
        Obs.: `beta_f`/`beta_b`/`clamp_logits` não são salvos aqui; ajuste-os no construtor."""
        payload = {
            "thresholds_norm": { name: p.detach().cpu() for name, p in self._thr_norm.items() },
            "ds_stats": self._ds_stats,
            "scale_mode": self.scale_mode,
        }
        # Backward-compat: also flatten thr_norm_* at top-level
        for name, p in self._thr_norm.items():
            payload[f"thr_norm_{name}"] = p.detach().cpu()
        torch.save(payload, path)
        print(f"[ConnectedThresholdLayer] thresholds NORMALIZADOS + ds_stats salvos em {path}")

    def get_descaled_threshold(self, channel: int = 0):
        # Converte cada `thr_norm` (escala normalizada) para o domínio BRUTO do
        # atributo, usando as estatísticas GLOBAIS acumuladas do dataset.
        """
        Converte cada `thr_norm` para o domínio BRUTO usando as stats GLOBAIS do dataset
        acumuladas até o momento (dataset-wide normalization).
        Independente de beta_f/beta_b, a desscala reflete as stats globais do dataset.
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
        # Força re-normalização de TODAS as chaves cacheadas com as estatísticas
        # atuais do dataset (`_stats_epoch`). Pode ser custoso em caches grandes.
        """Re-normaliza os atributos de TODAS as árvores cacheadas com as stats de dataset atuais.
        Não afeta `beta_f`/`beta_b`; apenas reusa suas configurações atuais.
        """
        for key in list(self._base_attrs.keys()):
            self._maybe_refresh_norm_for_key(key)

# Exporta as entidades públicas do módulo
__all__ = [
    'ConnectedFilterLayerBySingleThreshold',
    'ConnectedFilterFunctionBySingleThreshold',
]
