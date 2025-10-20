"""Interface Python para MTLearn."""

from importlib import import_module

try:
    # Torch precisa ser importado antes do módulo nativo para expor os
    # conversores de Tensor utilizados nos bindings compilados.
    import torch  # noqa: F401
except ImportError as exc:  # pragma: no cover - falha explícita em runtime
    raise ImportError("mtlearn requer o pacote torch para carregar os bindings compilados") from exc


from . import layers
from . import datasets as datasets

_bindings = import_module("._mtlearn", package=__name__)

WITH_TORCH = getattr(_bindings, "WITH_TORCH", False)

ConnectedFilterByMorphologicalTree = getattr(_bindings, "ConnectedFilterByMorphologicalTree", None)
ConnectedFilterByJacobian = getattr(_bindings, "ConnectedFilterByJacobian", None)
InfoTree = getattr(_bindings, "InfoTree", None)




__all__ = [
    "WITH_TORCH",
    "ConnectedFilterByMorphologicalTree",
    "ConnectedFilterByJacobian",
    "InfoTree",    
]

__version__ = "0.1.0"
