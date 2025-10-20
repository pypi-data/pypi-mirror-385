"""
# -----------------------------------------------------------------------------
# mtlearn.layers._helpers
# -----------------------------------------------------------------------------
# Utilitários compartilhados para camadas baseadas em árvores morfológicas:
#  - hashing por conteúdo (cache estável por imagem/canal)
#  - conversão para uint8
#  - construção de árvore (max/min/ToS)
#  - normalização por estatísticas de dataset (minmax / zscore_tree / none)
#  - (re)normalização de atributos cacheados por chave
#
# Observação importante
#   * A filtragem conectada em C++ (mtlearn.ConnectedFilterByMorphologicalTree)
#     é diferenciável. Já a construção de árvores e o cálculo de atributos não.
#   * Estes helpers são funcionais para facilitar reuso/testes; as camadas
#     chamam passando seus próprios dicionários/estados.
# -----------------------------------------------------------------------------
"""
from __future__ import annotations

import struct
import hashlib
from typing import Dict, Any, Tuple, Iterable, Mapping

import numpy as np
import torch
import mmcfilters

# --------------------------- hashing e conversão ----------------------------

def group_name(group: Iterable[Any]) -> str:
    """Gera um nome estável para um grupo de atributos (ex.: "AREA+GRAY_HEIGHT")."""
    return "+".join([getattr(t, "name", str(t)) for t in group])


def hash_tensor_sha256(t_u8: torch.Tensor, chan_idx: int) -> str:
    """Gera uma chave estável por (canal, shape, dtype, bytes) para uso em cache.

    Args:
        t_u8: tensor **CPU** e **contíguo** de dtype uint8 com shape (H, W)
        chan_idx: índice do canal que originou esta imagem
    """
    assert t_u8.device.type == "cpu", "hash só suporta tensor em CPU"
    if not t_u8.is_contiguous():
        t_u8 = t_u8.contiguous()
    assert t_u8.dtype == torch.uint8, "esperado uint8"
    h = hashlib.sha256()
    h.update(struct.pack("=I", int(chan_idx)))
    h.update(struct.pack("=I", t_u8.ndimension()))
    for s in t_u8.shape:
        h.update(struct.pack("=I", int(s)))
    h.update(str(t_u8.dtype).encode())
    # view sem cópia
    arr = t_u8.numpy()
    h.update(memoryview(arr))
    return h.hexdigest()


def to_numpy_u8(img2d_t: torch.Tensor) -> np.ndarray:
    """Converte (H,W) para uint8.

    Regras:
      • se max≤1.5 assume [0,1] e escala ×255;
      • caso contrário, realiza cast direto para uint8.
    Atenção: entradas >255 podem sofrer truncamento.
    """
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


# ---------------------------- árvores morfológicas --------------------------

def build_tree(img_np: np.ndarray, tree_type: str):
    """Constrói a árvore morfológica conforme `tree_type`.

    Args:
        img_np: imagem 2D em np.uint8
        tree_type: "max-tree" | "min-tree" | outro (ToS)
    """
    if tree_type == "max-tree":
        return mmcfilters.MorphologicalTree(img_np, True)
    elif tree_type == "min-tree":
        return mmcfilters.MorphologicalTree(img_np, False)
    else:
        return mmcfilters.MorphologicalTree(img_np)


# -------------------- normalização por estatísticas de dataset --------------
# Reutilizado pelas camadas ConnectedFilterLayerByThresholds e
# ConnectedFilterLayerBySingleThreshold para manter o cache consistente.

