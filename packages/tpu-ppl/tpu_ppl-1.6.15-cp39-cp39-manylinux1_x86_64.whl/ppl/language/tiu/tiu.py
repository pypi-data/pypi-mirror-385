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
    NC_TRANS
)

import inspect

T = TypeVar('T')

@builtin
def abs(*args, _builder=None):
    """
    对张量的元素取绝对值

        .. code-block:: python

            abs(dst, src) 或 dst = abs(src)

            dst = |src|

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def abs_kernel(
                input_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                in_global = pl.gtensor(shape, pl.GLOBAL, input_ptr)
                input = pl.make_tensor(shape, input_ptr.dtype)
                pl.dma.load(input, in_global)
                out = pl.tiu.abs(input)
                pl.dma.store(o_global, out)
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.abs(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.abs(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder), _builder)
    assert False

@builtin
def cast(*args, type:pl.dtype=void, mode:round_mode=RM_HALF_TO_EVEN,_builder=None):
    """
    a. 转换张量元素的数据类型

    b. 对标量做数据类型转换

        .. code-block:: python

            dst = cast(src, type, mode) or cast(dst, src, type, mode)

    参数:
        - ``dst`` (`ppl.language.tensor或标量`):local memory上的dst张量或标量

        - ``src`` (`ppl.language.tensor或标量`):local memory上的src张量或标量

        - ``dtype`` (`pl.dtype`): 目标转换数据类型

        - ``mode`` (`pl.round_mode`):  round模式

    返回值:
        - ``dst`` (`ppl.language.tensor或标量`):local memory上的dst张量或标量

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr, dtype, round_mode)) for t in args):
        tensors = [item for item in args if isinstance(item, (tensor, constexpr))]
        type_ = [item for item in args if isinstance(item, dtype)]
        mode_ = [item for item in args if isinstance(item, round_mode)]
        type = semantic.get_scalar_dtype(type_[0] if len(type_) == 1 else type)
        if len(tensors) == 1:
            tensors[0] = _to_tensor(tensors[0], _builder)
            return semantic.cast(tensors[0], type, _builder)
        elif len(tensors) == 2:
            tensors[0] = _to_tensor(tensors[0], _builder)
            tensors[1] = _to_tensor(tensors[1], _builder)
            mode = mode_[0] if len(mode_) == 1 else mode
            return semantic.cast_v2(tensors[0], tensors[1], type,
                                   _to_tensor(_constexpr_to_value(mode).val(), _builder),
                                   _builder)
    assert False


@builtin
def minimum(*args, _builder=None):
    """
    a. 两个张量的元素做取小运算

    b. 张量的元素与常数做取小运算

    c. 2个标量做取小运算

        .. code-block:: python

            dst = min(src0, src1) or min(dst, src0, src1)

    参数:
        - ``dst`` (`ppl.language.tensor或标量`):local memory上的dst张量或标量

        - ``src0`` (`ppl.language.tensor或标量`):local memory上的src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`):local memory上的src1张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量`):local memory上的dst张量或标量

    注意事项:
        也可以用别名api: minimum
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.minimum(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder), _builder)
        elif len(args) == 3:
            return semantic.minimum(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder), _builder)
    assert False

minimum.alias = 'min'
globals()[minimum.alias] = minimum

@builtin
def maximum(*args, _builder=None):
    """
    a. 两个张量的元素做取大运算

    b. 张量的元素与常数做取大运算

    c. 2个标量做取大运算

        .. code-block:: python

            dst = max(src0, src1) or max(dst, src0, src1)

    参数:
        - ``dst`` (`ppl.language.tensor或标量`):local memory上的dst张量或标量

        - ``src0`` (`ppl.language.tensor或标量`):local memory上的src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`):local memory上的src1张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量`):local memory上的dst张量或标量

    注意事项:
        也可以用别名api: maximum
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.maximum(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder), _builder)
        elif len(args) == 3:
            return semantic.maximum(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder), _builder)
    assert False
maximum.alias = 'max'
globals()[maximum.alias] = maximum

@builtin
def fmul(*args, saturation:bool=False,  _builder=None):
    """
    a. 两个浮点数据类型张量的元素相乘

    b. 一个张量与一个标量相乘

    c. 两个标量相乘

        .. code-block:: python

            fmul(dst, src0, src1) 或 dst = fmul(src0, src1)

            dst = src0 * src1

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``saturation`` (`bool`): True 表示需要做饱和，bm1684x及bm1688不支持此参数，bm1690仅当一个输入为fp8类型 tensor，另一个为标量时支持此参数。

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.mul(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder),
                        _to_tensor(0, _builder),
                        _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                        _to_tensor(saturation, _builder),
                        _builder)
        elif len(args) == 3:
            return semantic.mul(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder),
                                _to_tensor(0, _builder),
                                _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                                _to_tensor(saturation, _builder),
                                _builder)
    assert False

@builtin
def fadd(*args, saturation:bool=False, _builder=None):
    """
    a. 两个浮点数据类型张量的元素相加

    b. 一个张量与一个标量相加

    c. 两个标量相加

        .. code-block:: python

            fadd(dst, src0, src1) 或 dst = fadd(src0, src1)

            dst = src0 + src1

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``saturation`` (`bool`): True 表示需要做饱和，bm1684x及bm1688不支持此参数，bm1690仅当一个输入为fp8类型 tensor，另一个为标量时支持此参数。

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.add(None, _to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(0, _builder),
                            _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                            _to_tensor(False, _builder),
                            _builder)
        elif len(args) == 3:
            return semantic.add(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder),
                                _to_tensor(0, _builder),
                                _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                                _to_tensor(False, _builder),
                                _builder)
    assert False

