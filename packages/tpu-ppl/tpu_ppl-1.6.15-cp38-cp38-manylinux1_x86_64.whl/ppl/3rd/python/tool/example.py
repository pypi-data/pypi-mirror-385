#!/usr/bin/env python3

Y, N = True, False

unittest_list = {
    # (filename,                                              bm1684x, bm1688, bm1690, sg2260e, sg2262, 2262rv, masr3, bm1684xe, bm1684x2, bm1684x2rv)
    #                                                         [base, full]
    "regression/unittest/arith":
      [
       ("arith.pl",                                              Y,       Y,      Y,      Y,      N,      Y,     N,      N,     N,     Y),
      ],
    "regression/unittest/attention":
      [("rotary_embedding_static.pl",                            N,       N,      N,      N,      N,      N,     N,     N,     N,     N),
       ("mlp_left_trans_multicore.pl",                           N,       N,      Y,      N,      N,      N,     N,     N,     N,     N)],
    "regression/unittest/cmp":
      [("cmp.pl",                                                Y,       N,      Y,      Y,      N,      Y,     N,     N,     N,     N),],
    "regression/unittest/conv":
      [("Conv2D.pl",                                             Y,       N,      Y,      N,      N,      N,     N,     N,     N,     N),],
    "regression/unittest/dma":
      [("dma_test.pl",                                           Y,       Y,      Y,      Y,      N,      Y,     N,     N,     Y,     Y),
       ("dma_nonzero_l2s.pl",                                  [N,Y],     N,      N,      N,      N,      N,     N,     N,     N,     N),
       ("dma_nonzero_s2s.pl",                                  [N,Y],     N,      N,      N,      N,      N,     N,     N,     N,     N),],
    "regression/unittest/gather_scatter":
      [
       ("gather_test.pl",                                        Y,       N,      Y,      Y,      N,      Y,     N,     N,     N,     Y),
       ("scatter_test.pl",                                       Y,       N,      Y,      Y,      N,      Y,     N,     N,     N,     Y),
      ],
    "regression/unittest/hau":
      [
       ("hau.pl",                                                Y,       Y,      Y,      N,      N,      N,     N,     N,     N,     N),
      ],
    "regression/unittest/lin":
      [
       ("lin.pl",                                                N,       N,      N,      N,      N,      Y,     N,     N,     N,     N),
      ],
    "regression/unittest/reduce":
      [
       ("reduce.pl",                                             N,       N,      N,      N,      N,      Y,     N,     N,     N,     Y),
      ],
    "regression/unittest/special":
      [
        ("mask_select.pl",                                      [N,Y],    N,      Y,      Y,      N,      Y,     N,     N,     N,     Y),
        ("special.pl",                                            Y,      N,      N,      N,      N,      N,     N,     N,     N,     N),
        ],
    "regression/unittest/matmul":
      [("matmul.pl",                                             Y,       Y,      Y,      Y,      N,      Y,     Y,     Y,     N,     Y),
       ("mm_fp32.pl",                                          [N,Y],     N,      N,      N,      N,      N,     N,     N,     N,     N),],
    "regression/unittest/npu":
      [("npu_bcast_fp16.pl",                                   [N,Y],     N,      N,      N,    [N,Y],    N,     N,     N,     N,     N),],
    "regression/unittest/round":
      [("round_bf16.pl",                                       [N,Y],     N,      N,      N,      N,      N,     N,     N,     N,     N),],
    "regression/unittest/rqdq":
      [
       ("dq_test.pl",                                            Y,       Y,      Y,      Y,      Y,      Y,     N,     N,     Y,     Y),
       ("rq_test.pl",                                            Y,       Y,      Y,      Y,      Y,      Y,     N,     N,     Y,     Y),
      ],
    "regression/unittest/scalebias":
      [("fp_scale_bias_bf16.pl",                               [N,Y],     N,      N,      N,      N,      N,     N,     N,     N,     N),],
    "regression/unittest/sdma":
      [("sdma.pl",                                               N,       N,      Y,      Y,      N,      N,     N,     N,     Y,     N),],
    "regression/unittest/unary":[],
    "regression/unittest/fileload":
      [("read.pl",                                               Y,       N,      N,      N,      N,      N,     N,     N,    N,    N),],
    "regression/unittest/pool":
      [("pool2d.pl",                                           [N,Y],     N,      Y,      Y,      N,      Y,     N,     N,    N,    N),],
    "regression/unittest/func":
      [
        ("active.pl",                                            Y,       Y,      Y,      Y,      Y,      Y,     Y,     N,    Y,    Y),
      ]
}

