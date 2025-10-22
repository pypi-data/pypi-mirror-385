import os
import argparse
import numpy as np
import sys

def update_chip_kwargs(kwargs, chip):
  if chip == "bm1684x" or chip == "bm1690" or chip == "bm1684xe" or chip == "sg2260e":
    kwargs.update({"lane_num": 64})
    kwargs.update({"eu_num": 64})
  elif chip == "sg2262":
    kwargs.update({"lane_num": 16})
    kwargs.update({"eu_num": 32})
  elif chip == "sg2262rv":
    kwargs.update({"lane_num": 16})
    kwargs.update({"eu_num": 32})
  elif chip == "bm1688":
    kwargs.update({"lane_num": 32})
    kwargs.update({"eu_num": 16})
  elif chip == "mars3":
    kwargs.update({"lane_num": 8})
    kwargs.update({"eu_num": 16})
  elif chip == "bm1684x2":
    kwargs.update({"lane_num": 16})
    kwargs.update({"eu_num": 32})
  elif chip == "bm1684x2rv":
    kwargs.update({"lane_num": 16})
    kwargs.update({"eu_num": 32})
  else:
    raise ValueError(f"Unsupported chip: {chip}")

def test_processor(test_func):
    def wrapper(*args, **kwargs):
        parser = argparse.ArgumentParser()
        parser.add_argument("--path", type=str, default="./", help="target npz file path")
        parser.add_argument("--dir", type=str, help="target main function")
        parser.add_argument("--tole", type=str, default = "0.99,0.99", help="cos euc")
        parser.add_argument("--chip", type=str, default = "bm1684x", help="chip")

        cmd_args = parser.parse_args()

        dir = kwargs.get('dir') if 'dir' in kwargs else cmd_args.dir
        tole = kwargs.get('tole') if 'tole' in kwargs else cmd_args.tole
        inp_npz = cmd_args.path + f"test_{dir}/data/{dir}_input.npz"
        ori_npz = cmd_args.path + f"test_{dir}/data/{dir}_tar.npz"
        out_npz = "torch.npz"
        tpu_out = np.load(inp_npz)

        chip = kwargs.get('chip', cmd_args.chip)
        kwargs.update({'chip': chip})
        update_chip_kwargs(kwargs, chip)
        dic = test_func(tpu_out, **kwargs)

        np.savez(out_npz, **dic)
        cmd = ["npz_help.py", "compare", ori_npz, out_npz, "-vv --tolerance", tole]
        ret = os.system(" ".join(cmd))
        if ret != 0:
            sys.exit(1)
    return wrapper
