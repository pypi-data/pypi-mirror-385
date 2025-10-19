import torch
import pytest

from pelican.utils import (
    get_edge_index_from_ptr,
    get_edge_index_from_shape,
    get_batch_from_ptr,
    get_ptr_from_batch,
)


@pytest.mark.parametrize("B, N", [(1, 5), (4, 9)])
@pytest.mark.parametrize("remove_self_loops", [True, False])
def test_get_edge_index_tools(B, N, remove_self_loops, C=16):
    # test that the two get_edge_index functions give the same result
    tensor = torch.randn(B, N, C)
    ptr = torch.arange(B + 1) * N

    edge_index_from_shape, _ = get_edge_index_from_shape(
        tensor.shape, tensor.device, remove_self_loops=remove_self_loops
    )
    tensor_sparse = tensor.view(B * N, C)
    edge_index_from_ptr = get_edge_index_from_ptr(
        ptr, tensor_sparse.shape, remove_self_loops=remove_self_loops
    )

    assert torch.all(edge_index_from_shape == edge_index_from_ptr)


@pytest.mark.parametrize("B, N", [(1, 5), (4, 9)])
def test_ptr_batch_invertibility(B, N):
    ptr = torch.arange(B + 1) * N
    batch = get_batch_from_ptr(ptr)
    ptr_test = get_ptr_from_batch(batch)
    assert torch.all(ptr == ptr_test)