examples_list = {
    # (filename,                                            bm1684x, bm1688, bm1690, sg2260e, sg2262, 2262rv, masr3, bm1684xe, bm1684x2, bm1684x2rv)
    #                                                       [base, full]
    "examples/cxx/arith":
      [("add_c_dual_loop.pl",                                    N,       N,      N,      N,      N,      N,     N,     N,     N,     N),
       ("add_dyn_block.pl",                                      Y,       Y,      Y,      N,      N,      N,     Y,     N,     N,     N),
       ("add_pipeline.pl",                                       N,       N,    [N,Y],    N,      N,      N,     Y,     N,     N,     N),
       ("add_broadcast.pl",                                      N,       N,    [N,Y],    Y,    [N,Y],    Y,     Y,     N,     Y,     Y),
      ],
    "examples/cxx/llm":
      [("attention_dyn.pl",                                      Y,       Y,      Y,      N,      N,      N,     N,     N,     N,    N),
       ("exp.pl",                                                Y,       N,      Y,      Y,      N,      Y,     N,     N,     N,    Y),
       ("rope.pl",                                               Y,       N,      Y,      Y,      N,      Y,     N,     N,     N,    N),
       ("flash_attention.pl",                                    Y,       N,      N,      N,      N,      N,     N,     N,     N,    N),
       ("rmsnorm.pl",                                            Y,       N,      Y,      Y,      N,      Y,     N,     N,     N,    Y),
       ("mlp_multicore.pl",                                      N,       N,      Y,      N,      N,      N,     N,     N,     N,    N),
       ("swi_glu.pl",                                            Y,       N,      N,      N,    [N,Y],    N,     N,     N,     Y,    N),
       ("flash_attention_backward_multicore.pl",                 N,       N,    [N,Y],    N,    [N,Y],    N,     N,     N,     Y,    N),
       ("flash_attention_GQA_multicore.pl",                      N,       N,      Y,      Y,      Y,      Y,     N,     N,     Y,    Y),
       ("paged_attention_multicore.pl",                          N,       N,      Y,      N,      N,      N,     N,     N,     N,    N),
      ],
    "examples/cxx/llm/tgi":
      [("w4a16_matmul.pl",                                       N,       N,      Y,      Y,      N,      N,     N,     N,     N,    N),
       ("rmsnorm_small_row.pl",                                  N,       N,      Y,      N,      N,      N,     N,     N,     N,    N)
      ],
    "examples/cxx/llm/flash_attention_fp8":
      [
       ("attention_qkv_decode_fp8.pl",                           N,       N,      N,      N,      Y,      Y,     N,     N,     Y,    Y),
      ],
    "examples/cxx/moe":
      [
       ("mla_multi_core.pl",                                     N,       N,      Y,      Y,      N,      N,     N,     N,    N,    N),
       ("moe_multi_core.pl",                                     N,       N,      Y,      Y,      N,      N,     N,     N,    N,    N),
      ],
    "examples/cxx/matmul":
      [("mm2_fp16_sync.pl",                                      N,       N,      Y,      Y,      N,      N,     N,     N,    N,    N),
       ("mm.pl",                                               [N,Y],     N,      N,      N,      N,      N,     N,     N,    N,    N),
      ],
    "examples/cxx/activation":
      [("softmax_h_dim.pl",                                      Y,       N,    [N,Y],    N,      N,      N,     N,     N,    N,    N),],
}

full_pl_list = {**unittest_list, **examples_list}

sample_list = {
    # (filename,                      bm1684x, bm1688, bm1690, sg2260e, sg2262, 2262rv, mars3, bm1684xe, bm1684x2, bm1684x2rv)
    "samples/add_pipeline":
      [
        ("test",                         Y,       N,      Y,      N,      N,      N,      N,     N,     N,    N),
      ],
    "samples/llama2":
      [
        ("test",                         Y,       N,      N,      N,      N,      N,      N,     N,     N,    N),
      ],
    "regression/unittest/pl_with_cpp":
      [
        ("test",                         Y,       N,      N,      N,      N,      N,      N,     N,     N,    N),
      ],
    "regression/unittest/torch_tpu":
      [
        ("test",                         N,       N,      Y,      N,      N,      N,      N,     N,     N,    N),
      ],
    "regression/unittest/tpu_mlir":
      [
        ("test",                         N,       N,      Y,      N,      N,      N,      N,     N,     N,    N),
      ],
    "regression/unittest/torch_tpu_built_in_mode":
      [
        ("test",                         N,       N,      N,      Y,      N,      N,      N,     N,     N,    N),
      ],
}

python_list = {
    # (filename,                      bm1684x, bm1688, bm1690, sg2260e, sg2262, 2262rv, mars3, bm1684xe, bm1684x2, bm1684x2rv)
    "examples/python":
      [("01-element-wise.py",            Y,       Y,      Y,      Y,      Y,      N,      Y,     Y,     Y,     N),
       ("02-avg-max-pool.py",            Y,       Y,      N,      N,      N,      N,      N,     N,     N,     N),
       ("03-conv.py",                    Y,       Y,      Y,      N,      Y,      N,      N,     N,     Y,     N),
       ("04-matmul.py",                  Y,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("04-matmul-bm1688.py",           N,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("05-attention-GQA.py",           Y,       N,      Y,      N,      Y,      N,      N,     N,     Y,     N),
       ("06-gather-scatter.py",          Y,       Y,      Y,      N,      N,      N,      N,     Y,     N,     N),
       ("07-arange_broadcast.py",        Y,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("09-dma.py",                     Y,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("10-vc-op.py",                   Y,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("11-tiu-funcs.py",               Y,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("13-hau.py",                     Y,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("14-sdma.py",                    N,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("15-rq-dq.py",                   Y,       N,      Y,      N,      Y,      N,      N,     N,     N,     N),
       ("15-rq-dq-bm1688-bm1690.py",     N,       N,      N,      N,      N,      N,      N,     N,     N,     N),
       ("19_autotiling.py",              N,       N,      Y,      N,      N,      N,      N,     N,     N,     N),
       ("add_const_fp.py",               N,       N,      Y,      N,      N,      N,      N,     N,     N,     N),
       ],
}
