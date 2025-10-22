from __future__ import annotations

from contextlib import contextmanager
from enum import Enum
from functools import wraps
from typing import Callable, List, Sequence, TypeVar

from ppl._C.libppl.ppl import ir
from ppl.runtime.jit import jit
from .. import math, semantic
from ..core import (builtin, _to_tensor, get_npu_num, tensor, gtensor, dtype, _constexpr_to_value, float32)
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
    NC_TRANS,
    ALL_REDUCE_PSUM_WO,
    ALL_REDUCE_PSUM_WR,
    ALL_REDUCE_NOP,
    ALL_REDUCE_MUL,
    ALL_REDUCE_MAX,
    ALL_REDUCE_MIN,
    ALL_REDUCE_ADD,
)

import inspect

T = TypeVar('T')

@builtin
def load(*args, align_mode=TPU_ALIGN, _builder=None):
    """
    将张量的元素从 global / l2 memory拷贝到local memory, 并且按指定align_mode排列

        .. code-block:: python

            load(dst, src) or dst = load(src)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, c, h, w)}

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在local memory上的张量

        - ``src`` (`ppl.language.tensor`): src在global memory或L2上的张量

        - ``align_mode`` (`pl.align_mode`):  对齐模式, 默认为TPU_ALIGN

    返回值:
        - ``dst`` (`ppl.language.tensor`): dst张量或无返回值

    注意事项:
        无
    """
    align_mode = _constexpr_to_value(_constexpr_to_value(align_mode).val())
    if len(args) == 1 and isinstance(args[0], tensor):
        return semantic.load(None, args[0], align_mode, _builder)
    elif len(args) == 2 and all(isinstance(t, tensor) for t in args):
        return semantic.load(args[0], args[1], align_mode, _builder)
'''
from functools import singledispatch
@singledispatch
@builtin
def load(pointer, _builder=None):
   pass

@load.register
def _(pointer:tensor, _builder=None):
    return semantic.load(pointer, False, _builder)

@load.register
def _(pointer:list, _builder=None):
    pass
'''
@builtin
def load_compact(*args, _builder=None):
    """
    张量的元素从 global / l2 memory 拷贝到 local memory,并按照compact layout排列

        .. code-block:: python

            load_compact(dst, src) or dst = load_compact(src)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, c, h, w)}

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在local memory上的张量

        - ``src`` (`ppl.language.tensor`): src在global memory或L2上的张量

    返回值:
        - ``dst`` (`ppl.language.tensor`): dst张量或无返回值

    注意事项:
        无
    """
    align_mode = _constexpr_to_value(TPU_COMPACT).val()
    if len(args) == 1 and isinstance(args[0], tensor):
        return semantic.load(None, args[0], align_mode, _builder)
    elif len(args) == 2 and all(isinstance(t, tensor) for t in args):
        return semantic.load(args[0], args[1], align_mode, _builder)

@builtin
def store(dst, src, _builder=None):
    """
    将张量的元素从 local memory 拷贝到 global memory

        .. code-block:: python

            store(dst, src)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, c, h, w)}

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在global memory上的张量

        - ``src`` (`ppl.language.tensor`): local memory上的张量

    返回值:
        无

    注意事项:
        无
    """
    src = _to_tensor(src, _builder)
    return semantic.store(dst, src, _builder)

