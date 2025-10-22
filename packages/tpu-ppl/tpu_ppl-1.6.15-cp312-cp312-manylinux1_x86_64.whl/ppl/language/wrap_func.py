from __future__ import annotations

from ..runtime.jit import jit, autotiling
from . import core
import ppl.language as pl

@jit
def exp_no_overflow(input, m_n, m_c, m_h, m_w, t_n, t_c, t_h, t_w):
    """
    无数据溢出的 exp 指数计算

        .. code-block:: python

            output = exp_no_overflow(input, m_n, m_c, m_h, m_w, t_n, t_c, t_h, t_w)

    参数:
        - ``input`` (`ppl.language.tensor`): input 张量

        - ``m_n`` (`int`): 张量memory shape的N

        - ``m_c`` (`int`): 张量memory shape的C

        - ``m_h`` (`int`): 张量memory shape的H

        - ``m_w`` (`int`): 张量memory shape的W

        - ``t_n`` (`int`): 张量实际shape的N

        - ``t_c`` (`int`): 张量实际shape的C

        - ``t_h`` (`int`): 张量实际shape的H

        - ``t_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    min_C = 0
    if pl.get_scalar_dtype(input.dtype).is_fp32():
        min_C = -3.40282e35
    elif input.dtype.is_fp16():
        min_C = -45403.0
    else:
        min_C = -3.40282e35
    maxc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], input.dtype, [t_n, t_c, t_h, t_w])
    pl.max(maxc_tensor, input, min_C)
    minc_tensor1 = pl.make_tensor([m_n, m_c, m_h, m_w], input.dtype, [t_n, t_c, t_h, t_w])
    if input.dtype.is_fp16():
        min(minc_tensor1, maxc_tensor, 45403.0)
    else:
        pl.tiu.move(minc_tensor1, maxc_tensor)
    fp_mulc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], input.dtype, [t_n, t_c, t_h, t_w])
    pl.fmul(fp_mulc_tensor, minc_tensor1, 1.4426950)
    fp_floor_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], input.dtype, [t_n, t_c, t_h, t_w])
    pl.floor(fp_floor_tensor, fp_mulc_tensor)
    fp_mulc_tensor2 = pl.make_tensor([m_n, m_c, m_h, m_w], input.dtype, [t_n, t_c, t_h, t_w])
    pl.fmul(fp_mulc_tensor2, fp_floor_tensor, 0.69314718)
    fp_sub = pl.make_tensor([m_n, m_c, m_h, m_w], input.dtype, [t_n, t_c, t_h, t_w])
    pl.fsub(fp_sub, maxc_tensor, fp_mulc_tensor2)

    if pl.get_scalar_dtype(input.dtype).is_fp32():
        cast_out = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.tiu.cast(cast_out, fp_floor_tensor, pl.int16, pl.RM_HALF_AWAY_FROM_ZERO)
        minc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        min(minc_tensor, cast_out, pl.tiu.cast(127, pl.int16))
        maxc_tensor2 = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.max(maxc_tensor2, minc_tensor, pl.tiu.cast(-127, pl.int16))
        add_intc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int32, [t_n, t_c, t_h, t_w])
        pl.add(add_intc_tensor, maxc_tensor2, pl.tiu.cast(127, pl.int16), 23, pl.RM_HALF_AWAY_FROM_ZERO, True)
        exp_out = pl.make_tensor([m_n, m_c, m_h, m_w], pl.float32, [t_n, t_c, t_h, t_w])
        pl.fexp(exp_out, fp_sub)
        out = exp_out * add_intc_tensor
    elif input.dtype.is_fp16():
        cast_out = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int8, [t_n, t_c, t_h, t_w])
        pl.tiu.cast(cast_out, fp_floor_tensor, pl.int8, pl.RM_HALF_AWAY_FROM_ZERO)

        minc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int8, [t_n, t_c, t_h, t_w])
        #pl.min() or min() is both ok
        pl.min(minc_tensor, cast_out, pl.tiu.cast(15, pl.int16))
        maxc_tensor2 = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int8, [t_n, t_c, t_h, t_w])
        pl.max(maxc_tensor2, minc_tensor, pl.tiu.cast(-15, pl.int16))
        add_intc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.add(add_intc_tensor, maxc_tensor2, pl.tiu.cast(15, pl.int16), 10,
             pl.RM_HALF_AWAY_FROM_ZERO, True)

        exp_out = pl.make_tensor([m_n, m_c, m_h, m_w], pl.float16, [t_n, t_c, t_h, t_w])
        pl.fexp(exp_out, fp_sub)
        out = exp_out * add_intc_tensor
    elif input.dtype.is_bf16():
        cast_out = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.tiu.cast(cast_out, fp_floor_tensor, pl.int16, pl.RM_HALF_AWAY_FROM_ZERO)

        minc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.min(minc_tensor, cast_out, pl.tiu.cast(127, pl.int16))
        maxc_tensor2 = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.max(maxc_tensor2, minc_tensor, pl.tiu.cast(-127, pl.int16))
        add_intc_tensor = pl.make_tensor([m_n, m_c, m_h, m_w], pl.int16, [t_n, t_c, t_h, t_w])
        pl.add(add_intc_tensor, maxc_tensor2, pl.tiu.cast(127, pl.int16), 7,
             pl.RM_HALF_AWAY_FROM_ZERO, True)

        exp_out = pl.make_tensor([m_n, m_c, m_h, m_w], pl.bfloat16, [t_n, t_c, t_h, t_w])
        pl.fexp(exp_out, fp_sub)
        out = exp_out * add_intc_tensor
    return out

@jit
def sigmoid_fp32(local_input, block_n, block_c, block_h,
                 block_w, real_n, real_c, real_h, real_w):
    """
    fp32 sigmoid 计算

        .. code-block:: python

            output = sigmoid_fp32(local_input, block_n, block_c, block_h, block_w,
                                  real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    work_0 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    work_1 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fexp(work_0, local_input)
    pl.fdiv(work_1, 1, work_0, 3);
    pl.fadd(work_0, work_1, 1);
    pl.fdiv(work_1, 1, work_0, 3)
    return work_1;
    # return local_input

@jit
def prelu(local_input, alpha, block_n, block_c, block_h,
          block_w, real_n, real_c, real_h, real_w):
    """
    prelu 计算

        .. code-block:: python

            output = prelu(local_input, alpha, block_n, block_c, block_h, block_w,
                           real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``alpha`` (`float`): alpha 参数

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    if local_input.dtype.is_int_unsigned():
        out = local_input
        return out
    elif local_input.dtype.is_standard_floating():
        pl.fmul(out, local_input, alpha)
    else:
        pl.mul(out, local_input, alpha, 0, pl.RM_DOWN, True)
    pl.gt_select(out, local_input, 0, local_input, out)
    return out

@jit
def relu(local_input, block_n, block_c, block_h,
         block_w, real_n, real_c, real_h, real_w):
    """
    relu 计算

        .. code-block:: python

            output = relu(local_input, block_n, block_c, block_h, block_w,
                          real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.maximum(out, local_input, 0)
    return out

@jit
def flog(local_input, block_n, block_c, block_h,
         block_w, real_n, real_c, real_h, real_w):
    """
    float log计算

        .. code-block:: python

            output = flog(local_input, block_n, block_c, block_h, block_w,
                          real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    if local_input.dtype.is_fp32():
        max_C = 1.175494351e-38
        max_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.maximum(max_out, local_input, max_C)
        exp_part_out = pl.make_tensor(block_shape, pl.int32, real_shape)
        pl.fexp_part(exp_part_out, max_out)
        C = 254
        sub_out = pl.make_tensor(block_shape, pl.int32, real_shape)
        pl.sub(sub_out, C, exp_part_out, 23, pl.RM_HALF_AWAY_FROM_ZERO, True)
        mul_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fmul(mul_out, sub_out.view(dtype=local_input.dtype), max_out)
        sub_out2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fsub(sub_out2, mul_out, 1.)
        taylor_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.flog_base(taylor_out, sub_out2)
        eq_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        C2 = 127
        C3 = 0
        C4 = 0xFF800000
        pl.eq_select(eq_out, local_input, C3, C4, taylor_out)
        sub_out3 = pl.make_tensor(block_shape, pl.int32, real_shape)
        pl.sub(sub_out3, exp_part_out, C2, 0, pl.RM_HALF_AWAY_FROM_ZERO, True)
        cast_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.cast(cast_out, sub_out3)
        mul_out2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fmul(mul_out2, cast_out, 0.69314718056)
        out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fadd(out, eq_out, mul_out2)
        return out
    elif local_input.dtype.is_fp16():
        max_C = 1.175494351e-38
        max_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.maximum(max_out, local_input, max_C)
        exp_part_out = pl.make_tensor(block_shape, pl.int16, real_shape)
        pl.fexp_part(exp_part_out, max_out)
        C = 30
        sub_out = pl.make_tensor(block_shape, pl.int16, real_shape)
        pl.sub(sub_out, C, exp_part_out, 10, pl.RM_HALF_AWAY_FROM_ZERO, True)
        mul_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fmul(mul_out, sub_out.view(dtype=local_input.dtype), max_out)
        sub_out2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fsub(sub_out2, mul_out, 1.)
        taylor_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.flog_base(taylor_out, sub_out2)
        eq_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        C2 = 15
        C3 = 0
        C4 = 0xFF800000
        pl.eq_select(eq_out, local_input, C3, C4, taylor_out)
        sub_out3 = pl.make_tensor(block_shape, pl.int16, real_shape)
        pl.sub(sub_out3, exp_part_out, C2, 0, pl.RM_HALF_AWAY_FROM_ZERO, True)
        cast_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.cast(cast_out, sub_out3)
        mul_out2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fmul(mul_out2, cast_out, 0.69314718056)
        out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fadd(out, eq_out, mul_out2)
        return out
    elif local_input.dtype.is_bf16():
        max_C = 1.175494351e-38
        max_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.maximum(max_out, local_input, max_C)
        exp_part_out = pl.make_tensor(block_shape, pl.int16, real_shape)
        pl.fexp_part(exp_part_out, max_out)
        C = 254
        sub_out = pl.make_tensor(block_shape, pl.int16, real_shape)
        pl.sub(sub_out, C, exp_part_out, 7, pl.RM_HALF_AWAY_FROM_ZERO, True)
        mul_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fmul(mul_out, sub_out.view(dtype=local_input.dtype), max_out)
        sub_out2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fsub(sub_out2, mul_out, 1.)
        taylor_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.flog_base(taylor_out, sub_out2)
        eq_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        C2 = 127
        C3 = 0
        C4 = 0xFF800000
        pl.eq_select(eq_out, local_input, C3, C4, taylor_out)
        sub_out3 = pl.make_tensor(block_shape, pl.int16, real_shape)
        pl.sub(sub_out3, exp_part_out, C2, 0, pl.RM_HALF_AWAY_FROM_ZERO, True)
        cast_out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.cast(cast_out, sub_out3)
        mul_out2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fmul(mul_out2, cast_out, 0.69314718056)
        out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
        pl.fadd(out, eq_out, mul_out2)
        return out
    else:
        pl.static_assert(False, "Unsupported DataType")

@jit
def mish_f32(local_input, block_n, block_c, block_h,
             block_w, real_n, real_c, real_h, real_w):
    """
    float32 mish 计算

        .. code-block:: python

            output = mish_f32(local_input, block_n, block_c, block_h, block_w,
                              real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    t_sel_max = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sel_min = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_add_sqr = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_add_c = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_div = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_mul_c = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    float_sqrt_max = 1.84467e+19 # SQRT(FLT_MAX)
    float_sqrt_min = 1.08420e-19 # SQRT(FLT_MIN)
    C1 = 1.0
    C2 = -2.0
    t_exp = pl.exp_no_overflow(local_input, block_n, block_c, block_h, block_w,
                               real_n, real_c, real_h, real_w)
    pl.gt_select(t_sel_max, t_exp, float_sqrt_max, float_sqrt_min, t_exp)
    pl.lt_select(t_sel_min, t_sel_max, float_sqrt_min, float_sqrt_min, t_sel_max);
    pl.fadd_sqr(t_add_sqr, t_sel_min, C1)
    pl.fadd(t_add_c, t_add_sqr, C1)
    pl.fdiv(t_div, local_input, t_add_c)
    pl.fmul(t_mul_c, t_div, C2)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fadd(out, local_input, t_mul_c)
    return out

@jit
def pow_f32(base, exponent, block_n, block_c, block_h,
            block_w, real_n, real_c, real_h, real_w):
    """
    float32 pow 计算

        .. code-block:: python

            output = pow_f32(local_input, exponent, block_n, block_c, block_h, block_w,
                             real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``exponent`` (`int`): exponent 参数

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    t_mul = pl.make_tensor(block_shape, base.dtype, real_shape)
    t_log = pl.flog(base, block_n, block_c, block_h, block_w,
                    real_n, real_c, real_h, real_w)
    pl.fmul(t_mul, t_log, exponent)
    return pl.exp_no_overflow(t_mul, block_n, block_c, block_h, block_w,
                              real_n, real_c, real_h, real_w)

@jit
def softplus_f32(local_input, beta, block_n, block_c, block_h,
                 block_w, real_n, real_c, real_h, real_w):
    """
    float32 softplus 计算

        .. code-block:: python

            output = softplus_f32(local_input, block_n, block_c, block_h, block_w,
                                  real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    t_mul = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_add = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sel = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_mul = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    threshold = 20.0
    if beta != 1:
        pl.fmul(t_mul, local_input, beta)
        t_exp = pl.exp_no_overflow(t_mul, block_n, block_c, block_h,
                                   block_w, real_n, real_c, real_h, real_w)
        pl.fadd(t_add, t_exp, 1.0)
        t_log = pl.flog(t_add, block_n, block_c, block_h, block_w,
                        real_n, real_c, real_h, real_w)
        pl.fdiv(t_sel, t_log, beta)
        pl.gt_select(out, local_input, threshold, local_input, t_sel)
    else:
        t_exp = exp_no_overflow(local_input, block_n, block_c, block_h,
                                block_w, real_n, real_c, real_h, real_w);
        pl.fadd(t_add, t_exp, 1.0)
        t_sel = pl.flog(t_add, block_n, block_c, block_h, block_w,
                        real_n, real_c, real_h, real_w)
        pl.gt_select(out, local_input, threshold, local_input, t_sel)
    return out

@jit
def softsign_fp32(local_input, block_n, block_c, block_h,
                  block_w, real_n, real_c, real_h, real_w):
    """
    float32 softsign 计算

        .. code-block:: python

            output = softsign_fp32(local_input, block_n, block_c, block_h, block_w,
                                   real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    abs_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    add_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.abs(abs_res, local_input)
    pl.fadd(add_res, add_res, 1.)
    pl.fdiv(out, local_input, add_res)
    return out


@jit
def sqrt_fp32(local_input, block_n, block_c, block_h,
              block_w, real_n, real_c, real_h, real_w):
    """
    float32 sqrt 计算

        .. code-block:: python

            output = sqrt_fp32(local_input, block_n, block_c, block_h, block_w,
                               real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    zero = 0.0
    if local_input.dtype.is_fp32():
        neg_zero = 0x80000000
    elif local_input.dtype.is_fp16():
        neg_zero = 0x8000
    elif local_input.dtype.is_bf16():
        neg_zero = 0x8000
    else:
        pl.static_assert(False, "Unsupported DataType");
    rsqrt = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sel_0 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sel_neg0 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    pl.frsqrt(rsqrt, local_input);
    pl.eq_select(sel_0, local_input, zero, zero, rsqrt);
    pl.eq_select(sel_neg0, local_input, neg_zero, zero, sel_0);
    pl.fmul(out, sel_neg0, local_input);
    return out

@jit
def fsin(local_input, block_n, block_c, block_h,
         block_w, real_n, real_c, real_h, real_w):
    """
    float sin 计算

        .. code-block:: python

            output = fsin(local_input, block_n, block_c, block_h, block_w,
                          real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    C = 0.15915494309189535 # 1.0 / (2.0 * PI)
    work = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    work1 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    work2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fmul(work, local_input, C)
    pl.round(work1, work, r_mode=pl.RM_HALF_AWAY_FROM_ZERO)
    pl.fsub(work2, work, work1)
    pl.fmul(work1, work2, work2)
    pl.fsin_base(work, work2)
    pl.fmul(out, work2, work)
    return out

@jit
def fcos(local_input, block_n, block_c, block_h,
         block_w, real_n, real_c, real_h, real_w):
    """
    float cos 计算

        .. code-block:: python

            output = fcos(local_input, block_n, block_c, block_h, block_w,
                          real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    C = 0.159154943091895335769 # 1.0 / (2.0 * PI)
    work = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    work1 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    work2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fmul(work, local_input, C)
    pl.round(work1, work, r_mode=pl.RM_HALF_AWAY_FROM_ZERO)
    pl.fsub(work2, work, work1)
    pl.fmul(work1, work2, work2)
    pl.fcos_base(out, work1)
    return out

@jit
def farcsin(local_input, block_n, block_c, block_h,
            block_w, real_n, real_c, real_h, real_w):
    """
    float arcsin 计算

        .. code-block:: python

            output = farcsin(local_input, block_n, block_c, block_h, block_w,
                             real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    if local_input.dtype.is_fp32():
        sign_mask = 0x80000000
    elif local_input.dtype.is_fp16():
        sign_mask = 0x8000
    elif local_input.dtype.is_bf16():
        sign_mask = 0x8000
    else:
        pl.static_assert(False, "Unsupported DataType");

    t_square = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_mul025 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_025sub = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sqrt1 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_05sub = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sqrt2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_arcsin = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_mul2 = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sign = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    pl.fmul(t_square, local_input, local_input)
    pl.fmul(t_mul025, t_square, 0.25)
    pl.fsub(t_025sub, 0.25, t_mul025)
    pl.fsqrt(t_sqrt1, t_025sub)
    pl.fsub(t_05sub, 0.5, t_sqrt1)
    pl.fsqrt(t_sqrt2, t_05sub)
    pl.farcsin_base(t_arcsin, t_05sub)
    pl.fmul(t_sqrt1, t_sqrt2, t_arcsin)
    pl.fmul(t_mul2, t_sqrt1, 2.0)
    pl.bitwise_and(t_sign, local_input, sign_mask)
    pl.bitwise_or(out, t_sign, t_mul2)
    return out

@jit
def farccos(local_input, block_n, block_c, block_h,
            block_w, real_n, real_c, real_h, real_w):
    """
    float arccos 计算

        .. code-block:: python

            output = farccos(local_input, block_n, block_c, block_h, block_w,
                             real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    PI_05 = 1.57079632679489661923
    out = farcsin(local_input, block_n, block_c, block_h,
                  block_w, real_n, real_c, real_h, real_w);
    pl.fsub(out, PI_05, out)
    return out

@jit
def ftan(local_input, block_n, block_c, block_h,
         block_w, real_n, real_c, real_h, real_w):
    """
    float tan 计算

        .. code-block:: python

            output = ftan(local_input, block_n, block_c, block_h, block_w,
                          real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    if local_input.dtype.is_fp32():
        sign_mask = 0x80000000
    elif local_input.dtype.is_fp16():
        sign_mask = 0x8000
    elif local_input.dtype.is_bf16():
        sign_mask = 0x8000
    else:
        pl.static_assert(False, "Unsupported DataType");

    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    C = 0.318309886183790671538 # 1.0 / PI
    C025 = 0.25
    C1 = 1
    C2 = 2

    t_mul = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_round = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_rem = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_abs = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sub = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_tanx_sub_025pi = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_c_div = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sub_c = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_and = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    pl.fmul(t_mul, local_input, C)
    pl.round(t_round, t_mul, r_mode=pl.RM_HALF_TO_EVEN)
    pl.fsub(t_rem, t_mul, t_round)
    pl.abs(t_abs, t_rem)
    pl.fsub(t_sub, t_abs, C025)
    pl.fmul(t_round, t_sub, t_sub)
    pl.ftan_base(t_abs, t_round)
    pl.fmul(t_tanx_sub_025pi, t_sub, t_abs)
    pl.fsub(t_sub, C1, t_tanx_sub_025pi)
    pl.fdiv(t_c_div, C2, t_sub)
    pl.fsub(t_sub_c, t_c_div, C1)
    pl.bitwise_and(t_and, t_rem, sign_mask)
    pl.bitwise_or(out, t_and, t_sub_c)
    return out

@jit
def fcot(local_input, block_n, block_c, block_h,
         block_w, real_n, real_c, real_h, real_w):
    """
    float cot 计算

        .. code-block:: python

            output = fcot(local_input, block_n, block_c, block_h, block_w,
                          real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    if local_input.dtype.is_fp32():
        sign_mask = 0x80000000
    elif local_input.dtype.is_fp16():
        sign_mask = 0x8000
    elif local_input.dtype.is_bf16():
        sign_mask = 0x8000
    else:
        pl.static_assert(False, "Unsupported DataType");

    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    C = 0.318309886183790671538 # 1.0 / PI
    C05 = 0.5
    C025 = 0.25
    C1 = 1
    C2 = 2

    t_mul = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_csub = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_round = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_rem = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_abs = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sub = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_tanx_sub_025pi = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_c_div = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_sub_c = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    t_and = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    pl.fmul(t_mul, local_input, C)
    pl.fsub(t_csub, C05, t_mul)
    pl.round(t_round, t_csub, r_mode=pl.RM_HALF_TO_EVEN)
    pl.fsub(t_rem, t_csub, t_round)
    pl.abs(t_abs, t_rem)
    pl.fsub(t_sub, t_abs, C025)
    pl.fmul(t_round, t_sub, t_sub)
    pl.ftan_base(t_abs, t_round)
    pl.fmul(t_tanx_sub_025pi, t_sub, t_abs)
    pl.fsub(t_sub, C1, t_tanx_sub_025pi)
    pl.fdiv(t_c_div, C2, t_sub)
    pl.fsub(t_sub_c, t_c_div, C1)
    pl.bitwise_and(t_and, t_rem, sign_mask)
    pl.bitwise_or(out, t_and, t_sub_c)
    return out

@jit
def sinh_fp32(local_input, block_n, block_c, block_h,
              block_w, real_n, real_c, real_h, real_w):
    """
    float32 sinh 计算

        .. code-block:: python

            output = sinh_fp32(local_input, block_n, block_c, block_h, block_w,
                               real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    div_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sub_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    exp_res = pl.exp_no_overflow(local_input, block_n, block_c, block_h, block_w,
                                 real_n, real_c, real_h, real_w)
    pl.fdiv(div_res, 1., exp_res)
    pl.fsub(sub_res, exp_res, div_res)
    pl.fmul(out, sub_res, 0.5)
    return out

@jit
def cosh_fp32(local_input, block_n, block_c, block_h,
              block_w, real_n, real_c, real_h, real_w):
    """
    float32 cosh 计算

        .. code-block:: python

            output = cosh_fp32(local_input, block_n, block_c, block_h, block_w,
                               real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    div_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    add_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    exp_res = pl.exp_no_overflow(local_input, block_n, block_c, block_h, block_w,
                                 real_n, real_c, real_h, real_w)
    pl.fdiv(div_res, 1., exp_res)
    pl.fadd(add_res, exp_res, div_res)
    pl.fmul(out, add_res, 0.5)
    return out

@jit
def tanh_fp32(local_input, block_n, block_c, block_h,
              block_w, real_n, real_c, real_h, real_w):
    """
    float32 tanh 计算

        .. code-block:: python

            output = tanh_fp32(local_input, block_n, block_c, block_h, block_w,
                               real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    add_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    div_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)

    pl.fadd(add_res, local_input, local_input)
    exp_res = pl.exp_no_overflow(add_res, block_n, block_c, block_h,
                                 block_w, real_n, real_c, real_h, real_w)
    pl.fadd(add_res, exp_res, 1.)
    pl.fdiv(div_res, 2., add_res)
    pl.fsub(out, 1., div_res)
    return out

@jit
def arcsinh_fp32(local_input, block_n, block_c, block_h,
                 block_w, real_n, real_c, real_h, real_w):
    """
    float32 arcsinh 计算

        .. code-block:: python

            output = arcsinh_fp32(local_input, block_n, block_c, block_h, block_w,
                                  real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    mul_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    add_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sqrt_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fmul(mul_res, local_input, local_input)
    pl.fadd(add_res, mul_res, 1.0)
    pl.fsqrt(sqrt_res, add_res)
    pl.fadd(add_res, sqrt_res, local_input)
    return pl.flog(add_res, block_n, block_c, block_h, block_w,
                real_n, real_c, real_h, real_w)

@jit
def arccosh_fp32(local_input, block_n, block_c, block_h,
                 block_w, real_n, real_c, real_h, real_w):
    """
    float32 arccosh 计算

        .. code-block:: python

            output = arccosh_fp32(local_input, block_n, block_c, block_h, block_w,
                                  real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    mul_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sub_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sqrt_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    add_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fmul(mul_res, local_input, local_input)
    pl.fsub(sub_res, mul_res, 1.0)
    pl.fsqrt(sqrt_res, sub_res)
    pl.fadd(add_res, sqrt_res, local_input)
    return pl.flog(add_res, block_n, block_c, block_h, block_w,
                real_n, real_c, real_h, real_w)

@jit
def arctanh_fp32(local_input, block_n, block_c, block_h,
                 block_w, real_n, real_c, real_h, real_w):
    """
    float32 arctanh 计算

        .. code-block:: python

            output = arctanh_fp32(local_input, block_n, block_c, block_h, block_w,
                                  real_n, real_c, real_h, real_w)

    参数:
        - ``local_input`` (`ppl.language.tensor`): input 张量

        - ``block_n`` (`int`): 张量memory shape的N

        - ``block_c`` (`int`): 张量memory shape的C

        - ``block_h`` (`int`): 张量memory shape的H

        - ``block_w`` (`int`): 张量memory shape的W

        - ``real_n`` (`int`): 张量实际shape的N

        - ``real_c`` (`int`): 张量实际shape的C

        - ``real_h`` (`int`): 张量实际shape的H

        - ``real_w`` (`int`): 张量实际shape的W
    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        实际shape在所有维度上必须小于或等于memory shape
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    add_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    sub_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    div_res = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    out = pl.make_tensor(block_shape, local_input.dtype, real_shape)
    pl.fadd(add_res, local_input, 1.)
    pl.fsub(sub_res, 1., local_input)
    pl.fdiv(div_res, add_res, sub_res)
    log_res = pl.flog(div_res, block_n, block_c, block_h, block_w,
                      real_n, real_c, real_h, real_w)
    pl.fmul(out, log_res, 0.5)
    return out

@jit
def pooling2(qk_sub_tensor,
             tmp_tensor,
             real_q_h,
             real_m,
             real_k,
             mode):
    """
    高性能池化计算

        .. code-block:: python

            output = pooling2(qk_sub_tensor, tmp_tensor, real_q_h, real_m, real_k, mode)

    参数:
        - ``qk_sub_tensor`` (`ppl.language.tensor`): input张量

        - ``tmp_tensor`` (`ppl.language.tensor`): 中间缓存张量

        - ``real_q_h`` (`int`): input张量实际shape的N

        - ``real_m`` (`int`): input张量实际shape的C

        - ``real_k`` (`int`): input张量实际shape的W

        - ``mode`` (`int`): 池化类型, 0: max 1:avg

    返回值:
        - ``output`` (`ppl.language.tensor`): output张量

    注意事项:
        无
    """
    eu_num = pl.get_eu_num(qk_sub_tensor.dtype)
    align_w = pl.cdiv(real_k, eu_num) * eu_num
    slice = align_w // eu_num
    h = 1
    if (align_w > real_k):
        tensor_mv_out = qk_sub_tensor.sub_view([real_q_h, real_m, 1, real_k + eu_num - align_w], [0, 0, 0, align_w - eu_num])
        tensor_mv_in = qk_sub_tensor.sub_view([real_q_h, real_m, 1, eu_num], [0, 0, 0, align_w - eu_num])
        pl.tiu.zero(tmp_tensor.view(shape=[real_q_h, real_m, 1, eu_num]))
        pl.tiu.move(tmp_tensor.view(shape=[real_q_h, real_m, 1, real_k + eu_num - align_w]), tensor_mv_out)
        pl.tiu.move(tensor_mv_in, tmp_tensor.view(shape=[real_q_h, real_m, 1, eu_num]))
    if mode == 0:
        pl.pool_max(tmp_tensor.view(shape=[real_q_h * h, real_m, 1, eu_num]), qk_sub_tensor.view(shape=[real_q_h * h, real_m, slice, eu_num]),
                    [slice, 1], [0,0,0,0], [1,1],[1,1])
    else:
        pl.pool_avg(tmp_tensor.view(shape=[real_q_h * h, real_m, 1, eu_num]), qk_sub_tensor.view(shape=[real_q_h * h, real_m, slice, eu_num]),
                    [slice, 1], [0,0,0,0], [1,1],[1,1], 1.0)

    max_out = pl.make_tensor([-1, -1, -1, -1], tmp_tensor.dtype)
    if mode == 0:
        pl.pool_max(max_out.view(shape=[real_q_h, real_m, h, 1]), tmp_tensor.view(shape=[real_q_h, real_m, h, eu_num]),
                [1, eu_num], [0,0,0,0], [1,1],[1,1])
    else:
        pl.pool_avg(max_out.view(shape=[real_q_h, real_m, h, 1]), tmp_tensor.view(shape=[real_q_h, real_m, h, eu_num]),
                [1, eu_num], [0,0,0,0], [1,1],[1,1], 1.0)
    return max_out

@jit
def quick_pooling(out_tensor,
             in_tensor,
             block_n,
             block_c,
             block_h,
             block_w,
             real_n,
             real_c,
             real_h,
             real_w,
             fill = 0,
             mode = 0,
             scale = 1):
    """
    高性能池化计算

        .. code-block:: python


    参数:

    返回值:

    注意事项:
        无
    """
    block_shape = [block_n, block_c, block_h, block_w]
    real_shape = [real_n, real_c, real_h, real_w]
    n = real_shape[0]
    c = real_shape[1]
    w = real_shape[3]
    h = 1
    eu_num = pl.get_eu_num(in_tensor.dtype)
    align_w = pl.cdiv(real_w, eu_num) * eu_num
    slice = align_w // eu_num
    if (align_w > w):
        fill_offset = [0,0,0,w]
        fill_shape = [n, c, 1, align_w - w]
        fill_tensor = in_tensor.sub_view(fill_shape, fill_offset)
        pl.tiu.fill(fill_tensor, fill)
    in_reduce_h = [n*h, c, slice, eu_num]
    out_reduce_h = [n*h, c, 1, eu_num]
    in_reduce_w = [n, c, h, eu_num]
    out_reduce_w = [n, c, h, 1]

    tmp_block_shape = [block_shape[0], block_shape[1], 1, eu_num]
    tmp_tensor = pl.make_tensor(tmp_block_shape, in_tensor.dtype)
    if mode == 0:
        pl.pool_max(tmp_tensor.view(shape=out_reduce_h), in_tensor.view(shape=in_reduce_h),
                    [slice, 1], [0,0,0,0], [1,1],[1,1])
    else:
        pl.pool_avg(tmp_tensor.view(shape=out_reduce_h), in_tensor.view(shape=in_reduce_h),
                    [slice, 1], [0,0,0,0], [1,1],[1,1], 1.0)

    if mode == 0:
        pl.pool_max(out_tensor.view(shape=out_reduce_w), tmp_tensor.view(shape=in_reduce_w),
                [1, eu_num], [0,0,0,0], [1,1],[1,1])
    else:
        pl.pool_avg(out_tensor.view(shape=out_reduce_w), tmp_tensor.view(shape=in_reduce_w),
                [1, eu_num], [0,0,0,0], [1,1],[1,1], scale)

@jit
def matmul_rtrans_mc_kernel(out_ptr, left_ptr, right_ptr,
                     batch: pl.constexpr,
                     M,
                     K,
                     N,
                     m_slice: pl.constexpr,
                     k_slice: pl.constexpr,
                     n_slice: pl.constexpr):
    """
    w16a16_matmul

        .. code-block:: python

            matmul_rtrans_mc_kernel(out_ptr, left_ptr, right_ptr, batch, M, K, N, m_slice, k_slice, n_slice)

    参数:
        - ``out_ptr`` (`ppl.language.tensor`): output张量

        - ``left_ptr`` (`ppl.language.tensor`): 左矩阵张量

        - ``right_ptr`` (`ppl.language.tensor`): 右矩阵张量(转置)

        - ``batch`` (`int`): output矩阵的batch

        - ``M`` (`int`): output矩阵的M

        - ``K`` (`int`): 左矩阵的K

        - ``N`` (`int`): output矩阵的N

        - ``m_slice`` (`int`): M的切分slice

        - ``k_slice`` (`int`): K的切分slice

        - ``n_slice`` (`int`): N的切分slice

    返回值:
        无

    注意事项:
        输入右矩阵转置
    """
    core_num = pl.get_core_num()
    index = pl.get_core_index()

    n_core_slice = pl.cdiv(N, core_num)
    n_per_core = min(n_core_slice, N - index * n_core_slice)
    if (n_per_core <= 0):
        pass

    n_core_offset = index * n_core_slice
    left_global_shape = [batch, M, 1, K]
    right_global_shape = [batch, N, 1, K]
    res_global_shape = [batch, M, 1, N]

    left_block_shape = [1, m_slice, 1, k_slice]
    right_block_shape = [1, n_slice, 1, k_slice]
    res_block_shape = [1, m_slice, 1, n_slice]

    left_gtensor = pl.gtensor(left_global_shape, pl.GLOBAL, left_ptr)
    right_gtensor = pl.gtensor(right_global_shape, pl.GLOBAL, right_ptr)
    res_gtensor = pl.gtensor(res_global_shape, pl.GLOBAL, out_ptr)

    m_secs = pl.cdiv(M, m_slice)
    n_secs = pl.cdiv(n_per_core, n_slice)
    k_secs = pl.cdiv(K, k_slice)

    m_stride = k_secs * n_secs
    n_stride = k_secs
    for i in range(batch):
        for count in range(m_stride * m_secs):
            pl.enable_pipeline()
            remain = count
            m_count = remain // m_stride
            remain %= m_stride
            n_count = remain // n_stride
            k_count = remain % n_stride

            idx_m = m_count * m_slice
            idx_n = n_count * n_slice
            idx_k = k_count * k_slice

            cur_m = min(m_slice, M - idx_m)
            cur_n = min(n_slice, n_per_core - idx_n)
            cur_k = min(k_slice, K - idx_k)

            left_real_shape = [1, cur_m, 1, cur_k]
            right_real_shape = [1, cur_n, 1, cur_k]
            res_real_shape = [1, cur_m, 1, cur_n]

            left_local = pl.make_tensor(left_block_shape, left_ptr.dtype, left_real_shape)
            right_local = pl.make_tensor(right_block_shape, right_ptr.dtype, right_real_shape)
            res_local = pl.make_tensor(res_block_shape, out_ptr.dtype, res_real_shape)
            left_offset = [i, idx_m, 0, idx_k]
            right_offset = [i, idx_n + n_core_offset, 0, idx_k]
            res_offset = [i, idx_m, 0, idx_n + n_core_offset]
            pl.dma.load(left_local,
                left_gtensor[i:i+1, idx_m:idx_m+cur_m, :, idx_k:idx_k+cur_k])
            pl.dma.load(right_local,
                right_gtensor.sub_view(right_real_shape, right_offset))

            pl.tiu.dot(res_local, left_local, right_local, rtrans=True)
            pl.dma.store(res_gtensor.sub_view(res_real_shape, res_offset),
                 res_local)

@jit
def rms_norm_kernel(ptr_out,
                    ptr_input,
                    ptr_weight,
                    ptr_bias,
                    eps,
                    with_weight:pl.constexpr,
                    with_bias,
                    _N,
                    _C:pl.constexpr,
                    _H,
                    _W,
                    block_w:pl.constexpr):
    """
    rms_norm

        .. code-block:: python

            rms_norm_kernel(ptr_out, ptr_input, ptr_weight, ptr_bias, eps, with_weight, with_bias, _N, _C, _H, _W, block_w)

    参数:
        - ``ptr_out`` (`ppl.language.tensor`): output张量

        - ``ptr_input`` (`ppl.language.tensor`): input张量

        - ``ptr_weight`` (`ppl.language.tensor`): weight张量

        - ``ptr_bias`` (`ppl.language.tensor`): bias张量

        - ``eps`` (`标量`): eps

        - ``with_weight`` (`bool`): 是否有weight

        - ``with_bias`` (`bool`): 是否有bias

        - ``_N`` (`int`): input张量的N

        - ``_C`` (`int`): input张量的C

        - ``_H`` (`int`): input张量的H

        - ``_W`` (`int`): input张量的W

        - ``block_w`` (`int`): input张量的切分W

    返回值:
        无

    注意事项:
        无
    """
    core_idx = pl.get_core_index()
    core_num = pl.get_core_num()

    if core_idx < core_num:
      C = _N * _C
      W = _H * _W
      c_per_core = (C + core_num - 1) // core_num
      c_start = core_idx * c_per_core
      c_end = min(c_start + c_per_core, C)
      block_c = 64

      global_shape = [1, c_per_core, 1, W]
      global_weight_shape = [1,1,1,W]
      in_gtensor = pl.gtensor(global_shape, pl.GLOBAL, ptr_input)
      weight_gtensor = pl.gtensor(global_weight_shape, pl.GLOBAL, ptr_weight)
      bias_gtensor = pl.gtensor(global_weight_shape, pl.GLOBAL, ptr_bias)
      out_gtensor = pl.gtensor(global_shape, pl.GLOBAL, ptr_out)

      local_block_shape = [1, block_c, 1, block_w]
      local_avg_block_shape = [1, block_c, 1, 1]
      local_weight_shape = [1,1,1,block_w]
      for c_idx in range(c_start, c_end, block_c):
        c = min(block_c, c_end - c_idx)
        local_avg_shape = [1,c,1,1]
        avg_buffer = pl.make_tensor(local_avg_block_shape, pl.float32, local_avg_shape)
        pl.tiu.fill(avg_buffer, eps)

        for w_idx in range(0, W, block_w):
          pl.enable_pipeline()
          w = min(block_w, W - w_idx)
          local_in_shape = [1,c,1,w]
          input_global_offset = [0, c_idx, 0, w_idx]


          local_in = pl.make_tensor(local_block_shape, ptr_input.dtype, local_in_shape)
          pl.dma.load(local_in, in_gtensor.sub_view(local_in_shape, input_global_offset))

          local_in_fp32 = pl.make_tensor(local_block_shape, pl.float32, local_in_shape)
          pl.tiu.cast(local_in_fp32, local_in)

          local_in_tmp = pl.make_tensor(local_block_shape, pl.float32, local_in_shape)
          pl.tiu.fmul(local_in_tmp, local_in_fp32, local_in_fp32)
          sub_avg = pl.make_tensor(local_avg_block_shape, pl.float32, local_avg_shape)

          pl.quick_pooling(sub_avg, local_in_tmp, 1, block_c, 1, block_w, 1, c, 1, w, 0, 1, 1.0 / W)
          pl.tiu.fadd(avg_buffer, avg_buffer, sub_avg)

        local_mu = pl.make_tensor(local_avg_block_shape, pl.float32, local_avg_shape)
        pl.tiu.frsqrt(local_mu, avg_buffer, num_iter = 4)

        for w_idx in range(0, W, block_w):
          pl.enable_pipeline()
          w = min(block_w, W - w_idx)
          local_in_shape = [1,c,1,w]
          input_global_offset = [0, c_idx, 0, w_idx]

          local_in = pl.make_tensor(local_block_shape, ptr_input.dtype, local_in_shape)
          pl.dma.load(local_in, in_gtensor.sub_view(local_in_shape, input_global_offset))

          local_in_fp32_2 = pl.make_tensor(local_block_shape, pl.float32, local_in_shape)
          pl.tiu.cast(local_in_fp32_2, local_in)

          out_fp32 = pl.make_tensor(local_block_shape, pl.float32, local_in_shape)
          pl.tiu.fmul(out_fp32, local_in_fp32_2, local_mu)

          if with_weight:
            weight_offset = [0, 0, 0, w_idx]
            weight_real_shape = [1, 1, 1, w]
            local_weight_sub = pl.make_tensor(local_weight_shape, ptr_weight.dtype, weight_real_shape)
            pl.dma.load(local_weight_sub, weight_gtensor.sub_view(weight_real_shape, weight_offset))
            local_weight_sub_fp32 = pl.make_tensor(local_weight_shape, pl.float32, weight_real_shape)
            pl.tiu.cast(local_weight_sub_fp32, local_weight_sub)
            tmp_fp32 = pl.make_tensor(local_block_shape, pl.float32, local_in_shape)
            pl.tiu.broadcast(tmp_fp32, local_weight_sub_fp32)
            pl.tiu.fmul(out_fp32, out_fp32, tmp_fp32)

          if with_bias:
            bias_offset = [0, 0, 0 ,w_idx]
            bias_real_shape = [1, 1, 1, w]
            local_bias_sub = pl.make_tensor(local_weight_shape, ptr_bias.dtype, bias_real_shape)
            pl.dma.load(local_bias_sub, bias_gtensor.sub_view(bias_real_shape, bias_offset))
            local_bias_sub_fp32 = pl.make_tensor(local_weight_shape, pl.float32, bias_real_shape)
            pl.tiu.cast(local_bias_sub_fp32, local_bias_sub)
            tmp_fp32 = pl.make_tensor(local_block_shape, pl.float32, local_in_shape)
            pl.tiu.broadcast(tmp_fp32, local_bias_sub_fp32)
            pl.tiu.fadd(out_fp32, out_fp32, tmp_fp32)
          out = pl.make_tensor(local_block_shape, ptr_out.dtype, local_in_shape)
          pl.tiu.cast(out, out_fp32)
          pl.dma.store(out_gtensor.sub_view(local_in_shape, input_global_offset), out)

@jit
def mlp_kernel(out_ptr, input_ptr, weight0_ptr, weight1_ptr, weight2_ptr,
                batch: pl.constexpr,
                input_w: pl.constexpr,
                middle_w: pl.constexpr,
                block_b: pl.constexpr,
                block_iw: pl.constexpr,
                block_w: pl.constexpr):
    """
    mlp

        .. code-block:: python

            mlp_kernel(out_ptr, input_ptr, weight0_ptr, weight1_ptr, weight2_ptr, batch, input_w, middle_w, block_b, block_iw, block_w)

    参数:
        - ``out_ptr`` (`ppl.language.tensor`): output张量

        - ``input_ptr`` (`ppl.language.tensor`): input张量

        - ``weight0_ptr`` (`ppl.language.tensor`): weight0张量

        - ``weight1_ptr`` (`ppl.language.tensor`): weight1张量

        - ``weight2_ptr`` (`ppl.language.tensor`): weight2张量

        - ``batch`` (`int`): input张量的C

        - ``input_w`` (`int`): input张量的W

        - ``middle_w`` (`int`): weight0张量的W

        - ``block_b`` (`int`): input张量的切分C

        - ``block_iw`` (`int`): input张量的切分W

        - ``block_w`` (`int`): weight0张量的切分W

    返回值:
        无

    注意事项:
        无
    """
    core_num = pl.get_core_num()
    core_idx = pl.get_core_index()
    b_loop = pl.cdiv(batch, pl.LANE_NUM())
    for b_idx in range(b_loop):
        b_offset = b_idx * pl.LANE_NUM()
        b_slice = min(pl.LANE_NUM(), batch - b_offset)
        g_input_shape = [1, batch, 1, input_w]
        g_offset = [0, b_offset, 0, 0]

        slice_per_core = pl.cdiv(middle_w, core_num)
        core_offset = slice_per_core * core_idx
        slice_per_core = min(slice_per_core, middle_w - core_offset)
        input_shape = [1, b_slice, 1, input_w]
        input_block_shape = [1, block_b, 1, block_iw]
        l2_out_tensor = pl.gtensor(input_block_shape, pl.L2, dtype=pl.float16).view(shape=input_shape)
        if (slice_per_core > 0):
            weight0_global_shape = [1, input_w, 1, middle_w]
            weight2_global_shape = [1, middle_w, 1, input_w]

            weight0_block_shape = [1, block_iw, 1, block_w]
            weight2_block_shape = [1, block_w, 1, block_iw]
            middle_buffer_shape = [1, block_b, 1, block_w]

            input_gtensor = pl.gtensor(g_input_shape, pl.GLOBAL, input_ptr).sub_view(input_shape, g_offset)

            weight0_gtensor = pl.gtensor(weight0_global_shape, pl.GLOBAL, weight0_ptr)
            weight1_gtensor = pl.gtensor(weight0_global_shape, pl.GLOBAL, weight1_ptr)
            weight2_gtensor = pl.gtensor(weight2_global_shape, pl.GLOBAL, weight2_ptr)

            input_local = pl.make_tensor(input_block_shape, input_ptr.dtype, input_shape)
            out_f32_local = pl.make_tensor(input_block_shape, pl.float32, input_shape)

            pl.dma.load(input_local, input_gtensor)
            pl.dma.fill(out_f32_local, 0)

            for w_idx in range(0, slice_per_core, block_w):
                pl.enable_pipeline()
                middle_slice = min(block_w, slice_per_core - w_idx)
                weight0_shape = [1, input_w, 1, middle_slice]
                weight2_shape = [1, middle_slice, 1, input_w]
                weight0_offset = [0, 0, 0, core_offset + w_idx]
                weight2_offset = [0, core_offset + w_idx, 0, 0]
                weight0_local = pl.make_tensor(weight0_block_shape, pl.float16, weight0_shape)
                weight1_local = pl.make_tensor(weight0_block_shape, pl.float16, weight0_shape)
                weight2_local = pl.make_tensor(weight2_block_shape, pl.float16, weight2_shape)

                pl.dma.load(weight0_local, weight0_gtensor.sub_view(weight0_shape, weight0_offset))
                pl.dma.load(weight1_local, weight1_gtensor.sub_view(weight0_shape, weight0_offset))
                pl.dma.load(weight2_local, weight2_gtensor.sub_view(weight2_shape, weight2_offset))
                middle_real_shape = [1, b_slice, 1, middle_slice]
                middle_buffer_f16_local_1 = pl.make_tensor(middle_buffer_shape, pl.float16, middle_real_shape)
                middle_buffer_f16_local_2 = pl.make_tensor(middle_buffer_shape,  pl.float16, middle_real_shape)
                middle_buffer_f32_local = pl.make_tensor(middle_buffer_shape,  pl.float32, middle_real_shape)

                #matmul -> x f16
                pl.tiu.fmm2(middle_buffer_f16_local_1, input_local, weight1_local, out_dtype=pl.float16)
                # neg -> -x f16
                pl.tiu.fmul(middle_buffer_f16_local_2, middle_buffer_f16_local_1, -1.0)
                # cast -> f16 2 f32
                pl.tiu.cast(middle_buffer_f32_local, middle_buffer_f16_local_2, type=pl.float32)
                # exp -> exp^-x f32
                middle_buffer_f32_local = pl.exp_no_overflow(middle_buffer_f32_local, 1, block_b, 1, block_w,
                                                            1, b_slice, 1, middle_slice)

                # add -> 1 + exp^-x f32
                pl.tiu.fadd(middle_buffer_f32_local, middle_buffer_f32_local, 1.0)
                # div -> 1/(1 + exp^-x)  f32
                pl.tiu.fdiv(middle_buffer_f32_local, 1.0, middle_buffer_f32_local, num_iter=4)
                # cast -> f32 2 f16
                pl.tiu.cast(middle_buffer_f16_local_2, middle_buffer_f32_local, type=pl.float16)
                # mul -> x/(1+exp^-x) f16
                pl.tiu.fmul(middle_buffer_f16_local_1, middle_buffer_f16_local_1,  middle_buffer_f16_local_2)
                # matmul -> x1 f16
                pl.tiu.fmm2(middle_buffer_f16_local_2, input_local, weight0_local, out_dtype=pl.float16)
                # mul -> x1 * x/(1+exp^-x) f16
                pl.tiu.fmul(middle_buffer_f16_local_1, middle_buffer_f16_local_1,  middle_buffer_f16_local_2)
                # matmul -> out f32
                pl.tiu.fmm2(out_f32_local, middle_buffer_f16_local_1, weight2_local, result_add=True, out_dtype=pl.float32)

            pl.tiu.cast(input_local, out_f32_local, type=input_ptr.dtype)
            pl.dma.zero(l2_out_tensor)
            pl.sync()
            pl.dma.reduce(l2_out_tensor, input_local, pl.ALL_REDUCE_PSUM_WR, pl.ALL_REDUCE_ADD)

        ele_num = b_slice * input_w
        slice_per_core = pl.cdiv(ele_num, core_num)
        core_offset = slice_per_core * core_idx
        slice_per_core = min(slice_per_core, ele_num - core_idx * slice_per_core)
        if (slice_per_core > 0):
            output_shape = [1, 1, 1, b_slice * input_w]
            output_gtensor = pl.gtensor(g_input_shape, pl.GLOBAL, out_ptr).sub_view(output_shape, g_offset)
            real_shape = [1, 1, 1, slice_per_core]
            offset = [0, 0, 0, core_offset]
            pl.sync()
            pl.sdma.move(output_gtensor.sub_view(real_shape, offset), l2_out_tensor.view(shape=output_shape).sub_view(real_shape, offset))
            pl.sync()
