import os, sys
import torch
import shutil
import subprocess
import functools
from pathlib import Path
from torch.utils.cpp_extension import load
from .ppl_types import Chip
from .cache import LRUCache, default_cache_dir, get_folder_size
from tool.config import get_chip_code


def _os_system_log(cmd_str):
    # use subprocess to redirect the output stream
    # the file for saving the output stream should be set if using this function
    print("[Running]: {}".format(cmd_str))

    process = subprocess.run(
        cmd_str,
        shell=True,
        stdin=subprocess.PIPE,
        #  stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    ret = process.returncode
    if ret == 0 and process.stderr.find("error") == -1:
        print("[Success]: {}".format(cmd_str))
    else:
        print(process.stdout)
        print(process.stderr)
        raise RuntimeError("[!Error]: {}".format(cmd_str))


def _os_system(cmd: list, save_log: bool = False, inner_info: bool = True):
    cmd_str = ""
    for s in cmd:
        cmd_str += str(s) + " "
    if not save_log:
        print("[Running]: {}".format(cmd_str))
        if inner_info:
            ret = os.system(cmd_str)
        else:
            process = subprocess.run(cmd_str,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)
            ret = process.returncode
            if "error" in process.stderr.lower():
                print(process.stderr)
                raise RuntimeError("[!Error]: {}".format(cmd_str))
        if ret == 0:
            print("[Success]: {}".format(cmd_str))
        else:
            raise RuntimeError("[!Error]: {}".format(cmd_str))
    else:
        _os_system_log(cmd_str)

def build_code(work_path, build_debug, name, sources, chip=None, extra_cflags=None,
               extra_plflags=None, extra_ldflags=None, extra_include_paths=None):
    if isinstance(chip, Chip):
        chip_name = chip.str
    elif isinstance(chip, str):
        chip_name = chip
    elif chip is None:
        chip_name = os.getenv("CHIP", default="bm1684x")
    else:
        raise ValueError("chip must be a string or ppl.Chip")
    chip_code = get_chip_code(chip_name)
    ppl_root = os.environ["PPL_PROJECT_ROOT"]
    cur_dir = os.environ["PWD"]
    build_path = os.path.join(work_path, "build")

    if os.path.exists(work_path):
        shutil.rmtree(work_path)
    os.makedirs(work_path)
    # split to pl and cpp
    cpp_files = []
    for src in sources:
        if not os.path.exists(src):
            print("[ERROR] file {} not exists!".format(src))
            exit(1)
        if src.endswith(".pl"):
            pl_file = src
        elif src.endswith(".cpp"):
            cpp_files.append(src)
    # compile pl file
    cmd = [
        "ppl-compile", pl_file, "--print-debug-info", "--print-ir",
        "--chip {}".format(chip_code), "--O2", "--mode=2",
        "--o {}".format(work_path)
    ]
    _os_system(cmd, True)
    cmake_file = os.path.join(ppl_root, "deps/scripts/torch.cmake")
    shutil.copy(cmake_file, os.path.join(work_path, "CMakeLists.txt"))
    if not cpp_files:
        raise ValueError("tiling.cpp not found.")
    for f in cpp_files:
        shutil.copy(f, os.path.join(work_path, "host"))
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    os.chdir(build_path)
    # use torch libs
    torch_extra = ""
    torch_lib_path = os.environ.get('TORCH_TPU_RUNTIME_PATH')
    if torch_lib_path is not None:
        torch_extra = f"-DRUNTIME_PATH={os.path.dirname(torch_lib_path)}"
    _os_system([
        f"cmake .. -DDEBUG={build_debug} -DCHIP={chip_code} -DOUT_NAME={name} {torch_extra}"
        # + (f" -DEXTRA_PLFLAGS={':'.join(extra_plflags)}" if extra_plflags else "")  # todo
    ])
    _os_system(["make install"])
    os.chdir(cur_dir)
    return

class pl_extension:
    cache = LRUCache(cache_folde="cxx")
    @cache.register(cache_fn=build_code)
    @staticmethod
    def load(name, sources, chip=None, extra_cflags=None, extra_plflags=None,
             extra_ldflags=None, extra_include_paths=None):
        """
        Load and compile an extension module.

        Args:
            name (str, required): Module name. (Choose wich kernel_func in .pl should be load)
            sources (List[str], required): Source files (eg. ["a.pl", "a_tilling.cpp"])
            chip (str, optional): chip_type (eg. bm1690)
            extra_cflags (List[str], optional): Additional C/C++ flags. (eg. ['-g', '-DDEBUG'])
            extra_plflags (List[str], optional): Additional ppl-specific C/C++ flags.
            extra_ldflags (List[str], optional): Additional linker flags. (eg. ["-L{lib_path}", "-l{lib_name}"])
            extra_include_paths (List[str], optional): Additional include paths. (eg. ["a.h", "b.h"])

        Returns:
            module: The compiled Torch extension module.

        Example:
            ppl.pl_extension.load(
                name="add",
                sources=["add_dyn_block.pl","add_dyn_block_tiling.cpp"],
                chip=bm1690,
                extra_plflags=['-g', '-DDEBUG'])
            )
        """
        include_path = pl_extension.cache.get_cached_file("include")
        pl_extension.cache.get_cached_file("host")
        pl_extension.cache.get_cached_file("device")
        pl_extension.cache.get_cached_file("lib")
        # gen torch interface
        if isinstance(chip, Chip):
            chip_name = chip.str
        elif isinstance(chip, str):
            chip_name = chip
        elif chip is None:
            chip_name = os.getenv("CHIP", default="bm1690")
        else:
            raise ValueError("chip must be a string or ppl.Chip")
        chip_code = get_chip_code(chip_name)
        if extra_ldflags is None:
            extra_ldflags = []
        if extra_include_paths is None:
            extra_include_paths = []
        # prepare inclue path
        runtime_path = os.environ.get('PPL_RUNTIME_PATH')
        extra_include_paths.append(os.path.join(runtime_path, "common/host/include"))
        extra_include_paths.append(os.path.join(runtime_path, f"chip/{chip_code}/TPU1686/tpuDNN/include"))
        extra_include_paths.append(include_path)
        # prepare tpudnn lib path
        tpudnn_lib_path = os.environ.get('TORCH_TPU_RUNTIME_PATH')
        if tpudnn_lib_path is None:
            tpudnn_lib_path = os.path.join(runtime_path, f"chip/{chip_code}/lib")
            os.environ["TPU_EMULATOR_PATH"] = os.path.join(
                tpudnn_lib_path, "libtpuv7_emulator.so")
        # prepare utils path
        mem_files = []
        host = pl_extension.cache.get_cached_file("host")
        for dirpath, _, filenames in os.walk(host):
            for fn in filenames:
                mem_files.append(os.path.join(dirpath, fn))
        extra_ldflags.extend([
            f'-L{tpudnn_lib_path}',
            f'-ltpudnn',
            f'-Wl,-rpath,{tpudnn_lib_path}'
        ])
        # gen interface
        if not extra_cflags and extra_plflags:
            extra_cflags = extra_plflags
        module = torch.utils.cpp_extension.load(
            name=name,
            extra_include_paths=extra_include_paths,
            extra_cflags=extra_cflags,
            sources=mem_files,
            extra_ldflags=extra_ldflags)
        return module
