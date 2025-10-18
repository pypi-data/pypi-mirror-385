import warnings
from math import prod
from typing import TypeVar

from array_api_compat import array_namespace

TArray = TypeVar("TArray")


class AmbiguousBatchAxesWarning(RuntimeWarning):
    pass


def broadcast_without_repeating(
    *arrays: TArray, check_same_ndim: bool = False
) -> tuple[TArray, ...]:
    """
    Broadcast arrays without repeating the data.

    Parameters
    ----------
    arrays : TArray
        The arrays to broadcast.
    check_same_ndim : bool, optional
        Whether to check if all arrays have the same number of dimensions.
        Default is False.

    Returns
    -------
    tuple[TArray]
        The broadcasted arrays.

    """
    xp = array_namespace(*arrays)
    arrays_ = tuple(xp.asarray(a) for a in arrays)
    xp.broadcast_shapes(*[a.shape for a in arrays_])
    if check_same_ndim:
        if len({a.ndim for a in arrays_}) != 1:
            raise ValueError(
                "All arrays must have the same number of dimensions, "
                f"but got {tuple(a.ndim for a in arrays_)}"
            )
        return arrays_
    max_dim = max(a.ndim for a in arrays_)
    return tuple(array[(None,) * (max_dim - array.ndim) + (...,)] for array in arrays_)


def btensorsolve(
    a: TArray,
    b: TArray,
    /,
    *,
    axes: tuple[int] | None = None,
    num_batch_axes: int | None = None,
) -> TArray:
    """
    Solve the tensor equation ``a x = b`` for x.

    It is assumed that all indices of `x` are summed over in the product,
    together with the rightmost indices of `a`, as is done in, for example,
    ``tensordot(a, x, axes=x.ndim)``.

    Parameters
    ----------
    a : array_like
        Coefficient tensor, of shape ``b.shape + Q``. `Q`, a tuple, equals
        the shape of that sub-tensor of `a` consisting of the appropriate
        number of its rightmost indices, and must be such that
        **there exists i that**
        ``prod(Q) == prod(b.shape[i:])``
    b : array_like
        Right-hand tensor, which can be of any shape.
    axes : tuple of ints, optional
        Axes in `a` to reorder to the right, before inversion.
        If None (default), no reordering is done.
    num_batch_axes : int, optional
        The number of batch dimensions. If None (default), the number of batch
        dimensions is inferred from the shapes of `a` and `b`.

        Let ``shape = np.broadcast_shapes(a.shape[:b.ndim],
        b.shape) + a.shape[b.ndim:]``.

        It is recommended to specify this argument, as the inference
        might be wrong if there exists i >= 0, j > 0 that
        ``prod(shape[:i]) == prod(shape[i+j:])``. (j + 1 possibilities)

        For example, if `a` has shape (3, 1, 1, 2, 2) and `b` has shape
        (3, 1, 1, 2), it is possible that
        - axis 1 is the batch axes and desired output shape is (3, 2)
        - axis 1, 2 are the batch axes and desired output shape is (3, 1, 2)
        - axis 1, 2, 3 are the batch axes and desired output shape is (3, 1, 1, 2)

    Returns
    -------
    x : ndarray, shape Q

    Raises
    ------
    LinAlgError
        If `a` is singular or not 'square' (in the above sense).

    Warnings
    --------
    AmbiguousBatchAxesWarning
        If the number of batch axes cannot be inferred from the shapes of
        `a` and `b`, and `num_batch_axes` is not specified.

    See Also
    --------
    numpy.tensordot, tensorinv, numpy.einsum

    Examples
    --------
    >>> import numpy as np
    >>> rng = np.random.default_rng()
    >>> a = rng.normal(size=(2, 2*3, 4, 2, 3, 4))
    >>> b = rng.normal(size=(2, 2*3, 4))
    >>> x = np.linalg.tensorsolve(a, b)
    >>> x.shape
    (2, 2, 3, 4)
    >>> np.allclose(np.einsum('...ijklm,...klm->...ij', a, x), b)
    True

    """
    # https://github.com/numpy/numpy/blob/
    # e7a123b2d3eca9897843791dd698c1803d9a39c2/numpy/linalg/_linalg.py#L291
    xp = array_namespace(a, b)
    a_ = xp.asarray(a)
    b_ = xp.asarray(b)
    an = a_.ndim
    if axes is not None:
        allaxes = list(range(0, an))
        for k in axes:
            allaxes.remove(k)
            allaxes.insert(an, k)
        a_ = a_.transpose(allaxes)

    # find right dimensions
    # a = [2 (dim1) 2 2 3 (dim2) 2 6]
    # b = [2 (dim1) 2 2 3 (dim2)]
    axis_sol_last = b_.ndim
    ashape = a_.shape
    bshape = b_.shape
    shape = xp.broadcast_shapes(ashape[:axis_sol_last], bshape)

    # the dimension of the linear system
    sol_size = int(prod(ashape[axis_sol_last:]))
    if num_batch_axes is None:
        sol_size_current = 1
        for num_batch_axes in range(axis_sol_last - 1, -1, -1):
            sol_size_current *= shape[num_batch_axes]
            if sol_size_current == sol_size:
                break
        else:
            raise ValueError(
                "Unable to divide batch dimensions and solution dimensions"
            )

        if num_batch_axes > 0 and shape[num_batch_axes - 1] == 1:
            warnings.warn(
                "It is impossible to infer the number of "
                "batch axes from the shapes of `a` and `b`. "
                "Consider specifying `num_batch_axes` explicitly.",
                AmbiguousBatchAxesWarning,
                stacklevel=2,
            )

    a_ = xp.broadcast_to(
        a_,
        ashape[:num_batch_axes]
        + shape[num_batch_axes:axis_sol_last]
        + ashape[axis_sol_last:],
    )
    b_ = xp.broadcast_to(b_, bshape[:num_batch_axes] + shape[num_batch_axes:])
    a_ = a_.reshape(ashape[:num_batch_axes] + (sol_size, sol_size))
    b_ = b_.reshape(bshape[:num_batch_axes] + (sol_size, 1))
    x = xp.linalg.solve(a_, b_)
    x = x.reshape(shape[:num_batch_axes] + ashape[axis_sol_last:])
    return x
