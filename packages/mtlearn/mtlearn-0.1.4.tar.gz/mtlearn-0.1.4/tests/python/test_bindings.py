import mtlearn
import sys

if not getattr(mtlearn, "WITH_TORCH", False):
    print("SKIP build sem suporte ao LibTorch")
    sys.exit(0)

try:
    import torch
except Exception as exc:  # pragma: no cover
    print(f"SKIP torch indisponível: {exc}")
    sys.exit(0)


def test_make_tree_tensor_roundtrip():
    try:
        stats, tensor = mtlearn.make_tree_tensor(6)
    except ImportError:
        print("SKIP torch indisponível durante a chamada")
        return

    assert isinstance(stats, mtlearn.TreeStats)
    assert stats.num_nodes == 6

    assert isinstance(tensor, torch.Tensor)
    assert tensor.dtype == torch.float32
    assert tensor.shape == (6,)
    assert torch.allclose(tensor, torch.arange(6, dtype=torch.float32))


if __name__ == "__main__":
    test_make_tree_tensor_roundtrip()
    print("ok")
