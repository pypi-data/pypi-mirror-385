from __future__ import annotations  # remove after python 3.11

import warnings
import os
from functools import wraps
from typing import List, Optional, Sequence, Tuple, TypeVar

from .._C.libppl.ppl import ir
from . import core as pl
from enum import Enum
T = TypeVar('T')
class Coeff_table_mode(Enum):
    EXP = 0
    LOG = 1
    SIN = 2
    COS = 3
    TAN = 4
    ARCSIN = 5
    ERF_TAYLOR = 6

class Comparision_mode(Enum):
    GREATER = 0
    LESS = 1
    EQUAL = 2
    NOT_EQUAL = 3
    GREATER_EQUAL = 4
    LESS_EQUAL = 5

class Rounding_mode(Enum):
    RM_HALF_TO_EVEN = 0,
    RM_HALF_AWAY_FROM_ZERO = 1
    RM_TOWARDS_ZERO = 2
    RM_DOWN = 3
    RM_UP = 4
    RM_HALF_UP = 5
    RM_HALF_DOWN = 6

# Create custom exception that prints message "hello"
class Arith_mode(Enum):
    ARITH_AND = 7
    ARITH_OR = 8
    ARITH_XOR = 9
    ARITH_MIN = 5
    ARITH_MAX = 4
    ARITH_ADD = 2
    ARITH_SUB = 3
    ARITH_MUL = 0
    ARITH_DIV = 12
    ARITH_DIFF_ABS = 32
    ARITH_MAC = 18

class Data_type(Enum):
    DT_NONE = 0
    DT_FP32 = 1
    DT_FP16 = 2
    DT_BF16 = 3
    DT_FP8E5M2 = 4
    DT_FP8E4M3 = 5
    DT_FP20 = 6
    DT_TF32 = 7
    DT_INT32 = 8
    DT_UINT32 = 9
    DT_INT16 = 10
    DT_UINT16 = 11
    DT_INT8 = 12
    DT_UINT8 = 13
    DT_INT4 = 14
    DT_UINT4 = 15
    DT_INT64 = 16
    DT_UINT64 = 17

def get_scalar_dtype(out_dtype: pl.dtype) -> pl.dtype:
    if out_dtype.is_block():
        return get_scalar_dtype(out_dtype.scalar)
    elif out_dtype.is_ptr():
        return get_scalar_dtype(out_dtype.element_ty)
    else:
        return out_dtype
    assert False, "Faltal error"

def get_dtype_num(out_dtype: pl.dtype) -> int:
    if out_dtype.is_block():
        return get_dtype_num(out_dtype.scalar)
    elif out_dtype.is_ptr():
        return get_dtype_num(out_dtype.element_ty)
    else:
        if out_dtype is pl.void:
            return Data_type.DT_NONE.value
        elif out_dtype.is_fp32():
            return Data_type.DT_FP32.value
        elif out_dtype.is_fp16():
            return Data_type.DT_FP16.value
        elif out_dtype.is_bf16():
            return Data_type.DT_BF16.value
        elif out_dtype.is_fp8e5():
            return Data_type.DT_FP8E5M2.value
        elif out_dtype.is_fp8e4():
            return Data_type.DT_FP8E4M3.value
        elif out_dtype.is_int4():
            return Data_type.DT_INT4.value
        elif out_dtype.is_int8():
            return Data_type.DT_INT8.value
        elif out_dtype.is_int16():
            return Data_type.DT_INT16.value
        elif out_dtype.is_int32():
            return Data_type.DT_INT32.value
        elif out_dtype.is_int64():
            return Data_type.DT_INT64.value
        elif out_dtype.is_uint4():
            return Data_type.DT_UINT4.value
        elif out_dtype.is_uint8():
            return Data_type.DT_UINT8.value
        elif out_dtype.is_uint16():
            return Data_type.DT_UINT16.value
        elif out_dtype.is_uint32():
            return Data_type.DT_UINT32.value
        elif out_dtype.is_uint64():
            return Data_type.DT_UINT64.value
        assert False, "Todo"

def get_dst_dtype(*args):
    for arg in args:
        if arg.is_block():
            return get_scalar_dtype(arg)
    assert False

def arith_op_common(out, input, other, satu, mode, num_iter, ret_ty, builder):
    if out is None:
        return pl.tensor(builder.create_fp_arith(pl._to_tensor(out, builder).handle,
                                                      input.handle, other.handle, satu.handle, mode,
                                                      pl._to_tensor(num_iter, builder).handle), ret_ty)
    else:
        return pl.tensor(builder.create_fp_arith(out.handle, input.handle, other.handle, satu.handle,
                                                 mode, pl._to_tensor(num_iter, builder).handle), pl.void)

def arithint_op_common(out, input, other, mode, unsigned_flag, shift, r_mode,
                       saturation, ret_ty, builder):
    if out is None:
        return pl.tensor(builder.create_int_arith(pl._to_tensor(out, builder).handle,
                                                      input.handle, other.handle, mode,
                                                      unsigned_flag, shift.handle, r_mode.handle,
                                                      saturation.handle), ret_ty)
    else:
        return pl.tensor(builder.create_int_arith(out.handle, input.handle, other.handle, mode,
                                                  unsigned_flag, shift.handle, r_mode.handle,
                                                  saturation.handle), pl.void)

class IncompatibleTypeErrorImpl(Exception):
    def __init__(self, type_a, type_b):
        self.type_a = type_a
        self.type_b = type_b
        self.message = "invalid operands of type " + self.type_a.__repr__() + " and " + self.type_b.__repr__()
        super(IncompatibleTypeErrorImpl, self).__init__(self.message)


# ===----------------------------------------------------------------------===##
# Programming Model
# ===----------------------------------------------------------------------===##

def get_core_index(builder: ir.builder) -> pl.tensor:
    single_core = False
    arch = os.getenv("CHIP", default="bm1684x")
    if arch == "bm1684x":
        single_core = True
    return pl.tensor(builder.create_get_core_index(single_core), pl.int32)

def get_group_index(builder: ir.builder) -> pl.tensor:
    single_group = False
    arch = os.getenv("CHIP", default="bm1684x")
    if arch == "bm1684x" or arch == "bm1688":
        single_group = True
    return pl.tensor(builder.create_get_group_index(single_group), pl.int32)

def get_block_index(builder: ir.builder) -> pl.tensor:
    single_block = False
    arch = os.getenv("CHIP", default="bm1684x")
    if arch == "bm1684x":
        single_block = True
    return pl.tensor(builder.create_get_block_index(single_block), pl.int32)

# ===----------------------------------------------------------------------===//
#                               Implicit Casting Utilities
# ===----------------------------------------------------------------------===//


def integer_promote_impl(a_ty: pl.dtype, b_ty: pl.dtype) -> pl.dtype:
    a_rank = a_ty.int_bitwidth
    b_rank = b_ty.int_bitwidth
    a_sn = a_ty.int_signedness
    b_sn = b_ty.int_signedness
    # Rules for signedness taken from "Usual arithmetic conversions" on
    # https://en.cppreference.com/w/c/language/conversion.
    if a_sn == b_sn:
        return a_ty if a_rank > b_rank else b_ty
    elif a_sn == pl.dtype.SIGNEDNESS.UNSIGNED:
        return a_ty if a_rank >= b_rank else b_ty
    elif b_sn == pl.dtype.SIGNEDNESS.UNSIGNED:
        return b_ty if b_rank >= a_rank else a_ty
    assert False


def computation_type_impl(a_ty: pl.dtype, b_ty: pl.dtype, div_or_mod: bool) -> pl.dtype:
    # 1) if one operand is double, the other is implicitly
    #    converted to double
    if a_ty.is_fp64() or b_ty.is_fp64():
        return pl.float64
    # 2) if one operand is float, the other is implicitly
    #    converted to float
    if a_ty.is_fp32() or b_ty.is_fp32():
        return pl.float32
    # 3 ) if one operand is half, the other is implicitly converted to half
    #     unless we're doing / or %, which do not exist natively in PTX for fp16.
    #     Supported PTX op: add, sub, mul, fma, neg, abs, min, max, tanh, ex2, setp
    if a_ty.is_fp16() or b_ty.is_fp16():
        if div_or_mod:
            return pl.float32
        else:
            return pl.float16
    # 4) return bf16 only if both operands are of bf16
    if a_ty.is_bf16() or b_ty.is_bf16():
        if div_or_mod:
            return pl.float32
        if a_ty.is_bf16() and b_ty.is_bf16():
            return pl.bfloat16
        return pl.float32
    if not a_ty.is_int() or not b_ty.is_int():
        assert False
    # 5 ) both operands are integer and undergo
    #    integer promotion
    if div_or_mod and a_ty.int_signedness != b_ty.int_signedness:
        raise ValueError("Cannot use /, #, or % with " + a_ty.__repr__() + " and " + b_ty.__repr__() + " because they have different signedness;"
                         "this is unlikely to result in a useful answer. Cast them to the same signedness.")
    return integer_promote_impl(a_ty, b_ty)

# ===----------------------------------------------------------------------===//
#                               Binary Operators
# ===----------------------------------------------------------------------===//


def check_ptr_type_impl(type_a: pl.dtype, type_b: pl.dtype, allow_ptr_a: bool) -> None:
    if type_a.is_ptr():
        if not allow_ptr_a:
            raise IncompatibleTypeErrorImpl(type_a, type_b)
        # T* + U* with T != U
        if type_b.is_ptr() and (type_a != type_b):
            raise IncompatibleTypeErrorImpl(type_a, type_b)
        # T* + float
        if type_b.is_floating():
            raise IncompatibleTypeErrorImpl(type_a, type_b)


def binary_op_type_checking_impl(lhs: pl.tensor,
                                 rhs: pl.tensor,
                                 builder: ir.builder,
                                 allow_lhs_ptr=False, allow_rhs_ptr=False,
                                 arithmetic_check=True, div_or_mod=False
                                 ) -> Tuple[pl.tensor, pl.tensor]:
    # implicit broadcasting
    lhs, rhs = broadcast_impl_value(lhs, rhs, builder)
    # implicit typecasting
    lhs_sca_ty = lhs.type.scalar
    rhs_sca_ty = rhs.type.scalar
    check_ptr_type_impl(lhs_sca_ty, rhs_sca_ty, allow_lhs_ptr)
    check_ptr_type_impl(rhs_sca_ty, lhs_sca_ty, allow_rhs_ptr)
    if arithmetic_check and not lhs_sca_ty.is_ptr() and not rhs_sca_ty.is_ptr():
        ret_sca_ty = computation_type_impl(lhs_sca_ty, rhs_sca_ty, div_or_mod)
        lhs = cast(lhs, ret_sca_ty, builder)
        rhs = cast(rhs, ret_sca_ty, builder)
    return lhs, rhs


def add(out,
        input: pl.tensor,
        other: pl.tensor,
        shift: pl.tensor,
        r_mode: pl.tensor,
        saturation:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_ADD.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, saturation, mode, 0, ret_ty, builder)
        elif dst_type.is_int():
            return arithint_op_common(out, input, other, mode, dst_type.is_int_unsigned(), shift,
                                     r_mode, saturation, ret_ty, builder)
        assert False
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder, True, True)
        input_scalar_ty = get_scalar_dtype(input.type)
        if input_scalar_ty.is_floating():
            return pl.tensor(builder.create_fadd(input.handle, other.handle), input.type)
        # int scalar
        elif input_scalar_ty.is_int():
            return pl.tensor(builder.create_add(input.handle, other.handle), input.type)
def sub(out,
        input: pl.tensor,
        other: pl.tensor,
        shift: pl.tensor,
        r_mode: pl.tensor,
        saturation:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_SUB.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, saturation, mode, 0, ret_ty, builder)
        elif dst_type.is_int():
            return arithint_op_common(out, input, other, saturation, mode, dst_type.is_int_unsigned(), shift,
                                     r_mode, saturation, ret_ty, builder)
        assert False
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder, True, True)
        input_scalar_ty = get_scalar_dtype(input.type)
        if input_scalar_ty.is_floating():
            return pl.tensor(builder.create_fsub(input.handle, other.handle), input.type)
        elif input_scalar_ty.is_int():
            return pl.tensor(builder.create_sub(input.handle, other.handle), input.type)

def mul(out,
        input: pl.tensor,
        other: pl.tensor,
        shift: pl.tensor,
        r_mode: pl.tensor,
        saturation: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_MUL.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, saturation, mode, 0, ret_ty, builder)
        elif dst_type.is_int():
            return arithint_op_common(out, input, other, saturation, mode, dst_type.is_int_unsigned(), shift,
                                     r_mode, saturation, ret_ty, builder)
        assert False
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder, True, True)
        input_scalar_ty = get_scalar_dtype(input.type)
        if input_scalar_ty.is_floating():
            return pl.tensor(builder.create_fmul(input.handle, other.handle), input.type)
        elif input_scalar_ty.is_int():
            return pl.tensor(builder.create_mul(input.handle, other.handle), input.type)

