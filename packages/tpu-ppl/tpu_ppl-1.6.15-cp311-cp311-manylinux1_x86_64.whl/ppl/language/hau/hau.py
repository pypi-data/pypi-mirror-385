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
def topk(dst,
         src,
         K:int,
         descended:bool,
         dst_idx=None,
         src_idx=None,
         _builder=None):
    """
    a. 按升序或降序排序前 K 个最小或最大的数

        .. code-block:: python

                topk(dst, src, K, descended)

        .. math::
          \mathsf{dst(k) = src(i_k)}

      如果升序,则

        .. math::
          \mathsf{src(i_0)\leq src(i_1)\leq\cdots\leq src(i_{K - 1})\leq\cdots\leq src(i_{len - 1})}

      如果降序,则

        .. math::
          \mathsf{src(i_0)\geq src(i_1)\geq\cdots\geq src(i_{K - 1})\geq\cdots\geq src(i_{len - 1})}

      其中，:math:`\mathsf{i_0, i_1, \ldots, i_{len - 1}}` 互不相同，是 :math:`\mathsf{0, 1, \ldots, len - 1}` 的重排


    b. 按升序或降序稳定排序前 K 个最小或最大的数,并输出排序后的索引,排序前的索引是自然索引

        .. code-block:: python

            topk(dst, src, K, descended, dst_idx)

      .. math::
          \mathsf{dst\_data(k) = src(i_k)~~~~dst\_idx(k) = i_k}
      .. math::
          \mathsf{\text{如果}~src(i_{k}) = src(i_{k + 1})\text{,则}~i_{k}<i_{k + 1}}

      如果升序,则

      .. math::
          \mathsf{src(i_0)\leq src(i_1)\leq\cdots\leq src(i_{K - 1})\leq\cdots\leq src(i_{len - 1})}

      如果降序,则

      .. math::
          \mathsf{src(i_0)\geq src(i_1)\geq\cdots\geq src(i_{K - 1})\geq\cdots\geq src(i_{len - 1})}

      其中，:math:`\mathsf{i_0, i_1, \ldots, i_{len - 1}}` 互不相同，是 :math:`\mathsf{0, 1, \ldots, len - 1}` 的重排


    c. 按升序或降序稳定排序前 K 个最小或最大的数,并输出排序后的索引,排序前的索引是指定索引

        .. code-block:: python

            topk(dst, src, K, descended, dst_idx, src_idx)

      .. math::
          \mathsf{dst\_data(k) = src\_data(i_k)~~~~dst\_idx(k) = src\_idx(i_k)}

      .. math::
          \mathsf{\text{如果}~src\_data(i_{k}) = src\_data(i_{k + 1})\text{,则}~src\_idx(i_{k})\leq src\_idx(i_{k + 1})}

      如果升序,则

      .. math::
          \mathsf{src\_data(i_0)\leq src\_data(i_1)\leq\cdots\leq src\_data(i_{K - 1})\leq\cdots\leq src\_data(i_{len - 1})}

      如果降序,则

      .. math::
          \mathsf{src\_data(i_0)\geq src\_data(i_1)\geq\cdots\geq src\_data(i_{K - 1})\geq\cdots\geq src\_data(i_{len - 1})}

      其中，:math:`\mathsf{i_0, i_1, \ldots, i_{len - 1}}` 互不相同，是 :math:`\mathsf{0, 1, \ldots, len - 1}` 的重排。


    参数:
        - ``dst`` (`ppl.language.tensor`):  global memory上的dst张量

        - ``src`` (`ppl.language.tensor`):  global memory上的src张量

        - ``K`` (`int`):  排序长度

        - ``descended`` (`bool`):  降序的标志

        - ``dst_idx`` (`ppl.language.tensor`):  global memory上的dst索引张量

        - ``src_idx`` (`ppl.language.tensor`):  global memory上的src索引张量

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
            def topk_kernel(
                src_ptr,
                src_idx_ptr,
                output_ptr,
                output_idx_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr,
                K:pl.constexpr,
                descended:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                src_global = pl.gtensor(shape, pl.GLOBAL, src_ptr)
                src_idx_global = pl.gtensor(shape, pl.GLOBAL, src_idx_ptr)
                o_global = pl.gtensor([N, C, H, K], pl.GLOBAL, output_ptr)
                o_idx_global = pl.gtensor([N, C, H, K], pl.GLOBAL, output_idx_ptr)
                pl.hau.topk(o_global,  src_global, K, descended, src_idx =src_idx_global, dst_idx = o_idx_global)
    """
    return semantic.topk(_to_tensor(dst, _builder),
                        _to_tensor(dst_idx, _builder),
                        _to_tensor(src, _builder),
                        _to_tensor(src_idx, _builder),
                        _to_tensor(K, _builder),
                        _to_tensor(descended, _builder),
                        _builder)

@builtin
def gather_line(dst:pl.tensor,
                param:pl.tensor,
                index:pl.tensor,
                C,
                start:int,
                end:int,
                fill_const:bool,
                _builder=None):
    """
    通过 line 的索引取值得到输出张量,即 dst = param[index]

        .. code-block:: python

            gather_line(dst, param, index, C, start, end, fill_const)

    参数:
        - ``dst`` (`ppl.language.tensor`): 在global memory中的dst张量

        - ``param`` (`ppl.language.tensor`): 在global memory中的param张量

        - ``index`` (`ppl.language.tensor`): 在global memory中的index张量

        - ``C`` (`常数`): 填充的常数

        - ``start`` (`int`):  有效索引的起始值

        - ``end`` (`int`):  有效索引的结束值

        - ``fill_const`` (`bool`):  dst 在无效索引处填 C 的标志

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
            def gather_line_kernel(
                src_ptr,
                index_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr,
                line_num:pl.constexpr,
                const_val:pl.constexpr,
                start:pl.constexpr,
                end:pl.constexpr,
                fill_const:pl.constexpr
            ):
                pid = pl.get_core_index()
                src_global = pl.gtensor([N, C, line_num, W], pl.GLOBAL, src_ptr)
                index_ptr.set_dtype(pl.pu32_t)
                index_global = pl.gtensor([1, 1, 1, H], pl.GLOBAL, index_ptr)
                o_global = pl.gtensor([N, C, H, W], pl.GLOBAL, output_ptr)
                pl.hau.gather_line(o_global, src_global, index_global, const_val, start, end, fill_const)
    """
    return semantic.gather_line(
                            _to_tensor(dst, _builder),
                            _to_tensor(param, _builder),
                            _to_tensor(index, _builder),
                            _to_tensor(_constexpr_to_value(C), _builder),
                            _to_tensor(_constexpr_to_value(start), _builder),
                            _to_tensor(_constexpr_to_value(end), _builder),
                            _to_tensor(_constexpr_to_value(fill_const), _builder),
                            _builder)