@builtin
def fexp(*args, _builder=None):
    """
    张量的元素为指数,自然常数 e 为底数的指数运算

        .. code-block:: python

            fexp(dst, src) 或 dst = fexp(src)

    .. math:: \mathsf{dst(n, c, h, w) = e^{src(n, c, h, w)}}

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fexp(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.fexp(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _builder)
    assert False

@builtin
def fexp_part(*args, _builder=None):
    """
    对浮点数的exponent部分做exp运算

        .. code-block:: python

            fexp_part(dst, src) 或 dst = fexp_part(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fexp_part(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.fexp_part(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _builder)
    assert False

@builtin
def frsqrt(*args, num_iter = 3, _builder=None):
    """
    浮点倒数平方根指令。指令对输入浮点 Tensor src 求倒数平方根计算, 并输出结果到 Tensor dst 中

        .. code-block:: python

            frsqrt(dst, src, num_iter) 或 dst = frsqrt(src, num_iter)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

        - ``num_iter`` (`int`): 牛顿迭代次数

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.frsqrt(None, _to_tensor(args[0], _builder),
                                  _to_tensor(num_iter, _builder), _builder)
        elif len(args) == 2:
            return semantic.frsqrt(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                   _to_tensor(num_iter, _builder), _builder)
    assert False

@builtin
def fsqrt(*args, num_iter = 3, _builder=None):
    """
    浮点平方根指令。指令对输入浮点 Tensor src 求平方根计算, 并输出结果到 Tensor dst 中

        .. code-block:: python

            fsqrt(dst, src, num_iter) 或 dst = fsqrt(src, num_iter)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

        - ``num_iter`` (`int`): 牛顿迭代次数

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fsqrt(None, _to_tensor(args[0], _builder),
                                  _to_tensor(num_iter, _builder), _builder)
        elif len(args) == 2:
            return semantic.fsqrt(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                  _to_tensor(num_iter, _builder), _builder)
    assert False

@builtin
def fsin_base(*args, _builder=None):
    """
    对浮点数做sin运算

        .. code-block:: python

            fsin_base(dst, src) 或 dst = fsin_base(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fsin(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.fsin(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                 _builder)
    assert False

@builtin
def fcos_base(*args, _builder=None):
    """
    对浮点数做cos运算

        .. code-block:: python

            fcos_base(dst, src) 或 dst = fcos_base(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fcos(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.fcos(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                 _builder)
    assert False

@builtin
def ftan_base(*args, _builder=None):
    """
    对浮点数做tan运算

        .. code-block:: python

            ftan_base(dst, src) 或 dst = ftan_base(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.ftan(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.ftan(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                 _builder)
    assert False

@builtin
def farcsin_base(*args, _builder=None):
    """
    对浮点数做arcsin运算

        .. code-block:: python

            farcsin_base(dst, src) 或 dst = farcsin_base(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.farcsin(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.farcsin(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                 _builder)
    assert False

@builtin
def farccos_base(*args, _builder=None):
    """
    对浮点数做farccos运算

        .. code-block:: python

            farccos_base(dst, src) 或 dst = farccos_base(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.farccos(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.farccos(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                 _builder)
    assert False

@builtin
def flog_base(*args, _builder=None):
    """
    对浮点数做log运算

        .. code-block:: python

            flog_base(dst, src) 或 dst = flog_base(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor or None`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.flog(None, _to_tensor(args[0], _builder), _builder)
        elif len(args) == 2:
            return semantic.flog(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                 _builder)
    assert False

'''
@builtin
def flogx(*args, work0, coeff, x, _builder=None):
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.flogx(None, _to_tensor(args[0], _builder),
                                 _to_tensor(work0, _builder),
                                 _to_tensor(coeff, _builder),
                                 _to_tensor(x, _builder),
                                _builder)
        elif len(args) == 2:
            return semantic.flogx(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(work0, _builder),
                                 _to_tensor(coeff, _builder),
                                 _to_tensor(x, _builder),
                                _builder)
    assert False
'''
@builtin
def smem_bcast(dst, coeff_mode:coeff_table_mode, _builder=None):
    """
    指令将 coeff_mode 指向的 SMEM 上的数据复制到 dst 的每个 LANE 上

        .. code-block:: python

            smem_bcast(dst, coeff_mode)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): dst张量

        - ``coeff_mode`` (`pl.coeff_table_mode`): SMEM 上的数据 mode

    返回值:
        无

    注意事项:
        仅支持 SG2380
    """
    return semantic.smem_bcast(_to_tensor(dst, _builder),
                                  _to_tensor(_constexpr_to_value(coeff_mode).val(), _builder),
                                  _builder)

@builtin
def smem_dist(dst, coeff_mode:coeff_table_mode, _builder=None):
    """
    指令将 coeff_mode 指向的 SMEM 上的数据分散到 dst 的每个 LANE 上

        .. code-block:: python

            smem_dist(dst, coeff_mode)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): dst张量

        - ``coeff_mode`` (`pl.coeff_table_mode`): SMEM 上的数据 mode

    返回值:
        无

    注意事项:
        仅支持 SG2380
    """
    return semantic.smem_dist(_to_tensor(dst, _builder),
                                  _to_tensor(_constexpr_to_value(coeff_mode).val(), _builder),
                                  _builder)

@builtin
def add(*args, shift:int=-100, mode:round_mode=RM_HALF_TO_EVEN, saturation:bool=False, _builder=None):
    """
    a. 两个张量的元素相加,对结果做算术移位,再对结果做saturation(可选)

    b. 张量的元素和常数相加,对结果做算术移位,再对结果做saturation(可选)

    c. 两个张量的元素相加, 对结果按 channel 做算数移位,再对结果做saturation(可选)

    d. 张量的元素和常数相加,对结果按 channel 做算数移位,再对结果做saturation(可选)

    e. 两个标量相加

        .. code-block:: python

            add(dst, src0, src1, shift, mode, saturation) 或 dst = add(src0, src1, shift, mode, saturation)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``shift`` (`ppl.language.tensor或标量`): 移位数

        - ``mode`` (`pl.round_mode`): round mode

        - ``saturation`` (`bool`): 饱和处理标志
    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr, round_mode)) for t in args):
        tensors = [item for item in args if isinstance(item, (tensor, constexpr, round_mode))]
        mode_ = [item for item in args if isinstance(item, round_mode)]
        saturation_ = []
        if isinstance(tensors[-1], constexpr) \
            and  (int(_constexpr_to_value(tensors[-1])) == 1 \
                or int(_constexpr_to_value(tensors[-1])) == 0):
            saturation_.append(tensors[-1])

        mode = mode_[0] if len(mode_) == 1 else mode
        saturation = saturation_[0] if len(saturation_) == 1 else saturation
        shift_ = []
        tmp = tensors[len(tensors) - 1 - len(mode_) - len(saturation_)]
        if isinstance(tmp, constexpr) \
           and _constexpr_to_value(shift) == -100:
            shift_.append(tmp)
        shift = shift_[0] if len(shift_) == 1 else shift
        tensor_num = len(tensors) - len(shift_) - len(saturation_) - len(mode_)
        if  tensor_num == 2:
            return semantic.add(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder),
                        _to_tensor(shift, _builder),
                        _to_tensor(_constexpr_to_value(mode).val(), _builder),
                        _to_tensor(saturation, _builder),
                        _builder)
        elif tensor_num == 3:
            return semantic.add(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder),
                                _to_tensor(shift, _builder),
                                _to_tensor(_constexpr_to_value(mode).val(), _builder),
                                _to_tensor(saturation, _builder),
                                _builder)
    assert False

@builtin
def sub(*args, shift:int=-100, mode:round_mode=RM_HALF_TO_EVEN, saturation:bool=False, _builder=None):
    """
    a. 两个张量的元素相减,对结果做算术移位, 再对结果做saturation(可选)

    b. 张量的元素减常数,对结果做算术移位,再对结果做saturation(可选)

    c. 常数减张量的元素, 对结果做算术移位,再对结果做 saturation(可选)

    d. 两个张量的元素相减, 对结果按 channel 做算数移位,再对结果做saturation(可选)

    e. 张量的元素和常数相减,对结果按 channel 做算数移位,再对结果做saturation(可选)

    f. 两个标量相减

        .. code-block:: python

            sub(dst, src0, src1, shift, mode, saturation) 或 dst = sub(src0, src1, shift, mode, saturation)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``shift`` (`ppl.language.tensor或标量`): 移位数

        - ``mode`` (`pl.round_mode`): round mode

        - ``saturation`` (`bool`): 饱和处理标志
    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr, round_mode)) for t in args):
        tensors = [item for item in args if isinstance(item, (tensor, constexpr, round_mode))]
        mode_ = [item for item in args if isinstance(item, round_mode)]
        saturation_ = []
        if isinstance(tensors[-1], constexpr) \
            and  (int(_constexpr_to_value(tensors[-1])) == 1 \
                or int(_constexpr_to_value(tensors[-1])) == 0):
            saturation_.append(tensors[-1])

        mode = mode_[0] if len(mode_) == 1 else mode
        saturation = saturation_[0] if len(saturation_) == 1 else saturation
        shift_ = []
        tmp = tensors[len(tensors) - 1 - len(mode_) - len(saturation_)]
        if isinstance(tmp, constexpr) \
           and _constexpr_to_value(shift) == -100:
            shift_.append(tmp)
        shift = shift_[0] if len(shift_) == 1 else shift
        tensor_num = len(tensors) - len(shift_) - len(saturation_) - len(mode_)
        if  tensor_num == 2:
            return semantic.sub(None, _to_tensor(args[0], _builder),
                                _to_tensor(args[1], _builder),
                                _to_tensor(shift, _builder),
                                _to_tensor(_constexpr_to_value(mode).val(), _builder),
                                _to_tensor(saturation, _builder),
                                _builder)
        elif tensor_num == 3:
            return semantic.sub(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder),
                                _to_tensor(shift, _builder),
                                _to_tensor(_constexpr_to_value(mode).val(), _builder),
                                _to_tensor(saturation, _builder),
                                _builder)
    assert False

@builtin
def mul(*args, shift:int=-100, mode:round_mode=RM_HALF_TO_EVEN, saturation:bool=False, _builder=None):
    """
    a. 两个张量的元素相乘,对结果做算术移位, 再对结果做saturation(可选)

    b. 张量的元素和常数相乘,对结果做算术移位,再对结果做saturation(可选)

    c. 两个张量的元素相乘, 对结果按 channel 做算数移位,再对结果做saturation(可选)

    d. 张量的元素和常数相乘,对结果按 channel 做算数移位,再对结果做saturation(可选)

    e. 两个标量相乘

        .. code-block:: python

            mul(dst, src0, src1, shift, mode, saturation) 或 dst = mul(src0, src1, shift, mode, saturation)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``shift`` (`ppl.language.tensor或标量`): 移位数

        - ``mode`` (`pl.round_mode`): round mode

        - ``saturation`` (`bool`): 饱和处理标志
    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr, round_mode)) for t in args):
        tensors = [item for item in args if isinstance(item, (tensor, constexpr, round_mode))]
        mode_ = [item for item in args if isinstance(item, round_mode)]
        saturation_ = []
        if isinstance(tensors[-1], constexpr) \
            and  (int(_constexpr_to_value(tensors[-1])) == 1 \
                or int(_constexpr_to_value(tensors[-1])) == 0):
            saturation_.append(tensors[-1])

        mode = mode_[0] if len(mode_) == 1 else mode
        saturation = saturation_[0] if len(saturation_) == 1 else saturation
        shift_ = []
        tmp = tensors[len(tensors) - 1 - len(mode_) - len(saturation_)]
        if isinstance(tmp, constexpr) \
           and _constexpr_to_value(shift) == -100:
            shift_.append(tmp)
        shift = shift_[0] if len(shift_) == 1 else shift
        tensor_num = len(tensors) - len(shift_) - len(saturation_) - len(mode_)
        if  tensor_num == 2:
            return semantic.mul(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder),
                        _to_tensor(shift, _builder),
                        _to_tensor(_constexpr_to_value(mode).val(), _builder),
                        _to_tensor(saturation, _builder),
                        _builder)
        elif tensor_num == 3:
            return semantic.mul(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder), _to_tensor(shift, _builder),
                                _to_tensor(_constexpr_to_value(mode).val(), _builder),
                                _to_tensor(saturation, _builder),
                                _builder)
    assert False

@builtin
def mac(*args, lshift=0, rshift=0, r_mode=RM_HALF_TO_EVEN, _builder=None):
    """
    a. 两个张量的元素相乘,再对结果做累加,在累加之前会对结果的原数据算数左移,在累加之后对结果算数右移

    b. 张量的元素与常数相乘,再对结果做累加,在累加之前会对结果的原数据算数左移,在累加之后对结果算数右移

        .. code-block:: python

            mac(dst, src0, src1, lshift, rshift, r_mode)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``lshift`` (`int`): 左移位数

        - ``rshift`` (`int`): 右移位数

        - ``r_mode`` (`pl.round_mode`): round mode
    返回值:
        无

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 3:
            return semantic.mac(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder), _to_tensor(lshift, _builder),
                                _to_tensor(rshift, _builder),  _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                _builder)
    assert False

@builtin
def fsub(*args, saturation:bool=False, _builder=None):
    """
    两个张量的元素相减

        .. code-block:: python

            fsub(dst, src0, src1) 或 dst = fsub(src0, src1)

            dst = src0 - src1

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor 或常数`): src0张量或常数

        - ``src1`` (`ppl.language.tensor 或常数`): src1张量或常数

        - ``saturation`` (`bool`): True 表示需要做饱和，bm1684x及bm1688不支持此参数，bm1690仅当一个输入为fp8类型 tensor，另一个为标量时支持此参数。

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def fsub_sqr_kernel(
                src0_ptr,
                output_ptr,
                bias:pl.constexpr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                pid = pl.get_core_index()
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                src0_global = pl.gtensor(shape, pl.GLOBAL, src0_ptr)
                out = pl.make_tensor(shape, output_ptr.dtype)
                src0 = pl.make_tensor(shape, src0_ptr.dtype)
                pl.dma.load(src0, src0_global)
                out = pl.tiu.fsub_sqr(src0, bias)
                pl.dma.store(o_global, out)
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.sub(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder),
                        _to_tensor(0, _builder),
                        _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                        _to_tensor(False, _builder),
                        _builder)
        elif len(args) == 3:
            return semantic.sub(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder),
                                _to_tensor(0, _builder),
                                _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                                _to_tensor(False, _builder),
                                _builder)
    assert False

@builtin
def fmac(*args, _builder=None):
    """
    a. 两个张量的元素相乘, 再对结果做累加

    b. 张量的元素和常数相乘, 再对结果做累加

        .. code-block:: python

            fmac(dst, src0, src1)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或常数

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或常数

    返回值:
        无

    注意事项:
        无

    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 3:
            return semantic.mac(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder),  _to_tensor(0, _builder),
                                _to_tensor(0, _builder),  _to_tensor(_constexpr_to_value(RM_HALF_TO_EVEN).val(), _builder),
                                _builder)
    assert False

@builtin
def truediv(*args, _builder=None):
    """
    a. 两个张量的元素执行真除法(即不考虑操作数类型, 总是返回一个浮点数结果)

    b. 张量的元素和常数执行真除法

        .. code-block:: python

            truediv(dst, src0, src1) or dst = truediv(src0, src1)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或常数

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或常数

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        也可以使用 dst = src0 / src1, 效果相同

    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.truediv(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder), 3, _builder)
        elif len(args) == 3:
            return semantic.truediv(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder), 3, _builder)
    assert False

@builtin
def round(*args, r_mode:round_mode, _builder=None):
    """
    浮点类型的张量的元素舍入到附近的同类型的整数

        .. code-block:: python

            round(dst, src, r_mode) or dst = round(src, r_mode)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): src张量

        - ``r_mode`` (`pl.round_mode`): round mode

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.round(None, _to_tensor(args[0], _builder),
                                 _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                 _builder)
        elif len(args) == 2:
            return semantic.round(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                  _to_tensor(_constexpr_to_value(r_mode).val(), _builder), _builder)
    assert False

@builtin
def floor(*args, _builder=None):
    """
    浮点类型的张量的元素向负无穷舍入到附近的同类型的整数

        .. code-block:: python

            floor(dst, src) or dst = floor(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.round(None, _to_tensor(args[0], _builder),
                                 _to_tensor(semantic.Rounding_mode.RM_DOWN.value, _builder),
                                 _builder)
        elif len(args) == 2:
            return semantic.round(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                  _to_tensor(semantic.Rounding_mode.RM_DOWN.value, _builder),
                                  _builder)
    assert False

@builtin
def ceiling(*args, _builder=None):
    """
    浮点类型的张量的元素向正无穷舍入到附近的同类型的整数

        .. code-block:: python

            ceiling(dst, src) or dst = ceiling(src)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.round(None, _to_tensor(args[0], _builder),
                        _to_tensor(semantic.Rounding_mode.RM_UP.value, _builder),
                        _builder)
        elif len(args) == 2:
            return semantic.round(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(semantic.Rounding_mode.RM_UP.value, _builder),
                                _builder)
    assert False

@builtin
def pool_avg(output, pointer, kernel, padding, stride, dilation, scale, rshift=0, ins=None, _builder=None):
    """
    a. 整数数据类型2D均值池化,可自定义均值 scale 值,对结果做算术移位, 结果有 saturation

        .. code-block:: python

            pool_avg(output, pointer, kernel, padding, stride, dilation, scale, rshift, ins)

    b. 浮点数据类型2D均值池化, 可自定义均值 scale 值来代替传统的 1 / (kernel->h * kernel->w)

        .. code-block:: python

            pool_avg(output, pointer, kernel, padding, stride, dilation, scale, ins)
    参数:
        - ``output`` (`ppl.language.tensor`): output张量

        - ``pointer`` (`ppl.language.tensor`): src张量

        - ``kernel`` (`dim2`): kernel大小

        - ``padding`` (`dim4`): padding大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

        - ``scale`` (`int or float`): scale值

        - ``rshift`` (`int`): 右移位数, 在b中不需要

        - ``ins`` (`dim2`):  insert大小

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
            def avg_pool(
                x_ptr,  # *Pointer* to first input vector.
                output_ptr,  # *Pointer* to output vector.
                n:pl.constexpr,
                c:pl.constexpr,
                h:pl.constexpr,
                w:pl.constexpr,
                oh:pl.constexpr,
                ow:pl.constexpr,
                kh:pl.constexpr,
                kw:pl.constexpr,
                stride_h:pl.constexpr,
                stride_w:pl.constexpr,
                pad_h_up:pl.constexpr,
                pad_h_down:pl.constexpr,
                pad_w_l:pl.constexpr,
                pad_w_r:pl.constexpr,
                dilation_h:pl.constexpr,
                dilation_w:pl.constexpr,
                scale:pl.constexpr
            ):
                pid = pl.get_core_index()
                in_shape = [n, c, h, w]
                out_shape = [n, c, oh, ow]
                offset = [0, 0, 0, 0]
                kernel = [kh, kw]
                padding = [pad_h_up, pad_h_down, pad_w_l, pad_w_r]
                stride = [stride_h, stride_w]
                dilation  = [dilation_h, dilation_w]
                x_global = pl.gtensor(in_shape, pl.GLOBAL, x_ptr)
                o_global = pl.gtensor(out_shape, pl.GLOBAL, output_ptr)
                output = pl.make_tensor(out_shape, x_ptr.dtype)
                x = pl.dma.load(x_global[:,:,:,:])
                pl.tiu.pool_avg(output, x, kernel, padding, stride, dilation, scale)
                pl.dma.store(o_global[:,:,:,:], output)
    """
    scale = _to_tensor(scale, _builder)
    rshift = _to_tensor(rshift, _builder)
    return semantic.pool_avg(output, pointer, kernel, padding, stride, dilation, ins, scale, rshift, _builder)

@builtin
def pool_max(output, pointer, kernel, padding, stride, dilation, _builder=None):
    """
    2D最大池化
        .. code-block:: python

            pool_max(output, pointer, kernel, padding, stride, dilation)

    参数:
        - ``output`` (`ppl.language.tensor`): output张量

        - ``pointer`` (`ppl.language.tensor`): src张量

        - ``kernel`` (`dim2`): kernel大小

        - ``padding`` (`dim4`): padding大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

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
            def max_pool(
                x_ptr,  # *Pointer* to first input vector.
                output_ptr,  # *Pointer* to output vector.
                n:pl.constexpr,
                c:pl.constexpr,
                h:pl.constexpr,
                w:pl.constexpr,
                oh:pl.constexpr,
                ow:pl.constexpr,
                kh:pl.constexpr,
                kw:pl.constexpr,
                stride_h:pl.constexpr,
                stride_w:pl.constexpr,
                pad_h_up:pl.constexpr,
                pad_h_down:pl.constexpr,
                pad_w_l:pl.constexpr,
                pad_w_r:pl.constexpr,
                dilation_h:pl.constexpr,
                dilation_w:pl.constexpr
            ):
                pid = pl.get_core_index()
                in_shape = [n, c, h, w]
                out_shape = [n, c, oh, ow]
                offset = [0, 0, 0, 0]
                kernel = [kh, kw]
                padding = [pad_h_up, pad_h_down, pad_w_l, pad_w_r]
                stride = [stride_h, stride_w]
                dilation  = [dilation_h, dilation_w]
                x_global = pl.gtensor(in_shape, pl.GLOBAL, x_ptr)
                o_global = pl.gtensor(out_shape, pl.GLOBAL, output_ptr)
                output = pl.make_tensor(out_shape, x_ptr.dtype)
                x = pl.dma.load(x_global.sub_view(in_shape, offset))
                pl.tiu.pool_max(output, x, kernel, padding, stride, dilation)
                pl.dma.store(o_global.sub_view(out_shape, offset), output)
    """
    return semantic.pool_max(output, pointer, kernel, padding, stride, dilation, _builder)

@builtin
def pool_min(output, pointer, kernel, padding, stride, dilation, _builder=None):
    """
    2D最小池化
        .. code-block:: python

            pool_min(output, pointer, kernel, padding, stride, dilation)

    参数:
        - ``output`` (`ppl.language.tensor`): output张量

        - ``pointer`` (`ppl.language.tensor`): src张量

        - ``kernel`` (`dim2`): kernel大小

        - ``padding`` (`dim4`): padding大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

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
            def min_pool(
                x_ptr,  # *Pointer* to first input vector.
                output_ptr,  # *Pointer* to output vector.
                n:pl.constexpr,
                c:pl.constexpr,
                h:pl.constexpr,
                w:pl.constexpr,
                oh:pl.constexpr,
                ow:pl.constexpr,
                kh:pl.constexpr,
                kw:pl.constexpr,
                stride_h:pl.constexpr,
                stride_w:pl.constexpr,
                pad_h_up:pl.constexpr,
                pad_h_down:pl.constexpr,
                pad_w_l:pl.constexpr,
                pad_w_r:pl.constexpr,
                dilation_h:pl.constexpr,
                dilation_w:pl.constexpr
            ):
                pid = pl.get_core_index()
                in_shape = [n, c, h, w]
                out_shape = [n, c, oh, ow]
                offset = [0, 0, 0, 0]
                kernel = [kh, kw]
                padding = [pad_h_up, pad_h_down, pad_w_l, pad_w_r]
                stride = [stride_h, stride_w]
                dilation  = [dilation_h, dilation_w]
                x_global = pl.gtensor(in_shape, pl.GLOBAL, x_ptr)
                o_global = pl.gtensor(out_shape, pl.GLOBAL, output_ptr)
                output = pl.make_tensor(out_shape, x_ptr.dtype)
                x = pl.dma.load(x_global.sub_view(in_shape, offset))
                pl.tiu.pool_min(x, output,kernel, stride, padding, dilation)
                pl.dma.store(o_global.sub_view(out_shape, offset), output)
    """
    return semantic.pool_min(output, pointer, kernel, padding, stride, dilation, _builder)

@builtin
def fconv(output, input, filter, kernel, stride, dilation, padding,
        bias=None, oc=0, ins=None, result_relu=False, result_add=False,
        out_dtype=void, has_bias=True, saturate=False, kernel_rotate=False,
        _builder=None):
    """
    a. 2D 卷积, 结果按 channel 加 bias(可选), 再对结果做累加(可选)

        .. code-block:: python

            fconv(output, input, filter, kernel, stride, dilation, padding, bias, result_add=, has_bias)

    b. 核为常数的 2D 卷积,结果按 channel 加 bias(可选), 再对结果做累加(可选)

        .. code-block:: python

            fconv(output, input, filter, kernel, stride, dilation, padding, bias, result_add, has_bias)

    参数:
        - ``output`` (`ppl.language.tensor`): output张量

        - ``input`` (`ppl.language.tensor`): src张量

        - ``filter`` (`ppl.language.tensor或标量`): 卷积核张量或常数

        - ``kernel`` (`dim2`): kernel大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``bias`` (`ppl.language.tensor 或 None`): bias张量或None

        - ``oc`` (`int`): output张量的channel数

        - ``ins`` (`dim2或None`): insert大小或None

        - ``result_relu`` (`bool`): 对output张量是否做relu

        - ``result_add`` (`bool`):  对结果做累加的标志

        - ``out_dtype`` (`pl.dtype`):  结果数据类型

        - ``has_bias`` (`bool`):  是否有 bias

        - ``saturate`` (`bool`):  对结果做饱和

        - ``kernel_rotate`` (`bool`):  kernel核是否rotate
    返回值:
        无

    注意事项:
        因接口支持浮点数卷积各类运算, 使用灵活, 可以参考测试例03-conv.py中的使用组合

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def fconv2d_const_weight_kernel(
                x_ptr,
                z_ptr,
                output_ptr,
                n:pl.constexpr,
                ic:pl.constexpr,
                h:pl.constexpr,
                w:pl.constexpr,
                oc:pl.constexpr,
                oh:pl.constexpr,
                ow:pl.constexpr,
                kh:pl.constexpr,
                kw:pl.constexpr,
                stride_h:pl.constexpr,
                stride_w:pl.constexpr,
                pad_h_up:pl.constexpr,
                pad_h_down:pl.constexpr,
                pad_w_l:pl.constexpr,
                pad_w_r:pl.constexpr,
                dilation_h:pl.constexpr,
                dilation_w:pl.constexpr,
                const_val:pl.constexpr
            ):
                pid = pl.get_core_index()
                in_shape = [n, ic, h, w]
                out_shape = [n, oc, oh, ow]
                bias_shape = [1, oc, 1, 1]
                kernel = [kh, kw]
                stride = [stride_h, stride_w]
                dilation = [dilation_h, dilation_w]
                padding = [pad_h_up, pad_h_down, pad_w_l, pad_w_r]
                x_global = pl.gtensor(in_shape, pl.GLOBAL, x_ptr)

                bias_global = pl.gtensor(bias_shape, pl.GLOBAL, z_ptr)
                o_global = pl.gtensor(out_shape, pl.GLOBAL, output_ptr)
                output = pl.make_tensor(out_shape, output_ptr.dtype)
                x = pl.dma.load(x_global)

                bias = pl.dma.load_compact(bias_global)
                pl.tiu.fconv(output, x, const_val, kernel, stride, dilation, padding, bias=bias, oc=oc, out_dtype=output_ptr.dtype)
                pl.dma.store(o_global, output)
    """
    filter = _to_tensor(filter, _builder)
    if bias is None:
        bias = _to_tensor(None, _builder)
    oc = _to_tensor(oc, _builder)
    result_relu = _to_tensor(result_relu, _builder)
    result_add = _to_tensor(result_add, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    saturate = _to_tensor(saturate, _builder)
    kernel_rotate = _to_tensor(kernel_rotate, _builder)
    return semantic.fconv(output, input, filter, bias, oc,
                         kernel, stride, dilation, padding, ins,
                         result_relu, result_add, out_dtype,
                         has_bias, saturate, kernel_rotate,
                         _builder)

@builtin
def conv(output, input, filter, oc, kernel, stride, dilation, padding,\
        bias=None, ins=None, pad_val=0, result_relu=False, result_add=False,
        out_dtype=void,  has_bias=False, sym=True, quant=0, rq=False, requant=0,
        rq_shift=0, out_zp=0, saturate=False,
        round:round_mode=RM_HALF_UP, kernel_rotate=False, _builder=None):
    """
    a. 对称量化 2D 卷积, 结果按 channel 加 bias(可选), 再对结果做 ReLU(可选), 最后对结果做算数右移

        .. code-block:: python

            conv(output, input, filter, oc, kernel, stride, dilation, padding, bias, result_relu, quant, sym, has_bias)

    b. 对称量化 2D 卷积,结果按 channel 加 bias(可选),再对结果做 ReLU(可选), 最后对结果做requant

        .. code-block:: python

            conv(output, input, filter, oc, kernel, stride, dilation, padding, bias, quant, sym, rq, has_bias, saturate, requant)

    c. 非对称量化 2D 卷积, 支持对结果进行累加(可选),支持 pad, 支持 weight 减去 kzp

        .. code-block:: python

            conv(output, input, filter, oc, kernel, stride, dilation, padding, quant, out_dtype, has_bias, sym, rq)

    d. 非对称量化 2D 卷积, 支持对结果进行累加(可选),支持 pad,支持 weight 减去 kzp,支持对结果做 requant

        .. code-block:: python

            conv(output, input, filter, oc, kernel, stride, dilation, padding, quant=kzp, out_dtype=pl.void, sym=False, rq=False, pad_val=None)

    参数:
        - ``output`` (`ppl.language.tensor`): output张量

        - ``input`` (`ppl.language.tensor`): src张量

        - ``filter`` (`ppl.language.tensor或标量`): 卷积核张量或常数

        - ``oc`` (`int`): output张量的channel数

        - ``kernel`` (`dim2`): kernel大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``bias`` (`ppl.language.tensor或None`): bias张量或None

        - ``ins`` (`dim2或None`): insert大小或None

        - ``pad_val`` (`ppl.language.tensor或常数或None`): pad 填充值,当为 tensor时,shape 为 [1, oc, 1, 1], compact layout

        - ``result_relu`` (`bool`): 对output张量是否做relu

        - ``result_add`` (`bool`):  对结果做累加的标志

        - ``out_dtype`` (`pl.dtype`):  结果数据类型

        - ``has_bias`` (`bool`):  是否有 bias

        - ``sym`` (`bool`):  对称或非对称标志

        - ``quant`` (`ppl.language.tensor或常数`):  在a中作为算数右移位数, 在b、c、d中作为kzp

        - ``rq`` (`bool`):  是否做requant

        - ``requant`` (`ppl.language.tensor或常数`):  requant参数

        - ``rq_shift`` (`int`):  requant参数

        - ``out_zp`` (`int`):  requant参数

        - ``saturate`` (`bool`):  对结果做饱和

        - ``round`` (``):  round模式

        - ``kernel_rotate`` (`bool`):  kernel核是否rotate

    返回值:
        无

    注意事项:
        因接口支持对称及非对称, 使用灵活, 可以参考测试例03-conv.py中的使用组合

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def conv2d_asym_kzp_tensor_kernel(
                x_ptr,
                y_ptr,
                z_ptr,
                output_ptr,
                n:pl.constexpr,
                ic:pl.constexpr,
                h:pl.constexpr,
                w:pl.constexpr,
                oc:pl.constexpr,
                oh:pl.constexpr,
                ow:pl.constexpr,
                kh:pl.constexpr,
                kw:pl.constexpr,
                stride_h:pl.constexpr,
                stride_w:pl.constexpr,
                pad_h_up:pl.constexpr,
                pad_h_down:pl.constexpr,
                pad_w_l:pl.constexpr,
                pad_w_r:pl.constexpr,
                dilation_h:pl.constexpr,
                dilation_w:pl.constexpr
            ):
                pid = pl.get_core_index()
                in_shape = [n, ic, h, w]
                out_shape = [n, oc, oh, ow]
                kernel = [kh, kw]
                stride = [stride_h, stride_w]
                dilation = [dilation_h, dilation_w]
                padding = [pad_h_up, pad_h_down, pad_w_l, pad_w_r]
                x_global = pl.gtensor(in_shape, pl.GLOBAL, x_ptr)
                #32IC/16IC for bm1688, eu_num for int8是16 at bm1688
                ws_w = 32
                ws_h = (ic + ws_w - 1) // ws_w * kh * kw
                if pl.get_scalar_dtype(y_ptr.dtype).is_fp32():
                    filter_global = pl.gtensor([1, oc, 1, ic * kh * kw], pl.GLOBAL, y_ptr)
                else:
                    filter_global = pl.gtensor([1, oc, ws_h, ws_w], pl.GLOBAL, y_ptr)

                kzp_global = pl.gtensor([1, oc, 1, 1], pl.GLOBAL, z_ptr)
                o_global = pl.gtensor(out_shape, pl.GLOBAL, output_ptr)
                output = pl.make_tensor(out_shape, output_ptr.dtype)
                kzp = pl.dma.load_compact(kzp_global)
                x = pl.dma.load(x_global)
                filter = pl.dma.load_compact(filter_global)

                pl.tiu.conv(output, x, filter, oc, kernel, stride, dilation, padding, \
                        quant=kzp, out_dtype=pl.void, sym=False, rq=False, pad_val=None)
                pl.dma.store(o_global, output)
    """
    filter = _to_tensor(filter, _builder)
    if bias is None:
        bias = _to_tensor(None, _builder)
    else:
        bias = _to_tensor(bias, _builder)
    oc = _to_tensor(oc, _builder)
    pad_val = _to_tensor(pad_val, _builder)
    result_relu = _to_tensor(result_relu, _builder)
    result_add = _to_tensor(result_add, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    sym =  _to_tensor(sym, _builder)
    rq = _to_tensor(rq, _builder)
    requant = _to_tensor(requant, _builder)
    quant = _to_tensor(quant, _builder)
    return semantic.conv(output, input, filter, bias, oc,
                         kernel, stride, dilation, padding, ins,
                         pad_val,
                         result_relu,
                         result_add,
                         out_dtype,
                         has_bias,
                         sym,
                         quant,
                         rq,
                         requant,
                         _to_tensor(rq_shift, _builder),
                         _to_tensor(out_zp, _builder),
                         _to_tensor(saturate, _builder),
                         _to_tensor(_constexpr_to_value(round).val(), _builder),
                         _to_tensor(kernel_rotate, _builder),
                         _builder)

@builtin
def sub_abs(*args, _builder=None):
    """
    a. 计算两个张量的元素的差的绝对值

        .. code-block:: python

           dst = sub_abs(src0, src1) 或 sub_abs(dst, src0, src1)

        .. math:: \mathsf{dst(n, c, h, w) = |src0(n, c, h, w) - src1(n, c, h, w)|}

    b. 计算张量的元素与常数的差的绝对值

        .. code-block:: python

           dst = sub_abs(src0, C) 或 sub_abs(dst, src0, C)

        .. math:: \mathsf{dst(n, c, h, w) = |src(n, c, h, w) - C|}

    参数:
        - ``dst`` (`ppl.language.tensor`): dst张量

        - ``src0`` (`ppl.language.tensor或常数`): src0张量或常数

        - ``src1`` (`ppl.language.tensor或常数`): src1张量或常数

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

    注意事项:
        无

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def sub_abs_kernel(
                x_ptr,  # *Pointer* to first input vector.
                y_ptr,  # *Pointer* to second input vector.
                output_ptr,  # *Pointer* to output vector.
                n_elements,  # Size of the vector.
                BLOCK_SIZE: pl.constexpr,
            ):
                pid = pl.get_core_index()
                shape = [1, 1, 1, n_elements]
                x_global = pl.gtensor(shape, pl.GLOBAL, x_ptr)
                y_global = pl.gtensor(shape, pl.GLOBAL, y_ptr)
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                for off in range(0, n_elements, BLOCK_SIZE):
                    pid_start = off
                    cur_slice = min(n_elements - pid_start, BLOCK_SIZE)
                    cur_shape = [1, 1, 1, cur_slice]
                    cur_offset = [0,0,0,pid_start]
                    x = pl.dma.load(x_global.sub_view(cur_shape, cur_offset))
                    y = pl.dma.load(y_global.sub_view(cur_shape, cur_offset))
                    output = pl.tiu.sub_abs(x, y)
                    pl.dma.store(o_global.sub_view([1,1,1,cur_slice], cur_offset), output)
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.sub_abs(None, _to_tensor(args[0], _builder),
                                       _to_tensor(args[1], _builder),
                                       _builder)
        elif len(args) == 3:
            return semantic.sub_abs(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _builder)
    assert False

@builtin
def dot(dst, left, right, bias=None, ltrans=False, rtrans=False, rst_trans=False, do_relu=False,
        result_add=False, out_dtype=void, has_bias=False, saturate=False, _builder=None):
    """
    两个矩阵相乘/左矩阵乘以右矩阵的转置/两个矩阵的转置相乘,结果也转置,再对结果做累加(可选),可对结果做Relu(可选)

        .. code-block:: python

            fmm2(dst, left, right)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst张量

        - ``left`` (`ppl.language.tensor`): left矩阵张量

        - ``right`` (`ppl.language.tensor`): right矩阵张量

        - ``bias`` (`ppl.language.tensor或None`): bias张量或None

        - ``ltrans`` (`bool`): 左矩阵转置标志

        - ``rtrans`` (`bool`): 右矩阵转置标志

        - ``rst_trans`` (`bool`):  结果矩阵转置标志, 只有当ltrans和rtrans都为true时,rst_trans为true, 其他情况都为false

        - ``do_relu`` (`bool`): 对结果做 ReLU 的标志

        - ``result_add`` (`bool`):  对结果做累加的标志

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``has_bias`` (`bool`): 是否有bias

        - ``saturate`` (`bool`): 对结果做饱和标志
    返回值:
        无

    注意事项:
        也可以用别名api: dot

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def matmul_kernel(
                x_ptr,
                y_ptr,
                output_ptr,
                M:pl.constexpr,
                N:pl.constexpr,
                K:pl.constexpr
            ):
                pid = pl.get_core_index()
                x_global = pl.gtensor([1, M, 1, K], pl.GLOBAL, x_ptr)
                y_global = pl.gtensor([1, K, 1, N], pl.GLOBAL, y_ptr)
                o_global = pl.gtensor([1, M, 1, N], pl.GLOBAL, output_ptr)

                block_m = 128
                block_k = 256
                block_n = 256
                #res_max_shape = [1, block_m, 1, block_n]
                for idx_m in range(0, M, block_m):
                for idx_n in range(0, N, block_n):
                    m = min(block_m, M - idx_m)
                    n = min(block_n, N - idx_n)
                    sub_res = pl.make_tensor([1, block_m, 1, block_n], pl.float32, [1, m, 1, n])
                    pl.tiu.zero(sub_res)
                    for idx_k in range(0, K, block_k):
                        pl.enable_pipeline()
                        k = min(block_k, K - idx_k)
                        sub_left = pl.dma.load(x_global.sub_view([1, m, 1, k], [0, idx_m, 0, idx_k]))
                        sub_right = pl.dma.load(y_global.sub_view([1, k, 1, n], [0, idx_k, 0, idx_n]))
                        pl.tiu.fmm2(sub_res, sub_left, sub_right, result_add=True, out_dtype=pl.float32)
                    res_fp16 = pl.tiu.cast(sub_res, x_ptr.dtype)
                    pl.dma.store(o_global.sub_view([1, m, 1, n], [0, idx_m, 0, idx_n]), res_fp16)
    """
    ltrans = _to_tensor(ltrans, _builder)
    rtrans = _to_tensor(rtrans, _builder)
    rst_trans = _to_tensor(rst_trans, _builder)
    do_relu = _to_tensor(do_relu, _builder)
    result_add = _to_tensor(result_add, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    saturate = _to_tensor(saturate, _builder)
    bias = _to_tensor(bias, _builder)
    return semantic.dot(dst, left, right, bias, ltrans, rtrans, rst_trans, do_relu,
                        result_add, out_dtype, has_bias, saturate, _builder)

dot.alias = 'fmm2'
globals()[dot.alias] = dot

@builtin
def mm2(dst,
        left,
        right,
        bias=None,
        r_zp=None,
        requant=None,
        multiplier=1,
        rshift=0,
        y_zp=0,
        ltrans=False,
        rtrans=False,
        rst_trans=False,
        result_add=False,
        out_dtype=void,
        has_bias=False,
        do_relu=False,
        do_rq=False,
        saturate=False,
        round_mode: round_mode = RM_HALF_AWAY_FROM_ZERO,
        _builder=None):
    """
    两个矩阵相乘/左矩阵乘以右矩阵的转置/两个矩阵的转置相乘,结果也转置,其中右矩阵的
    元素减 zero-point,再对结果做累加(可选), 结果没有 saturation

        .. code-block:: python

            mm2(dst, left, right)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst张量

        - ``left`` (`ppl.language.tensor`): left矩阵张量

        - ``right`` (`ppl.language.tensor`): right矩阵张量

        - ``bias`` (`ppl.language.tensor或None`): bias张量或None

        - ``r_zp`` (`ppl.language.tensor或常数None`):  zero-point 的 tensor 或常数

        - ``requant`` (`ppl.language.tensor或常数None`):  requant参数

        - ``multiplier`` (`int`):  requant参数

        - ``rshift`` (`int`):  requant参数

        - ``y_zp`` (`int`):  requant参数

        - ``ltrans`` (`bool`): 左矩阵转置标志

        - ``rtrans`` (`bool`): 右矩阵转置标志

        - ``rst_trans`` (`bool`): 输出矩阵转置标志

        - ``result_add`` (`bool`):  对结果做累加的标志

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``has_bias`` (`bool`): 是否有bias

        - ``do_relu`` (`bool`): 对结果做 ReLU 的标志

        - ``do_rq`` (`bool`): 是否做requant标志

        - ``saturate`` (`bool`): 对结果做饱和标志

        - ``round_mode`` (`pl.round_mode`): round模式
    返回值:
        无

    注意事项:
        支持定点数多种mm2计算(requant或普通的定点计算),使用灵活, 可以参考测试例04-matmul.py
    """
    left = _to_tensor(left, _builder)
    right = _to_tensor(right, _builder)
    bias = _to_tensor(bias, _builder)
    r_zp = _to_tensor(r_zp, _builder)
    requant = _to_tensor(requant, _builder)
    multiplier = _to_tensor(multiplier, _builder)
    rshift = _to_tensor(rshift, _builder)
    y_zp = _to_tensor(y_zp, _builder)
    ltrans = _to_tensor(ltrans, _builder)
    rtrans = _to_tensor(rtrans, _builder)
    rst_trans = _to_tensor(rst_trans, _builder)
    result_add = _to_tensor(result_add, _builder)
    out_dtype = _to_tensor(
        semantic.get_dtype_num(_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    do_relu = _to_tensor(do_relu, _builder)
    do_rq = _to_tensor(do_rq, _builder)
    saturate = _to_tensor(saturate, _builder)
    round_mode = _to_tensor(_constexpr_to_value(round_mode).val(), _builder)
    return semantic.mm2_int8(dst, left, right, bias, r_zp, requant, multiplier,
                             rshift, y_zp, ltrans, rtrans, rst_trans,
                             result_add, out_dtype, has_bias, do_relu, do_rq,
                             saturate, round_mode, _builder)

@builtin
def mm(dst, left, right, bias=None, ltrans=False, rtrans=False, result_add=False, lshift=0,
       rshift=0, do_relu=False, round_mode:round_mode=RM_HALF_UP, _builder=None):
    """
    a. 两个矩阵相乘

        .. code-block:: python

            mm(dst, left, right, ltrans, rtrans)

    b. 两个矩阵相乘,对结果做累加(可选,在累加之前可对结果的原数据算数左移),再对结果做 ReLU(可选), 最后对结果做算数右移

        .. code-block:: python

            mm(dst, left, right, ltrans, rtrans, result_add, lshift, rshift, do_relu)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst张量

        - ``left`` (`ppl.language.tensor`): left矩阵张量

        - ``right`` (`ppl.language.tensor`): right矩阵张量

        - ``bias`` (`ppl.language.tensor或None`): bias张量或None

        - ``ltrans`` (`bool`): 左矩阵转置标志

        - ``rtrans`` (`bool`): 右矩阵转置标志

        - ``result_add`` (`bool`):  对结果做累加的标志

        - ``lshift`` (`int`):  左移位数

        - ``rshift`` (`int`):  右移位数

        - ``do_relu`` (`bool`): 对结果做 ReLU 的标志

        - ``round_mode`` (`pl.round_mode`): round模式
    返回值:
        无

    注意事项:
        使用灵活, 可以参考测试例04-matmul.py

    使用示例:
        .. highlight:: python
        .. code-block:: python

            import ppl
            import ppl.language as pl

            @ppl.jit
            def mm_kernel(
                x_ptr,
                y_ptr,
                output_ptr,
                M:pl.constexpr,
                N:pl.constexpr,
                K:pl.constexpr,
                ltrans:pl.constexpr
            ):
                pid = pl.get_core_index()
                l_cols_perchannel = 16
                r_cols_perchannel = 16
                if ltrans:
                    x_global = pl.gtensor([K, M // l_cols_perchannel, 1, l_cols_perchannel], pl.GLOBAL, x_ptr)
                else:
                    x_global = pl.gtensor([M, K // l_cols_perchannel, 1, l_cols_perchannel], pl.GLOBAL, x_ptr)

                y_global = pl.gtensor([K, N // r_cols_perchannel, 1, r_cols_perchannel], pl.GLOBAL, y_ptr)
                o_global = pl.gtensor([M, N // r_cols_perchannel, 1, r_cols_perchannel], pl.GLOBAL, output_ptr)
                output = pl.make_tensor([M, N // r_cols_perchannel, 1, r_cols_perchannel], output_ptr.dtype)

                x = pl.dma.load(x_global)
                y = pl.dma.load(y_global)
                pl.tiu.mm(output, x, y, ltrans=ltrans, result_add=False)
                pl.dma.store(o_global, output)
    """
    ltrans = _to_tensor(ltrans, _builder)
    rtrans = _to_tensor(rtrans, _builder)
    result_add = _to_tensor(result_add, _builder)
    lshift = _to_tensor(lshift, _builder)
    rshift = _to_tensor(rshift, _builder)
    do_relu = _to_tensor(do_relu, _builder)
    left = _to_tensor(left, _builder)
    bias = _to_tensor(bias, _builder)
    round_mode = _to_tensor(_constexpr_to_value(round_mode).val(), _builder)
    return semantic.mm(dst, left, right, bias, ltrans, rtrans, result_add,
                       lshift, rshift, do_relu, round_mode, _builder)
@builtin
def fmm(dst, left, right, bias=None, ltrans=False,
        result_add=False, _builder=None):
    """
    两个矩阵相乘,再对结果做累加(可选)

        .. code-block:: python

            fmm(dst, left, right, bias, ltrans, result_add)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst张量

        - ``left`` (`ppl.language.tensor`): left矩阵张量

        - ``right`` (`ppl.language.tensor`): right矩阵张量

        - ``bias`` (`ppl.language.tensor或None`): bias张量或None

        - ``ltrans`` (`bool`): 左矩阵转置标志

        - ``result_add`` (`bool`):  对结果做累加的标志

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
            def fmm_kernel(
                x_ptr,
                y_ptr,
                output_ptr,
                M:pl.constexpr,
                N:pl.constexpr,
                K:pl.constexpr,
                ltrans:pl.constexpr
            ):
                pid = pl.get_core_index()
                l_cols_perchannel = 16
                r_cols_perchannel = 16
                if ltrans:
                    x_global = pl.gtensor([K, M // l_cols_perchannel, 1, l_cols_perchannel], pl.GLOBAL, x_ptr)
                else:
                    x_global = pl.gtensor([M, K // l_cols_perchannel, 1, l_cols_perchannel], pl.GLOBAL, x_ptr)

                y_global = pl.gtensor([K, N // r_cols_perchannel, 1, r_cols_perchannel], pl.GLOBAL, y_ptr)
                o_global = pl.gtensor([M, N // r_cols_perchannel, 1, r_cols_perchannel], pl.GLOBAL, output_ptr)
                output = pl.make_tensor([M, N // r_cols_perchannel, 1, r_cols_perchannel], output_ptr.dtype)

                x = pl.dma.load(x_global)
                y = pl.dma.load(y_global)
                pl.tiu.fmm(output, x, y, ltrans=ltrans, result_add=False)
                pl.dma.store(o_global, output)
    """
    ltrans = _to_tensor(ltrans, _builder)
    rtrans = _to_tensor(False, _builder)
    result_add = _to_tensor(result_add, _builder)
    lshift = _to_tensor(0, _builder)
    rshift = _to_tensor(0, _builder)
    do_relu = _to_tensor(False, _builder)
    left = _to_tensor(left, _builder)
    bias = _to_tensor(bias, _builder)
    round_mode = RM_HALF_UP
    round_mode = _to_tensor(_constexpr_to_value(round_mode).val(), _builder)
    return semantic.mm(dst, left, right, bias, ltrans, rtrans, result_add,
                      lshift, rshift, do_relu, round_mode, _builder)

@builtin
def fdiv(*args, num_iter:int=-100, _builder=None):
    """
    a.两个张量的元素相除

    b. 张量作为被除数,常量作为除数

    c. 张量作为除数, 常量作为被除数

        .. code-block:: python

            fdiv(dst, src0, src1) or dst = fdiv(src0, src1)

    参数:
        - ``dst`` (`ppl.language.tensor`):  dst在local memory上的张量

        - ``src0`` (`ppl.language.tensor or 标量`): local memory上的张量

        - ``src1`` (`ppl.language.tensor or 标量`): local memory上的张量
    返回值:
        - ``dst`` (`ppl.language.tensor or None`):  dst张量或None

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        tensors = [item for item in args if isinstance(item, (tensor, constexpr))]
        num_iter_ = []
        tmp = tensors[len(tensors) - 1]
        if isinstance(tmp, constexpr) \
           and _constexpr_to_value(num_iter) == -100:
            num_iter_.append(tmp)
        tensor_num = len(tensors) - len(num_iter_)
        num_iter = num_iter_[0] if len(num_iter_) == 1 else num_iter
        if tensor_num == 2:
            return semantic.truediv(None, _to_tensor(args[0], _builder),
                        _to_tensor(args[1], _builder), _constexpr_to_value(num_iter), _builder)
        elif tensor_num == 3:
            return semantic.truediv(_to_tensor(args[0], _builder), _to_tensor(args[1], _builder),
                                _to_tensor(args[2], _builder), _constexpr_to_value(num_iter), _builder)
    assert False

@builtin
def gather_hw(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              const_val=0, fill_const=False, _builder=None):
    """
    a. 通过 h 和 w 维度的索引取值得到输出张量, 即 output = param[index]

        .. code-block:: python

            gather_hw(output, param, index)

    b. 通过 h 和 w 维度的索引取值得到输出张量, 即 output = param[index], 索引的最大值特殊处理

        .. code-block:: python

            gather_hw(output, param, index, const_val, fill_const)

    参数:
        - ``output`` (`ppl.language.tensor`): output在local memory中张量

        - ``param`` (`ppl.language.tensor`): param在local memory中张量

        - ``index`` (`ppl.language.tensor`): index在local memory中张量

        - ``const_val`` (`标量`): 填充的常数

        - ``fill_const`` (`bool`):  dst 在索引最大值处填const_val的标志
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
            def gather_hw_kernel(param_ptr,
                                index_ptr,
                                output_ptr,
                                N:pl.constexpr,
                                C:pl.constexpr,
                                H:pl.constexpr,
                                W:pl.constexpr,
                                param_h:pl.constexpr,
                                param_w:pl.constexpr,
                                const_val,
                                fill_const:pl.constexpr):
            pid = pl.get_core_index()
            #torch.Tensor don't support uint16
            index_ptr.set_dtype(pl.pu16_t)
            shape = [N, C, H, W]
            param_global = pl.gtensor([N, C, param_h, param_w], pl.GLOBAL, param_ptr)
            index_global = pl.gtensor([1, H * W, 1, 2], pl.GLOBAL, index_ptr)
            o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
            param = pl.dma.load(param_global)
            index = pl.dma.load_compact(index_global)
            output = pl.make_tensor(shape, output_ptr.dtype)
            pl.tiu.gather_hw(output, param, index, const_val, fill_const)
            pl.dma.store(o_global, output)
    """
    return semantic.gather_hw(output, param, index, \
                             _to_tensor(const_val, _builder), \
                             _to_tensor(fill_const, _builder), _builder)

@builtin
def gather_w(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              is_param_repeated=False,
              const_val=0, fill_const=False,
              _builder=None):
    """
    a. 通过 w 维度的索引取值得到输出张量, 即 output = param[index]

        .. code-block:: python

            gather_w(output, param, index)

    b. 通过 w 维度的索引取值得到输出张量,即 output = param[index], 索引的最大值特殊处理

        .. code-block:: python

            gather_w(output, param, index, const_val, fill_const)

    c. 通过 w 维度的索引取值得到输出张量,即 output = param[index], param 的 batch 被广播

        .. code-block:: python

            gather_w(output, param, index, is_param_repeated)

    d. 通过 w 维度的索引取值得到输出张量, 即 output = param[index], param 的 batch 被广播, 索引的最大值特殊处理

        .. code-block:: python

            gather_w(output, param, index, is_param_repeated, const_val, fill_const)

    参数:
        - ``output`` (`ppl.language.tensor`): output在local memory中张量

        - ``param`` (`ppl.language.tensor`): param在local memory中张量

        - ``index`` (`ppl.language.tensor`): index在local memory中张量

        - ``is_param_repeated`` (`bool`): param 重复的标志

        - ``const_val`` (`标量`): 填充的常数

        - ``fill_const`` (`bool`):  dst 在索引最大值处填const_val的标志
    返回值:
        无

    注意事项:
        使用灵活,请参考06-gather-scatter.py中的测试例
    """
    return semantic.gather_w(output, param, index, \
                             _to_tensor(is_param_repeated, _builder), \
                             _to_tensor(const_val, _builder), \
                             _to_tensor(fill_const, _builder), _builder)

@builtin
def scatter_hw(output:pl.tensor, param:pl.tensor, index:pl.tensor,
               _builder=None):
    """
    通过 h 和 w 维度的索引取值得到输出张量,即 output = param[index],索引的最大值特殊处理

        .. code-block:: python

            scatter_hw(output, param, index)

    .. math:: \mathsf{dst(n, c, h, w) = param(n, c, h_{param}, w_{param})}
    .. math:: \mathsf{h = index(0, h_{param}\times W_{param} + w_{param}, 0, 1)}
    .. math:: \mathsf{w = index(0, h_{param}\times W_{param} + w_{param}, 0, 0)}

    参数:
        - ``output`` (`ppl.language.tensor`): output在local memory中张量

        - ``param`` (`ppl.language.tensor`): param在local memory中张量

        - ``index`` (`ppl.language.tensor`): index在local memory中张量

    返回值:
        无

    注意事项:
        无
    """
    return semantic.scatter_hw(output, param, index, _builder)

@builtin
def scatter_w(output:pl.tensor, param:pl.tensor, index:pl.tensor,
                bcast=False,
                is_param_repeated=False,
               _builder=None):
    """
    a. 通过 w 维度的索引改变输出张量的对应元素,即 output[index] = param

        .. code-block:: python

            scatter_w(output, param, index)

    b. 通过 w 维度的索引改变输出张量的对应元素,即 output[index] = param, param 的 batch 被广播(可选)

        .. code-block:: python

            scatter_w(output, param, index, bcast, is_param_repeated)

    参数:
        - ``output`` (`ppl.language.tensor`): output在local memory中张量

        - ``param`` (`ppl.language.tensor`): param在local memory中张量

        - ``index`` (`ppl.language.tensor`): index在local memory中张量

        - ``bcast`` (`bool`): param的batch被广播标志

        - ``is_param_repeated`` (`bool`): param重复的标志

    返回值:
        无

    注意事项:
        使用灵活,请参考06-gather-scatter.py中的测试例
    """
    return semantic.scatter_w(output, param, index, _to_tensor(bcast,_builder), \
                              _to_tensor(is_param_repeated, _builder), _builder)

@builtin
def arange_broadcast(output:pl.tensor, start, step, num,
                     _builder=None):
    """
    生成等差数列,C 维度广播到 LANE_NUM

        .. code-block:: python

            arange_broadcast(output, start, step, num)

    参数:
        - ``output`` (`ppl.language.tensor`): output在local memory中张量

        - ``start`` (`标量`): 等差数列的首项

        - ``step`` (`标量`): 等差数列的步长

        - ``num`` (`标量`): 等差数列的项数

    返回值:
        无

    注意事项:
        无
    """
    return semantic.arange_broadcast(output,\
                              _to_tensor(start, _builder),\
                              _to_tensor(step, _builder), \
                              _to_tensor(num, _builder), \
                              _builder)


@builtin
def fmul_add(*args, _builder=None):
    """
    两个张量(也可以是标量)相乘, 再累加另外一个张量(也可以是标量)

        .. code-block:: python

            fmul_add(dst, src0, src1, src2) 或 dst = fmul_add(src0, src1, src2)

            dst = src0 * src1 + src2

    参数:
        - ``dst`` (`ppl.language.tensor或标量`): 运算张量结果或标量

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``src2`` (`ppl.language.tensor或标量`): src2张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量`): 运算张量结果或标量

    注意事项:
        1. 只支持SG2380
        2. 也可以使用别名api: fma
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 3:
            return semantic.fmul_add(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(args[2], _builder),_builder)
        elif len(args) == 4:
            return semantic.fmul_add(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(args[3], _builder),
                            _builder)
    assert False

fmul_add.alias = 'fma'
globals()[fmul_add.alias] = fmul_add

@builtin
def fadd_sqr(*args, _builder=None):
    """
    a. 张量的元素按channel加bias,结果再平方

    b. 张量的元素加标量,结果再平方

    c. 标量加 bias,结果再平方

        .. code-block:: python

            fadd_sqr(dst, src, bias) 或 dst = fadd_sqr(src, bias)

            dst = (src + bias)^2

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor或标量`): src张量或标量

        - ``bias`` (`ppl.language.tensor或标量`): bias张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

    注意事项:
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.fadd_sqr(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder), _builder)
        elif len(args) == 3:
            return semantic.fadd_sqr(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _builder)
    assert False

@builtin
def fsub_sqr(*args, _builder=None):
    """
    a. 张量的元素按channel减bias,结果再平方

    b. 张量的元素减标量,结果再平方

    c. 标量减bias,结果再平方

        .. code-block:: python

            fsub_sqr(dst, src, bias) 或 dst = fsub_sqr(src, bias)

            dst = (src - bias)^2

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor或标量`): src张量或标量

        - ``bias`` (`ppl.language.tensor或标量`): bias张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

    注意事项:
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.fsub_sqr(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder), _builder)
        elif len(args) == 3:
            return semantic.fsub_sqr(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _builder)
    assert False

@builtin
def fscale(*args, scale, bias, _builder=None):
    """
    一个张量与另外一个张量(也可以是标量)相乘, 结果再加第三个张量(或标量)

        .. code-block:: python

            fscale(dst, src, scale, bias) 或 dst = fscale(src, scale, bias)

            dst = (src * scale) + bias

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): src张量

        - ``scale`` (`ppl.language.tensor或标量`): scale张量或标量

        - ``bias`` (`ppl.language.tensor或标量`): bias张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fscale(None, _to_tensor(args[0], _builder),
                                    _to_tensor(scale, _builder),
                                    _to_tensor(bias, _builder),
                                    _builder)
        elif len(args) == 2:
            return semantic.fscale(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(scale, _builder),
                            _to_tensor(bias, _builder),
                            _builder)
    assert False

@builtin
def fbias(*args, bias, _builder=None):
    """
    一个张量与另外一个张量(也可以是标量)相加

        .. code-block:: python

            fbias(dst, src, bias) 或 dst = fbias(src, bias)

            dst = src + bias

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): src张量

        - ``bias`` (`ppl.language.tensor或标量`): bias张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.fscale(None, _to_tensor(args[0], _builder),
                                    _to_tensor(None, _builder),
                                    _to_tensor(bias, _builder),
                                    _builder)
        elif len(args) == 2:
            return semantic.fscale(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(None, _builder),
                            _to_tensor(bias, _builder),
                            _builder)
    assert False

@builtin
def bitwise_and(*args, _builder=None):
    """
    a. 两个张量的元素做按位与运算

    b. 张量的元素与常数做按位与运算

    c. 两个标量做按位与运算

        .. code-block:: python

            bitwise_and(dst, src0, src1) 或 dst = bitwise_and(src0, src1)

            dst = src0 & src1

    参数:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或无返回值

    注意事项:
        也可以使用 dst = src0 & src1, 功能相同
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.and_(None, _to_tensor(args[0], _builder),
                                       _to_tensor(args[1], _builder),
                                       _builder)
        elif len(args) == 3:
            return semantic.and_(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _builder)
    assert False

@builtin
def bitwise_or(*args, _builder=None):
    """
    a. 两个张量的元素做按位或运算

    b. 张量的元素与常数做按位或运算

    c. 两个标量做按位或运算

        .. code-block:: python

            bitwise_or(dst, src0, src1) 或 dst = bitwise_or(src0, src1)

            dst = src0 | src1

    参数:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或无返回值

    注意事项:
        也可以使用 dst = src0 | src1, 功能相同
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.or_(None, _to_tensor(args[0], _builder),
                                       _to_tensor(args[1], _builder),
                                       _builder)
        elif len(args) == 3:
            return semantic.or_(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _builder)
    assert False

@builtin
def bitwise_xor(*args, _builder=None):
    """
    a. 两个张量的元素做按位异或运算

    b. 张量的元素与常数做按位异或运算

    c. 两个标量做按位异或运算

        .. code-block:: python

            bitwise_xor(dst, src0, src1) 或 dst = bitwise_xor(src0, src1)

            dst = src0 ^ src1

    参数:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或无返回值

    注意事项:
        也可以使用 dst = src0 ^ src1, 功能相同
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.xor_(None, _to_tensor(args[0], _builder),
                                       _to_tensor(args[1], _builder),
                                       _builder)
        elif len(args) == 3:
            return semantic.xor_(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _builder)
    assert False

@builtin
def bitwise_not(*args, _builder=None):
    """
    a. 对张量的元素按位取反

    c. 对标量做按位取反

        .. code-block:: python

            bitwise_not(dst, src) 或 dst = bitwise_not(src)

            dst = ~src

    参数:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或None

        - ``src`` (`ppl.language.tensor或标量`): src张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或标量或None`): 运算张量结果或标量或无返回值

    注意事项:
        也可以使用 dst = ~src, 功能相同
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.minus(None, _to_tensor(args[0], _builder),
                                       _builder)
        elif len(args) == 2:
            return semantic.minus(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _builder)
    assert False

@builtin
def gt(*args, true_val = 1, _builder=None):
    """
    a. 比较张量的元素是否大于另一个张量的元素, 可自定义真值

    b. 比较张量的元素是否大于常数, 可自定义真值

        .. code-block:: python

            gt(dst, src0, src1, true_val) 或 dst = gt(src0, src1, true_val)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``true_val`` (`标量`): 自定义真值

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.greater_than(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(true_val, _builder),
                                    _builder)
        elif len(args) == 3:
            return semantic.greater_than(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(true_val, _builder),
                            _builder)
    assert False

@builtin
def lt(*args, true_val = 1, _builder=None):
    """
    a. 比较张量的元素是否小于另一个张量的元素, 可自定义真值

    b. 比较张量的元素是否小于常数, 可自定义真值

        .. code-block:: python

            lt(dst, src0, src1, true_val) 或 dst = lt(src0, src1, true_val)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``true_val`` (`标量`): 自定义真值

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.less_than(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(true_val, _builder),
                                    _builder)
        elif len(args) == 3:
            return semantic.less_than(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(true_val, _builder),
                            _builder)
    assert False

@builtin
def eq(*args, true_val = 1, _builder=None):
    """
    a. 比较张量的元素是否等于另一个张量的元素, 可自定义真值

    b. 比较张量的元素是否等于常数, 可自定义真值

        .. code-block:: python

            eq(dst, src0, src1, true_val) 或 dst = eq(src0, src1, true_val)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``true_val`` (`标量`): 自定义真值

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.equal(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(true_val, _builder),
                                    _builder)
        elif len(args) == 3:
            return semantic.equal(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(true_val, _builder),
                            _builder)
    assert False

@builtin
def gt_select(*args, _builder=None):
    """
    两个张量的元素比较大小,选取另外两个张量的元素作为结果

        .. code-block:: python

            gt_select(dst, src0, src1, src2, src3) 或 dst = gt_select(src0, src1, src2, src3)

                dst = src0 > src1 ? src2 : src3

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``src2`` (`ppl.language.tensor或标量`): src2张量或标量

        - ``src3`` (`ppl.language.tensor或标量`): src3张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 4:
            return semantic.gt_select(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(args[2], _builder),
                                    _to_tensor(args[3], _builder),
                                    _builder)
        elif len(args) == 5:
            return semantic.gt_select(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(args[3], _builder),
                            _to_tensor(args[4], _builder),
                            _builder)
    assert False

@builtin
def lt_select(*args, _builder=None):
    """
    两个张量的元素比较大小, 选取另外两个张量的元素作为结果

        .. code-block:: python

            lt_select(dst, src0, src1, src2, src3) 或 dst = lt_select(src0, src1, src2, src3)

                dst = src0 < src1 ? src2 : src3

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``src2`` (`ppl.language.tensor或标量`): src2张量或标量

        - ``src3`` (`ppl.language.tensor或标量`): src3张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 4:
            return semantic.lt_select(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(args[2], _builder),
                                    _to_tensor(args[3], _builder),
                                    _builder)
        elif len(args) == 5:
            return semantic.lt_select(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(args[3], _builder),
                            _to_tensor(args[4], _builder),
                            _builder)
    assert False

@builtin
def eq_select(*args, _builder=None):
    """
    两个张量的元素是否相等, 选取另外两个张量的元素作为结果

        .. code-block:: python

            eq_select(dst, src0, src1, src2, src3) 或 dst = eq_select(src0, src1, src2, src3)

                dst = src0 == src1 ? src2 : src3

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``src2`` (`ppl.language.tensor或标量`): src2张量或标量

        - ``src3`` (`ppl.language.tensor或标量`): src3张量或标量

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 4:
            return semantic.eq_select(None, _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(args[2], _builder),
                                    _to_tensor(args[3], _builder),
                                    _builder)
        elif len(args) == 5:
            return semantic.eq_select(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(args[2], _builder),
                            _to_tensor(args[3], _builder),
                            _to_tensor(args[4], _builder),
                            _builder)
    assert False

@builtin
def max_gt_select(out0, out1, src0, src1, src2, src3, _builder=None):
    """
    两个张量的元素比较大小, 选取其中较大的和另外两个张量的元素作为结果

        .. code-block:: python

            max_gt_select(out0, out1, src0, src1, src2, src3)

                out0 = max(src0, src1) &&  out1 = src0 > src1 ? src2 : src3

    参数:
        - ``out0`` (`ppl.language.tensor`): 运算张量结果

        - ``out1`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``src2`` (`ppl.language.tensor或标量`): src2张量或标量

        - ``src3`` (`ppl.language.tensor或标量`): src3张量或标量

    返回值:
        无

    注意事项:
        无
    """
    mode = semantic.Comparision_mode.GREATER.value
    return semantic.maxmin_cmp_select(_to_tensor(out0, _builder),
                                _to_tensor(out1, _builder),
                                _to_tensor(src0, _builder),
                                _to_tensor(src1, _builder),
                                _to_tensor(src2, _builder),
                                _to_tensor(src3, _builder),
                                _constexpr_to_value(mode),
                                _builder)

@builtin
def min_lt_select(out0, out1, src0, src1, src2, src3, _builder=None):
    """
    两个张量的元素比较大小, 选取其中较小的和另外两个张量的元素作为结果

        .. code-block:: python

            min_lt_select(out0, out1, src0, src1, src2, src3)

                out0 = min(src0, src1) &&  out1 = src0 < src1 ? src2 : src3

    参数:
        - ``out0`` (`ppl.language.tensor`): 运算张量结果

        - ``out1`` (`ppl.language.tensor`): 运算张量结果

        - ``src0`` (`ppl.language.tensor或标量`): src0张量或标量

        - ``src1`` (`ppl.language.tensor或标量`): src1张量或标量

        - ``src2`` (`ppl.language.tensor或标量`): src2张量或标量

        - ``src3`` (`ppl.language.tensor或标量`): src3张量或标量

    返回值:
        无

    注意事项:
        无
    """
    mode = semantic.Comparision_mode.LESS.value
    return semantic.maxmin_cmp_select(_to_tensor(out0, _builder),
                                _to_tensor(out1, _builder),
                                _to_tensor(src0, _builder),
                                _to_tensor(src1, _builder),
                                _to_tensor(src2, _builder),
                                _to_tensor(src3, _builder),
                                _constexpr_to_value(mode),
                                _builder)

@builtin
def shift(*args, shift, r_mode=RM_HALF_TO_EVEN, _builder=None):
    """
    张量的元素做算术移位运算

        .. code-block:: python

            shift(dst, src, shift, r_mode) or dst = shift(src, shift, r_mode)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): 运算张量结果

        - ``shift`` (`ppl.language.tensor或标量`): 移位张量或标量

        - ``r_mode`` (`pl.round_mode`): round mode

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.shift(None, _to_tensor(args[0], _builder),
                                    _to_tensor(shift, _builder),
                                    _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                    True,
                                    _builder)
        elif len(args) == 2:
            return semantic.shift(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(shift, _builder),
                            _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                            True,
                            _builder)
    assert False

@builtin
def logical_shift(*args, shift, r_mode=RM_HALF_TO_EVEN, _builder=None):
    """
    张量的元素做逻辑移位运算

        .. code-block:: python

            logical_shift(dst, src, shift, r_mode) or dst = logical_shift(src, shift, r_mode)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): 运算张量结果

        - ``shift`` (`ppl.language.tensor或标量`): 移位张量或标量

        - ``r_mode`` (`pl.round_mode`): round mode

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.logical_shift(None, _to_tensor(args[0], _builder),
                                        _to_tensor(shift, _builder),
                                        _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                        _builder)
        elif len(args) == 2:
            return semantic.logical_shift(_to_tensor(args[0], _builder),
                                        _to_tensor(args[1], _builder),
                                        _to_tensor(shift, _builder),
                                        _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                        _builder)
    assert False

@builtin
def circular_shift(*args, shift, r_mode=RM_HALF_TO_EVEN, _builder=None):
    """
    张量的元素做绕回移位运算

        .. code-block:: python

            circular_shift(dst, src, shift, r_mode) or dst = circular_shift(src, shift, r_mode)

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src`` (`ppl.language.tensor`): 运算张量结果

        - ``shift`` (`ppl.language.tensor或标量`): 移位张量或标量

        - ``r_mode`` (`pl.round_mode`): round mode

    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.circular_shift(None, _to_tensor(args[0], _builder),
                                        _to_tensor(shift, _builder),
                                        _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                        _builder)
        elif len(args) == 2:
            return semantic.circular_shift(_to_tensor(args[0], _builder),
                                        _to_tensor(args[1], _builder),
                                        _to_tensor(shift, _builder),
                                        _to_tensor(_constexpr_to_value(r_mode).val(), _builder),
                                        _builder)
    assert False

@builtin
def norm(dst:pl.tensor, src:pl.tensor,
        _builder=None):
    """
    提取浮点数指数部分指令。指令对输入浮点 Tensor src 提取指数部分并转化为整型输出到 Tensor dst 中

        .. code-block:: python

            norm(dst, src)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        无

    注意事项:
        只支持SG2380
    """
    return semantic.norm(
                        _to_tensor(dst, _builder),
                        _to_tensor(src, _builder),
                        _builder)
@builtin
def clz(dst:pl.tensor, src:pl.tensor,
        _builder=None):
    """
    指令用于计算 Tensor src 元素从最高位到低位遇到第一个 1 所间隔的位数。
    并且支持当操作数 src 的 n、h 或 w 维大小为 1 时, 广播计算

        .. code-block:: python

            clz(dst, src)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        无

    注意事项:
        只支持SG2380
    """
    return semantic.clz(
                        _to_tensor(dst, _builder),
                        _to_tensor(src, _builder),
                        _builder)

@builtin
def clo(dst:pl.tensor, src:pl.tensor,
        _builder=None):
    """
    指令用于计算 Tensor src 元素从最高位到低位遇到第一个 0 所间隔的位数。
    并且支持当操作数 src 的 n、h 或 w 维大小为 1 时, 广播计算

        .. code-block:: python

            clo(dst, src)

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        无

    注意事项:
        只支持SG2380
    """
    return semantic.clo(
                        _to_tensor(dst, _builder),
                        _to_tensor(src, _builder),
                        _builder)
'''
@builtin
def taylor(*args,
          coeff:pl.tensor,
          length:int,
         _builder=None):
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 1:
            return semantic.taylor(None, _to_tensor(args[0], _builder),
                                    _to_tensor(coeff, _builder),
                                    _to_tensor(_constexpr_to_value(length), _builder),
                                    _builder)
        elif len(args) == 2:
            return semantic.taylor(_to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(coeff, _builder),
                                    _to_tensor(_constexpr_to_value(length), _builder),
                                    _builder)
    assert False
'''
@builtin
def vc_min(*args,
            _builder=None):
    """
    两个向量的元素交叉做取小运算

        .. code-block:: python

            dst = vc_min(src0, src1) or vc_min(dst, src0, src1)

    .. math:: \mathsf{dst(m, n) = min(src0(m), src1(n))}

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor`): src0张量

        - ``src1`` (`ppl.language.tensor`): src1张量
    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    mode = semantic.Arith_mode.ARITH_MIN.value
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.vc_op(None,
                                    _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(mode, _builder),
                                    _builder)
        elif len(args) == 3:
            return semantic.vc_op(_to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(args[2], _builder),
                                    _to_tensor(mode, _builder),
                                    _builder)
    assert False

@builtin
def vc_max(*args,
            _builder=None):
    """
    两个向量的元素交叉做取大运算

        .. code-block:: python

            dst = vc_max(src0, src1) or vc_max(dst, src0, src1)

    .. math:: \mathsf{dst(m, n) = max(src0(m), src1(n))}

    参数:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或None

        - ``src0`` (`ppl.language.tensor`): src0张量

        - ``src1`` (`ppl.language.tensor`): src1张量
    返回值:
        - ``dst`` (`ppl.language.tensor或None`): 运算张量结果或无返回值

    注意事项:
        无
    """
    mode = semantic.Arith_mode.ARITH_MAX.value
    if all(isinstance(t, (tensor, constexpr)) for t in args):
        if len(args) == 2:
            return semantic.vc_op(None,
                                    _to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(mode, _builder),
                                    _builder)
        elif len(args) == 3:
            return semantic.vc_op(_to_tensor(args[0], _builder),
                                    _to_tensor(args[1], _builder),
                                    _to_tensor(args[2], _builder),
                                    _to_tensor(mode, _builder),
                                    _builder)
    assert False

@builtin
def transpose_wc(dst:pl.tensor,
                 src:pl.tensor,
                _builder=None):
    """
    张量的 W 与 C 两个维度转置

        .. code-block:: python

            transpose_wc(dst, src)

    .. math:: \mathsf{dst(n, c, h, w) = src(n, w, h, c)}

    参数:
        - ``dst`` (`ppl.language.tensor`): 运算张量结果

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        无

    注意事项:
        无
    """
    return semantic.transpose_wc(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                _builder)

@builtin
def fdeconv(output, src, weight, bias, oc, kernel, dilation, padding, insert, result_add, out_dtype, has_bias, _builder=None):
    """
    做2D反卷积的2D卷积(input可以插零,kernel做旋转), 结果按channel加bias(可选), 再对结果做累加(可选)

        .. code-block:: python

            fdeconv(output, src, weight, bias, oc, kernel, dilation, padding, insert, result_add, out_dtype, has_bias)

    参数:
        - ``output`` (`ppl.language.tensor`): local memory上的output张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``weight`` (`ppl.language.tensor`): local memory上的weight张量

        - ``bias`` (`ppl.language.tensor or None`): local memory上的bias张量或None

        - ``oc`` (`int`): output的channel数

        - ``kernel`` (`dim2`): kernel大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``insert`` (`dim2`): insert大小

        - ``result_add`` (`bool`): 对结果做累加的标志

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``has_bias`` (`bool`): 是否有bias
    返回值:
        无

    注意事项:
        无
    """
    bias = _to_tensor(bias, _builder)
    assert (not dilation is None) or (not insert is None)
    oc =  _to_tensor(oc, _builder)
    result_add = _to_tensor(result_add, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    return semantic.fdeconv(output, src, weight, bias, oc, kernel, dilation, padding, insert, result_add, out_dtype, has_bias, _builder)

#deconv_sym and deconv_asym
@builtin
def deconv(output, src, weight, bias, oc, kernel, dilation, padding,
           insert, has_bias, pad_val=None, insert_val=0, result_relu=False,
           result_add=False, out_dtype=void, sym=True, quant=0, _builder=None):
    """
    a.对称量化 2D 反卷积, 结果按 channel 加 bias(可选), 再对结果做 ReLU(可选),最后对结
      果做算数右移, 支持 pad, 支持 insert, 支持指定输出类型(可选)

        .. code-block:: python

            deconv(output, src, weight, bias, oc, kernel, dilation, padding, insert, result_relu, out_dtype, has_bias, quant, sym=True)

    b.非对称量化2D反卷积,支持对结果进行累加(可选),支持 pad,支持 weight 减去 kzp 常数, 支持常数 insert,支持指定输出类型(可选)

        .. code-block:: python

            deconv(output, src, weight, None, oc, kernel, dilation, padding, insert, pad_val, insert_val, result_add, out_dtype, quant, has_bias=False, sym=False)

    参数:
        - ``output`` (`ppl.language.tensor`): local memory上的output张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``weight`` (`ppl.language.tensor`): local memory上的weight张量

        - ``bias`` (`ppl.language.tensor or None`): local memory上的bias张量或None

        - ``oc`` (`int`): output的channel数

        - ``kernel`` (`dim2`): kernel大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``insert`` (`dim2`): insert大小

        - ``has_bias`` (`bool`): 是否有bias

        - ``pad_val`` (`标量或None`): pad 的值

        - ``insert_val`` (`标量`): insert 的值

        - ``result_relu`` (`bool`): 对结果做 ReLU 的标志

        - ``result_add`` (`bool`): 对结果做累加的标志

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``sym`` (`bool`): 对称还是非对称标志

        - ``quant`` (`标量`): 对称时是rshift, 非对称为kzp
    返回值:
        无

    注意事项:
        因api同时支持对称和非对称(通过关键字参数), 使用灵活, 可以参考测试例03-conv.py的使用组合
    """
    bias = _to_tensor(bias, _builder)
    oc = _to_tensor(oc, _builder)
    has_bias = _to_tensor(has_bias, _builder)
    pad_val = _to_tensor(pad_val, _builder)
    insert_val = _to_tensor(insert_val, _builder)
    result_relu = _to_tensor(result_relu, _builder)
    result_add = _to_tensor(result_add, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    sym = _to_tensor(sym, _builder)
    quant = _to_tensor(quant, _builder)
    return semantic.deconv(output, src, weight, bias, oc, kernel, dilation, padding, insert, pad_val,
                    insert_val, result_relu, result_add, out_dtype, has_bias, sym, quant, _builder)

@builtin
def fdw_deconv(output, src, weight, bias, kernel, dilation, padding, insert, out_dtype, has_bias, _builder=None):
    """
    2D depthwise反卷积(input可以插零,kernel做旋转), 结果按channel加bias(可选)

        .. code-block:: python

            fdw_deconv(output, src, weight, bias, kernel, dilation, padding, insert, out_dtype, has_bias)

    参数:
        - ``output`` (`ppl.language.tensor`): local memory上的output张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``weight`` (`ppl.language.tensor`): local memory上的weight张量

        - ``bias`` (`ppl.language.tensor or None`): local memory上的bias张量或None

        - ``kernel`` (`dim2`): kernel大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``insert`` (`dim2`): insert大小

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``has_bias`` (`bool`): 是否有bias

    返回值:
        无

    注意事项:
        无
    """
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    return semantic.fdw_deconv(output, src, weight, bias, kernel, dilation, padding, insert, out_dtype, has_bias, _builder)

@builtin
def dw_deconv(output, src, weight, bias, kernel, dilation, padding, insert, pad_val, result_relu, out_dtype, has_bias, rshift, round_mode:round_mode, _builder=None):
    """
    2D depthwise反卷积,结果按channel加bias(可选),再对结果做 ReLU(可选), 最后对结果做算数右移,支持insert,支持pad填充常数,支持对结果做饱和

        .. code-block:: python

            dw_deconv(output, src, weight, bias, kernel, dilation, padding, insert, pad_val, result_relu, out_dtype, has_bias, rshift, round_mode)

    参数:
        - ``output`` (`ppl.language.tensor`): local memory上的output张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``weight`` (`ppl.language.tensor`): local memory上的weight张量

        - ``bias`` (`ppl.language.tensor or None`): local memory上的bias张量或None

        - ``kernel`` (`dim2`): kernel大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``insert`` (`dim2`): insert大小

        - ``pad_val`` (`标量`): pad 的值

        - ``result_relu`` (`bool`): 对结果做 ReLU 的标志

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``has_bias`` (`bool`): 是否有bias

        - ``rshift`` (`int`): 右移位数

        - ``round_mode`` (`pl.round_mode`): 舍入模式
    返回值:
        无

    注意事项:
        无
    """
    bias = _to_tensor(bias, _builder)
    pad_val = _to_tensor(pad_val, _builder)
    result_relu = _to_tensor(result_relu, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    rshift = _to_tensor(rshift, _builder)
    round_mode = _to_tensor(_constexpr_to_value(round_mode).val(), _builder)
    return semantic.dw_deconv(output, src, weight, bias, kernel, dilation, padding,
                             insert, pad_val, result_relu, out_dtype, has_bias, rshift,
                             round_mode, _builder)

@builtin
def fdw_conv(output, src, weight, bias, kernel, stride, dilation, padding, has_bias, _builder=None):
    """
    2D depthwise卷积,结果按channel加bias(可选), 再对结果做累加(可选)。

        .. code-block:: python

            fdw_conv(output, src, weight, bias, kernel, stride, dilation, padding, has_bias)

    参数:
        - ``output`` (`ppl.language.tensor`): local memory上的output张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``weight`` (`ppl.language.tensor`): local memory上的weight张量

        - ``bias`` (`ppl.language.tensor or None`): local memory上的bias张量或None

        - ``kernel`` (`dim2`): kernel大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``has_bias`` (`bool`): 是否有bias
    返回值:
        无

    注意事项:
        无
    """
    bias = _to_tensor(bias, _builder)
    has_bias = _to_tensor(has_bias, _builder)
    return semantic.fdw_conv(output, src, weight, bias, kernel, stride, dilation, padding,
                              has_bias, _builder)

@builtin
def dw_conv(output, src, weight, bias, kernel, stride, dilation, padding, pad_val, result_relu,
           out_dtype, has_bias, round_mode:round_mode,
           rshift=0, rq=False,  requant=None, saturate=False,
           _builder=None):
    """
    2D depthwise卷积(卷积核可以为常数), 结果按 channel 加 bias(可选), 再对结果做 ReLU(可选),
    最后对结果做算数右移, 支持 pad 填充常数, 支持对结果做饱和

        .. code-block:: python

            dw_conv(output, src, weight, bias, kernel, stride, dilation, padding, pad_val, result_relu, out_dtype, has_bias, round_mode, rshift, rq, requant, saturate)

    参数:
        - ``output`` (`ppl.language.tensor`): local memory上的output张量

        - ``src`` (`ppl.language.tensor`): local memory上的src张量

        - ``weight`` (`ppl.language.tensor或标量`): local memory上的weight张量或标量

        - ``bias`` (`ppl.language.tensor or None`): local memory上的bias张量或None

        - ``kernel`` (`dim2`): kernel大小

        - ``stride`` (`dim2`): stride大小

        - ``dilation`` (`dim2`): dilation大小

        - ``padding`` (`dim4`): padding大小

        - ``pad_val`` (`标量`): pad 填充的常数值

        - ``result_relu`` (`bool`): 对结果做 ReLU 的标志

        - ``out_dtype`` (`pl.dtype`): 结果数据类型

        - ``has_bias`` (`bool`): 是否有bias

        - ``round_mode`` (`pl.round_mode`): 舍入模式

        - ``rshift`` (`int`): 右移位数

        - ``rq`` (`bool`): 是否做rq

        - ``requant`` (`ppl.language.tensor或None`): requant参数

        - ``saturate`` (`bool`): saturate标志

    返回值:
        无

    注意事项:
        因api同时支持rq或非rq, 使用灵活, 可以参考测试例03-conv.py的使用组合
    """
    weight = _to_tensor(weight, _builder)
    bias = _to_tensor(bias, _builder)
    pad_val = _to_tensor(pad_val, _builder)
    result_relu = _to_tensor(result_relu, _builder)
    out_dtype = _to_tensor(semantic.get_dtype_num
                 (_constexpr_to_value(out_dtype)), _builder)
    has_bias = _to_tensor(has_bias, _builder)
    round_mode = _to_tensor(_constexpr_to_value(round_mode).val(), _builder)
    rshift = _to_tensor(rshift, _builder)
    rq = _to_tensor(rq, _builder)
    requant = _to_tensor(requant, _builder)
    saturate = _to_tensor(saturate, _builder)
    return semantic.dw_conv(output, src, weight, bias, kernel, stride, dilation, padding, pad_val,
                             result_relu, out_dtype, has_bias, rshift, rq, requant, saturate,
                             round_mode, _builder)

@builtin
def rq0(output, input, dst_round_mode:round_mode, src_round_mode:round_mode,
        scale=0, offset=0, quant=None, _builder=None):
    """
    1. 重量化张量的元素, 结果有saturation

        .. code-block:: python

            rq0(output, input, dst_round_mode, src_round_mode, scale, offset)

    2. 按channel重量化张量的元素, 结果有saturation

        .. code-block:: python

            rq0(output, input, dst_round_mode, src_round_mode, quant)

    参数:
        - ``output`` (`ppl.language.tensor`): 在local memory中dst张量

        - ``input`` (`ppl.language.tensor`): 在local memory中的src张量

        - ``dst_round_mode`` (`pl.round_mode`): 浮点数转化到 dst 的元素的舍入模式

        - ``src_round_mode`` (`pl.round_mode`): src 的元素转化到浮点数的舍入模式

        - ``scale`` (`float`): 乘子常数

        - ``offset`` (`float`): 补偿常数

        - ``quant`` (`ppl.language.tensor`):  local memory 上的 quant 张量
    返回值:
        无

    注意事项:
        无
    """
    if not quant is None:
        return semantic.rq_pc_fp(output, input,
                            _to_tensor(quant, _builder),
                            _to_tensor(_constexpr_to_value(dst_round_mode).val(), _builder),
                            _to_tensor(_constexpr_to_value(src_round_mode).val(), _builder),
                            _builder)
    else:
        return semantic.rq_fp(output, input,
                            _to_tensor(scale, _builder),
                            _to_tensor(offset, _builder),
                            _to_tensor(_constexpr_to_value(dst_round_mode).val(), _builder),
                            _to_tensor(_constexpr_to_value(src_round_mode).val(), _builder),
                            _builder)

@builtin
def rq1(output, input, round_mode:round_mode,
        multiplier=0, shift=0, offset=0, quant=None, _builder=None):
    """
    1. 重量化张量的元素, 结果有, 结果有saturation

        .. code-block:: python

            rq1(output, input, round_mode, multiplier, shift, offset)

    2. 按channel重量化张量的元素, 结果有saturation

        .. code-block:: python

            rq1(output, input, round_mode, quant)

    参数:
        - ``output`` (`ppl.language.tensor`): 在local memory中dst张量

        - ``input`` (`ppl.language.tensor`): 在local memory中的src张量

        - ``round_mode`` (`pl.round_mode`): 右移舍入模式

        - ``multiplier`` (`int`): 乘子常数

        - ``shift`` (`int`): 移位数

        - ``offset`` (`int`): 补偿常数

        - ``quant`` (`ppl.language.tensor`):  local memory 上的 quant 张量
    返回值:
        无

    注意事项:
        无
    """
    if not quant is None:
        return semantic.rq_pc_int(output, input,
                            _to_tensor(quant, _builder),
                            _to_tensor(_constexpr_to_value(round_mode).val(), _builder),
                            _builder)
    else:
        return semantic.rq_int(output, input,
                            _to_tensor(multiplier, _builder),
                            _to_tensor(shift, _builder),
                            _to_tensor(offset, _builder),
                            _to_tensor(_constexpr_to_value(round_mode).val(), _builder),
                            _builder)

@builtin
def dq0(output, input, round_mode:round_mode,
        offset=0, scale=0, quant=None, _builder=None):
    """
    1. 反量化张量的元素

        .. code-block:: python

            dq0(output, input, round_mode, offset, scale)

    2. 按channel反量化张量的元素

        .. code-block:: python

            dq0(output, input, round_mode, quant)

    参数:
        - ``output`` (`ppl.language.tensor`): 在local memory中dst张量

        - ``input`` (`ppl.language.tensor`): 在local memory中的src张量

        - ``round_mode`` (`pl.round_mode`): 右移舍入模式

        - ``offset`` (`int`): 补偿常数

        - ``scale`` (`float`): 乘子常数

        - ``quant`` (`ppl.language.tensor`):  local memory 上的 quant 张量
    返回值:
        无

    注意事项:
        无
    """
    if not quant is None:
        return semantic.dq_pc_fp(output, input,
                            _to_tensor(quant, _builder),
                            _to_tensor(_constexpr_to_value(round_mode).val(), _builder),
                            _builder)
    else:
        return semantic.dq_fp(output, input,
                            _to_tensor(offset, _builder),
                            _to_tensor(scale, _builder),
                            _to_tensor(_constexpr_to_value(round_mode).val(), _builder),
                            _builder)

@builtin
def dq1(output, input, round_mode:round_mode,
        offset=0, multiplier=0, shift=0, quant=None, _builder=None):
    """
    1. 反量化张量的元素,结果有saturation

        .. code-block:: python

            dq1(output, input, round_mode, offset, multiplier, shift)

    2. 按channel反量化张量的元素,结果有saturation

        .. code-block:: python

            dq1(output, input, round_mode, quant)

    参数:
        - ``output`` (`ppl.language.tensor`): 在local memory中dst张量

        - ``input`` (`ppl.language.tensor`): 在local memory中的src张量

        - ``round_mode`` (`pl.round_mode`): 右移舍入模式

        - ``offset`` (`int`): 补偿常数

        - ``multiplier`` (`int`): 乘子常数

        - ``shift`` (`int`): 移位数

        - ``quant`` (`ppl.language.tensor`):  local memory 上的 quant 张量
    返回值:
        无

    注意事项:
        无
    """
    if not quant is None:
        return semantic.dq_pc_int(output, input,
                            _to_tensor(quant, _builder),
                            _to_tensor(_constexpr_to_value(round_mode).val(), _builder),
                            _builder)
    else:
        return semantic.dq_int(output, input,
                            _to_tensor(offset, _builder),
                            _to_tensor(multiplier, _builder),
                            _to_tensor(shift, _builder),
                            _to_tensor(_constexpr_to_value(round_mode).val(), _builder),
                            _builder)

@builtin
def dq2(output, input, offset_scale:pl.tensor, gsize:int, _builder=None):
    """
    反量化张量的元素并将结果转为半精度浮点数;
    支持按照 gsize 进行反量化;支持使用反量化结果减去 offset,然后在使用 scale 做缩放

        .. code-block:: python

            dq2(output, input, offset_scale, gsize)

    参数:
        - ``output`` (`ppl.language.tensor`): 在local memory中dst张量

        - ``input`` (`ppl.language.tensor`): 在local memory中的src张量

        - ``offset_scale`` (`ppl.language.tensor`): 在local memory中offset和scale 张量

        - ``gsize`` (`int`): group size 常数
    返回值:
        无

    注意事项:
        无
    """
    return semantic.dq2(output, input,
                        offset_scale,
                        _to_tensor(gsize, _builder),
                        _builder)


@builtin
def zero(input, _builder=None):
    """
    将张量的元素置成0

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
    return semantic.fill(input, value, dtype, True, _builder)

@builtin
def fill(input, value, _builder=None):
    """
    将张量的元素置成常数

        .. code-block:: python

            fill(input, value)

            input = value

    参数:
        - ``input`` (`ppl.language.tensor`): 结果张量

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
            def tiu_fill(
                input_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                ...
                mi_sub_tensor = pl.make_tensor([block_h, block_m, 1, 1], q_ptr.dtype, [real_q_h, real_m, 1, 1])
                pl.tiu.fill(mi_sub_tensor, -15000)
    """
    dtype = input.dtype.scalar
    if dtype.is_bf16() or dtype.is_fp16() or dtype.is_fp8():
        dtype = float32
    value = _constexpr_to_value(value)
    dtype = _constexpr_to_value(dtype)
    return semantic.fill(input, value, dtype, True, _builder)

@builtin
def move(dst, src, _builder=None):
    """
    拷贝张量的元素

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
            def move(
                input_ptr,
                output_ptr,
                N:pl.constexpr,
                C:pl.constexpr,
                H:pl.constexpr,
                W:pl.constexpr
            ):
                ...
                dst = pl.make_tensor([block_h, block_m, 1, 1], q_ptr.dtype, [real_q_h, real_m, 1, 1])
                src = pl.make_tensor([block_h, block_m, 1, 1], q_ptr.dtype, [real_q_h, real_m, 1, 1])
                pl.tiu.move(dst, src)
    """
    return semantic.move(dst, src, True, _builder)

@builtin
def move_cross_lane(dst:pl.tensor,
                src:pl.tensor,
                _builder=None):
    """
    跨 LANE 拷贝张量的元素

        .. code-block:: python

            move_cross_lane(dst, src)

    参数:
        - ``dst`` (`ppl.language.tensor`): local memory上的张量

        - ``src`` (`ppl.language.tensor`): local memory上的张量

        - ``trans_mode`` (`ppl.transpose_mode`): 转置模式
    返回值:
        无

    注意事项:
        无
    """
    return semantic.move_cross_lane(_to_tensor(dst, _builder),
                                        _to_tensor(src, _builder),
                                        _builder)

@builtin
def mask_select(dst, dst_cnt, src, mask, _builder=None):
    """
    将 mask 为 1 相同位置上的 src 的 W 维元素写到 dst 中, 并返回每个 Channel 的元素的个数并写
    到 dst_cnt 中

        .. code-block:: python

            mask_select(dst, dst_cnt, src, mask)

    参数:
        - ``dst`` (`ppl.language.tensor`): dst张量

        - ``dst_cnt`` (`ppl.language.tensor`): dst_cnt张量

        - ``src`` (`ppl.language.tensor`): src张量

        - ``mask`` (`ppl.language.tensor`): mask张量

    返回值:
        无

    注意事项:
        无

    使用示例:
        无
    """
    return semantic.tiu_mask_select(_to_tensor(dst, _builder),
                                _to_tensor(dst_cnt, _builder),
                                _to_tensor(src, _builder),
                                _to_tensor(mask, _builder),
                                _builder)

@builtin
def broadcast(*args, npu_num=0, _builder=None):
    """
    广播张量的元素到其他 lane

        .. code-block:: python

            broadcast(dst, src, npu_num) or dst = broadcast(src, npu_num)
            dst(n, c, h,w) = src(n, 1, h,w)


    参数:
        - ``dst`` (`ppl.language.tensor`): dst张量

        - ``src`` (`ppl.language.tensor`): src张量

        - ``npu_num`` (`常数`): C 维度广播数量, 默认为 LANE_NUM

    返回值:
        - ``dst`` (`ppl.language.tensor`): 张量运算结果或无返回值

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
                o_global = pl.gtensor([N, oc, H, W], pl.GLOBAL, output_ptr)
                src_global = pl.gtensor([N, 1, H, W], pl.GLOBAL, src_ptr)
                out = pl.make_tensor([N, oc, H, W], output_ptr.dtype)
                src = pl.dma.load(src_global)
                pl.tiu.broadcast(out, src, npu_num=oc)
                pl.dma.store(o_global, out)
    """
    assert _constexpr_to_value(npu_num) <= get_npu_num()
    if all(isinstance(t, tensor) for t in args):
        if len(args) == 1:
            return semantic.broadcast(None, _to_tensor(args[0], _builder),
                                         _to_tensor(npu_num, _builder),
                                         True,
                                         _builder)
        elif len(args) == 2:
            return semantic.broadcast(_to_tensor(args[0], _builder),
                            _to_tensor(args[1], _builder),
                            _to_tensor(npu_num, _builder),
                            True,
                            _builder)
    assert False

@builtin
def nonzero(dst, dst_cnt, src, _builder=None):
    """
    生成非 0 元素索引的指令。指令 Tensor src 的 W 维非 0 元素的索引写到 Tensor dst 中,返
    回每个 channel 的非 0 元素的个数并写到 Tensor dst_cnt 中

        .. code-block:: python

            nonzero(dst, dst_cnt, src)

    参数:
        - ``dst`` (`ppl.language.tensor`): dst张量

        - ``dst_cnt`` (`ppl.language.tensor`): dst_cnt张量

        - ``src`` (`ppl.language.tensor`): src张量

    返回值:
        无

    注意事项:
        无

    使用示例:
        无
    """
    return semantic.tiu_nonzero(_to_tensor(dst, _builder),
                                _to_tensor(dst_cnt, _builder),
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
        无

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
                out = pl.make_tensor([N, W, H, C], output_ptr.dtype, align_mode=pl.TPU_ROW_ALIGN)
                src = pl.dma.load(src_global)
                pl.tiu.transpose_cw(out, src)
                pl.dma.store(o_global, out)
    """
    return semantic.transpose_cw(_to_tensor(dst, _builder),
                                _to_tensor(src, _builder),
                                True,
                                _builder)

@builtin
def gather_h(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              is_param_repeated=False,
              const_val=0, fill_const=False,
              _builder=None):
    """
    通过 h 维度的索引取值得到输出张量,即 dst = param[index], param 的 batch 被广播. 如果fill_const为True, 索
    引的最大值特殊处理

        .. code-block:: python

            gather_h(output, param, index, is_param_repeated, const_val, fill_const)

    参数:
        - ``output`` (`ppl.language.tensor`): dst张量

        - ``param`` (`ppl.language.tensor`): param张量

        - ``index`` (`ppl.language.tensor`): index张量

        - ``is_param_repeated`` (`bool`): param重复的标志

        - ``const_val`` (`常数`): 填充的常数,在fill_const=True时才有效

        - ``在fill_const`` (`bool`):  dst 在索引最大值处是否填 const_val 的标志
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
            def bcast_h_gather_kernel(param_ptr,
                                index_ptr,
                                output_ptr,
                                N:pl.constexpr,
                                C:pl.constexpr,
                                H:pl.constexpr,
                                W:pl.constexpr,
                                param_c:pl.constexpr,
                                param_h:pl.constexpr,
                                is_param_repeated:pl.constexpr,
                                const_val,
                                fill_const:pl.constexpr):
            pid = pl.get_core_index()
            #torch.Tensor don't support uint16
            index_ptr.set_dtype(pl.pu16_t)
            shape = [N, C, H, W]
            param_global = pl.gtensor([1, param_c, param_h, W], pl.GLOBAL, param_ptr)
            index_global = pl.gtensor([N, C, H, 1], pl.GLOBAL, index_ptr)
            o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
            param = pl.dma.load(param_global, align_mode=pl.TPU_ROW_ALIGN)
            index = pl.dma.load(index_global)
            output = pl.make_tensor(shape, output_ptr.dtype, align_mode=pl.TPU_ROW_ALIGN)
            pl.tiu.gather_h(output, param, index, is_param_repeated, const_val, fill_const)
            pl.dma.store(o_global, output)
    """
    return semantic.gather_h(output, param, index, \
                             _to_tensor(is_param_repeated, _builder), \
                             _to_tensor(const_val, _builder), \
                             _to_tensor(fill_const, _builder), _builder)

@builtin
def scatter_h(output:pl.tensor, param:pl.tensor, index:pl.tensor,
                is_param_repeated=False,
               _builder=None):
    """
    通过 h 维度的索引改变输出张量的对应元素,即 dst[index] = param, param 的 batch 被广播

        .. code-block:: python

            scatter_h(output, param, index, is_param_repeated)

    参数:
        - ``output`` (`ppl.language.tensor`): dst张量

        - ``param`` (`ppl.language.tensor`): param张量

        - ``index`` (`ppl.language.tensor`): index张量

        - ``is_param_repeated`` (`bool`): param重复的标志

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
            def scatter_h_kernel(param_ptr,
                                index_ptr,
                                output_ptr,
                                N:pl.constexpr,
                                C:pl.constexpr,
                                H:pl.constexpr,
                                W:pl.constexpr,
                                param_h:pl.constexpr,
                                param_w:pl.constexpr,
                                is_param_repeated:pl.constexpr):
                pid = pl.get_core_index()
                #torch.Tensor don't support uint16
                index_ptr.set_dtype(pl.pu16_t)
                index_global = pl.gtensor([N, C, param_h, 1], pl.GLOBAL, index_ptr)
                param_global = pl.gtensor([1, C, param_h, param_w], pl.GLOBAL, param_ptr)
                shape = [N, C, H, W]
                o_global = pl.gtensor(shape, pl.GLOBAL, output_ptr)
                output = pl.make_tensor(shape, output_ptr.dtype, align_mode=pl.TPU_ROW_ALIGN)
                pl.dma.load(output, o_global)
                param = pl.dma.load(param_global, align_mode=pl.TPU_ROW_ALIGN)
                index = pl.dma.load(index_global)
                pl.tiu.scatter_h(output, param, index, is_param_repeated)
                pl.dma.store(o_global, output)
    """
    return semantic.scatter_h(output, param, index, \
                              _to_tensor(is_param_repeated, _builder), _builder)