def mac(out:pl.tensor,
        input: pl.tensor,
        other: pl.tensor,
        lshift: pl.tensor,
        rshift: pl.tensor,
        r_mode: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        dst_type = get_dst_dtype(out.type, input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return pl.tensor(builder.create_mac(out.handle, input.handle, other.handle,
                                                lshift.handle, rshift.handle, r_mode.handle, True), ret_ty)
        elif dst_type.is_int():
            return pl.tensor(builder.create_mac(out.handle, input.handle, other.handle,
                                               lshift.handle, rshift.handle, r_mode.handle, False), ret_ty)
        assert False
    else:
        assert out is None
        #Todo: support scalar

def truediv(out,
            input: pl.tensor,
            other: pl.tensor,
            num_iter: int,
            builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_DIV.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 3, ret_ty, builder)
        assert False
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder, False, False, True, True)
        input_scalar_ty = input.type.scalar
        other_scalar_ty = other.type.scalar
        # float / int
        if input_scalar_ty.is_floating() and other_scalar_ty.is_int():
            other = cast(other, input_scalar_ty, builder)
        # int / float
        elif input_scalar_ty.is_int() and other_scalar_ty.is_floating():
            input = cast(input, other_scalar_ty, builder)
        # int / int (cast to pl.float32)
        elif input_scalar_ty.is_int() and other_scalar_ty.is_int():
            input = cast(input, pl.float32, builder)
            other = cast(other, pl.float32, builder)
        # float / float (cast to the highest exponent type)
        elif input_scalar_ty.is_floating() and other_scalar_ty.is_floating():
            if input_scalar_ty.fp_mantissa_width > other_scalar_ty.fp_mantissa_width:
                other = cast(other, input_scalar_ty, builder)
            else:
                input = cast(input, other_scalar_ty, builder)
        # unreachable
        else:
            raise TypeError(f"unexpected type {input_scalar_ty}")
        return pl.tensor(builder.create_fdiv(input.handle, other.handle), input.type)

def floordiv(input: pl.tensor,
             other: pl.tensor,
             builder: ir.builder) -> pl.tensor:
    if input.type.scalar.is_floating():
        if input.type.scalar.primitive_bitwidth == 8:
            input = cast(input, pl.int8, builder)
        elif input.type.scalar.primitive_bitwidth == 16:
            input = cast(input, pl.int16, builder)
        elif input.type.scalar.primitive_bitwidth == 32:
            input = cast(input, pl.int32, builder)
        elif input.type.scalar.primitive_bitwidth == 64:
            input = cast(input, pl.int64, builder)
        else:
            assert False
    if other.type.scalar.is_floating():
        if other.type.scalar.primitive_bitwidth == 8:
            other = cast(other, pl.int8, builder)
        elif other.type.scalar.primitive_bitwidth == 16:
            other = cast(other, pl.int16, builder)
        elif other.type.scalar.primitive_bitwidth == 32:
            other = cast(other, pl.int32, builder)
        elif other.type.scalar.primitive_bitwidth == 64:
            other = cast(other, pl.int64, builder)
        else:
            assert False
    input, other = binary_op_type_checking_impl(input, other, builder, False, False, True, True)
    input_scalar_ty = input.type.scalar
    other_scalar_ty = other.type.scalar
    if input_scalar_ty.is_int() and other_scalar_ty.is_int():
        ret_ty = integer_promote_impl(input_scalar_ty, other_scalar_ty)
        input = cast(input, ret_ty, builder)
        other = cast(other, ret_ty, builder)
        if ret_ty.is_int_signed():
            return pl.tensor(builder.create_sdiv(input.handle, other.handle), input.type)
        else:
            return pl.tensor(builder.create_udiv(input.handle, other.handle), input.type)
    assert False


def fdiv(input: pl.tensor,
         other: pl.tensor,
         ieee_rounding: bool,
         builder: ir.builder) -> pl.tensor:
    input_scalar_ty = input.type.scalar
    other_scalar_ty = other.type.scalar
    mode = Arith_mode.ARITH_DIV.value
    if not input_scalar_ty.is_floating() or not other_scalar_ty.is_floating():
        raise ValueError("both operands of fdiv must have floating scalar type")
    input, other = binary_op_type_checking_impl(input, other, builder, False, False, False, True)
    ret = builder.create_fp_arith(pl._to_tensor(None, builder).handle,
                                  input.handle, other.handle, pl._to_tensor(False, builder).handle, mode,
                                  pl._to_tensor(3, builder).handle)
    ret_ty = pl.block_type(get_scalar_dtype(input.type), [1])
    return pl.tensor(ret, ret_ty)


def mod(input: pl.tensor,
        other: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    input, other = binary_op_type_checking_impl(input, other, builder, False, False, True, True)
    scalar_ty = input.type.scalar
    other_scalar_ty = other.type.scalar
    # float % float
    if scalar_ty.is_floating():
        assert False, "don't support now"
        # input - input.div(other, rounding_mode="floor") * other
        ret = sub(None,
                input,
                mul(floor(fdiv(input, other, False, builder), builder), other, builder),
                pl._to_tensor(0, builder),
                pl._to_tensor(pl._constexpr_to_value(pl.RM_HALF_TO_EVEN).val(), builder),
                pl._to_tensor(False, builder), builder)
        return ret
    # % int
    elif scalar_ty.is_int():
        if scalar_ty.int_signedness != other_scalar_ty.int_signedness:
            raise ValueError("Cannot mod " + scalar_ty.__repr__() + " by " + other_scalar_ty.__repr__() + " "
                             "because they have different signedness;"
                             "this is unlikely to result in a useful answer. Cast them to the same signedness.")
        if scalar_ty.is_int_signed():
            return pl.tensor(builder.create_srem(input.handle, other.handle), input.type)
        else:
            return pl.tensor(builder.create_urem(input.handle, other.handle), input.type)
    assert False

##############
# bitwise ops
##############


def bitwise_op_type_checking_impl(input: pl.tensor,
                                  other: pl.tensor,
                                  builder: ir.builder) -> Tuple[pl.tensor, pl.tensor]:
    input, other = binary_op_type_checking_impl(input, other, builder, False, False, False)
    input_sca_ty = input.type.scalar
    other_sca_ty = other.type.scalar
    if not input_sca_ty.is_int() or not other_sca_ty.is_int():
        raise IncompatibleTypeErrorImpl(input_sca_ty, other_sca_ty)
    ret_sca_ty = integer_promote_impl(input_sca_ty, other_sca_ty)
    if ret_sca_ty != input_sca_ty:
        input = cast(input, ret_sca_ty, builder)
    if ret_sca_ty != other_sca_ty:
        other = cast(other, ret_sca_ty, builder)
    return input, other


def and_(out,
         input: pl.tensor,
         other: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_AND.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 0, ret_ty, builder)
    else:
        assert out is None
        input, other = bitwise_op_type_checking_impl(input, other, builder)
        return pl.tensor(builder.create_and(input.handle, other.handle), input.type)

def or_(out,
        input: pl.tensor,
        other: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_OR.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 0, ret_ty, builder)
    else:
        assert out is None
        input, other = bitwise_op_type_checking_impl(input, other, builder)
        return pl.tensor(builder.create_or(input.handle, other.handle), input.type)

def xor_(out,
         input: pl.tensor,
         other: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_XOR.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 0, ret_ty, builder)
    else:
        assert out is None
        input, other = bitwise_op_type_checking_impl(input, other, builder)
        return pl.tensor(builder.create_xor(input.handle, other.handle), input.type)

def logical_and(input: pl.tensor, other: pl.tensor, builder: ir.builder) -> pl.tensor:
    if not input.type.is_int1():
        input = bitcast(input, pl.dtype("int1"), builder)
    if not other.type.is_int1():
        other = bitcast(other, pl.dtype("int1"), builder)
    return and_(None, input, other, builder)


def logical_or(input: pl.tensor, other: pl.tensor, builder: ir.builder) -> pl.tensor:
    if not input.type.is_int1():
        input = bitcast(input, pl.dtype("int1"), builder)
    if not other.type.is_int1():
        other = bitcast(other, pl.dtype("int1"), builder)
    return or_(None, input, other, builder)


def not_(out, input: pl.tensor, builder: ir.builder):
    if not input.type.is_int1():
        input = bitcast(input, pl.dtype("int1"), builder)
    return invert(out, input, builder)


def lshr(input: pl.tensor,
         other: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    input, other = bitwise_op_type_checking_impl(input, other, builder)
    return pl.tensor(builder.create_lshr(input.handle, other.handle), input.type)


def ashr(input: pl.tensor,
         other: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    input, other = bitwise_op_type_checking_impl(input, other, builder)
    return pl.tensor(builder.create_ashr(input.handle, other.handle), input.type)


def shl(input: pl.tensor,
        other: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    input, other = bitwise_op_type_checking_impl(input, other, builder)
    return pl.tensor(builder.create_shl(input.handle, other.handle), input.type)

# ===----------------------------------------------------------------------===//
#                               Unary Operators
# ===----------------------------------------------------------------------===//


def plus(input: pl.tensor) -> pl.tensor:
    return input


def minus(out,
          input: pl.tensor,
          builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False
    input_sca_ty = get_scalar_dtype(input.type)
    ret_ty = pl.block_type(input_sca_ty, [1])
    if input.type.is_block():
        if out is None:
            return pl.tensor(builder.create_bitwise_not(pl._to_tensor(None, builder).handle,
                                                input.handle), ret_ty)
        else:
            return pl.tensor(builder.create_bitwise_not(out.handle, input.handle), pl.void)
    else:
        _0 = pl.tensor(builder.get_null_value(input_sca_ty.to_ir(builder)), input_sca_ty)
        return sub(out, _0, input, pl._to_tensor(0, builder),
                            pl._to_tensor(pl._constexpr_to_value(pl.RM_HALF_TO_EVEN).val(), builder),
                            pl._to_tensor(False, builder), builder)

def invert(out,
           input: pl.tensor,
           builder: pl.tensor) -> pl.tensor:
    input_sca_ty = input.type.scalar
    if input_sca_ty.is_ptr() or input_sca_ty.is_floating():
        raise ValueError("wrong type argument to unary invert (" + input_sca_ty.__repr__() + ")")
    _1 = pl.tensor(builder.get_all_ones_value(input_sca_ty.to_ir(builder)), input_sca_ty)
    return xor_(out, input, _1, builder)


# ===----------------------------------------------------------------------===//
#                               Comparison Operators
# ===----------------------------------------------------------------------===//
def _bool_like(v: pl.tensor) -> pl.block_type:
    if not v.type.is_block():
        return pl.int1
    shape = v.type.shape
    return pl.block_type(pl.int1, shape)

def greater_than(out,
                 input: pl.tensor,
                 other: pl.tensor,
                 true_val: pl.tensor,
                 builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Comparision_mode.GREATER.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if out is None:
            return pl.tensor(builder.create_cmp(pl._to_tensor(None, builder).handle, input.handle,
                                other.handle, mode, true_val.handle), ret_ty)
        else:
            return pl.tensor(builder.create_cmp(out.handle, input.handle,
                                other.handle, mode, true_val.handle), ret_ty)
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder)
        scalar_ty = input.type.scalar
        # float > float
        if scalar_ty.is_floating():
            return pl.tensor(builder.create_fcmpOGT(input.handle, other.handle), _bool_like(input))
        # > int
        elif scalar_ty.is_int():
            if scalar_ty.is_int_signed():
                return pl.tensor(builder.create_icmpSGT(input.handle, other.handle), _bool_like(input))
            else:
                return pl.tensor(builder.create_icmpUGT(input.handle, other.handle), _bool_like(input))
        raise TypeError(f"unexpected type {scalar_ty}")

def greater_equal(input: pl.tensor,
                  other: pl.tensor,
                  builder: ir.builder) -> pl.tensor:
    input, other = binary_op_type_checking_impl(input, other, builder)
    scalar_ty = input.type.scalar
    # float >= float
    if scalar_ty.is_floating():
        return pl.tensor(builder.create_fcmpOGE(input.handle, other.handle), _bool_like(input))
    # >= int
    elif scalar_ty.is_int():
        if scalar_ty.is_int_signed():
            return pl.tensor(builder.create_icmpSGE(input.handle, other.handle), _bool_like(input))
        else:
            return pl.tensor(builder.create_icmpUGE(input.handle, other.handle), _bool_like(input))
    assert False


def less_than(out,
              input: pl.tensor,
              other: pl.tensor,
              true_val: pl.tensor,
              builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Comparision_mode.LESS.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if out is None:
            return pl.tensor(builder.create_cmp(pl._to_tensor(None, builder).handle, input.handle,
                                other.handle, mode, true_val.handle), ret_ty)
        else:
            return pl.tensor(builder.create_cmp(out.handle, input.handle,
                                other.handle, mode, true_val.handle), ret_ty)
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder)
        scalar_ty = input.type.scalar
        # float < float
        if scalar_ty.is_floating():
            return pl.tensor(builder.create_fcmpOLT(input.handle, other.handle), _bool_like(input))
        # < int
        elif scalar_ty.is_int():
            if scalar_ty.is_int_signed():
                return pl.tensor(builder.create_icmpSLT(input.handle, other.handle), _bool_like(input))
            else:
                return pl.tensor(builder.create_icmpULT(input.handle, other.handle), _bool_like(input))
        raise TypeError(f"unexpected type {scalar_ty}")


def less_equal(input: pl.tensor,
               other: pl.tensor,
               builder: ir.builder) -> pl.tensor:
    input, other = binary_op_type_checking_impl(input, other, builder)
    scalar_ty = input.type.scalar
    # float < float
    if scalar_ty.is_floating():
        return pl.tensor(builder.create_fcmpOLE(input.handle, other.handle), _bool_like(input))
    # < int
    elif scalar_ty.is_int():
        if scalar_ty.is_int_signed():
            return pl.tensor(builder.create_icmpSLE(input.handle, other.handle), _bool_like(input))
        else:
            return pl.tensor(builder.create_icmpULE(input.handle, other.handle), _bool_like(input))
    assert False


def equal(out,
          input: pl.tensor,
          other: pl.tensor,
          true_val:pl.tensor,
          builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Comparision_mode.EQUAL.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if out is None:
            return pl.tensor(builder.create_cmp(pl._to_tensor(None, builder).handle, input.handle,
                                other.handle, mode, true_val.handle), ret_ty)
        else:
            return pl.tensor(builder.create_cmp(out.handle, input.handle,
                                other.handle, mode, true_val.handle), ret_ty)
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder)
        scalar_ty = input.type.scalar
        # float == float
        if scalar_ty.is_floating():
            return pl.tensor(builder.create_fcmpOEQ(input.handle, other.handle), _bool_like(input))
        # == int
        elif scalar_ty.is_int():
            return pl.tensor(builder.create_icmpEQ(input.handle, other.handle), _bool_like(input))
        raise TypeError(f"unexpected type {scalar_ty}")


def not_equal(input: pl.tensor,
              other: pl.tensor,
              builder: ir.builder) -> pl.tensor:
    input, other = binary_op_type_checking_impl(input, other, builder)
    scalar_ty = input.type.scalar
    # float == float
    if scalar_ty.is_floating():
        return pl.tensor(builder.create_fcmpUNE(input.handle, other.handle), _bool_like(input))
    # == int
    elif scalar_ty.is_int():
        return pl.tensor(builder.create_icmpNE(input.handle, other.handle), _bool_like(input))
    assert False

# ===----------------------------------------------------------------------===//
#                               Block Creation
# ===----------------------------------------------------------------------===//


def arange(start: int, end: int, builder: ir.builder) -> pl.tensor:
    if not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("arange's arguments must be of type pl.constexpr")
    is_start_int64 = bool(start >> 32)
    is_end_int64 = bool(end >> 32)
    if is_start_int64 or is_end_int64:
        raise ValueError("arange must fit in int32")
    if end <= start:
        raise ValueError("arange's end argument must be greater than the start argument")

    shape = [end - start]
    ret_ty = pl.block_type(pl.int32, shape)
    return pl.tensor(builder.create_make_range(start, end), ret_ty)


def fill(input: pl.tensor, value, dtype: pl.dtype, tiu: bool, builder: ir.builder) -> pl.tensor:
    if tiu:
        if isinstance(value, pl.tensor):
            assert value.numel.value == 1, "only accepts size-1 tensor"
            value = cast(value, dtype, builder)
            #ret_ty = pl.block_type(value.dtype, shape)
            return pl.tensor(builder.create_fill(input.handle, value.handle), pl.void)
        else:
            # scalar
            if value == 0:
                value = builder.get_null_value(dtype.to_ir(builder))
            else:
                get_value_fn = getattr(builder, f"get_{dtype.name}")
                value = get_value_fn(value)
            if dtype is None:
                raise ValueError("dtype must be specified when value is not a tensor")
            #ret_ty = pl.block_type(dtype, shape)
            return pl.tensor(builder.create_fill(input.handle, value), pl.void)
    else:
        return pl.tensor(builder.create_dma_fill(input.handle,
                                   pl._to_tensor(value, builder).handle), pl.void)


# ===----------------------------------------------------------------------===//
#                               Shape Manipulation
# ===----------------------------------------------------------------------===//


def view(input: pl.tensor,
         shape,
         stride,
         dtype,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(input.type.scalar, [1])
    if shape is None:
        shape = [builder.get_null_value(pl.int8.to_ir(builder))]
    else:
        shape = _convert_to_ir_values(builder, shape, require_i64=False)
    if stride is None:
        stride = [builder.get_null_value(pl.int8.to_ir(builder))]
    else:
        stride = _convert_to_ir_values(builder, stride, require_i64=False)

    return pl.tensor(builder.create_view(input.handle, shape, stride,
                     pl.void.to_ir(builder) if dtype is None else dtype.to_ir(builder),
                     get_scalar_dtype(input.type).is_int_unsigned()),
                      ret_ty if dtype is None else pl.block_type(dtype, [1]))

def reshape(input: pl.tensor,
            dst_shape: List[int],
            builder: ir.builder) -> pl.tensor:
    raise ValueError("`reshape` is not supported yet. Please use `view` instead if applicable. "
                     "Note that view may reorder elements in an implementation- and context- dependent way.")


def expand_dims(input: pl.tensor, axis: int, builder: ir.builder) -> pl.tensor:
    dst_shape = list(input.type.shape)
    dst_shape.insert(axis, 1)
    ret_ty = pl.block_type(input.type.scalar, dst_shape)
    return pl.tensor(builder.create_expand_dims(input.handle, axis), ret_ty)


def cat(lhs: pl.tensor, rhs: pl.tensor, can_reorder: bool, builder: ir.builder) -> pl.tensor:
    assert can_reorder, "current implementation of `cat` always may reorder elements"
    assert len(lhs.shape) == 1
    ret_type = pl.block_type(lhs.type.scalar, [lhs.shape[0] + rhs.shape[0]])
    return pl.tensor(builder.create_cat(lhs.handle, rhs.handle), ret_type)


def trans(input: pl.tensor, builder: ir.builder) -> pl.tensor:
    if len(input.shape) != 2:
        raise ValueError("Only 2D tensors can be transposed")
    ret_type = pl.block_type(input.type.scalar, [input.shape[1], input.shape[0]])
    return pl.tensor(builder.create_trans(input.handle), ret_type)


def broadcast_impl_shape(input: pl.tensor,
                         shape: List[int],
                         builder: ir.builder) -> pl.tensor:
    if not input.type.is_block():
        ret_ty = pl.block_type(input.type, shape)
        return pl.tensor(builder.create_splat(input.handle, shape), ret_ty)
    src_shape = input.type.get_block_shapes()
    if len(src_shape) != len(shape):
        raise ValueError(f"Cannot broadcast, rank mismatch: {src_shape}, {shape}")
    if shape == src_shape:
        return input
    for i, item in enumerate(src_shape):
        if shape[i] != item and item != 1:
            raise ValueError(f"Cannot broadcast, the expanded size of the tensor ({shape[i]})"
                             f" must match the existing size ({item}) at non-singleton dimension"
                             f" {i}: {src_shape}, {shape}")
    ret_ty = pl.block_type(input.type.scalar, shape)
    return pl.tensor(builder.create_broadcast(input.handle, shape), ret_ty)


def broadcast_impl_value(lhs: pl.tensor,
                         rhs: pl.tensor,
                         builder: ir.builder) -> pl.tensor:
    lhs_ty = lhs.type
    rhs_ty = rhs.type

    # make_shape_compatible(block, scalar)
    if lhs_ty.is_block() and not rhs_ty.is_block():
        rhs_ty = pl.block_type(rhs_ty.scalar, lhs_ty.shape)
        rhs = pl.tensor(builder.create_splat(rhs.handle, lhs_ty.get_block_shapes()), rhs_ty)
    # make_shape_compatible(scalar, block)
    elif not lhs_ty.is_block() and rhs_ty.is_block():
        lhs_ty = pl.block_type(lhs_ty.scalar, rhs_ty.shape)
        lhs = pl.tensor(builder.create_splat(lhs.handle, rhs_ty.get_block_shapes()), lhs_ty)
    # make_shape_compatible(block, block)
    elif lhs_ty.is_block() and rhs_ty.is_block():
        lhs_shape = lhs_ty.get_block_shapes()
        rhs_shape = rhs_ty.get_block_shapes()

        if len(lhs_shape) < len(rhs_shape):
            # Add new axes to lhs
            for dim in range(len(lhs_shape), len(rhs_shape)):
                lhs = pl.tensor(builder.create_expand_dims(lhs.handle, 0), pl.block_type(lhs_ty.scalar, [1] + lhs_shape))
                lhs_ty = lhs.type
                lhs_shape = lhs_ty.get_block_shapes()
        elif len(rhs_shape) < len(lhs_shape):
            # Add new axes to rhs
            for dim in range(len(rhs_shape), len(lhs_shape)):
                rhs = pl.tensor(builder.create_expand_dims(rhs.handle, 0), pl.block_type(rhs_ty.scalar, [1] + rhs_shape))
                rhs_ty = rhs.type
                rhs_shape = rhs_ty.get_block_shapes()
        assert len(rhs_shape) == len(lhs_shape)

        ret_shape = []
        for i, left in enumerate(lhs_shape):
            right = rhs_shape[i]
            if left == 1:
                ret_shape.append(right)
            elif right == 1:
                ret_shape.append(left)
            elif left == right:
                ret_shape.append(left)
            else:
                raise ValueError("Cannot make_shape_compatible: incompatible dimensions "
                                 "at index " + str(i) + ": " + str(left) + " and " + str(right))
        if lhs_shape != ret_shape:
            ret_ty = pl.block_type(lhs_ty.scalar, ret_shape)
            lhs = pl.tensor(builder.create_broadcast(lhs.handle, ret_shape), ret_ty)
        if rhs_shape != ret_shape:
            ret_ty = pl.block_type(rhs_ty.scalar, ret_shape)
            rhs = pl.tensor(builder.create_broadcast(rhs.handle, ret_shape), ret_ty)
    # (scalar, scalar) => returns original blocks
    return lhs, rhs

#######
# cast
#######


def bitcast(input: pl.tensor,
            dst_ty: pl.dtype,
            builder: ir.builder) -> pl.tensor:
    src_ty = input.type
    if src_ty.is_block():
        dst_ty = pl.block_type(dst_ty.scalar, input.type.get_block_shapes())
    if src_ty == dst_ty:
        return input
    src_sca_ty = src_ty.scalar
    dst_sca_ty = dst_ty.scalar
    if src_sca_ty.is_ptr() or dst_sca_ty.is_ptr():
        return cast(input, dst_ty, builder)
    # Bitcast
    src_bits = src_sca_ty.primitive_bitwidth
    dst_bits = dst_sca_ty.primitive_bitwidth
    if src_bits != dst_bits:
        raise ValueError("Cannot bitcast data-type of size " + str(src_bits) + " to "
                         "data-type of size " + str(dst_bits))
    return pl.tensor(builder.create_bitcast(input.handle, dst_ty.to_ir(builder)),
                     dst_ty)

def cast(input: pl.tensor,
         dst_ty: pl.dtype,
         builder: ir.builder) -> pl.tensor:
    src_ty = input.type
    if isinstance(dst_ty, pl.constexpr):
        dst_ty = dst_ty.value
    if src_ty.is_block():
        dst_ty = pl.block_type(dst_ty.scalar, input.type.get_block_shapes())
    if src_ty == dst_ty:
        return input

    src_sca_ty = get_scalar_dtype(src_ty)
    dst_sca_ty = get_scalar_dtype(dst_ty)
    if src_ty.is_block():
        ret_ty = pl.block_type(get_scalar_dtype(dst_ty), [1])
        return pl.tensor(builder.create_cast(input.handle, pl.block_type(dst_sca_ty, [1]).to_ir(builder),
                                             dst_sca_ty.is_int_unsigned()), ret_ty)
    else:
        # Casting with customized floating types involved: fp8 <=> bf16, fp16, fp32, fp64
        if (src_sca_ty.is_fp8() and dst_sca_ty.is_floating()) or \
        (src_sca_ty.is_floating() and dst_sca_ty.is_fp8()):
            return pl.tensor(builder.create_fp_to_fp(input.handle, dst_ty.to_ir(builder)),
                            dst_ty)

        # bf16 <=> (not fp32)
        if (src_sca_ty.is_fp16() and not dst_sca_ty.is_fp32()) or \
        (src_sca_ty.is_bf16() and not dst_sca_ty.is_fp32()):
            return cast(cast(input, pl.float32, builder), dst_sca_ty, builder)

        # Standard floating types' casting: truncation
        #   fp64 => fp32, fp16, bf16
        #   fp32 => fp16, bf16
        truncate_fp = src_sca_ty.is_floating() and \
            dst_sca_ty.is_floating() and \
            src_sca_ty.primitive_bitwidth > dst_sca_ty.primitive_bitwidth
        if truncate_fp:
            return pl.tensor(builder.create_fp_trunc(input.handle,
                                                    dst_ty.to_ir(builder)),
                            dst_ty)

        # Standard floating types' casting: extension
        #   fp32 => fp64
        #   fp16 => fp32, fp64
        #   bf16 => fp32, fp64
        ext_fp = src_sca_ty.is_floating() and \
            dst_sca_ty.is_floating() and \
            src_sca_ty.primitive_bitwidth < dst_sca_ty.primitive_bitwidth
        if ext_fp:
            return pl.tensor(builder.create_fp_ext(input.handle,
                                                dst_ty.to_ir(builder)),
                            dst_ty)

        # Casting between integer types
        if src_sca_ty.is_int() and dst_sca_ty.is_int() and \
        (src_sca_ty.int_bitwidth != dst_sca_ty.int_bitwidth or src_sca_ty.int_signedness != dst_sca_ty.int_signedness):
            sign_extend = src_sca_ty.is_int_signed() and not src_sca_ty.is_bool()
            if dst_sca_ty.is_bool():
                ty = input.dtype.to_ir(builder)
                _0 = pl.tensor(builder.get_null_value(ty), input.dtype)
                return not_equal(input, _0, builder)
            else:
                dstUnsiged = False
                dst_ty_ = dst_ty
                if src_sca_ty.is_int_signed() and dst_sca_ty.is_int_unsigned():
                    dstUnsiged = True
                    if dst_sca_ty.is_uint4():
                        dst_ty_ = pl.int4
                    elif dst_sca_ty.is_uint8():
                        dst_ty_ = pl.int8
                    elif dst_sca_ty.is_uint16():
                        dst_ty_ = pl.int16
                    elif dst_sca_ty.is_uint32():
                        dst_ty_= pl.int32
                    else:
                        dst_ty_ = pl.int64
                return pl.tensor(builder.create_int_cast(input.handle,
                                                    dst_ty_.to_ir(builder), sign_extend, dstUnsiged),
                                    dst_ty_)

        # Casting standard floating types to integer types
        if src_sca_ty.is_standard_floating() and dst_sca_ty.is_int():
            if dst_sca_ty.is_bool():
                ty = input.dtype.to_ir(builder)
                _0 = pl.tensor(builder.get_null_value(ty), input.dtype)
                return not_equal(input, _0, builder)
            elif dst_sca_ty.is_int_signed():
                return pl.tensor(builder.create_fp_to_si(input.handle,
                                                        dst_ty.to_ir(builder)),
                                dst_ty)
            else:
                return pl.tensor(builder.create_fp_to_ui(input.handle,
                                                        dst_ty.to_ir(builder)),
                                dst_ty)

        # Casting integer types to standard floating types
        if src_sca_ty.is_int() and dst_sca_ty.is_standard_floating():
            if src_sca_ty.is_bool() or not src_sca_ty.is_int_signed():
                return pl.tensor(builder.create_ui_to_fp(input.handle,
                                                        dst_ty.to_ir(builder)),
                                dst_ty)
            else:
                return pl.tensor(builder.create_si_to_fp(input.handle,
                                                        dst_ty.to_ir(builder)),
                                dst_ty)

        # Casting pointer types to integer types
        if src_sca_ty.is_ptr() and dst_sca_ty.is_int():
            bitwidth = dst_sca_ty.int_bitwidth
            if bitwidth == 64:
                return pl.tensor(builder.create_ptr_to_int(input.handle, dst_ty.to_ir(builder)),
                                dst_ty)
            if bitwidth == 1:
                return not_equal(cast(input, pl.int64, builder),
                                pl.tensor(builder.get_int64(0), pl.int64),
                                builder)

        # Casting integer types to pointer types
        if src_sca_ty.is_int() and dst_sca_ty.is_ptr():
            return pl.tensor(builder.create_int_to_ptr(input.handle, dst_ty.to_ir(builder)), dst_ty)

        # Casting pointer types to pointer types
        if src_sca_ty.is_ptr() and dst_sca_ty.is_ptr():
            return pl.tensor(builder.create_bitcast(input.handle, dst_ty.to_ir(builder)), dst_ty)

        assert False, f'cannot cast {input} to {dst_ty}'

def cast_v2(dst: pl.tensor,
            input: pl.tensor,
            dst_ty: pl.dtype,
            round_mode: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if dst_ty is pl.void:
        dst_ty = get_scalar_dtype(dst.type)
    return pl.tensor(builder.create_cast_v2(dst.handle, input.handle, dst_ty.to_ir(builder), round_mode.handle),
                         pl.block_type(dst_ty, [1]))
# ===----------------------------------------------------------------------===//
#                               Memory Operators
# ===----------------------------------------------------------------------===//


def _str_to_load_cache_modifier(cache_modifier):
    cache = ir.CACHE_MODIFIER.NONE  # default
    if cache_modifier:
        if cache_modifier == ".ca":
            cache = ir.CACHE_MODIFIER.CA
        elif cache_modifier == ".cg":
            cache = ir.CACHE_MODIFIER.CG
        else:
            raise ValueError(f"Cache modifier {cache_modifier} not supported")
    return cache


def _str_to_store_cache_modifier(cache_modifier):
    cache = ir.CACHE_MODIFIER.NONE  # default
    if cache_modifier:
        if cache_modifier == ".wb":
            cache = ir.CACHE_MODIFIER.WB
        elif cache_modifier == ".cg":
            cache = ir.CACHE_MODIFIER.CG
        elif cache_modifier == ".cs":
            cache = ir.CACHE_MODIFIER.CS
        elif cache_modifier == ".wt":
            cache = ir.CACHE_MODIFIER.WT
        else:
            raise ValueError(f"Cache modifier {cache_modifier} not supported")
    return cache


def _str_to_eviction_policy(eviction_policy):
    eviction = ir.EVICTION_POLICY.NORMAL  # default
    if eviction_policy:
        if eviction_policy == "evict_last":
            eviction = ir.EVICTION_POLICY.EVICT_LAST
        elif eviction_policy == "evict_first":
            eviction = ir.EVICTION_POLICY.EVICT_FIRST
        else:
            raise ValueError(f"Eviction policy {eviction_policy} not supported")
    return eviction


def _str_to_padding_option(padding_option):
    padding = None  # default
    if padding_option:
        if padding_option == "zero":
            padding = ir.PADDING_OPTION.PAD_ZERO
        elif padding_option == "nan":
            padding = ir.PADDING_OPTION.PAD_NAN
        else:
            raise ValueError(f"Padding option {padding_option} not supported")
    return padding


def _str_to_sem(sem_option):
    sem = ir.MEM_SEMANTIC.ACQUIRE_RELEASE
    if sem_option:
        if sem_option == "acquire":
            sem = ir.MEM_SEMANTIC.ACQUIRE
        elif sem_option == "release":
            sem = ir.MEM_SEMANTIC.RELEASE
        elif sem_option == "acq_rel":
            sem = ir.MEM_SEMANTIC.ACQUIRE_RELEASE
        elif sem_option == "relaxed":
            sem = ir.MEM_SEMANTIC.RELAXED
        else:
            raise ValueError(f"Memory semantic {sem_option} not supported")
    return sem


def _canonicalize_boundary_check(boundary_check, block_shape):
    if boundary_check:
        if not hasattr(boundary_check, "__iter__"):
            boundary_check = [boundary_check]
        boundary_check = [elem.value if isinstance(elem, pl.constexpr) else elem for elem in boundary_check]
        for dim in boundary_check:
            assert isinstance(dim, int) and 0 <= dim < len(block_shape)
        assert len(boundary_check) > 0
        assert len(boundary_check) == len(set(boundary_check)), "Duplicate dimension in `boundary_check`"
        return sorted(boundary_check)
    return tuple()


def _load_block_pointer(ptr, mask, other, boundary_check, padding, cache, eviction, is_volatile, builder):
    # Load by a block pointer: `pointer_type<block_type<>>`
    # Block pointer can not have `mask` and `other` arguments
    if mask or other:
        raise ValueError("`mask` and `other` arguments cannot be specified for loading block pointers")

    elt_ty = ptr.type.element_ty.element_ty
    assert elt_ty != pl.int1, "`pl.int1` should be rewrited in `pl.make_block_ptr`"
    if elt_ty.is_int() and padding == ir.PADDING_OPTION.PAD_NAN:
        raise ValueError("Padding option `nan` is not supported for integer block pointers")

    # `dst_ty` is de-referenced type of the pointer type
    dst_ty = ptr.type.element_ty

    # Check `boundary_check` argument
    boundary_check = _canonicalize_boundary_check(boundary_check, dst_ty.get_block_shapes())

    # Build IR
    return pl.tensor(builder.create_tensor_pointer_load(ptr.handle, boundary_check, padding, cache, eviction,
                                                        is_volatile), dst_ty)


def _load_legacy(ptr, mask, other, boundary_check, padding, cache, eviction, is_volatile, builder):
    # Load by a tensor of pointers or a pointer of scalar: `block_type<pointer_type<>>` or `pointer_type<>`
    if not ptr.type.scalar.is_ptr():
        raise ValueError(f"Unsupported ptr type {ptr.type.__repr__()} in `pl.load`")

    # Check `mask`, `other`, `boundary_check`, and `padding` arguments
    if not mask and other:
        raise ValueError("`other` cannot be provided without `mask`")
    if padding or boundary_check:
        raise ValueError("`padding_option` or `boundary_check` argument is not supported for loading a tensor of"
                         "pointers or loading a scalar. Because the compiler does not know the boundary; please "
                         "use block pointers (defined by `make_block_ptr`) instead")

    # For a pointer of scalar, check the type of `mask` and `other`
    if not ptr.type.is_block():
        if mask and mask.type.is_block():
            raise ValueError("Mask argument cannot be block type if pointer argument is not a block")
        if other and other.type.is_block():
            raise ValueError("Other argument cannot be block type if pointer argument is not a block")

    # Make `mask` and `other` into the same shape as `ptr`
    if ptr.type.is_block():
        if mask:
            mask = broadcast_impl_shape(mask, ptr.type.get_block_shapes(), builder)
        if other:
            other = broadcast_impl_shape(other, ptr.type.get_block_shapes(), builder)

    # Get `pointer_type<elt_ty>` and `elt_ty`
    ptr_ty = ptr.type.scalar
    elt_ty = ptr_ty.element_ty

    # Treat `pointer_type<pl.int1>` as `pointer_type<pl.int8>`
    if elt_ty == pl.int1:
        elt_ty = pl.int8
        ptr_ty = pl.pointer_type(elt_ty, ptr_ty.address_space)
        ptr = cast(ptr, ptr_ty, builder)

    # Cast `other` into `ele_ty` type
    if other:
        other = cast(other, elt_ty, builder)

    # Create loaded result type `dst_ty`
    if ptr.type.is_block():
        shape = ptr.type.get_block_shapes()
        dst_ty = pl.block_type(elt_ty, shape)
    else:
        # Load by de-referencing the pointer of scalar
        dst_ty = elt_ty

    # Build IR
    if not mask:
        return pl.tensor(builder.create_load(ptr.handle, cache, eviction, is_volatile), dst_ty)
    else:
        return pl.tensor(builder.create_masked_load(ptr.handle, mask.handle, other.handle if other else None, cache,
                                                    eviction, is_volatile), dst_ty)
def load(dest,
         ptr: pl.tensor,
         align_mode:int,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(ptr.type), [1])
    unsigned = get_scalar_dtype(ptr.type).is_int_unsigned()
    if dest is None:
        return pl.tensor(builder.create_load(pl._to_tensor(None, builder).handle, ptr.handle, align_mode,
                         get_scalar_dtype(ptr.type).is_int(), unsigned), ret_ty)
    else:
        return pl.tensor(builder.create_load(dest.handle, ptr.handle, align_mode,
                         get_scalar_dtype(ptr.type).is_int(), unsigned), pl.void)

def _store_block_pointer(ptr, val, mask, boundary_check, cache, eviction, builder):
    # Store by a block pointer: `pointer_type<block_type<>>`
    # Block pointers can not have the `mask` argument
    if mask:
        raise ValueError("`mask` and `other` arguments cannot be specified for loading block pointers")

    # Check same shape and element type
    block_shape = ptr.type.element_ty.get_block_shapes()
    if not val.type.is_block():
        val = broadcast_impl_shape(val, block_shape, builder)
    assert val.type.is_block(), "Value argument must be block type or a scalar"
    assert block_shape == val.type.get_block_shapes(), "Block shape and value shape mismatch"
    assert ptr.type.element_ty.element_ty == val.type.element_ty, "Block element type and value element type mismatch"

    elt_ty = ptr.type.element_ty.element_ty
    assert elt_ty != pl.int1, "`pl.int1` should be rewrited in `pl.make_block_ptr`"

    # Check `boundary_check` argument
    boundary_check = _canonicalize_boundary_check(boundary_check, block_shape)

    # Build IR
    return pl.tensor(builder.create_tensor_pointer_store(ptr.handle, val.handle, boundary_check, cache, eviction),
                     pl.void)


def _store_legacy(ptr, val, mask, boundary_check, cache, eviction, builder):
    # Store by a tensor of pointers or a pointer of scalar: `block_type<pointer_type<>>` or `pointer_type<>`
    if not ptr.type.scalar.is_ptr():
        raise ValueError(f"Unsupported ptr type {ptr.type.__repr__()} in `pl.store`")

    # Check `boundary_check` argument
    if boundary_check:
        raise ValueError("`boundary_check` argument is not supported for storing a tensor of pointers or storing a "
                         "scalar. Because the compiler does not know the boundary; please use block pointers "
                         "(defined by `make_block_ptr`) instead")

    # For a pointer of scalar, check the type of `val` and `mask`
    if not ptr.type.is_block():
        if val.type.is_block():
            raise ValueError("Value argument cannot be block type if pointer argument is not a block")
        if mask and mask.type.is_block():
            raise ValueError("Mask argument cannot be block type if pointer argument is not a block")

    # Make `mask` and `val` into the same shape as `ptr`
    if ptr.type.is_block():
        val = broadcast_impl_shape(val, ptr.type.get_block_shapes(), builder)
        if mask:
            mask = broadcast_impl_shape(mask, ptr.type.get_block_shapes(), builder)

    ptr_ty = ptr.type.scalar
    elt_ty = ptr_ty.element_ty

    # Treat `pointer_type<pl.int1>` as `pointer_type<pl.int8>`
    if elt_ty == pl.int1:
        elt_ty = pl.int8
        ptr_ty = pl.pointer_type(elt_ty, ptr_ty.address_space)
        ptr = cast(ptr, ptr_ty, builder)

    # Cast to target data type
    val = cast(val, elt_ty, builder)

    # Build IR
    if not mask:
        return pl.tensor(builder.create_store(ptr.handle, val.handle, cache, eviction), pl.void)
    if not mask.type.scalar.is_bool():
        raise ValueError("Mask must have boolean scalar type")
    return pl.tensor(builder.create_masked_store(ptr.handle, val.handle, mask.handle, cache, eviction), pl.void)


def store(ptr: pl.tensor,
          val: pl.tensor,
          builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_store(ptr.handle, val.handle), pl.void)


#########
# atomic
#########


def atomic_cas(ptr: pl.tensor,
               cmp: pl.tensor,
               val: pl.tensor,
               sem: str,
               builder: ir.builder) -> pl.tensor:
    sem = _str_to_sem(sem)
    element_ty = ptr.type.scalar.element_ty
    if element_ty.primitive_bitwidth not in [16, 32, 64]:
        raise ValueError("atomic_cas only supports elements with width {16, 32, 64}")
    return pl.tensor(builder.create_atomic_cas(ptr.handle, cmp.handle, val.handle, sem), val.type)


def atom_red_typechecking_impl(ptr: pl.tensor,
                               val: pl.tensor,
                               mask: pl.tensor,
                               op: str,
                               builder: ir.builder) -> Tuple[pl.tensor, pl.tensor, pl.tensor]:
    if not ptr.type.scalar.is_ptr():
        raise ValueError("Pointer argument of store instruction is " + ptr.type.__repr__())
    element_ty = ptr.type.scalar.element_ty
    if element_ty is pl.float16 and op != 'add':
        raise ValueError("atomic_" + op + " does not support fp16")
    if element_ty in [pl.int1, pl.int4, pl.int8, pl.int16, pl.bfloat16]:
        raise ValueError("atomic_" + op + " does not support " + str(element_ty))
    if ptr.type.is_block():
        if mask:
            mask = broadcast_impl_shape(mask, ptr.type.get_block_shapes(), builder)
        if val:
            val = broadcast_impl_shape(val, ptr.type.get_block_shapes(), builder)
    val = cast(val, ptr.type.scalar.element_ty, builder)
    if not mask:
        mask_ir = builder.get_int1(True)
        mask_ty = pl.int1
        if ptr.type.is_block():
            mask_ir = builder.create_splat(mask_ir, ptr.type.get_block_shapes())
            mask_ty = pl.block_type(pl.int1, ptr.type.get_block_shapes())
        mask = pl.tensor(mask_ir, mask_ty)
    return ptr, val, mask


def atomic_max(ptr: pl.tensor,
               val: pl.tensor,
               mask: pl.tensor,
               sem: str,
               builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'max', builder)
    sem = _str_to_sem(sem)
    sca_ty = val.type.scalar
    # direct call to atomic_max for integers
    if sca_ty.is_int():
        if sca_ty.is_int_signed():
            return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.MAX,
                                                       ptr.handle,
                                                       val.handle,
                                                       mask.handle,
                                                       sem),
                             val.type)
        else:
            return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.UMAX,
                                                       ptr.handle,
                                                       val.handle,
                                                       mask.handle,
                                                       sem),
                             val.type)
    # for float
    # return atomic_smax(i_ptr, i_val) if val >= 0
    # return atomic_umin(i_ptr, i_val) if val < 0
    i_val = bitcast(val, pl.int32, builder)
    i_ptr = bitcast(ptr, pl.pointer_type(pl.int32, 1), builder)
    pos = greater_equal(val, pl.tensor(builder.get_fp32(0), sca_ty), builder)
    neg = less_than(val, pl.tensor(builder.get_fp32(0), sca_ty), builder)
    pos_ret = pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.MAX, i_ptr.handle, i_val.handle, and_(mask, pos, builder).handle, sem), i_val.type)
    neg_ret = pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.UMIN, i_ptr.handle, i_val.handle, and_(mask, neg, builder).handle, sem), i_val.type)
    return where(pos, pos_ret, neg_ret, builder)


