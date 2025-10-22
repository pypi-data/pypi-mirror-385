
from __future__ import annotations

from ..runtime.jit import jit
from . import core
import ppl.language as pl

@jit
def get_stride(N, C, H, W, align_mode, start_idx, eu_num):
  stride_n = 1
  stride_c = 1
  stride_h = 1
  stride_w = 1
  if align_mode is pl.TPU_ALIGN:
    stride_h = W
    stride_c = H * stride_h
    stride_c = pl.align(stride_c, eu_num)
    stride_n = pl.cdiv(start_idx + C, pl.LANE_NUM()) * stride_c
    stride_w = 1
  elif align_mode is pl.TPU_COMPACT:
    stride_h = W
    stride_c = H * stride_h
    stride_n = pl.cdiv(start_idx + C, pl.LANE_NUM()) * stride_c
    stride_w = 1
  elif align_mode is pl.TPU_ROW_ALIGN:
    stride_w = 1
    stride_h = pl.align(W, eu_num)
    stride_c = H * stride_h
    stride_n = pl.cdiv(start_idx + C, pl.LANE_NUM()) * stride_c
  else:
    stride_n = C * H * W
    stride_c = H * W
    stride_h = W
    stride_w = 1
  return (stride_n, stride_c, stride_h, stride_w)

@jit
def aligned_stride_4d(N, C, H, W, align_mode, start_idx, dtype):
    """
    获取tensor的stride

        .. code-block:: python

            stride_n, stride_c, stride_h, stride_w = aligned_stride_4d(N, C, H, W, start_idx, dtype)

    参数:
        - ``N`` (`标量`):张量的N维度

        - ``C`` (`标量`):张量的C维度

        - ``H`` (`标量`):张量的H维度

        - ``W`` (`标量`):张量的W维度

        - ``align_mode`` (`pl.align_mode`):对齐模式

        - ``start_idx`` (`标量`):C的开始索引

        - ``dtype`` (`pl.dtype`): tensor数据类型

    返回值:
        - ``stride_n, stride_c, stride_h, stride_w`` (`tuple`):张量对应维度的stride

    注意事项:
        无
    """
    eu_num = pl.get_eu_num(dtype)
    return get_stride(N, C, H, W, align_mode, start_idx, eu_num)