def update_ds_stats(ds_stats: Dict[Any, Dict[str, torch.Tensor]],
                    scale_mode: str,
                    attr_type: Any,
                    a_raw_1d: torch.Tensor) -> bool:
    """Atualiza estatísticas do **dataset**. Retorna True se elas mudaram.

    Para `minmax01`: expande [amin, amax] conforme chegam novas amostras.
    Para `zscore_tree`: acumula `count`, `sum`, `sumsq`.
    Para `none`: não faz nada.
    """
    if scale_mode == "minmax01":
        amin_new = torch.min(a_raw_1d.detach())
        amax_new = torch.max(a_raw_1d.detach())
        changed = False
        if attr_type not in ds_stats:
            ds_stats[attr_type] = {"amin": amin_new, "amax": amax_new}
            changed = True
        else:
            st = ds_stats[attr_type]
            if amin_new < st["amin"]:
                st["amin"] = amin_new
                changed = True
            if amax_new > st["amax"]:
                st["amax"] = amax_new
                changed = True
        return changed
    elif scale_mode == "zscore_tree":
        v = a_raw_1d.detach().to(torch.float32)
        cnt = torch.tensor(v.numel(), dtype=torch.long)
        sm = torch.sum(v)
        sq = torch.sum(v * v)
        if attr_type not in ds_stats:
            ds_stats[attr_type] = {"count": cnt, "sum": sm, "sumsq": sq}
        else:
            ds_stats[attr_type]["count"] = ds_stats[attr_type]["count"] + cnt
            ds_stats[attr_type]["sum"]   = ds_stats[attr_type]["sum"] + sm
            ds_stats[attr_type]["sumsq"] = ds_stats[attr_type]["sumsq"] + sq
        return True
    elif scale_mode == "none":
        return False
    else:
        raise ValueError(f"scale_mode desconhecido: {scale_mode}")


def normalize_with_ds_stats(ds_stats: Mapping[Any, Dict[str, torch.Tensor]],
                            scale_mode: str,
                            eps: float,
                            attr_type: Any,
                            a_raw_1d: torch.Tensor) -> torch.Tensor:
    """Normaliza um vetor 1D usando `ds_stats`+`scale_mode`.

    • minmax01: (x−amin)/(amax−amin)
    • zscore_tree: (x−μ)/σ
    • none: identidade
    """
    if scale_mode == "minmax01":
        stats = ds_stats.get(attr_type, None)
        if stats is None:
            amin = torch.min(a_raw_1d)
            amax = torch.max(a_raw_1d)
        else:
            amin = stats["amin"]
            amax = stats["amax"]
        denom = torch.clamp(amax - amin, min=eps)
        return (a_raw_1d - amin) / denom
    elif scale_mode == "zscore_tree":
        stats = ds_stats.get(attr_type, None)
        if stats is None or stats["count"].item() == 0:
            mean = torch.mean(a_raw_1d)
            std  = torch.std(a_raw_1d).clamp_min(eps)
        else:
            count = stats["count"].to(torch.float32)
            mean  = stats["sum"] / count
            var   = stats["sumsq"] / count - mean * mean
            std   = torch.sqrt(torch.clamp(var, min=eps))
        return (a_raw_1d - mean) / std
    elif scale_mode == "none":
        return a_raw_1d
    else:
        raise ValueError(f"scale_mode desconhecido: {scale_mode}")


def maybe_refresh_norm_for_key(key: str,
                               base_attrs: Dict[Any, Dict[Any, torch.Tensor]],
                               norm_attrs: Dict[Any, Dict[Any, torch.Tensor]],
                               all_attr_types: Iterable[Any],
                               ds_stats: Mapping[Any, Dict[str, torch.Tensor]],
                               scale_mode: str,
                               eps: float,
                               norm_epoch_by_key: Dict[str, int],
                               current_epoch: int) -> None:
    """Re-normaliza atributos cacheados da `key` quando `current_epoch` avança."""
    last_epoch = norm_epoch_by_key.get(key, -1)
    if last_epoch == current_epoch:
        return
    per_attr_raw = base_attrs[key]
    per_attr_norm = {}
    for attr_type in all_attr_types:
        a_raw_1d = per_attr_raw[attr_type].squeeze(1)
        a_norm   = normalize_with_ds_stats(ds_stats, scale_mode, eps, attr_type, a_raw_1d)
        per_attr_norm[attr_type] = a_norm
    norm_attrs[key] = per_attr_norm
    norm_epoch_by_key[key] = current_epoch


__all__ = [
    "group_name",
    "hash_tensor_sha256",
    "to_numpy_u8",
    "build_tree",
    "update_ds_stats",
    "normalize_with_ds_stats",
    "maybe_refresh_norm_for_key",
]