def atomic_min(ptr: pl.tensor,
               val: pl.tensor,
               mask: pl.tensor,
               sem: str,
               builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'min', builder)
    sem = _str_to_sem(sem)
    sca_ty = val.type.scalar
    # direct call to atomic_min for integers
    if sca_ty.is_int():
        if sca_ty.is_int_signed():
            return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.MIN,
                                                       ptr.handle,
                                                       val.handle,
                                                       mask.handle,
                                                       sem),
                             val.type)
        else:
            return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.UMIN,
                                                       ptr.handle,
                                                       val.handle,
                                                       mask.handle,
                                                       sem),
                             val.type)
    # for float
    # return atomic_smin(i_ptr, i_val) if val >= 0
    # return atomic_umax(i_ptr, i_val) if val < 0
    i_val = bitcast(val, pl.int32, builder)
    i_ptr = bitcast(ptr, pl.pointer_type(pl.int32, 1), builder)
    pos = greater_equal(val, pl.tensor(builder.get_fp32(0), sca_ty), builder)
    neg = less_than(val, pl.tensor(builder.get_fp32(0), sca_ty), builder)
    pos_ret = pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.MIN,
                                                  i_ptr.handle,
                                                  i_val.handle,
                                                  and_(mask, pos, builder).handle,
                                                  sem),
                        i_val.type)
    neg_ret = pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.UMAX,
                                                  i_ptr.handle,
                                                  i_val.handle,
                                                  and_(mask, neg, builder).handle,
                                                  sem),
                        i_val.type)
    return where(pos, pos_ret, neg_ret, builder)