@builtin
def load_transpose_cw(dst:pl.tensor,
                    src:pl.tensor,
                    _builder=None):
    """
    将张量的元素从 global / l2 memory 拷贝到 local memory, 并进行 C 和 W 的维度转置

        .. code-block:: python

            load_transpose_cw(dst, src)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, w, h, c)}

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory 上的张量

        - ``src`` (`ppl.language.tensor`): global / l2 memory 上的张量

    返回值:
        无

    注意事项:
        无
    """
    return semantic.load_transpose_cw(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def load_transpose_nc(dst:pl.tensor,
                    src:pl.tensor,
                    _builder=None):
    """
    将张量的元素从 global / l2 memory 拷贝到 local memory, 并进行 N 和 C 的维度转置

        .. code-block:: python

            load_transpose_nc(dst, src)

    .. math:: \mathsf{dst(n, c, h, w) = src(c, n, h, w)}

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory 上的张量

        - ``src`` (`ppl.language.tensor`): global / l2 memory 上的张量

    返回值:
        无

    注意事项:
        无
    """
    return semantic.load_transpose_nc(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def load_transpose(dst:pl.tensor,
                    src:pl.tensor,
                    trans_mode:transpose_mode=CW_TRANS,
                    _builder=None):
    """
    将张量的元素从 global / l2 memory 拷贝到 local memory, 支持N和C维度转置,也支持C和W维度转置

        .. code-block:: python

            load_transpose(dst, src, trans_mode)

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory 上的张量

        - ``src`` (`ppl.language.tensor`): global / l2 memory 上的张量

        - ``trans_mode`` (`pl.transpose_mode`): 转置模式
    返回值:
        无

    注意事项:
        无
    """
    if trans_mode is CW_TRANS:
        return semantic.load_transpose_cw(_to_tensor(dst, _builder),
                                        _to_tensor(src, _builder),
                                        _builder)
    else:
        return semantic.load_transpose_nc(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def store_transpose_cw(dst:pl.tensor,
                    src:pl.tensor,
                    _builder=None):
    """
    将张量的元素从 local memory 拷贝到 global memory, 并进行 C 和 W 的维度转置

        .. code-block:: python

            store_transpose_cw(dst, src)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, w, h, c)}

    参数:
        - ``dst`` (`ppl.language.tensor`): global memory 上的张量

        - ``src`` (`ppl.language.tensor`): local memory 上的张量

    返回值:
        无

    注意事项:
        无
    """
    return semantic.store_transpose_cw(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def store_transpose_nc(dst:pl.tensor,
                    src:pl.tensor,
                    _builder=None):
    """
    将张量的元素从 local memory 拷贝到 global memory, 并进行 N 和 C 的维度转置

        .. code-block:: python

            store_transpose_nc(dst, src)

    .. math:: \mathsf{dst(n, c, h, w) = src(c, n, h, w)}

    参数:
        - ``dst`` (`ppl.language.tensor`): global memory 上的张量

        - ``src`` (`ppl.language.tensor`): local memory 上的张量

    返回值:
        无

    注意事项:
        无
    """
    return semantic.store_transpose_nc(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def store_transpose(dst:pl.tensor,
                    src:pl.tensor,
                    trans_mode:transpose_mode=CW_TRANS,
                    _builder=None):
    """
    将张量的元素从 local memory 拷贝到 global memory, 支持N和C维度转置,也支持C和W维度转置

        .. code-block:: python

            store_transpose(dst, src, trans_mode)

    参数:
        - ``dst`` (`ppl.language.tensor`): global memory 上的张量

        - ``src`` (`ppl.language.tensor`): local memory 上的张量

        - ``trans_mode`` (`pl.transpose_mode`): 转置模式
    返回值:
        无

    注意事项:
        无
    """
    if trans_mode is CW_TRANS:
        return semantic.store_transpose_cw(_to_tensor(dst, _builder),
                                        _to_tensor(src, _builder),
                                        _builder)
    else:
        return semantic.store_transpose_nc(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def load_broadcast(dst:pl.tensor,
                    src:pl.tensor,
                    npu_num=0,
                    _builder=None):
    """
    将张量的元素从 global memory 拷贝到 local memory, 并在 C 维度进行广播

        .. code-block:: python

            load_broadcast(dst, src, npu_num)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, 1, h, w)}

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory 上的张量

        - ``src`` (`ppl.language.tensor`): global memory上的张量

        - ``npu_num`` (`int`): C维度广播数量, 默认为LANE_NUM

    返回值:
        无

    注意事项:
        无
    """
    return semantic.load_broadcast(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _to_tensor(npu_num, _builder),
                                    _builder)

@builtin
def transpose_nc(dst:pl.tensor,
                src:pl.tensor,
                _builder=None):
    """
    将global memory或local memory上的张量做NC转置

        .. code-block:: python

            transpose_nc(dst, src, npu_num)

    参数:
        - ``dst`` (`ppl.language.tensor`): global memory或local memory上的张量

        - ``src`` (`ppl.language.tensor`): global memory或local memory上的张量

    返回值:
        无

    注意事项:
        只支持SG2380
    """
    return semantic.transpose_nc(_to_tensor(dst, _builder),
                                    _to_tensor(src, _builder),
                                    _builder)

@builtin
def transpose(dst:pl.tensor,
                src:pl.tensor,
                trans_mode:transpose_mode=CW_TRANS,
                _builder=None):
    """
    将global memory或local memory上的张量做NC转置或CW转置

        .. code-block:: python

            transpose(dst, src, trans_mode)

    参数:
        - ``dst`` (`ppl.language.tensor`): global memory或local memory上的张量

        - ``src`` (`ppl.language.tensor`): global memory或local memory上的张量

        - ``trans_mode`` (`ppl.transpose_mode`): 转置模式
    返回值:
        无

    注意事项:
        只支持SG2380
    """
    if trans_mode is CW_TRANS:
        return semantic.transpose_cw(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                False,
                                _builder)
    else:
        return semantic.transpose_nc(_to_tensor(dst, _builder),
                                        _to_tensor(src, _builder),
                                        _builder)

@builtin
def mask_batch_bcast(dst:pl.tensor,
                    count: pl.tensor,
                    src:pl.tensor,
                    mask:pl.tensor,
                    is_repeat:bool=False,
                    _builder=None):
    """
    通过 w 维度的蒙版取值得到输出张量, 即 dst = src[mask], 并统计蒙版中的非零值数量, src 的 batch 被广播

        .. code-block:: python

            mask_batch_bcast(dst, count, src, mask, is_repeat)

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory上的dst张量

        - ``count`` (`ppl.language.tensor`): local memory上的count张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``mask`` (`ppl.language.tensor`): local memory上的mask张量

        - ``is_repeat`` (`bool`): src 重复的标志

    返回值:
        无

    注意事项:
        无
    """
    return semantic.mask_batch_bcast(_to_tensor(dst, _builder),
                                        _to_tensor(count, _builder),
                                        _to_tensor(src, _builder),
                                        _to_tensor(mask, _builder),
                                        _to_tensor(_constexpr_to_value(is_repeat), _builder),
                                        _builder)

@builtin
def reverse(dst:pl.tensor,
            src:pl.tensor,
            dim:int,
            _builder=None):
    """
    将 tensor 数据沿着 dim 维度做倒置, 支持 8/16/32 bit 等数据位宽

        .. code-block:: python

            reverse(dst, src, dim)

    参数:
        - ``dst`` (`ppl.language.tensor`): global/local memory 上的dst张量

        - ``src`` (`ppl.language.tensor`): global/local memory 上的src张量

        - ``dim`` (`int`): 倒置的维度

    返回值:
        无

    注意事项:
        只支持SG2380
    """
    return semantic.reverse(_to_tensor(dst, _builder),
                            _to_tensor(src, _builder),
                            _to_tensor(_constexpr_to_value(dim), _builder),
                            _builder)
@builtin
def vload(dst_v_idx,
        src:pl.tensor,
        _builder=None):
    """
    将张量的元素从 global / l2 memory 拷贝到 vector 寄存器

        .. code-block:: python

            vload(dst_v_idx, src)

    参数:
        - ``dst_v_idx`` (`int`): vector 寄存器的索引

        - ``src`` (`ppl.language.tensor`): global memory 上的src张量

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用 vector 寄存器之前, 必须先设置寄存器状态;
            若 vector 寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx 必须是 vset 所设置的 lmul 数值的整数倍
    """
    return semantic.vload(_to_tensor(_constexpr_to_value(dst_v_idx), _builder),
                            _to_tensor(src, _builder),
                            _builder)

@builtin
def vstore(dst:pl.tensor,
            v_idx:int,
            _builder=None):
    """
    将张量的元素从 vector 寄存器拷贝到 global memory

        .. code-block:: python

            vstore(dst, v_idx)

    参数:
        - ``dst`` (`ppl.language.tensor`): global memory 上的dst张量

        - ``v_idx`` (`int`): vector 寄存器的索引

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用 vector 寄存器之前, 必须先设置寄存器状态;
            若 vector 寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx 必须是 vset 所设置的 lmul 数值的整数倍
    """
    return semantic.vstore(_to_tensor(dst, _builder),
                            _to_tensor(_constexpr_to_value(v_idx), _builder),
                            _builder)

@builtin
def move_tv(dst,
            v_idx:int,
            _builder=None):
    """
    从 vector 寄存器加载数据到 LMEM/SMEM 的指令。指令将一组 vector 寄存器的数据加载到 LMEM 或 SMEM 上

        .. code-block:: python

            move_tv(dst, v_idx)

    参数:
        - ``dst`` (`ppl.language.tensor或标量`): local memory 上的dst张量 或 static memory 上的地址偏移量

        - ``v_idx`` (`int`): vector 寄存器的索引

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用vector寄存器之前, 必须先设置寄存器状态;
            若vector寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx必须是vset所设置的 lmul 数值的整数倍
        4. 该指令搬运的数据须为 64bit 的倍数
    """
    if isinstance(dst, tensor):
        return semantic.move_tv(_to_tensor(dst, _builder),
                                _to_tensor(_constexpr_to_value(v_idx), _builder),
                                _builder)
    else:
        return semantic.move_tv(_to_tensor(_constexpr_to_value(dst), _builder),
                                _to_tensor(_constexpr_to_value(v_idx), _builder),
                                _builder)

@builtin
def move_distv(dst:pl.tensor,
                v_idx:int,
                _builder=None):
    """
    从 vector 寄存器分发数据到 LMEM 的指令。指令将一组 vector 寄存器的数据均分到所有 Lane 上

        .. code-block:: python

            move_distv(dst, v_idx)

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory上的dst张量

        - ``v_idx`` (`int`): vector 寄存器的索引

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用vector寄存器之前, 必须先设置寄存器状态;
            若vector寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx必须是vset所设置的 lmul 数值的整数倍
        4. 该指令搬运的数据大小须为 64bit 的倍数,并且数据元素个数须能被 LANE_NUM 整除
    """
    return semantic.move_distv(_to_tensor(dst, _builder),
                                _to_tensor(_constexpr_to_value(v_idx), _builder),
                                _builder)

@builtin
def move_vv(dst,
            v_idx0:int,
            v_idx1:int,
            _builder=None):
    """
    从 vector 寄存器加载数据到 LMEM/SMEM 的指令。指令将两组 vector 寄存器的数据拼接加载到 LMEM或SMEM 上

        .. code-block:: python

            move_vv(dst, v_idx0, v_idx1)

    参数:
        - ``dst`` (`ppl.language.tensor或int`): local memory上的dst张量 或static memory 上的地址偏移量

        - ``v_idx0`` (`int`): vector 寄存器的索引

        - ``v_idx1`` (`int`): vector 寄存器的索引

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用vector寄存器之前, 必须先设置寄存器状态;
            若vector寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx必须是vset所设置的 lmul 数值的整数倍
        4. 该指令搬运的数据大小须为 64bit 的倍数
    """
    if isinstance(dst, tensor):
        return semantic.move_vv(_to_tensor(dst, _builder),
                                _to_tensor(_constexpr_to_value(v_idx0), _builder),
                                _to_tensor(_constexpr_to_value(v_idx1), _builder),
                                _builder)
    else:
        return semantic.move_vv(_to_tensor(_constexpr_to_value(dst), _builder),
                                _to_tensor(_constexpr_to_value(v_idx0), _builder),
                                _to_tensor(_constexpr_to_value(v_idx1), _builder),
                                _builder)

@builtin
def move_distvv(dst:pl.tensor,
                v_idx0:int,
                v_idx1:int,
                _builder=None):
    """
    从 vector 寄存器分发数据到 LMEM 的指令。指令将两组 vector 寄存器的数据均分到所有 Lane 上

        .. code-block:: python

            move_distvv(dst, v_idx0, v_idx1)

    参数:
        - ``dst`` (`ppl.language.tensor或int`): local memory上的dst张量

        - ``v_idx0`` (`int`): vector 寄存器的索引

        - ``v_idx1`` (`int`): vector 寄存器的索引

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用vector寄存器之前, 必须先设置寄存器状态;
            若vector寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx必须是vset所设置的 lmul 数值的整数倍
        4. 该指令搬运的数据大小须为 64bit 的倍数,并且数据元素个数须能被 LANE_NUM 整除
    """
    return semantic.move_distvv(_to_tensor(dst, _builder),
                                _to_tensor(_constexpr_to_value(v_idx0), _builder),
                                _to_tensor(_constexpr_to_value(v_idx1), _builder),
                                _builder)

@builtin
def move_vt(dst_v_idx:int,
            src,
            _builder=None):
    """
    从 LMEM/SMEM 存储数据到 vector 寄存器的指令。指令将 LMEM或SMEM 中的数据存储到一组 vector 寄存器中

        .. code-block:: python

            move_vt(dst_v_idx, src)

    参数:
        - ``dst_v_idx`` (`int`): vector 寄存器的索引

        - ``src`` (`ppl.language.tensor或int`): local memory上的src张量或static memory 上的地址偏移量

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用vector寄存器之前, 必须先设置寄存器状态;
            若vector寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx必须是vset所设置的 lmul 数值的整数倍
        4. 该指令搬运的数据大小须为 64bit 的倍数
    """
    if isinstance(src, tensor):
        return semantic.move_vt(
                                _to_tensor(_constexpr_to_value(dst_v_idx), _builder),
                                _to_tensor(src, _builder),
                                _builder)
    else:
        return semantic.move_vt(_to_tensor(_constexpr_to_value(dst_v_idx), _builder),
                                _to_tensor(_constexpr_to_value(src), _builder),
                                _builder)

@builtin
def move_vcoll(dst_v_idx,
            src:pl.tensor,
            _builder=None):
    """
    从 LMEM 收集数据到 vector 寄存器的指令。指令从 LMEM 各个 LANE 相同位置收集数据并存储到一组 vector 寄存器上

        .. code-block:: python

            move_vcoll(dst_v_idx, src)

    参数:
        - ``dst_v_idx`` (`int`): vector 寄存器的索引

        - ``src`` (`ppl.language.tensor`): local memory 上的src张量

    返回值:
        无

    注意事项:
        1. 只支持SG2380
        2. 必须配合vset使用, 即在使用vector寄存器之前, 必须先设置寄存器状态;
            若vector寄存器被多个api使用, 则仅需第一次使用前设置一次
        3. v_idx必须是vset所设置的 lmul 数值的整数倍
        4. 该指令搬运的数据大小须为 64bit 的倍数,并且数据元素个数须能被 LANE_NUM 整除
    """
    return semantic.move_vcoll(_to_tensor(_constexpr_to_value(dst_v_idx), _builder),
                            _to_tensor(src, _builder),
                            _builder)

@builtin
def move(dst, src, _builder=None):
    """
    将张量的元素从 local memory 拷贝到 local memory
    或 将张量的元素从 global 拷贝到 global

        .. code-block:: python

            move(dst, src)
            dst = src

    参数:
        - ``dst`` (`ppl.language.tensor`): dst张量

        - ``src`` (`ppl.language.tensor`): src张量

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
            def move_l2l_kernel(
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
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                out = pl.make_tensor(shape, output_ptr.dtype)
                src = pl.dma.load(src_global)
                pl.dma.move(out, src)
                pl.dma.store(o_global, out)
    """
    return semantic.move(dst, src, False, _builder)

@builtin
def mask_select(dst, src, mask, _builder=None):
    """
    将 local memory或global memory中存储的张量按照 mask 筛选后拷贝到 global memory 中

        .. code-block:: python

            mask_select(dst, src, mask)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在global memory上的张量

        - ``src`` (`ppl.language.tensor`): src在local memory或global memory上的张量

        - ``mask`` (`ppl.language.tensor`): mask在global memory上的张量或在local memory中的张量

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
            def mask_select_S2S_kernel(
                src_ptr,
                mask_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                src_global = pl.gtensor(shape, pl.GLOBAL, src_ptr)
                mask_global = pl.gtensor(shape, pl.GLOBAL, mask_ptr)
                pl.dma.mask_select(o_global, src_global, mask_global)
    """
    return semantic.mask_select(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                _to_tensor(mask, _builder),
                                _builder)

@builtin
def broadcast(*args, npu_num=0, _builder=None):
    """
    将张量的元素从 local memory 拷贝到 local memory,并在 C 维度进行广播

        .. code-block:: python

            broadcast(dst, src, npu_num) or dst = broadcast(src, npu_num)
            dst = src

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在local memory上的张量

        - ``src`` (`ppl.language.tensor`): src在local memory上的张量

        - ``npu_num`` (`常数`):  C 维度广播数量,默认为 LANE_NUM

    返回值:
        - ``dst`` (`ppl.language.tensor`): dst张量或无返回值

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def broadcast_kernel(
                src_ptr,
                output_ptr,
                N:pl.constexpr,
                oc:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, oc, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                src_global = pl.gtensor([N, 1, H, W], pl.GLOBAL, src_ptr)
                out = pl.make_tensor(shape, output_ptr.dtype)
                src = pl.dma.load(src_global)
                pl.dma.broadcast(out, src, npu_num=oc)
                pl.dma.store(o_global, out)
    """
    if all(isinstance(t, tensor) for t in args):
        if len(args) == 2:
            return semantic.broadcast(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(npu_num, _builder),
                            False,
                            _builder)
    assert False

@builtin
def nonzero(dst, src, _builder=None):
    """
    将local memory 的输入张量中不为 0 的元素的 index 输出到 global memory 中
    或将global memory 的输入张量中不为 0 的元素的 index 输出到 global memory 中

        .. code-block:: python

            nonzero(dst, src)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在global memory上的张量

        - ``src`` (`ppl.language.tensor`): src在local memory或global memory上的张量

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
            def nonzero_kernel(
                src_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                src_global = pl.gtensor(shape, pl.GLOBAL, src_ptr)
                src = pl.dma.load(src_global)
                #pl.dma.nonzero(o_global, src_global)
                pl.dma.nonzero(o_global, src)
    """
    return semantic.nonzero(_to_tensor(dst, _builder),
                            _to_tensor(src, _builder),
                            _builder)

@builtin
def transpose_cw(dst:pl.tensor,
                 src:pl.tensor,
                _builder=None):
    """
    张量的 C 与 W 两个维度转置,推荐在 tensor C > W 时使用

        .. code-block:: python

            transpose_cw(dst, src)
            dst(n, c, h,w) = src(n,w, h, c)

    参数:
        - ``dst`` (`ppl.language.tensor`): dst张量

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        无

    注意事项:
        sg2380支持

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def transpose_cw_kernel(
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
                o_global = pl.gtensor([N, W, H, C], pl.GLOBAL, output_ptr)
                pl.dma.transpose_cw(o_global, src_global)

    """
    return semantic.transpose_cw(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                False,
                                _builder)

@builtin
def zero(input,
        _builder=None):
    """
    将global memory中的或local memory中的张量元素置成0

        .. code-block:: python

            zero(input)
            input = 0

    参数:
        - ``input`` (`ppl.language.tensor`): 结果张量

    返回值:
        无

    注意事项:
        无
    """
    dtype = input.dtype.scalar
    if dtype.is_bf16() or dtype.is_fp16() or dtype.is_fp8():
        dtype = float32
    value = _constexpr_to_value(0)
    dtype = _constexpr_to_value(dtype)
    return semantic.fill(input, value, dtype, False, _builder)

@builtin
def fill(input, value, _builder=None):
    """
    将global memory中的或local memory中的张量元素置成常数

        .. code-block:: python

            fill(input, value)

            input = value

    参数:
        - ``input`` (`ppl.language.tensor`): 张量

        - ``value`` (`常数`): 常数

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
            def fill_g_kernel(
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr,
                const:pl.constexpr
            ):
                pid = pl.get_core_index()
                o_global = pl.gtensor([N, C, H, W], pl.GLOBAL, output_ptr)
                pl.dma.fill(o_global, const)
    """
    dtype = input.dtype.scalar
    if dtype.is_bf16() or dtype.is_fp16() or dtype.is_fp8():
        dtype = float32
    value = _constexpr_to_value(value)
    dtype = _constexpr_to_value(dtype)
    return semantic.fill(input, value, dtype, False, _builder)

@builtin
def gather_h(output:pl.tensor,
             param:pl.tensor,
             index:pl.tensor,
             const_val=0,
             index_start_pos=0,
             _builder=None):
    """
    通过 h 维度的索引取值得到输出张量, 即 dst = param[index]

        .. code-block:: python

            gather_h(output, param, index, const_val, index_start_pos)

    参数:
        - ``output`` (`ppl.language.tensor`): dst在global memory或local memory中张量

        - ``param`` (`ppl.language.tensor`): param在global memory或local memory中张量

        - ``index`` (`ppl.language.tensor`): index在global memory或local memory中张量

        - ``const_val`` (`常数`): 填充的常数

        - ``index_start_pos`` (`常数`):  index开始的pos, 默认为0
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
            def gather_h_s2l_kernel(
                param_ptr,
                index_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr,
                param_h:pl.constexpr,
                const_val:pl.constexpr,
                index_start_pos:pl.constexpr
            ):
                pid = pl.get_core_index()
                index_ptr.set_dtype(pl.pu32_t)
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                param_global = pl.gtensor([N, C, param_h, W], pl.GLOBAL, param_ptr)
                index_global = pl.gtensor([N, C, H, 1], pl.GLOBAL, index_ptr)
                out = pl.make_tensor(shape, output_ptr.dtype)
                #param = pl.dma.load(param_global)
                index = pl.dma.load(index_global)
                pl.dma.gather_h(out, param_global, index, const_val, index_start_pos)
                pl.dma.store(o_global, out)
    """
    return semantic.dma_gather_h(output, param, index, \
                             _to_tensor(const_val, _builder), \
                             _to_tensor(index_start_pos, _builder), _builder)

@builtin
def scatter_h(output:pl.tensor,
             param:pl.tensor,
             index:pl.tensor,
             index_start_pos=0,
             inplace_add=False,
             _builder=None):
    """
    通过 h 维度的索引取值得到输出张量, 即 dst = param[index]

        .. code-block:: python

            scatter_h(output, param, index)

        .. math:: \mathsf{dst(1, c, index(1, c, h, 1), w) = param(1, c, h, w)}

    参数:
        - ``output`` (`ppl.language.tensor`): dst张量

        - ``param`` (`ppl.language.tensor`): param张量

        - ``index`` (`ppl.language.tensor`): index张量

        - ``index_start_pos`` (`常数`):  index开始的pos, 默认为0

        - ``inplace_add`` (`bool`):  累加到output, 默认为False

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
            def scatter_h_l2l_kernel(
                param_ptr,
                index_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr,
                param_h:pl.constexpr
            ):
                pid = pl.get_core_index()
                index_ptr.set_dtype(pl.pu32_t)
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                param_global = pl.gtensor([N, C, param_h, W], pl.GLOBAL, param_ptr)
                index_global = pl.gtensor([N, C, param_h, 1], pl.GLOBAL, index_ptr)
                out = pl.make_tensor(shape, output_ptr.dtype)
                pl.tiu.zero(out)
                param = pl.dma.load(param_global)
                index = pl.dma.load(index_global)
                pl.dma.scatter_h(out, param, index)
                pl.dma.store(o_global, out)
    """
    return semantic.dma_scatter_h(output, param, index,
                                  _to_tensor(index_start_pos, _builder),
                                  _to_tensor(inplace_add, _builder),
                                  _builder)

@builtin
def reduce(output:pl.tensor,
            input:pl.tensor,
            psum:pl.all_reduce_psum,
            opcode:pl.all_reduce_opcode,
            _builder=None):
    """
    将张量的元素从 global memory/L2 memory/local memory 到 L2 memory, 进行归约

        .. code-block:: python

            reduce(output, input, psum, opcode)

    参数:
        - ``output`` (`ppl.language.tensor`): L2 memory 上的结果张量

        - ``input`` (`ppl.language.tensor`): global memory/L2 memory/local memory 上的张量

        - ``psum`` (`pl.all_reduce_psum`): ALL_REDUCE_PSUM_WO(Write Only,不操作,仅数据搬运),ALL_REDUCE_PSUM_WR(Read Write,执行计算操作)

        - ``opcode`` (`pl.all_reduce_opcode`): ALL_REDUCE_NOP(不操作,仅数据搬运),ALL_REDUCE_MUL(乘法操作),ALL_REDUCE_MAX(最大值操作),ALL_REDUCE_MIN(最小值操作),ALL_REDUCE_ADD(加法操作)

    返回值:
        无

    注意事项:
        无

    使用示例:
        无
    """
    psum = _to_tensor(psum.val(), _builder)
    opcode = _to_tensor(opcode.val(), _builder)
    return semantic.dma_reduce(output, input, psum, opcode, _builder)
