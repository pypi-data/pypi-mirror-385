from __future__ import annotations

from ..runtime.jit import jit
from . import core

# -----------------------
# Standard library
# -----------------------
@jit
def align(x, div):
    """
    对齐操作

        .. code-block:: python

            output = align(x, div)

    参数:
        - ``x`` (`int`): 被除数

        - ``div`` (`int`): 除数

    返回值:
        - ``output`` (`int`): 对齐操作的结果

    """
    return (x + div - 1) // div * div

@jit
def cdiv(x, div):
    """
    向上取整, ceiling计算

        .. code-block:: python

            output = cdiv(x, div)

    参数:
        - ``x`` (`int`): 被除数

        - ``div`` (`int`): 除数

    返回值:
        - ``output`` (`int`): 向上取整的结果

    """
    return (x + div - 1) // div


@jit
@core._add_math_1arg_docstr("sigmoid")
def sigmoid(x):
    return 1 / (1 + core.exp(-x))


@jit
@core._add_math_1arg_docstr("softmax")
def softmax(x, ieee_rounding=False):
    z = x - core.max(x, 0)
    num = core.exp(z)
    den = core.sum(num, 0)
    return core.fdiv(num, den, ieee_rounding)


@jit
def ravel(x):
    """
    Returns a contiguous flattened view of :code:`x`.

    :param x: the input tensor
    :type x: Block
    """
    return core.view(x, [x.numel])


@jit
def swizzle2d(i, j, size_i, size_j, size_g):
    """
    Transforms indices of a row-major size_i*size_j matrix into those
    of one where indices are row major for each group of size_j rows.
    For example, for size_i = size_j = 4 and size_g = 2, it will transform
    [[0 , 1 , 2 , 3 ],
     [4 , 5 , 6 , 7 ],
     [8 , 9 , 10, 11],
     [12, 13, 14, 15]]
    into
    [[0, 2,  4 , 6 ],
     [1, 3,  5 , 7 ],
     [8, 10, 12, 14],
     [9, 11, 13, 15]]
    """
    # "unrolled index in array"
    ij = i * size_j + j
    # number of elements in `size_g` groups
    # of `size_j` columns
    size_gj = size_g * size_j
    # index of the group in which (i,j) is
    group_id = ij // size_gj
    # row-index of the first element of this group
    off_i = group_id * size_g
    # last group may have fewer rows
    size_g = core.minimum(size_i - off_i, size_g)
    # new row and column indices
    new_i = off_i + (ij % size_g)
    new_j = (ij % size_gj) // size_g
    return new_i, new_j