def atomic_add(ptr: pl.tensor,
               val: pl.tensor,
               mask: pl.tensor,
               sem: str,
               builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'add', builder)
    sem = _str_to_sem(sem)
    sca_ty = val.type.scalar
    op = ir.ATOMIC_OP.FADD if sca_ty.is_floating() else ir.ATOMIC_OP.ADD
    return pl.tensor(builder.create_atomic_rmw(op, ptr.handle, val.handle, mask.handle, sem), val.type)


def atomic_and(ptr: pl.tensor,
               val: pl.tensor,
               mask: pl.tensor,
               sem: str,
               builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'and', builder)
    sem = _str_to_sem(sem)
    return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.AND, ptr.handle, val.handle, mask.handle, sem), val.type)


def atomic_or(ptr: pl.tensor,
              val: pl.tensor,
              mask: pl.tensor,
              sem: str,
              builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'or', builder)
    sem = _str_to_sem(sem)
    return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.OR, ptr.handle, val.handle, mask.handle, sem), val.type)


def atomic_xor(ptr: pl.tensor,
               val: pl.tensor,
               mask: pl.tensor,
               sem: str,
               builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'xor', builder)
    sem = _str_to_sem(sem)
    return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.XOR, ptr.handle, val.handle, mask.handle, sem), val.type)


