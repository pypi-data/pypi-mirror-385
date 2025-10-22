from __future__ import annotations

from contextlib import contextmanager
from enum import Enum
from functools import wraps
from typing import Callable, List, Sequence, TypeVar

from ppl._C.libppl.ppl import ir
from ppl.runtime.jit import jit
from .. import math, semantic
from ..core import (builtin, _to_tensor, get_npu_num, tensor, gtensor, dtype,
                    _constexpr_to_value, float32)
from ..core import (
    bfloat16,
    block_type,
    constexpr,
    dtype,
    float16,
    float32,
    float64,
    float8e4b15,
    float8e4,
    float8e5,
    function_type,
    int1,
    int16,
    int32,
    int64,
    int8,
    mtype,
    pvoid_t,
    pi1_t,
    pi8_t,
    pi16_t,
    pi32_t,
    pi64_t,
    pu8_t,
    pu16_t,
    pu32_t,
    pu64_t,
    pfp8e4_t,
    pfp8e5_t,
    pfp8e4b15_t,
    pfp16_t,
    pbf16_t,
    pfp32_t,
    pfp64_t,
    pointer_type,
    gtensor,
    GLOBAL,
    L2,
    LOCAL,
    tensor,
    # ppl,
    uint16,
    uint32,
    uint64,
    uint8,
    void,
    get_eu_num,
    get_nic,
    lane_num,
    LANE_NUM,
    round_mode,
    RM_HALF_TO_EVEN,
    RM_HALF_AWAY_FROM_ZERO,
    RM_TOWARDS_ZERO,
    RM_DOWN,
    RM_UP,
    RM_HALF_UP,
    RM_HALF_DOWN,
    align_mode,
    CONTINUOUS,
    TPU_ALIGN,
    TPU_COMPACT,
    TPU_ROW_ALIGN,
    NONE_ALIGN,
    coeff_table_mode,
    EXP,
    LOG,
    SIN,
    COS,
    TAN,
    ARCSIN,
    ERF_TAYLOR,
    transpose_mode,
    CW_TRANS,
    NC_TRANS
)

import inspect

T = TypeVar('T')

@builtin
def move(dst, src, port_id:int=-1, _builder=None):
    """
    将张量的元素在 global memory 与 l2 memory 之间搬运

        .. code-block:: python

            move(dst, src)
            dst = src

    参数:
        - ``dst`` (`ppl.language.tensor`):  l2 memory 或 global memory 上的张量

        - ``src`` (`ppl.language.tensor`):  l2 memory 或 global memory 上的张量

    返回值:
        无

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def sdma_move_kernel(
                src_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                src_global = pl.gtensor(shape, pl.GLOBAL, src_ptr)
                l2_global = pl.gtensor(shape, pl.L2, dtype=src_ptr.dtype)
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                pl.sdma.move(l2_global, src_global)
                pl.sdma.move(o_global, l2_global)
    """
    return semantic.sdma_move(dst, src,
                              _to_tensor(_constexpr_to_value(port_id), _builder), _builder)
'''
@builtin
def transpose_cw(dst:pl.tensor,
                 src:pl.tensor,
                 port_id:int=-1,
                _builder=None):
    return semantic.sdma_transpose_cw(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                _to_tensor(_constexpr_to_value(port_id)),
                                _builder)
'''
@builtin
def transpose_nc(dst:pl.tensor,
                 src:pl.tensor,
                 port_id:int=-1,
                _builder=None):
    """
    将张量的元素在 global memory 与 l2 memory 之间拷贝, 并进行 C 和 N 的维度转置

        .. code-block:: python

            transpose_nc(dst, src)
            dst(n, c, h,w) = src(c, n, h,w)

    参数:
        - ``dst`` (`ppl.language.tensor`):  l2 memory 或 global memory 上的张量

        - ``src`` (`ppl.language.tensor`):  l2 memory 或 global memory 上的张量

    返回值:
        无

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def transpose_nc_kernel(
                src_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                src_global = pl.gtensor(shape, pl.GLOBAL, src_ptr)
                l2_global = pl.gtensor([C, N, H, W], pl.L2, dtype=src_ptr.dtype)
                o_global = pl.gtensor([C, N, H, W], pl.GLOBAL, output_ptr)
                pl.sdma.transpose_nc(l2_global, src_global)
                pl.sdma.move(o_global, l2_global)
    """
    return semantic.sdma_transpose_nc(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                _to_tensor(_constexpr_to_value(port_id), _builder),
                                _builder)

@builtin
def transpose(dst:pl.tensor,
                src:pl.tensor,
                trans_mode:transpose_mode=NC_TRANS,
                port_id:int=-1,
                _builder=None):
    """
    将张量的元素在 global memory 与 l2 memory 之间拷贝, 并进行 C 和 N 的维度转置

        .. code-block:: python

            transpose(dst, src)
            dst(n, c, h,w) = src(c, n, h,w)

    参数:
        - ``dst`` (`ppl.language.tensor`):  l2 memory 或 global memory 上的张量

        - ``src`` (`ppl.language.tensor`):  l2 memory 或 global memory 上的张量

        - ``trans_mode`` (``):  默认为NC_TRANS, 不需要配置
    返回值:
        无

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def transpose_kernel(
                src_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                src_global = pl.gtensor(shape, pl.GLOBAL, src_ptr)
                l2_global = pl.gtensor([C, N, H, W], pl.L2, dtype=src_ptr.dtype)
                o_global = pl.gtensor([C, N, H, W], pl.GLOBAL, output_ptr)
                pl.sdma.transpose(l2_global, src_global, trans_mode=pl.NC_TRANS)
                pl.sdma.move(o_global, l2_global)
    """
    if trans_mode is CW_TRANS:
        '''
        return semantic.sdma_transpose_cw(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                _builder)
        '''
        assert False, "don't support"
    else:
        return semantic.sdma_transpose_nc(_to_tensor(dst, _builder),
                                        _to_tensor(src, _builder),
                                        _to_tensor(_constexpr_to_value(port_id), _builder), _builder)


