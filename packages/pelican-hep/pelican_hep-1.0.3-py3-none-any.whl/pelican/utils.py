"""Utility functions for handling batch and pointer representations."""
import torch


def get_batch_from_ptr(ptr):
    """Reconstruct batch indices (batch) from pointer (ptr).

    Parameters
    ----------
    ptr : torch.Tensor
        Pointer tensor indicating the start of each batch.
        Tensor of shape (B+1,) where B is the number of batches.

    Returns
    -------
    torch.Tensor
        A tensor where each element indicates the batch index for each item.
        Tensor of shape (N,) where N is the total number of items across all batches.
    """
    return torch.arange(len(ptr) - 1, device=ptr.device).repeat_interleave(
        ptr[1:] - ptr[:-1],
    )


def get_ptr_from_batch(batch):
    """Reconstruct pointer (ptr) from batch indices (batch).

    Parameters
    ----------
    batch : torch.Tensor
        A tensor where each element indicates the batch index for each item.
        Tensor of shape (N,) where N is the total number of items across all batches.

    Returns
    -------
    torch.Tensor
        A pointer tensor indicating the start of each batch.
        Tensor of shape (B+1,) where B is the number of batches.
    """
    ptr = torch.cat(
        [
            torch.tensor([0], device=batch.device),
            torch.where(batch[1:] - batch[:-1] != 0)[0] + 1,
            torch.tensor([batch.shape[0]], device=batch.device),
        ],
        0,
    )
    return ptr


def get_edge_index_from_ptr(ptr, shape, remove_self_loops=True):
    """Construct edge index of fully connected graph from pointer (ptr).
    This function should be used for graphs represented by sparse tensors,
    i.e. graphs where the number of nodes per graph can vary.

    Parameters
    ----------
    ptr : torch.Tensor
        Pointer tensor indicating the start of each batch.
        Tensor of shape (B+1,) where B is the number of batches.
    shape : torch.Size
        Shape of the node tensor, expected to be (N, C)
    remove_self_loops : bool, optional
        Whether to remove self-loops from the edge index, by default True.

    Returns
    -------
    torch.Tensor
        A tensor of shape (2, E) where E is the number of edges, representing the edge index.
    """
    N = shape[0]

    diff = ptr[1:] - ptr[:-1]
    starts = torch.zeros(N, dtype=torch.long, device=ptr.device)
    starts.scatter_(0, ptr[:-1], torch.ones_like(ptr[:-1]))
    node2graph = starts.cumsum(0) - 1

    counts = diff[node2graph] - (1 if remove_self_loops else 0)
    E = counts.sum()
    row = torch.repeat_interleave(counts, output_size=E)

    g = node2graph[row]
    offset = ptr[g]
    row_local = row - offset

    start = counts.cumsum(0) - counts
    idx = torch.arange(row.numel(), device=ptr.device, dtype=torch.long)
    pos = idx - start[row]

    if remove_self_loops:
        col_local = pos + (pos >= row_local).to(torch.long)
    else:
        col_local = pos
    col = col_local + offset

    edge_index = torch.stack([row, col], dim=0)
    return edge_index


def get_edge_index_from_shape(
    shape, device=torch.device("cpu"), remove_self_loops=True
):
    """Construct edge index of fully connected graph from the shape of a corresponding dense tensor.
    This function should be used for graphs represented by dense tensors,
    i.e. graphs where the number of nodes per graph is fixed.

    Parameters
    ----------
    shape : torch.Size
        Shape of the dense node tensor, expected to be (B, N, C)
        where B is the batch size and N is the number of nodes.
    device : torch.device
        Device on which the tensors are allocated. Default is CPU.
    remove_self_loops : bool, optional
        Whether to remove self-loops from the edge index, by default True.

    Returns
    -------
    torch.Tensor
        A tensor of shape (2, E) where E is the number of edges, representing the edge index.
    """
    B, N, _ = shape

    nodes = torch.arange(N, device=device)

    if remove_self_loops:
        row = nodes.repeat_interleave(N - 1)
        base = torch.arange(N - 1, device=device)
        i = nodes.unsqueeze(1)
        col_2d = base.unsqueeze(0).expand(N, -1)
        col_2d = col_2d + (col_2d >= i)
        col = col_2d.reshape(-1)
    else:
        row = nodes.repeat_interleave(N)
        col = nodes.repeat(N)

    edge_base = torch.stack([row, col], dim=0)

    offsets = torch.arange(B, device=device, dtype=torch.long) * N
    batched = edge_base.unsqueeze(2) + offsets.view(1, 1, -1)
    edge_index_global = batched.permute(0, 2, 1).reshape(2, -1)

    batch = torch.arange(B, device=device).repeat_interleave(N)
    return edge_index_global, batch


def get_edge_attr(fourmomenta, edge_index, eps=1e-10):
    """Calculate edge attributes based on the squared Lorentz norm of the sum of four-momenta.

    Parameters
    ----------
    fourmomenta : torch.Tensor
        A tensor of shape (B, N, 4) representing the four-momenta of particles.
    edge_index : torch.Tensor
        A tensor of shape (2, E) representing the edge index of the graph.
    eps : float, optional
        A small value to avoid log(0) issues, by default 1e-10.

    Returns
    -------
    torch.Tensor
        A tensor of shape (E,) representing the edge attributes, which are the logarithm of the squared Lorentz norm.
    """
    mij2 = lorentz_squarednorm(fourmomenta[edge_index[0]] + fourmomenta[edge_index[1]])
    edge_attr = mij2.clamp(min=eps).log()
    return edge_attr


def lorentz_squarednorm(v):
    """Lorentz norm, i.e. v^T @ g @ v

    Parameters
    ----------
    v : torch.Tensor
        Tensor of shape (..., 4)

    Returns
    -------
    torch.Tensor
        Lorentz norm of shape (..., )
    """
    t = v[..., 0] * v[..., 0]
    s = (v[..., 1:] * v[..., 1:]).sum(dim=-1)
    return t - s