def atomic_xchg(ptr: pl.tensor,
                val: pl.tensor,
                mask: pl.tensor,
                sem: str,
                builder: ir.builder) -> pl.tensor:
    ptr, val, mask = atom_red_typechecking_impl(ptr, val, mask, 'xchg', builder)
    sem = _str_to_sem(sem)
    return pl.tensor(builder.create_atomic_rmw(ir.ATOMIC_OP.XCHG, ptr.handle, val.handle, mask.handle, sem), val.type)

# ===----------------------------------------------------------------------===//
#                               Linear Algebra
# ===----------------------------------------------------------------------===//
def dot(output: pl.tensor,
        lhs: pl.tensor,
        rhs: pl.tensor,
        bias:pl.tensor,
        ltrans:pl.tensor,
        rtrans:pl.tensor,
        rst_trans:pl.tensor,
        do_relu:pl.tensor,
        result_add: pl.tensor,
        out_dtype: pl.tensor,
        has_bias:pl.tensor,
        saturate: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    assert lhs.type.is_block() and rhs.type.is_block()
    assert lhs.dtype == rhs.dtype, f"First input ({lhs.dtype}) and second input ({rhs.dtype}) must have the same dtype!"
    return pl.tensor(builder.create_dot(output.handle, lhs.handle, rhs.handle,
                     bias.handle, ltrans.handle, rtrans.handle, rst_trans.handle, do_relu.handle,
                     result_add.handle, out_dtype.handle, has_bias.handle, saturate.handle),
                     pl.void)


def mm2_int8(output: pl.tensor, lhs: pl.tensor, rhs: pl.tensor,
             bias: pl.tensor, r_zp: pl.tensor, requant: pl.tensor,
             multiplier: pl.tensor, rshift: pl.tensor, y_zp: pl.tensor,
             ltrans: pl.tensor, rtrans: pl.tensor, rst_trans: pl.tensor,
             result_add: pl.tensor, out_dtype: pl.tensor, has_bias: pl.tensor,
             do_relu: pl.tensor, do_rq: pl.tensor, saturate: pl.tensor,
             round_mode: pl.tensor, builder: ir.builder) -> pl.tensor:
    assert lhs.type.is_block() and rhs.type.is_block()
    return pl.tensor(
        builder.create_mm2_int8(output.handle, lhs.handle, rhs.handle,
                                bias.handle, r_zp.handle, requant.handle,
                                multiplier.handle, rshift.handle, y_zp.handle,
                                ltrans.handle, rtrans.handle, rst_trans.handle,
                                result_add.handle, out_dtype.handle,
                                has_bias.handle, do_relu.handle, do_rq.handle,
                                saturate.handle, round_mode.handle), pl.void)

def mm(output: pl.tensor,
            lhs: pl.tensor,
            rhs: pl.tensor,
            bias:pl.tensor,
            ltrans:pl.tensor,
            rtrans:pl.tensor,
            result_add:pl.tensor,
            lshift:pl.tensor,
            rshift:pl.tensor,
            do_relu:pl.tensor,
            round_mode:pl.tensor,
            builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_mm(output.handle, lhs.handle, rhs.handle,
                     bias.handle, ltrans.handle, rtrans.handle, result_add.handle,
                     lshift.handle, rshift.handle, do_relu.handle, round_mode.handle),
                     pl.void)
# ===----------------------------------------------------------------------===//
#                               Indexing
# ===----------------------------------------------------------------------===//

def where(condition: pl.tensor,
          x: pl.tensor,
          y: pl.tensor,
          builder: ir.builder) -> pl.tensor:
    condition = cast(condition, pl.int1, builder)
    if condition.type.is_block():
        condition, x = broadcast_impl_value(condition, x, builder)
        x, y = broadcast_impl_value(x, y, builder)
        condition, x = broadcast_impl_value(condition, x, builder)

    x, y = binary_op_type_checking_impl(x, y, builder, True, True)
    if not condition.type.is_block():
        condition, _ = broadcast_impl_value(condition, x, builder)
    ret_ty = x.type
    return pl.tensor(builder.create_select(condition.handle, x.handle, y.handle), ret_ty)

# ===----------------------------------------------------------------------===//
#                               Reduction
# ===----------------------------------------------------------------------===


def reduction(
    inputs: Sequence[pl.tensor], axis: int, region_builder_fn, builder: ir.builder
) -> Tuple[pl.tensor, ...]:
    if axis is None:
        new_inputs = []
        for i in range(len(inputs)):
            new_shape = [inputs[i].numel.value]
            new_inputs.append(view(inputs[i], new_shape, builder))
        inputs = tuple(new_inputs)
        axis = 0
    # get result shape
    shape = inputs[0].type.shape
    ret_shape = [s for i, s in enumerate(shape) if i != axis]
    for t in inputs:
        assert t.type.shape == shape

    def wrap_tensor(x, scalar_ty):
        if ret_shape:
            res_ty = pl.block_type(scalar_ty, ret_shape)
        else:
            # 0d-tensor -> scalar
            res_ty = scalar_ty
        return pl.tensor(x, res_ty)

    reduce_op = builder.create_reduce([t.handle for t in inputs], axis)
    region_builder_fn(reduce_op)
    reduce_op.verify()

    return tuple(
        wrap_tensor(reduce_op.get_result(i), inputs[i].type.scalar)
        for i in range(len(inputs))
    )


# ===----------------------------------------------------------------------===
#                               Associative Scan
# ===----------------------------------------------------------------------===


def associative_scan(
    inputs: Sequence[pl.tensor], axis: int, region_builder_fn, builder: ir.builder
) -> Tuple[pl.tensor, ...]:
    if len(inputs) != 1:
        raise ValueError("Current implementation only support single tensor input")
    shape = inputs[0].type.shape

    def wrap_tensor(x, scalar_ty):
        res_ty = pl.block_type(scalar_ty, shape)
        return pl.tensor(x, res_ty)

    scan_op = builder.create_scan([t.handle for t in inputs], axis)
    region_builder_fn(scan_op)
    scan_op.verify()

    return tuple(
        wrap_tensor(scan_op.get_result(i), inputs[i].type.scalar)
        for i in range(len(inputs))
    )


# ===----------------------------------------------------------------------===
#                               Math
# ===----------------------------------------------------------------------===

def _check_dtype(dtypes: List[str]) -> T:
    """
    We following libdevice's convention to check accepted data types for math functions.
    It is not a good practice to support all data types as accelerators/GPUs don't support
    many float16 and bfloat16 math operations.
    We should let the users know that they are using and invoke explicit cast to convert
    the data type to the supported one.
    """
    def wrapper(fn):
        @wraps(fn)
        def check(*args, **kwargs):
            # concatenate args and kwargs
            all_args = list(args) + list(kwargs.values())
            for arg in [a for a in all_args if isinstance(a, pl.tensor)]:
                if arg.type.scalar.name not in dtypes:
                    raise ValueError(f"Expected dtype {dtypes} but got {arg.type.scalar.name}")
            return fn(*args, **kwargs)
        return check

    return wrapper


def umulhi(x: pl.tensor, y: pl.tensor, builder: ir.builder) -> pl.tensor:
    x, y = binary_op_type_checking_impl(x, y, builder)
    # FIXME(Keren): not portable, should be fixed
    from . import math
    return math.mulhi(x, y, _builder=builder)


@_check_dtype(dtypes=["fp32", "fp64"])
def floor(x: pl.tensor, builder: ir.builder) -> pl.tensor:
    # FIXME(Keren): not portable, should be fixed
    from . import math
    return math.floor(x, _builder=builder)


@_check_dtype(dtypes=["fp32", "fp64"])
def exp(x: pl.tensor, builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_exp(x.handle), x.type)


@_check_dtype(dtypes=["fp32", "fp64"])
def log(x: pl.tensor, builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_log(x.handle), x.type)


@_check_dtype(dtypes=["fp32", "fp64"])
def cos(x: pl.tensor, builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_cos(x.handle), x.type)


@_check_dtype(dtypes=["fp32", "fp64"])
def sin(x: pl.tensor, builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_sin(x.handle), x.type)


@_check_dtype(dtypes=["fp32", "fp64"])
def sqrt(x: pl.tensor, builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_sqrt(x.handle), x.type)

def multiple_of(x: pl.tensor, values: List[int]) -> pl.tensor:
    if len(x.shape) != len(values):
        raise ValueError("Shape of input to multiple_of does not match the length of values")
    x.handle.set_attr("tt.divisibility", ir.make_attr(values, x.handle.get_context()))
    return x

def max_contiguous(x: pl.tensor, values: List[int]) -> pl.tensor:
    if len(x.shape) != len(values):
        raise ValueError("Shape of input to max_contiguous does not match the length of values")
    x.handle.set_attr("tt.contiguity", ir.make_attr(values, x.handle.get_context()))
    return x


def max_constancy(x: pl.tensor, values: List[int]) -> pl.tensor:
    if len(x.shape) != len(values):
        raise ValueError("Shape of input to max_constancy does not match the length of values")
    x.handle.set_attr("tt.constancy", ir.make_attr(values, x.handle.get_context()))
    return x


def debug_barrier(builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_barrier(), pl.void)


def device_print(prefix: str, args: List[pl.tensor], builder: ir.builder) -> pl.tensor:
    new_args = []
    for arg in args:
        new_args.append(arg.handle)
    return pl.tensor(builder.create_print(prefix, new_args), pl.void)


def device_assert(cond: pl.tensor, msg: str, file_name: str, func_name, lineno: int, builder: ir.builder) -> pl.tensor:
    cond_ty = cond.type
    if not cond_ty.is_block():
        cond_ty = pl.block_type(cond_ty.scalar, (1,))
        cond = pl.tensor(builder.create_splat(cond.handle, (1,)), cond_ty)
    return pl.tensor(builder.create_assert(cond.handle, msg, file_name, func_name, lineno), pl.void)


def _convert_elem_to_ir_value(builder, elem, require_i64):
    if isinstance(elem, int):
        elem = pl.constexpr(elem)
    if isinstance(elem, pl.constexpr):
        return builder.get_int64(elem.value) if require_i64 else builder.get_int32(elem.value)
    elif isinstance(elem, pl.tensor):
        assert elem.numel.value == 1, "Expected a scalar in shape/strides/offsets"
        assert elem.dtype.is_int(), "Expected an integer scalar type in shape/strides/offsets"
        if elem.dtype != pl.int64 and require_i64:
            return builder.create_int_cast(elem.handle, builder.get_int64_ty(), elem.dtype.is_int_signed(), False)
        elif elem.dtype != pl.int32:
            return builder.create_int_cast(elem.handle, builder.get_int32_ty(), elem.dtype.is_int_signed(), False)
        return elem.handle
    assert False, f"Unsupported element type in shape/strides/offsets: {type(elem)}"


def _convert_to_ir_values(builder, list_like, require_i64=True):
    if hasattr(list_like, "__iter__"):
        return [_convert_elem_to_ir_value(builder, elem, require_i64) for elem in list_like]
    return [_convert_elem_to_ir_value(builder, list_like, require_i64)]


def make_block_ptr(base: pl.tensor, shape, strides, offsets, block_shape, order, builder: ir.builder) -> pl.tensor:
    # Convert dynamic arguments to IR values
    # NOTES(Chenggang): current `shape/strides` are `int64_t`, while `offsets/block_shape` are `int32_t`
    shape = _convert_to_ir_values(builder, shape)
    strides = _convert_to_ir_values(builder, strides)
    offsets = _convert_to_ir_values(builder, offsets, require_i64=False)

    # Check `base` type
    if not base.type.is_ptr() or base.type.element_ty.is_block():
        raise ValueError("Expected `base` to be a pointer type (but not a block pointer type or others)")

    # Treat `pointer_type<pl.int1>` as `pointer_type<pl.int8>`
    if base.type.element_ty == pl.int1:
        base = cast(base, pl.pointer_type(pl.int8, base.type.address_space), builder)

    # Check whether `block_shape` is static
    if not hasattr(block_shape, "__iter__"):
        block_shape = [block_shape]
    block_shape = [elem.value if isinstance(elem, pl.constexpr) else elem for elem in block_shape]
    assert all([isinstance(elem, int) and -2**31 <= elem < 2**31 for elem in block_shape]), \
        "Expected a list of constant integers (`int32_t` range) in `block_shape`"

    # Check `order`
    if not hasattr(order, "__iter__"):
        order = [order]
    order = [elem.value if isinstance(elem, pl.constexpr) else elem for elem in order]
    assert sorted(order) == list(range(len(order))), "Expected a permutation of (0, 1, ..., len(order)-1) in order"

    # Must have same length
    assert all([len(block_shape) == len(list_like) for list_like in [shape, strides, offsets, order]]), \
        "Expected shape/strides/offsets/block_shape to have the same length"

    # Build value, the type is:
    #   `pointer_type<blocked<shape, element_type>>` in Python
    #   `tt.ptr<tensor<shape, element_type>>` in MLIR
    handle = builder.create_make_block_ptr(base.handle, shape, strides, offsets, block_shape, order)
    return pl.tensor(handle, pl.pointer_type(pl.block_type(base.type.element_ty, block_shape)))


def advance(base: pl.tensor, offsets, builder: ir.builder) -> pl.tensor:
    # Convert dynamic offsets to IR values
    offsets = _convert_to_ir_values(builder, offsets, require_i64=False)

    # Advanced block pointer type is the same as before
    return pl.tensor(builder.create_advance(base.handle, offsets), base.type)

# ===----------------------------------------------------------------------===
#                               Tensor
# ===----------------------------------------------------------------------===

def make_gtensor(base: pl.gtensor, ptr, unsigned_flag, builder: ir.builder) -> pl.tensor:
    # Convert dynamic offsets to IR values
    shape = _convert_to_ir_values(builder, base.shape, require_i64=False)
    assert len(shape) == 4, "Expected a 4D tensor shape"
    ret_ty = pl.block_type(get_scalar_dtype(base.dtype), [1])
    # Advanced block pointer type is the same as before
    #import pdb;pdb.set_trace()
    return pl.tensor(builder.create_gtensor(shape, base.mem.val(), ptr.handle, unsigned_flag, base.dtype.to_ir(builder)), ret_ty)

def make_tensor(mem_shape: List[int], tensor_shape, dtype: pl.dtype,
                unsigned_flag, align_mode, builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(dtype), [1])
    mem_shape = _convert_to_ir_values(builder, mem_shape, require_i64=False)
    if tensor_shape is None:
        tensor_shape = [builder.get_null_value(pl.int8.to_ir(builder))]
    else:
        assert len(tensor_shape) == 4, "Expected a 4D tensor shape"
        tensor_shape = _convert_to_ir_values(builder, tensor_shape, require_i64=False)
    return pl.tensor(builder.create_tensor(mem_shape, tensor_shape, unsigned_flag, dtype.to_ir(builder), align_mode),  ret_ty)

def get_dim(input:tl.tensor,
           dim:int,
           builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_get_dim(input.handle,
                                           dim), pl.int32)

def sub_view(input: pl.tensor,
            shape: list_like,
            offset,
            stride,
            builder: ir.builder) -> pl.tensor:
    shape = _convert_to_ir_values(builder, shape, require_i64=False)
    ret_ty = pl.block_type(get_scalar_dtype(input.type), [1])
    if offset is None:
        offset = [builder.get_null_value(pl.int8.to_ir(builder))]
    else:
        assert len(offset) == 4, "Expected a 4D tensor offset"
        offset = _convert_to_ir_values(builder, offset, require_i64=False)

    if stride is None:
        stride = [builder.get_null_value(pl.int8.to_ir(builder))]
    else:
        assert len(stride) == 4, "Expected a 4D tensor stride"
        stride = _convert_to_ir_values(builder, stride, require_i64=False)
    return pl.tensor(builder.create_sub_view(input.handle, shape, offset, stride, get_scalar_dtype(input.type).is_int_unsigned()), ret_ty)

def affine_load(input: pl.tensor,
                index: pl.tensor,
                builder: ir.builder) -> pl.tensor:
    if not isinstance(index, slice):
        index = [index]
    return pl.tensor(builder.create_affine_load(input.handle, index), pl.int32)

def pool_avg(output: pl.tensor,
             input: pl.tensor,
             kernel: List[int],
             padding: List[int],
             stride: List[int],
             dilation: List[int],
             ins: List[int],
             scale: pl.tensor,
             rshift: pl.tensor,
             builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    if ins is None:
        ins = [builder.get_null_value(pl.int8.to_ir(builder))]
    else:
        ins = _convert_to_ir_values(builder, ins, require_i64=False)
    return pl.tensor(builder.create_pool_avg(output.handle, input.handle, kernel, padding, stride, dilation,
                                             ins, scale.handle, rshift.handle), pl.void)

def pool_max(output: pl.tensor,
             input: pl.tensor,
             kernel: List[int],
             padding: List[int],
             stride: List[int],
             dilation: List[int],
             builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_pool_max(output.handle, input.handle, kernel, padding, stride, dilation), pl.void)

def pool_min(output: pl.tensor,
             input: pl.tensor,
             kernel: List[int],
             padding: List[int],
             stride: List[int],
             dilation: List[int],
             builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_pool_min(output.handle, input.handle, kernel, padding, stride, dilation), pl.void)

def fconv(output: pl.tensor,
        input: pl.tensor,
        filter: pl.tensor,
        bias: pl.tensor,
        oc : pl.tensor,
        kernel: List[int],
        stride: List[int],
        dilation: List[int],
        padding: List[int],
        ins: List[int],
        result_relu: pl.tensor,
        result_add: pl.tensor,
        out_dtype: pl.tensor,
        has_bias: pl.tensor,
        saturate: pl.tensor,
        kernel_rotate: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    if ins is None:
        ins = [builder.get_none_value()]
    else:
        ins = _convert_to_ir_values(builder, ins, require_i64=False)
    return pl.tensor(builder.create_fconv(output.handle, input.handle, filter.handle,
             bias.handle, oc.handle, kernel, stride, dilation, padding,
             ins, result_relu.handle, result_add.handle, out_dtype.handle, has_bias.handle,
             saturate.handle, kernel_rotate.handle), pl.void)

def conv(output: pl.tensor,
        input: pl.tensor,
        filter: pl.tensor,
        bias: pl.tensor,
        oc : pl.tensor,
        kernel: List[int],
        stride: List[int],
        dilation: List[int],
        padding: List[int],
        ins: List[int],
        pad_val:pl.tensor,
        result_relu: pl.tensor,
        result_add:pl.tensor,
        out_dtype: pl.tensor,
        has_bias: pl.tensor,
        sym: pl.tensor,
        quant:pl.tensor,
        rq:pl.tensor,
        requant:pl.tensor,
        rq_shift:pl.tensor,
        out_zp:pl.tensor,
        saturate:pl.tensor,
        round:pl.tensor,
        kernel_rotate: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    if ins is None:
        ins = [builder.get_none_value()]
    else:
        ins = _convert_to_ir_values(builder, ins, require_i64=False)
    return pl.tensor(builder.create_conv(output.handle, input.handle, filter.handle,
             bias.handle,
             oc.handle, kernel, stride, dilation, padding, ins,
             pad_val.handle, result_relu.handle,
             result_add.handle, out_dtype.handle, has_bias.handle,
             sym.handle, quant.handle, rq.handle, requant.handle,
             rq_shift.handle, out_zp.handle, saturate.handle,
             round.handle, kernel_rotate.handle), pl.void)

def maximum(out,
            input: pl.tensor,
            other: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_MAX.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 0, ret_ty, builder)
        elif dst_type.is_int():
            return arithint_op_common(out, input, other, mode, dst_type.is_int_unsigned(),
                                     pl._to_tensor(0, builder),
                                     pl._to_tensor(0, builder),
                                     pl._to_tensor(0, builder),
                                     ret_ty, builder)
        assert False
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder)
        input_scalar_ty = get_scalar_dtype(input.type)
        if input_scalar_ty.is_int_signed():
            return pl.tensor(builder.create_maxsi(input.handle, other.handle), input.type)
        elif input_scalar_ty.is_int_unsigned():
            return pl.tensor(builder.create_maxui(input.handle, other.handle), input.type)
        else:
            raise TypeError(f"Unexpected dtype {input_scalar_ty}")

def minimum(out,
            input: pl.tensor,
            other: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_MIN.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 0, ret_ty, builder)
        elif dst_type.is_int():
            return arithint_op_common(out, input, other, mode, dst_type.is_int_unsigned(),
                                     pl._to_tensor(0, builder),
                                     pl._to_tensor(0, builder),
                                     pl._to_tensor(0, builder), ret_ty, builder)
        assert False
    else:
        assert out is None
        input, other = binary_op_type_checking_impl(input, other, builder)
        input_scalar_ty = get_scalar_dtype(input.type)
        if input_scalar_ty.is_int_signed():
            return pl.tensor(builder.create_minsi(input.handle, other.handle), input.type)
        elif input_scalar_ty.is_int_unsigned():
            return pl.tensor(builder.create_minui(input.handle, other.handle), input.type)
        else:
            raise TypeError(f"Unexpected dtype {input_scalar_ty}")

def round(out,
          lhs: pl.tensor,
          round_mode: pl.tensor,
          builder: ir.builder) -> pl.tensor:
    scalar_ty = lhs.type.scalar
    if lhs.type.is_block():
        ret_ty = pl.block_type(get_scalar_dtype(lhs.type), [1])
        if out is None:
            return pl.tensor(builder.create_round(pl._to_tensor(None, builder).handle, lhs.handle,
                                 round_mode.handle, get_scalar_dtype(lhs.type).is_int_unsigned()), ret_ty)
        else:
            return pl.tensor(builder.create_round(out.handle, lhs.handle, round_mode.handle,
                             get_scalar_dtype(lhs.type).is_int_unsigned()), pl.void)
    else:
        assert False, "ToDo"

def sub_abs(out,
            input: pl.tensor,
            other: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    assert input.type.is_ptr() is False or other.type.is_ptr() is False
    if input.type.is_block() or other.type.is_block():
        mode = Arith_mode.ARITH_DIFF_ABS.value
        dst_type = get_dst_dtype(input.type, other.type)
        ret_ty = pl.block_type(dst_type, [1])
        if dst_type.is_floating():
            return arith_op_common(out, input, other, pl._to_tensor(False, builder), mode, 0, ret_ty, builder)
        assert False
    else:
        assert False

def get_eu_num(type:pl.dtype, builder: ir.builder) -> pl.tensor:
    core = 1
    arch = os.getenv("CHIP", default="bm1684x")
    if arch == "bm1684x":
        core = 1
    elif arch == "bm1688":
        core = 2
    elif arch == "bm1690":
        core = 8
    size = 4
    dtype = get_scalar_dtype(type)
    if dtype == pl.float32 or dtype == pl.int32 or dtype == pl.uint32:
        size = 4
    elif dtype == pl.float16 or dtype == pl.bfloat16 or dtype == pl.int16 or dtype == pl.uint16:
        size = 2
    elif dtype == pl.int8 or dtype == pl.uint8 or dtype == pl.float8e5 or dtype == pl.float8e4:
        size = 1
    elif dtype == pl.int4 or dtype == pl.uint4:
        if arch == "bm1690" or arch == "bm1688":
            size = 1
        else:
            assert False, "don't support int4"
    else:
        assert 0, "toDo"
    return pl.tensor(builder.create_get_eu_num(core, size), pl.int32)

def lane_num(builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_lane_num(), pl.int32)

def move(dst: pl.tensor,
         src: pl.tensor,
         tiu: bool,
         builder: ir.builder) -> pl.tensor:
    if tiu:
        return pl.tensor(builder.create_move(dst.handle, src.handle), pl.void)
    else:
        return pl.tensor(builder.create_dma_move(dst.handle, src.handle), pl.void)

def fexp(dst,
         src: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_fexp(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_fexp(dst.handle, src.handle), pl.void)

def fexp_part(dst,
         src: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_fexp_part(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_fexp_part(dst.handle, src.handle), pl.void)

def frsqrt(dst,
         src: pl.tensor,
         num_iter: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_frsqrt(pl._to_tensor(None, builder).handle, src.handle, num_iter.handle), ret_ty)
    else:
        return pl.tensor(builder.create_frsqrt(dst.handle, src.handle, num_iter.handle), pl.void)

def fsqrt(dst,
         src: pl.tensor,
         num_iter: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_fsqrt(pl._to_tensor(None, builder).handle, src.handle, num_iter.handle), ret_ty)
    else:
        return pl.tensor(builder.create_fsqrt(dst.handle, src.handle, num_iter.handle), pl.void)

def fsin(dst,
         src: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_fsin(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_fsin(dst.handle, src.handle), pl.void)

def fcos(dst,
         src: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_fcos(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_fcos(dst.handle, src.handle), pl.void)

def ftan(dst,
         src: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_ftan(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_ftan(dst.handle, src.handle), pl.void)

def farcsin(dst,
                 src: pl.tensor,
                 builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_farcsin(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_farcsin(dst.handle, src.handle), pl.void)

def farccos(dst,
                 src: pl.tensor,
                 builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_farccos(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_farccos(dst.handle, src.handle), pl.void)

def flog(dst,
         src: pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_flog(pl._to_tensor(None, builder).handle, src.handle), ret_ty)
    else:
        return pl.tensor(builder.create_flog(dst.handle, src.handle), pl.void)

def flogx(dst,
         src: pl.tensor,
         work0:pl.tensor,
         coeff:pl.tensor,
         x:pl.tensor,
         builder: ir.builder) -> pl.tensor:
    ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
    if dst is None:
        return pl.tensor(builder.create_flogx(pl._to_tensor(None, builder).handle, src.handle,
                                              work0.handle, coeff.handle, x.handle), ret_ty)
    else:
        return pl.tensor(builder.create_flogx(dst.handle, src.handle, work0.handle, coeff.handle, x.handle), pl.void)

def enable_pipeline(builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_pipeline(), pl.void)

def gather_hw(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              const_val:pl.tensor, fill_const:pl.tensor, builder:ir.builder):
    return pl.tensor(builder.create_gather_hw(output.handle, param.handle, index.handle,
                                              const_val.handle, fill_const.handle), pl.void)

def gather_w(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              is_param_repeated:pl.tensor, const_val:pl.tensor,
              fill_const:pl.tensor, builder:ir.builder):
    return pl.tensor(builder.create_gather_w(output.handle, param.handle, index.handle,
                                             is_param_repeated.handle, const_val.handle,
                                             fill_const.handle,
                                             pl._to_tensor(0, builder).handle), pl.void)

def gather_h(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              is_param_repeated:pl.tensor, const_val:pl.tensor,
              fill_const:pl.tensor, builder:ir.builder):
    return pl.tensor(builder.create_gather_h(output.handle, param.handle, index.handle,
                                             is_param_repeated.handle, const_val.handle,
                                             fill_const.handle), pl.void)

def scatter_hw(output:pl.tensor, param:pl.tensor, index:pl.tensor,
               builder:ir.builder):
    return pl.tensor(builder.create_scatter_hw(output.handle, param.handle, index.handle), pl.void)

def scatter_w(output:pl.tensor, param:pl.tensor, index:pl.tensor,
               bcast:pl.tensor,
               is_param_repeated:pl.tensor,
               builder:ir.builder):
    return pl.tensor(builder.create_scatter_w(output.handle, param.handle, index.handle,
                                            bcast.handle, is_param_repeated.handle,
                                            pl._to_tensor(0, builder).handle), pl.void)

def scatter_h(output:pl.tensor, param:pl.tensor, index:pl.tensor,
               is_param_repeated:pl.tensor,
               builder:ir.builder):
    return pl.tensor(builder.create_scatter_h(output.handle, param.handle, index.handle,
                                            is_param_repeated.handle), pl.void)

def arange_broadcast(output:pl.tensor, start:pl.tensor, step:pl.tensor,
                     num:pl.tensor, builder:ir.builder):
    return pl.tensor(builder.create_arange_broadcast(output.handle, start.handle, step.handle,
                                            num.handle), pl.void)

def abs(out,
        input: pl.tensor,
        builder: ir.builder) -> pl.tensor:
    scalar_ty = get_scalar_dtype(input.type)
    ret_ty = pl.block_type(get_scalar_dtype(input.type), [1])
    if input.type.is_block():
        if out is None:
            return pl.tensor(builder.create_abs(pl._to_tensor(None, builder).handle,
                                                input.handle), ret_ty)
        else:
            return pl.tensor(builder.create_abs(out.handle, input.handle), pl.void)
    else:
        if input.type.is_floating():
            return pl.tensor(builder.create_fabs(input.handle), input.type)
        elif input.type.is_int_signed():
            return pl.tensor(builder.create_iabs(input.handle), input.type)
        elif input.type.is_int_unsigned():
            return input  # no-op
        else:
            assert False, f"Unexpected dtype {dtype}"

def fmul_add(out,
            src0: pl.tensor,
            src1: pl.tensor,
            src2: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block() or src1.type.is_block() or src2.type.is_block():
        scalar_ty = get_scalar_dtype(src0.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        if out is None:
            return pl.tensor(builder.create_fmul_add(pl._to_tensor(None, builder).handle,
                                                     src0.handle, src1.handle, src2.handle), ret_ty)
        else:
            return pl.tensor(builder.create_fmul_add(out.handle, src0.handle,
                                                 src1.handle, src2.handle), pl.void)
    else:
        return pl.tensor(builder.create_fma(src0.handle, src1.handle, src2.handle), src0.type)

def fadd_sqr(out,
            src0: pl.tensor,
            src1: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block() or src1.type.is_block():
        scalar_ty = get_scalar_dtype(src0.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        if out is None:
            return pl.tensor(builder.create_fadd_sqr(pl._to_tensor(None, builder).handle,
                                                    src0.handle, src1.handle), ret_ty)
        else:
            return pl.tensor(builder.create_fadd_sqr(out.handle, src0.handle,
                                                 src1.handle), pl.void)
    assert False

def fsub_sqr(out,
            src0: pl.tensor,
            src1: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block() or src1.type.is_block():
        scalar_ty = get_scalar_dtype(src0.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        if out is None:
            return pl.tensor(builder.create_fsub_sqr(pl._to_tensor(None, builder).handle,
                                                     src0.handle, src1.handle), ret_ty)
        else:
            return pl.tensor(builder.create_fsub_sqr(out.handle, src0.handle,
                                                 src1.handle), pl.void)
    assert False

def fscale(out,
            src0: pl.tensor,
            scale: pl.tensor,
            bias: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block():
        scalar_ty = get_scalar_dtype(src0.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        if out is None:
            return pl.tensor(builder.create_fscale(pl._to_tensor(None, builder).handle, src0.handle,
                                        scale.handle, bias.handle), ret_ty)
        else:
            return pl.tensor(builder.create_fscale(out.handle, src0.handle,
                                                 scale.handle, bias.handle), pl.void)
    assert False

def gt_select(out,
            src0: pl.tensor,
            src1: pl.tensor,
            src2: pl.tensor,
            src3: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block() or src1.type.is_block() or src2.type.is_block() or src3.type.is_block():
        scalar_ty = get_dst_dtype(src0.type, src1.type, src2.type, src3.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        mode = Comparision_mode.GREATER.value
        if out is None:
            return pl.tensor(builder.create_cmp_select(pl._to_tensor(None, builder).handle, src0.handle,
                                        src1.handle, src2.handle, src3.handle, mode), ret_ty)
        else:
            return pl.tensor(builder.create_cmp_select(out.handle, src0.handle,
                                                 src1.handle, src2.handle, src3.handle, mode), pl.void)
    assert False

def lt_select(out,
            src0: pl.tensor,
            src1: pl.tensor,
            src2: pl.tensor,
            src3: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block() or src1.type.is_block() or src2.type.is_block() or src3.type.is_block():
        scalar_ty = get_dst_dtype(src0.type, src1.type, src2.type, src3.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        mode = Comparision_mode.LESS.value
        if out is None:
            return pl.tensor(builder.create_cmp_select(pl._to_tensor(None, builder).handle, src0.handle,
                                        src1.handle, src2.handle, src3.handle, mode), ret_ty)
        else:
            return pl.tensor(builder.create_cmp_select(out.handle, src0.handle,
                                                 src1.handle, src2.handle, src3.handle, mode), pl.void)
    assert False

def eq_select(out,
            src0: pl.tensor,
            src1: pl.tensor,
            src2: pl.tensor,
            src3: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    if src0.type.is_block() or src1.type.is_block() or src2.type.is_block() or src3.type.is_block():
        scalar_ty = get_dst_dtype(src0.type, src1.type, src2.type, src3.type)
        ret_ty = pl.block_type(scalar_ty, [1])
        mode = Comparision_mode.EQUAL.value
        if out is None:
            return pl.tensor(builder.create_cmp_select(pl._to_tensor(None, builder).handle, src0.handle,
                                        src1.handle, src2.handle, src3.handle, mode), ret_ty)
        else:
            return pl.tensor(builder.create_cmp_select(out.handle, src0.handle,
                                                 src1.handle, src2.handle, src3.handle, mode), pl.void)
    assert False

def maxmin_cmp_select(out0: pl.tensor,
                  out1: pl.tensor,
                  src0: pl.tensor,
                  src1: pl.tensor,
                  src2: pl.tensor,
                  src3: pl.tensor,
                  mode:int,
                  builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_maxmin_cmp_select(out0.handle, out1.handle, src0.handle,
                                                 src1.handle, src2.handle, src3.handle, mode), pl.void)
def mask_select(dst: pl.tensor,
                  src: pl.tensor,
                  mask: pl.tensor,
                  builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_mask_select(dst.handle, src.handle, mask.handle), pl.int32)

def tiu_mask_select(dst: pl.tensor,
                    dst_cnt: pl.tensor,
                    src: pl.tensor,
                    mask: pl.tensor,
                    builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_tiu_mask_select(dst.handle, dst_cnt.handle, src.handle, mask.handle,
                                                    pl._to_tensor(0, builder).handle), pl.void)

def broadcast(dst,
            src: pl.tensor,
            npu_num: pl.tensor,
            tiu:bool,
            builder: ir.builder) ->pl.tensor:
    if tiu:
        if dst is None:
            ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
            return pl.tensor(builder.create_tiu_broadcast(pl._to_tensor(None, builder).handle,
                                                        src.handle, npu_num.handle), ret_ty)
        else:
            return pl.tensor(builder.create_tiu_broadcast(dst.handle, src.handle, npu_num.handle), pl.void)
    else:
        return pl.tensor(builder.create_dma_broadcast(dst.handle, src.handle, npu_num.handle), pl.void)

def fp_load_coeff(coeff:pl.tensor,
                  mode:int,
                  builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_fp_load_coeff(coeff.handle, mode), pl.void)

def smem_bcast(dst:pl.tensor,
                  mode:int,
                  builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_smem_bcast(dst.handle, mode), pl.void)

def smem_dist(dst:pl.tensor,
                  mode:int,
                  builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_smem_dist(dst.handle, mode), pl.void)

def shift(dst,
        src: pl.tensor,
        shift: pl.tensor,
        r_mode: pl.tensor,
        lshift: bool,
        builder: ir.builder) ->pl.tensor:
    if src.type.is_block() or shift.type.is_block():
        if dst is None:
            ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
            if lshift:
                return pl.tensor(builder.create_shift(pl._to_tensor(None, builder).handle,
                                                        src.handle, shift.handle, r_mode.handle), ret_ty)
            else:
                res = minus(None, shift, builder)
                return pl.tensor(builder.create_shift(pl._to_tensor(None, builder).handle,
                                                        src.handle, res.handle, r_mode.handle), ret_ty)
        else:
            if lshift:
                return pl.tensor(builder.create_shift(dst.handle, src.handle, shift.handle, r_mode.handle), pl.void)
            else:
                res = minus(None, shift, builder)
                return pl.tensor(builder.create_shift(dst.handle, src.handle, res.handle, r_mode.handle), pl.void)
    else:
        assert dst is None
        if lshift:
            return shl(src, shift, builder)
        else:
            if get_scalar_dtype(src.type).is_int_signed():
                return ashr(src, shift, builder)
            else:
                return lshr(src, shift, builder)


def logical_shift(dst,
                src: pl.tensor,
                shift: pl.tensor,
                r_mode: pl.tensor,
                builder: ir.builder) ->pl.tensor:
    if src.type.is_block() or shift.type.is_block():
        if dst is None:
            ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
            return pl.tensor(builder.create_logical_shift(pl._to_tensor(None, builder).handle,
                                                        src.handle, shift.handle, r_mode.handle), ret_ty)
        else:
            return pl.tensor(builder.create_logical_shift(dst.handle, src.handle, shift.handle, r_mode.handle), pl.void)

def circular_shift(dst,
                src: pl.tensor,
                shift: pl.tensor,
                r_mode: pl.tensor,
                builder: ir.builder) ->pl.tensor:
    if src.type.is_block() or shift.type.is_block():
        if dst is None:
            ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
            return pl.tensor(builder.create_circular_shift(pl._to_tensor(None, builder).handle,
                                                        src.handle, shift.handle, r_mode.handle), ret_ty)
        else:
            return pl.tensor(builder.create_circular_shift(dst.handle, src.handle, shift.handle, r_mode.handle), pl.void)

def nonzero(dst:pl.tensor,
            src:pl.tensor,
            builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_nonzero(dst.handle, src.handle), pl.int32)

def tiu_nonzero(dst:pl.tensor,
                dst_cnt:pl.tensor,
                src:pl.tensor,
                builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_tiu_nonzero(dst.handle, dst_cnt.handle, src.handle,
                                                pl._to_tensor(0, builder).handle), pl.void)

def norm(dst:pl.tensor,
        src:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_norm(dst.handle, src.handle), pl.void)

def clz(dst:pl.tensor,
        src:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_clz(dst.handle, src.handle), pl.void)

def clo(dst:pl.tensor,
        src:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_clo(dst.handle, src.handle), pl.void)

def taylor(dst,
            src: pl.tensor,
            coeff: pl.tensor,
            len: pl.tensor,
            builder: ir.builder) ->pl.tensor:
    if src.type.is_block() or coeff.type.is_block():
        if dst is None:
            ret_ty = pl.block_type(get_scalar_dtype(src.type), [1])
            return pl.tensor(builder.create_taylor(pl._to_tensor(None, builder).handle,
                                                    src.handle, coeff.handle, len.handle), ret_ty)
        else:
            return pl.tensor(builder.create_taylor(dst.handle, src.handle, coeff.handle, len.handle), pl.void)
    assert False

def vc_op(dst,
            src0: pl.tensor,
            src1: pl.tensor,
            mode: pl.tensor,
            builder: ir.builder) ->pl.tensor:
    if src0.type.is_block() or src1.type.is_block():
        if dst is None:
            sca_ty = get_dst_dtype(src0.type, src1.type)
            ret_ty = pl.block_type(sca_ty, [1])
            return pl.tensor(builder.create_vc_op(pl._to_tensor(None, builder).handle,
                                                    src0.handle, src1.handle, mode.handle), ret_ty)
        else:
            return pl.tensor(builder.create_vc_op(dst.handle, src0.handle, src1.handle, mode.handle), pl.void)
    assert False

def transpose_cw(dst: pl.tensor,
                src: pl.tensor,
                tiu: bool,
                builder: ir.builder) ->pl.tensor:
    if tiu:
        return pl.tensor(builder.create_transpose_cw(dst.handle, src.handle), pl.void)
    else:
        return pl.tensor(builder.create_gdma_transpose_cw(dst.handle, src.handle), pl.void)

def transpose_wc(dst: pl.tensor,
                src: pl.tensor,
                builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_transpose_wc(dst.handle, src.handle), pl.void)

def load_transpose_cw(dst: pl.tensor,
                    src: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_load_transpose_cw(dst.handle, src.handle), pl.void)

def load_transpose_nc(dst: pl.tensor,
                    src: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_load_transpose_nc(dst.handle, src.handle), pl.void)

def store_transpose_cw(dst: pl.tensor,
                    src: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_store_transpose_cw(dst.handle, src.handle), pl.void)

def store_transpose_nc(dst: pl.tensor,
                    src: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_store_transpose_nc(dst.handle, src.handle), pl.void)

def load_broadcast(dst: pl.tensor,
                    src: pl.tensor,
                    npu_num: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_load_broadcast(dst.handle, src.handle, npu_num.handle), pl.void)

def transpose_nc(dst: pl.tensor,
                    src: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_transpose_nc(dst.handle, src.handle), pl.void)

def dma_gather_h(output:pl.tensor, param:pl.tensor, index:pl.tensor,
              const_val:pl.tensor,
              index_start_pos:pl.tensor,
              builder:ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_dma_gather_h(output.handle, param.handle,
                                                index.handle, const_val.handle,
                                                index_start_pos.handle), pl.void)

def dma_scatter_h(output:pl.tensor,
                param:pl.tensor,
                index:pl.tensor,
                index_start_pos:pl.tensor,
                inplace_add:pl.tensor,
                builder:ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_dma_scatter_h(output.handle, param.handle,
                                                index.handle,  index_start_pos.handle,
                                                inplace_add.handle), pl.void)

def move_cross_lane(dst: pl.tensor,
                    src: pl.tensor,
                    builder: ir.builder) ->pl.tensor:
    return pl.tensor(builder.create_move_cross_lane(dst.handle, src.handle), pl.void)

def mask_batch_bcast(dst:pl.tensor,
                    count: pl.tensor,
                    src:pl.tensor,
                    mask:pl.tensor,
                    is_repeat:pl.tensor,
                    builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_mask_batch_bcast(dst.handle, count.handle,
                                                     src.handle, mask.handle, is_repeat.handle,
                                                     pl._to_tensor(0, builder).handle), pl.void)

def reverse(dst:pl.tensor,
            src:pl.tensor,
            dim:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_reverse(dst.handle, src.handle, dim.handle), pl.void)

def vload(dst_v_idx:pl.tensor,
            src:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_vload(dst_v_idx.handle, src.handle), pl.void)

def vstore(dst:pl.tensor,
            v_idx:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_vstore(dst.handle, v_idx.handle), pl.void)

def move_tv(dst:pl.tensor,
            v_idx:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_move_tv(dst.handle, v_idx.handle), pl.void)

def move_distv(dst:pl.tensor,
            v_idx:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_move_distv(dst.handle, v_idx.handle), pl.void)

def move_vv(dst:pl.tensor,
            v_idx0:pl.tensor,
            v_idx1:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_move_vv(dst.handle, v_idx0.handle, v_idx1.handle), pl.void)

def move_distvv(dst:pl.tensor,
            v_idx0:pl.tensor,
            v_idx1:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_move_distvv(dst.handle, v_idx0.handle, v_idx1.handle), pl.void)

def move_vt(dst_v_idx:pl.tensor,
            src:pl.tensor,
            builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_move_vt(dst_v_idx.handle, src.handle), pl.void)

def move_vcoll(dst_v_idx:pl.tensor,
                src:pl.tensor,
                builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_move_vcoll(dst_v_idx.handle, src.handle), pl.void)

def topk(dst:pl.tensor,
         dst_idx:pl.tensor,
         src:pl.tensor,
         src_idx:pl.tensor,
         K:pl.tensor,
         descended:pl.tensor,
         builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_topk(dst.handle, dst_idx.handle, src.handle, src_idx.handle,
                                                K.handle, descended.handle
                                                ), pl.void)
def gather_line(dst:pl.tensor,
                param:pl.tensor,
                index:pl.tensor,
                C:pl.tensor,
                start:pl.tensor,
                end:pl.tensor,
                fill_const:pl.tensor,
                builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_gather_line(dst.handle, param.handle, index.handle, C.handle,
                                                start.handle, end.handle, fill_const.handle), pl.void)

def sdma_move(dst:pl.tensor,
                src:pl.tensor,
                port_id:pl.tensor,
                builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_sdma_move(dst.handle, src.handle, port_id.handle
                                                ), pl.void)

def sdma_transpose_cw(dst:pl.tensor,
                src:pl.tensor,
                port_id:pl.tensor,
                builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_sdma_transpose_cw(dst.handle, src.handle, port_id.handle
                                                ), pl.void)

def sdma_transpose_nc(dst:pl.tensor,
                src:pl.tensor,
                port_id:pl.tensor,
                builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_sdma_transpose_nc(dst.handle, src.handle, port_id.handle
                                                ), pl.void)

def get_core_num(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_get_core_num(), pl.int32)

def get_group_num(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_get_group_num(), pl.int32)

def get_block_num(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_get_block_num(), pl.int32)
'''
def tpu_sync_core(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_tpu_sync_core(), pl.void)
'''
def sync(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_sync(), pl.void)

def hau_poll(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_hau_poll(), pl.void)

def tpu_poll(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_tpu_poll(), pl.void)

def msg_send(msg_idx:pl.tensor,
             wait_cnt:pl.tensor,
             is_dma:pl.tensor,
             builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_msg_send(msg_idx.handle, wait_cnt.handle, is_dma.handle), pl.void)

def msg_wait(msg_idx:pl.tensor,
             send_cnt:pl.tensor,
             is_dma:pl.tensor,
             builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_msg_wait(msg_idx.handle, send_cnt.handle, is_dma.handle), pl.void)

def fence(builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_fence(), pl.void)

def lane_mask(mask:pl.tensor,
             long_valid:pl.tensor,
             builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_lane_mask(mask.handle, long_valid.handle), pl.void)

def vset(v_idx:pl.tensor,
        lmul:pl.tensor,
        v_len:pl.tensor,
        builder: ir.builder)->pl.tensor:
    return pl.tensor(builder.create_vset(v_idx.handle, lmul.handle, v_len.handle), pl.void)

def fdeconv(output: pl.tensor,
            input: pl.tensor,
            filter: pl.tensor,
            bias: pl.tensor,
            oc : pl.tensor,
            kernel: List[int],
            dilation: List[int],
            padding: List[int],
            ins: List[int],
            result_add: pl.tensor,
            out_dtype: pl.tensor,
            has_bias: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    ins = _convert_to_ir_values(builder, ins, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_fdeconv(output.handle, input.handle, filter.handle,
                                            bias.handle, oc.handle, kernel,dilation,padding,ins,
                                            result_add.handle, out_dtype.handle, has_bias.handle),
                                            pl.void)

def deconv(output: pl.tensor,
            input: pl.tensor,
            filter: pl.tensor,
            bias: pl.tensor,
            oc : pl.tensor,
            kernel: List[int],
            dilation: List[int],
            padding: List[int],
            ins: List[int],
            pad_val:pl.tensor,
            insert_val:pl.tensor,
            result_relu: pl.tensor,
            result_add: pl.tensor,
            out_dtype: pl.tensor,
            has_bias: pl.tensor,
            sym: pl.tensor,
            quant:pl.tensor,
            builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    if ins is None:
        ins = [builder.get_none_value()]
    else:
        ins = _convert_to_ir_values(builder, ins, require_i64=False)
    return pl.tensor(builder.create_deconv(output.handle, input.handle, filter.handle,
             bias.handle, oc.handle, kernel, dilation, padding, ins,
             pad_val.handle, insert_val.handle, result_relu.handle, result_add.handle,
             out_dtype.handle, has_bias.handle, sym.handle, quant.handle), pl.void)


def fdw_deconv(output: pl.tensor,
            input: pl.tensor,
            filter: pl.tensor,
            bias: pl.tensor,
            kernel: List[int],
            dilation: List[int],
            padding: List[int],
            ins: List[int],
            out_dtype: pl.tensor,
            has_bias: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    ins = _convert_to_ir_values(builder, ins, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_fdw_deconv(output.handle, input.handle, filter.handle,
             bias.handle, kernel, dilation, padding, ins, out_dtype.handle,
             has_bias.handle), pl.void)

def dw_deconv(output: pl.tensor,
            input: pl.tensor,
            filter: pl.tensor,
            bias: pl.tensor,
            kernel: List[int],
            dilation: List[int],
            padding: List[int],
            ins: List[int],
            pad_val: pl.tensor,
            result_relu: pl.tensor,
            out_dtype: pl.tensor,
            has_bias: pl.tensor,
            rshift: pl.tensor,
            round_mode: pl.tensor,
            builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    ins = _convert_to_ir_values(builder, ins, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_dw_deconv(output.handle, input.handle, filter.handle,
                    bias.handle,
                    kernel, dilation, padding, ins,
                    pad_val.handle,
                    result_relu.handle,
                    out_dtype.handle, has_bias.handle,
                    rshift.handle,
                    round_mode.handle), pl.void)

def fdw_conv(output: pl.tensor,
            input: pl.tensor,
            filter: pl.tensor,
            bias: pl.tensor,
            kernel: List[int],
            stride: List[int],
            dilation: List[int],
            padding: List[int],
            has_bias:pl.tensor,
            builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_fdw_conv(output.handle, input.handle, filter.handle,
                    bias.handle, kernel, stride, dilation, padding, has_bias.handle), pl.void)

def dw_conv(output: pl.tensor,
            input: pl.tensor,
            filter: pl.tensor,
            bias:pl.tensor,
            kernel: List[int],
            stride: List[int],
            dilation: List[int],
            padding: List[int],
            pad_val:pl.tensor,
            result_relu:pl.tensor,
            out_dtype:pl.tensor,
            has_bias:pl.tensor,
            rshift:pl.tensor,
            rq:pl.tensor,
            requant:pl.tensor,
            saturate:pl.tensor,
            round_mode:pl.tensor,
            builder: ir.builder) -> pl.tensor:
    kernel = _convert_to_ir_values(builder, kernel, require_i64=False)
    stride = _convert_to_ir_values(builder, stride, require_i64=False)
    padding = _convert_to_ir_values(builder, padding, require_i64=False)
    dilation = _convert_to_ir_values(builder, dilation, require_i64=False)
    return pl.tensor(builder.create_dw_conv(output.handle, input.handle, filter.handle,
                    bias.handle, kernel, stride, dilation, padding,
                    pad_val.handle, result_relu.handle, out_dtype.handle,
                    has_bias.handle, rshift.handle, rq.handle, requant.handle,
                    saturate.handle, round_mode.handle), pl.void)

def rq_fp(output: pl.tensor,
        input: pl.tensor,
        scale:pl.tensor,
        offset: pl.tensor,
        dst_round_mode:pl.tensor,
        src_round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_rq_fp(output.handle,
                                        input.handle,
                                        scale.handle,
                                        offset.handle,
                                        dst_round_mode.handle,
                                        src_round_mode.handle), pl.void)

def rq_pc_fp(output: pl.tensor,
        input: pl.tensor,
        quant:pl.tensor,
        dst_round_mode:pl.tensor,
        src_round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_rq_pc_fp(output.handle,
                                        input.handle,
                                        quant.handle,
                                        dst_round_mode.handle,
                                        src_round_mode.handle), pl.void)

def rq_int(output: pl.tensor,
        input: pl.tensor,
        multiplier:pl.tensor,
        shift:pl.tensor,
        offset: pl.tensor,
        round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_rq_int(output.handle,
                                        input.handle,
                                        multiplier.handle,
                                        shift.handle,
                                        offset.handle,
                                        round_mode.handle), pl.void)

def rq_pc_int(output: pl.tensor,
        input: pl.tensor,
        quant:pl.tensor,
        round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_rq_pc_int(output.handle,
                                        input.handle,
                                        quant.handle,
                                        round_mode.handle), pl.void)

def dq_fp(output: pl.tensor,
        input: pl.tensor,
        offset: pl.tensor,
        scale:pl.tensor,
        round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_dq_fp(output.handle,
                                        input.handle,
                                        offset.handle,
                                        scale.handle,
                                        round_mode.handle), pl.void)

def dq_pc_fp(output: pl.tensor,
        input: pl.tensor,
        quant:pl.tensor,
        round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_dq_pc_fp(output.handle,
                                        input.handle,
                                        quant.handle,
                                        round_mode.handle), pl.void)

def dq_int(output: pl.tensor,
        input: pl.tensor,
        offset: pl.tensor,
        multiplier:pl.tensor,
        shift:pl.tensor,
        round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_dq_int(output.handle,
                                        input.handle,
                                        offset.handle,
                                        multiplier.handle,
                                        shift.handle,
                                        round_mode.handle), pl.void)

def dq_pc_int(output: pl.tensor,
        input: pl.tensor,
        quant:pl.tensor,
        round_mode:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_dq_pc_int(output.handle,
                                        input.handle,
                                        quant.handle,
                                        round_mode.handle), pl.void)
def dq2(output: pl.tensor,
        input: pl.tensor,
        offset_scale:pl.tensor,
        gsize:pl.tensor,
        builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_dq2(output.handle,
                                        input.handle,
                                        offset_scale.handle,
                                        gsize.handle), pl.void)

def dma_reduce(output: pl.tensor,
              input: pl.tensor,
              psum: pl.tensor,
              opcode: pl.tensor,
              builder: ir.builder) -> pl.tensor:
    return pl.tensor(builder.create_dma_reduce(output.handle,
                                        input.handle,
                                        psum.handle,
                                        opcode.handle), pl.void)
