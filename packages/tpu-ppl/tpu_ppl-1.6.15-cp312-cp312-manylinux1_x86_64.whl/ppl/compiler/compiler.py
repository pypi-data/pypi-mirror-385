from __future__ import annotations
import time
import functools
import hashlib
import json
import os
import re
import subprocess
import logging
import tempfile
import torch
from collections import namedtuple
from pathlib import Path
from typing import Any, Tuple
import shutil
from .._C.libppl.ppl import (ir)
# from ..runtime import driver, jit, JITFunction
# TODO: runtime.errors
from ..runtime.autotuner import OutOfResources
from ..runtime.cache import get_cache_manager
from ..runtime.jit import (JITFunction, version_key)
from .code_generator import ast_to_ttir
from tool.config import get_chip_code
def _os_system_log(cmd_str):
    # use subprocess to redirect the output stream
    # the file for saving the output stream should be set if using this function
    print("[Running]: {}".format(cmd_str))

    process = subprocess.Popen(cmd_str,
                               shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    log = process.communicate()
    ret = process.returncode
    err_log = log[1]
    if ret == 0 and err_log.find("error") == -1:
        print("[Success]: {}".format(cmd_str))
    else:
        print(err_log)
        raise RuntimeError("[!Error]: {}".format(cmd_str))

def _os_system(cmd: list, save_log: bool = False):
    cmd_str = ""
    for s in cmd:
        cmd_str += str(s) + " "
    if not save_log:
        print("[Running]: {}".format(cmd_str))
        ret = os.system(cmd_str)
        if ret == 0:
            print("[Success]: {}".format(cmd_str))
        else:
            raise RuntimeError("[!Error]: {}".format(cmd_str))
    else:
        _os_system_log(cmd_str)

def inline_ppl_ir(mod):
    pm = ir.pass_manager(mod.context)
    pm.enable_debug()
    pm.add_pipeline_prior_pass()
    pm.add_inliner_pass()
    pm.add_symbol_dce_pass()
    #pm.add_cf_to_scf_pass()
    pm.run(mod)
    return mod

def generate_tensor(chip, tensorNum):
    if chip == "tpu_6_0" or chip == "tpul_6_0" or chip == "tpu_6_0_e" or chip == "tpul_8_1":
        return ", ".join(f"bm_mem_get_device_addr(tar_dev_data[{i}])" for i in range(int(tensorNum)))
    elif chip == "tpub_7_1" or chip == "tpub_9_0" or chip == "tpub_9_0_rv":
        return ", ".join(f"(unsigned long long)(tar_dev_data[{i}])" for i in range(int(tensorNum)))

def generate_params(sig_key):
    tensor_idx = 0
    variable_defs = []
    function_call_params = []
    for idx, value in enumerate(sig_key):
        if isinstance(value, torch.dtype):
            if value == torch.bfloat16:
                is_bf16 = "true"
            else:
                is_bf16 = "false"
            variable_defs.append(f"parse_tensor(data_info[{tensor_idx}], params[{idx}], data_dir, {is_bf16});")
            function_call_params.append(f"(unsigned long long)data_info[{tensor_idx}].dev_data")
            tensor_idx += 1
        elif value is None:
            variable_defs.append(f"parse_tensor(data_info[{tensor_idx}], params[{idx}], data_dir, false);")
            function_call_params.append(f"(unsigned long long)data_info[{tensor_idx}].dev_data")
            tensor_idx += 1
        elif isinstance(value, str):
            if value == 'i32':
                variable_defs.append(f"int32_t v_{idx} = ConvertToInt(params[{idx}]);")
                function_call_params.append(f"v_{idx}")
            elif value == 'i1':
                variable_defs.append(f"bool v_{idx} = ConvertToInt(params[{idx}]);")
                function_call_params.append(f"v_{idx}")
            elif value == 'fp32':
                variable_defs.append(f"float v_{idx} = ConvertToFloat(params[{idx}]);")
                function_call_params.append(f"v_{idx}")
            elif value.startswith('tuple_i32'):
                variable_defs.append(f"std::vector<int32_t> v_{idx} = ConvertToIntArray(params[{idx}]);")
                function_call_params.append(f"v_{idx}.data()")
            elif value.startswith('tuple_bool'):
                variable_defs.append(f"std::vector<int32_t> v_{idx} = ConvertToIntArray(params[{idx}]);")
                function_call_params.append(f"v_{idx}.data()")
            elif value.startswith('tuple_fp32'):
                variable_defs.append(f"std::vector<float> v_{idx} = ConvertToFloatArray(params[{idx}]);")
                function_call_params.append(f"v_{idx}.data()")
            else:
                raise RuntimeError(f"Unsupported type: {value}")
        else:
            raise RuntimeError(f"Unsupported type: {value}")

    variable_defs_str = '\n    '.join(variable_defs)
    function_call_params_str = ', '.join(function_call_params)
    return variable_defs_str, function_call_params_str, tensor_idx

def codegen(path, chip, sig_key, function_name, build_debug, mode, only_emit_kernel):
    os.environ["CHIP_ARCH"] = chip
    os.environ["TPUKERNEL_DEV_MODE"] = mode
    if only_emit_kernel:
        import subprocess
        ppl_root = os.getenv("PPL_PROJECT_ROOT", default=None)
        os.environ['CHIP'] = chip
        os.environ['DEV_MODE'] = mode
        so = os.path.join(os.path.join(path, "lib"), '{name}.so'.format(name=function_name))
        cc = os.environ.get("CC")
        if cc is None:
            clang = shutil.which("clang")
            gcc = shutil.which("gcc")
            cc = gcc if gcc is not None else clang
            if cc is None:
                raise RuntimeError("Failed to find C compiler. Please specify via CC environment variable.")
        src = os.path.join(os.path.join(path, "device"), '{name}.c'.format(name=function_name))
        include_dirs = [os.path.join(ppl_root, "deps/common/host/include"),
                        os.path.join(ppl_root, "deps/common/dev/kernel"),
                        os.path.join(ppl_root, "deps/chip/{chip}/TPU1686/kernel/include".format(chip=chip))]
        libraries = ["tpuv7_emulator" if (chip == "tpub_7_1" or chip == "tpub_9_0" or chip == "tpub_9_0_rv") else "cmodel_firmware"]
        library_dirs = [os.path.join(ppl_root, "deps/runtime/tpuv7-runtime/lib".format(chip=chip))
                        if chip == "tpub_7_1" else
                        os.path.join(ppl_root, "deps/chip/{chip}/lib".format(chip=chip))]
        if build_debug:
          cc_cmd = [cc, src, "-g", "-shared", "-fPIC", "-Wno-psabi", "-o", so]
        else:
          cc_cmd = [cc, src, "-O2", "-shared", "-fPIC", "-Wno-psabi", "-o", so]
        cc_cmd += [f"-I{dir}" for dir in include_dirs if dir is not None]
        cc_cmd += [f'-l{lib}' for lib in libraries]
        cc_cmd += [f"-L{dir}" for dir in library_dirs]
        ret = subprocess.check_call(cc_cmd)
        if ret == 0:
            return
    cmake_file = os.path.join(os.environ["PPL_RUNTIME_PATH"],
                            "scripts/{}.cmake".format(mode))
    shutil.copy(cmake_file, os.path.join(path, "CMakeLists.txt"))
    build_path = os.path.join(path, "build")
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    os.chdir(build_path)

    tensorNum = 0
    variable_definitions, final_param, tensorNum = generate_params(sig_key)

    parse_param_str = f"""
            auto ConvertToInt = [&](const std::string &str) {{
              try {{
                int32_t val = std::stoi(str);
                return val;
              }} catch (const std::invalid_argument &e) {{
                assert(0 && "invalid param from python\\n");
              }} catch (const std::out_of_range &e) {{
                assert(0 && "param out of range from python\\n");
              }}
              return 0;
            }};
            auto ConvertToFloat = [&](const std::string &str) {{
              try {{
                float val = std::stof(str);
                return val;
              }} catch (const std::invalid_argument &e) {{
                assert(0 && "invalid param from python\\n");
              }} catch (const std::out_of_range &e) {{
                assert(0 && "param out of range from python\\n");
              }}
              return 0.0f;
            }};
            auto ConvertToIntArray = [&](const std::string &str) {{
              std::vector<int32_t> result;
              std::stringstream ss(str);
              std::string item;
              while (std::getline(ss, item, ',')) {{
                result.push_back(ConvertToInt(item));
              }}
              return result;
            }};
            auto ConvertToFloatArray = [&](const std::string &str) {{
              std::vector<float> result;
              std::stringstream ss(str);
              std::string item;
              while (std::getline(ss, item, ',')) {{
                result.push_back(ConvertToFloat(item));
              }}
              return result;
            }};
    """

    #create main.cpp
    if chip == "tpu_6_0" or chip == "tpu_6_0_e" or chip == "tpul_8_1":
        data = f"""
        #include "tpu_defs.h"
        #include "bmlib_runtime.h"
        #include "{function_name}.h"
        #include "host_test_utils.h"
        #include "npz_helper.h"
        #include <filesystem>
        #include <fstream>
        #include <tpuDNN.h>
        namespace fs = std::filesystem;

        struct DataInfo {{
          size_t data_size;
          char *data;
          long long dev_data;
          bm_device_mem_t dev_handle;
          int dtype;
        }};

        void parse_tensor(DataInfo &data_info, std::string param, std::string data_dir,
                              bool is_bf16) {{
          if (param.find(".npz") == std::string::npos) {{
            printf("input tensor file %s not npz\\n", param.c_str());
            return;
          }}
          auto data_path = fs::path(data_dir);
          auto npz_file = data_path / fs::path(param);
          if (!fs::exists(npz_file)) {{
            printf("input file %s not found\\n", param.c_str());
            return;
          }}
          cnpy::NpyArray nparray = cnpy::npz_load(npz_file.string(), "0");
          int32_t shape[] = {{1, 1, 1, 1}};
          for (int32_t i = nparray.shape.size() - 1; i >= 0; i--) {{
            shape[4 - nparray.shape.size() + i] = nparray.shape[i];
          }}

          std::size_t dtype = DT_FP32;
          if (nparray.type == 'f') {{
            if (nparray.word_size == 4 && is_bf16)
              dtype = DT_BFP16;
            else if (nparray.word_size == 4) {{
              dtype = DT_FP32;
            }} else if (nparray.word_size == 2) {{
              dtype = DT_FP16;
            }}
          }} else if (nparray.type == 'i') {{
            if (nparray.word_size == 4)
              dtype = DT_INT32;
            else if (nparray.word_size == 2) {{
              dtype = DT_INT16;
            }}
            if (nparray.word_size == 1)
              dtype = DT_INT8;
          }} else if (nparray.type == 'u') {{
            if (nparray.word_size == 4)
              dtype = DT_UINT32;
            else if (nparray.word_size == 2) {{
              dtype = DT_UINT16;
            }}
            if (nparray.word_size == 1)
              dtype = DT_UINT8;
          }}
          if (dtype == DT_BFP16)
            data_info.data_size = static_cast<size_t>(shape[0]) * shape[1] * shape[2] *
                                  shape[3] * nparray.word_size / 2;
          else
            data_info.data_size = static_cast<size_t>(shape[0]) * shape[1] * shape[2] *
                                  shape[3] * nparray.word_size;
          data_info.dtype = dtype;

          MallocWrap(handle, &data_info.dev_handle,(u64 *)&data_info.data, data_info.data_size);
          if (dtype == DT_BFP16) {{
            char *tmp_data = new char[data_info.data_size * 2];
            memcpy(tmp_data, nparray.data<char>(), nparray.num_bytes());
            for (int32_t k = 0; k < nparray.num_vals; k++) {{
            #define type_size 2
                char *src = tmp_data + k * sizeof(float);
                bf16 value = fp32_to_bf16(*(fp32 *)src);
                memcpy(data_info.data + k * type_size, &value, type_size);
            }}
            delete[] tmp_data;
          }} else {{
            memcpy(data_info.data, nparray.data<char>(), nparray.num_bytes());
          }}
          MemcpyS2D(handle, &data_info.dev_handle, data_info.data, data_info.data_size);
          data_info.dev_data = bm_mem_get_device_addr(data_info.dev_handle);
        }}


        int main () {{
            std::map<std::string, std::pair<size_t, size_t>> data_sizes;
            std::string data_dir = getenv("PPL_DATA_PATH");
            if (data_dir.empty()) {{
                printf("Please set env PPL_DATA_PATH to data dir\\n");
                return -1;
            }}
            std::string file_name = "{function_name}";
            bm_status_t ret = BM_SUCCESS;
            ret = bm_dev_request(&handle, 0);
            if (ret != BM_SUCCESS)
                throw("bm_dev_request_failed");
            const unsigned int *p = kernel_module_data;
            size_t length = sizeof(kernel_module_data);
            tpu_module = tpu_kernel_load_module(handle, (const char *)p, length);
            if (!tpu_module) {{
            printf("tpu_kernel_load_module failed");
            return -1;
            }}
            printf("tpu_kernel_load_module  success!\\n");
            auto t_handle = tpudnnHandleFromStream(0, handle, tpu_module);
            int tensorNum = {tensorNum};
            DataInfo data_info[{tensorNum}];
            {parse_param_str}
            std::vector<std::string> params;
            std::ifstream param_file(data_dir + "/param.txt");
            if (param_file.fail()) {{
              printf("param.txt not found\\n");
              return -1;
            }}
            while (!param_file.eof()) {{
              std::string line;
              std::getline(param_file, line);
              params.push_back(line);
            }}

            bm_profile_t start, end;
            bm_get_profile(handle, &start);
            {variable_definitions}
            int rst = {function_name}(t_handle, {final_param});
            tpudnnSync(t_handle);
            bm_get_profile(handle, &end);
            if (rst != 0) {{
                std::cout << "kernel_launch failed" << "\\n";
                return -1;
            }} else {{
                size_t npu_time = end.tpu_process_time - start.tpu_process_time;
                std::cout << "npu time = " << npu_time << "(us) --> ";
                std::cout << "kernel_launch success" << "\\n";
            }}

            for (int32_t i = 0; i < tensorNum; i++) {{
                MemcpyD2S(handle, &data_info[i].dev_handle, data_info[i].data, data_info[i].data_size);
                dump_data(data_dir, file_name, "_tar_", ".out", i, data_info[i].data, data_info[i].data_size, data_info[i].dtype);
                FreeWrap(handle, &data_info[i].dev_handle, data_info[i].data);
            }}
            tpu_kernel_free_module(handle, tpu_module);
            bm_dev_free(handle);
            tpudnnDestroy(t_handle);
            return 0;
        }}"""
    elif chip == "tpul_6_0" or chip == "tpub_9_3":
        core_num = 0
        if chip == "tpul_6_0":
          core_num = 2
        elif chip == "tpub_9_3":
          core_num = 4
        data = f"""
        #include "tpu_defs.h"
        #include "bmlib_runtime.h"
        #include "{function_name}.h"
        #include "host_test_utils.h"
        #include "npz_helper.h"
        #include <filesystem>
        #include <fstream>
        #include <tpuDNN.h>
        namespace fs = std::filesystem;

        struct DataInfo {{
          size_t data_size;
          char *data;
          long long dev_data;
          bm_device_mem_t dev_handle;
          int dtype;
        }};

        void parse_tensor(DataInfo &data_info, std::string param, std::string data_dir,
                              bool is_bf16) {{
          if (param.find(".npz") == std::string::npos) {{
            printf("input tensor file %s not npz\\n", param.c_str());
            return;
          }}
          auto data_path = fs::path(data_dir);
          auto npz_file = data_path / fs::path(param);
          if (!fs::exists(npz_file)) {{
            printf("input file %s not found\\n", param.c_str());
            return;
          }}
          cnpy::NpyArray nparray = cnpy::npz_load(npz_file.string(), "0");
          int32_t shape[] = {{1, 1, 1, 1}};
          for (int32_t i = nparray.shape.size() - 1; i >= 0; i--) {{
            shape[4 - nparray.shape.size() + i] = nparray.shape[i];
          }}

          std::size_t dtype = DT_FP32;
          if (nparray.type == 'f') {{
            if (nparray.word_size == 4 && is_bf16)
              dtype = DT_BFP16;
            else if (nparray.word_size == 4) {{
              dtype = DT_FP32;
            }} else if (nparray.word_size == 2) {{
              dtype = DT_FP16;
            }}
          }} else if (nparray.type == 'i') {{
            if (nparray.word_size == 4)
              dtype = DT_INT32;
            else if (nparray.word_size == 2) {{
              dtype = DT_INT16;
            }}
            if (nparray.word_size == 1)
              dtype = DT_INT8;
          }} else if (nparray.type == 'u') {{
            if (nparray.word_size == 4)
              dtype = DT_UINT32;
            else if (nparray.word_size == 2) {{
              dtype = DT_UINT16;
            }}
            if (nparray.word_size == 1)
              dtype = DT_UINT8;
          }}
          if (dtype == DT_BFP16)
            data_info.data_size = static_cast<size_t>(shape[0]) * shape[1] * shape[2] *
                                  shape[3] * nparray.word_size / 2;
          else
            data_info.data_size = static_cast<size_t>(shape[0]) * shape[1] * shape[2] *
                                  shape[3] * nparray.word_size;
          data_info.dtype = dtype;

          MallocWrap(handle, &data_info.dev_handle,(u64 *)&data_info.data, data_info.data_size);
          if (dtype == DT_BFP16) {{
            char *tmp_data = new char[data_info.data_size * 2];
            memcpy(tmp_data, nparray.data<char>(), nparray.num_bytes());
            for (int32_t k = 0; k < nparray.num_vals; k++) {{
            #define type_size 2
                char *src = tmp_data + k * sizeof(float);
                bf16 value = fp32_to_bf16(*(fp32 *)src);
                memcpy(data_info.data + k * type_size, &value, type_size);
            }}
            delete[] tmp_data;
          }} else {{
            memcpy(data_info.data, nparray.data<char>(), nparray.num_bytes());
          }}
          MemcpyS2D(handle, &data_info.dev_handle, data_info.data, data_info.data_size);
          data_info.dev_data = bm_mem_get_device_addr(data_info.dev_handle);
        }}


        int main () {{
            std::map<std::string, std::pair<size_t, size_t>> data_sizes;
            std::string data_dir = getenv("PPL_DATA_PATH");
            if (data_dir.empty()) {{
                printf("Please set env PPL_DATA_PATH to data dir\\n");
                return -1;
            }}
            std::string file_name = "{function_name}";
            bm_status_t ret = BM_SUCCESS;
            ret = bm_dev_request(&handle, 0);
            if (ret != BM_SUCCESS)
                throw("bm_dev_request_failed");
            const unsigned int *p = kernel_module_data;
            size_t length = sizeof(kernel_module_data);
            for (int i = 0; i < {core_num}; ++i) {{
                tpu_module[i] = tpu_kernel_load_module_to_core(handle, (const char *)p, length, i);
                if (!tpu_module[i]) {{
                    printf("tpu_kernel_load_module failed");
                    return -1;
                }}
            }}
            printf("tpu_kernel_load_module  success!\\n");
            auto t_handle = tpudnnHandleFromStream(0, handle, tpu_module);
            int tensorNum = {tensorNum};
            DataInfo data_info[{tensorNum}];
            {parse_param_str}
            std::vector<std::string> params;
            std::ifstream param_file(data_dir + "/param.txt");
            if (param_file.fail()) {{
              printf("param.txt not found\\n");
              return -1;
            }}
            while (!param_file.eof()) {{
              std::string line;
              std::getline(param_file, line);
              params.push_back(line);
            }}


            bm_profile_t start, end;
            bm_get_profile(handle, &start);
            {variable_definitions}
            int rst = {function_name}(t_handle, {final_param});
            tpudnnSync(t_handle);
            bm_get_profile(handle, &end);
            if (rst != 0) {{
                std::cout << "kernel_launch failed" << "\\n";
                return -1;
            }} else {{
                size_t npu_time = end.tpu_process_time - start.tpu_process_time;
                std::cout << "npu time = " << npu_time << "(us) --> ";
                std::cout << "kernel_launch success" << "\\n";
            }}

            for (int32_t i = 0; i < tensorNum; i++) {{
                MemcpyD2S(handle, &data_info[i].dev_handle, data_info[i].data, data_info[i].data_size);
                dump_data(data_dir, file_name, "_tar_", ".out", i, data_info[i].data, data_info[i].data_size, data_info[i].dtype);
                FreeWrap(handle, &data_info[i].dev_handle, data_info[i].data);
            }}
            for (int i = 0; i < {core_num}; ++i) {{
                tpu_kernel_free_module(handle, tpu_module[i]);
            }}
            bm_dev_free(handle);
            tpudnnDestroy(t_handle);
            return 0;
        }}"""
    elif chip == "tpub_7_1" or chip == "tpub_9_0" or chip == "tpub_9_0_rv" or chip == "tpub_7_1_e":
        data = f"""
            #include <tpuv7_rt.h>
            #include <tpuDNN.h>
            #include "host_test_utils.h"
            #include "npz_helper.h"
            #include <cstring>
            #include "{function_name}.h"
            #include <filesystem>
            #include <fstream>
            #include <vector>
            namespace fs = std::filesystem;

            struct DataInfo {{
              size_t data_size;
              char *data;
              void *dev_data;
              int dtype;
            }};

            void parse_tensor(DataInfo &data_info, std::string param, std::string data_dir,
                              bool is_bf16) {{
              if (param.find(".npz") == std::string::npos) {{
                printf("input tensor file %s not npz\\n", param.c_str());
                return;
              }}
              auto data_path = fs::path(data_dir);
              auto npz_file = data_path / fs::path(param);
              if (!fs::exists(npz_file)) {{
                printf("input file %s not found\\n", param.c_str());
                return;
              }}
              cnpy::NpyArray nparray = cnpy::npz_load(npz_file.string(), "0");
              int32_t shape[] = {{1, 1, 1, 1}};
              for (int32_t i = nparray.shape.size() - 1; i >= 0; i--) {{
                shape[4 - nparray.shape.size() + i] = nparray.shape[i];
              }}

              std::size_t dtype = DT_FP32;
              if (nparray.type == 'f') {{
                if (nparray.word_size == 4 && is_bf16)
                  dtype = DT_BFP16;
                else if (nparray.word_size == 4) {{
                  dtype = DT_FP32;
                }} else if (nparray.word_size == 2) {{
                  dtype = DT_FP16;
                }}
              }} else if (nparray.type == 'i') {{
                if (nparray.word_size == 4)
                  dtype = DT_INT32;
                else if (nparray.word_size == 2) {{
                  dtype = DT_INT16;
                }}
                if (nparray.word_size == 1)
                  dtype = DT_INT8;
              }} else if (nparray.type == 'u') {{
                if (nparray.word_size == 4)
                  dtype = DT_UINT32;
                else if (nparray.word_size == 2) {{
                  dtype = DT_UINT16;
                }}
                if (nparray.word_size == 1)
                  dtype = DT_UINT8;
              }}
              if (dtype == DT_BFP16)
                data_info.data_size = static_cast<size_t>(shape[0]) * shape[1] * shape[2] *
                                      shape[3] * nparray.word_size / 2;
              else
                data_info.data_size = static_cast<size_t>(shape[0]) * shape[1] * shape[2] *
                                      shape[3] * nparray.word_size;
              data_info.dtype = dtype;

              data_info.data = new char[data_info.data_size];
              if (dtype == DT_BFP16) {{
                char *tmp_data = new char[data_info.data_size * 2];
                memcpy(tmp_data, nparray.data<char>(), nparray.num_bytes());
                for (int32_t k = 0; k < nparray.num_vals; k++) {{
            #define type_size 2
                  char *src = tmp_data + k * sizeof(float);
                  bf16 value = fp32_to_bf16(*(fp32 *)src);
                  memcpy(data_info.data + k * type_size, &value, type_size);
                }}
                delete[] tmp_data;
              }} else {{
                memcpy(data_info.data, nparray.data<char>(), nparray.num_bytes());
              }}
              tpuRtMalloc((void **)(&data_info.dev_data), data_info.data_size, 0);
              tpuRtMemcpyS2D(data_info.dev_data, data_info.data, data_info.data_size);
            }}

            int main() {{
              std::string data_dir = getenv("PPL_DATA_PATH");
              if (data_dir.empty()) {{
                printf("Please set env PPL_DATA_PATH to data dir\\n");
                return -1;
              }}
              std::string file_name = "{function_name}";
              tpuRtStatus_t ret;
              ret = tpuRtInit();
              if (ret != tpuRtSuccess) {{
                printf("tpuRtDeviceInit failed");
                return -1;
              }}
              printf("tpuRtDeviceInit success");
              tpuRtSetDevice(0);
              tpuRtStreamCreate(&stream);
              auto kernel_dir = getenv("PPL_KERNEL_PATH");
              if (!kernel_dir) {{
                printf("Please set env PPL_KERNEL_PATH to libkernel.so path\\n");
                return -2;
              }}
              tpu_module = tpuRtKernelLoadModuleFile(kernel_dir, stream);
              if (NULL == tpu_module) {{
                printf("tpuRtKernelLoadModuleFile failed\\n");
                return -2;
              }}
              auto t_handle = tpudnnHandleFromStream(0, stream, tpu_module);
              int tensorNum = {tensorNum};
              DataInfo data_info[{tensorNum}];
              {parse_param_str}
              std::vector<std::string> params;
              std::ifstream param_file(data_dir + "/param.txt");
              if (param_file.fail()) {{
                printf("param.txt not found\\n");
                return -1;
              }}
              while (!param_file.eof()) {{
                std::string line;
                std::getline(param_file, line);
                params.push_back(line);
              }}

              {variable_definitions}
              int rst = {function_name} (t_handle, {final_param});
              if (rst != 0) {{
                return -1;
              }}
              tpudnnSync(t_handle);

              for (int32_t i = 0; i < tensorNum; i++) {{
                tpuRtMemcpyD2S(data_info[i].data, data_info[i].dev_data,
                               data_info[i].data_size);
                dump_data(data_dir, file_name, "_tar_", ".out", i, data_info[i].data,
                          data_info[i].data_size, data_info[i].dtype);
                delete[] data_info[i].data;
                tpuRtFree(&data_info[i].dev_data, 0);
              }}
              tpuRtKernelUnloadModule(tpu_module, stream);
              tpuRtStreamDestroy(stream);
              tpudnnDestroy(t_handle);
              return 0;
            }}"""
    else:
        print("create main.cpp failed")
    file_path = os.path.join(path, "src/main.cpp")
    with open(file_path, 'w') as file:
        file.write(data)
    _os_system([
            "cmake .. -DDEBUG={} -DCHIP={} -DDEV_MODE={}".format(
                build_debug, chip, mode)
    ])
    if build_debug:
        _os_system(["make install VERBOSE=1"])
    else:
        _os_system(["make install"])
    _os_system(["rm -rf ", build_path])
    os.chdir(os.environ["PPL_PROJECT_ROOT"])
    return

def validate(path, arch, function_name, mode, only_emit_kernel, debug, desc=False):
    if only_emit_kernel:
        return
    import numpy as np
    if desc:
        os.environ["PPL_SRC_PATH"] = os.environ["PPL_PROJECT_ROOT"]
        os.environ["PPL_WORK_PATH"] = path
    os.environ["PPL_DATA_PATH"] = os.path.join(path, "data")
    runtime_root_path = os.environ["PPL_RUNTIME_PATH"]
    if mode == "cmodel":
        if arch in ["tpu_6_0", "tpu_6_0_e", "tpul_8_1", "tpul_6_0", "tpub_9_3"]:
            runtime_path = os.path.join(runtime_root_path, "runtime/bmlib/lib")
        else:
            runtime_path = os.path.join(runtime_root_path, "runtime/tpuv7-runtime/lib")
        cmodel_path = os.path.join(runtime_root_path, f"chip/{arch}/lib")
        os.environ["LD_LIBRARY_PATH"] = os.path.join(
            path, "lib") + ":" + cmodel_path + ":" + runtime_path

        if arch == "tpub_7_1" or arch == "tpub_9_0" or arch == "tpub_9_0_rv" or arch == "tpub_7_1_e":
            os.environ["TPU_KERNEL_PATH"] = os.path.join(
                os.path.relpath(path, os.getcwd()), "lib")
            os.environ["PPL_KERNEL_PATH"] = os.path.join(
                path, "lib/libcmodel.so")
            os.environ["TPU_EMULATOR_PATH"] = os.path.join(
                cmodel_path, "libtpuv7_emulator.so")
            os.environ["TPU_SCALAR_EMULATOR_PATH"] = os.path.join(
                runtime_path, "libtpuv7_scalar_emulator.so")
            if arch == "tpub_7_1_e":
                os.environ["TPU_RT_CORE_NUM"] = "4"
    else:
        if arch == "tpub_7_1" or arch == "tpub_9_0" or arch == "tpub_9_0_rv" or arch == "tpub_7_1_e":
            os.environ["TPU_KERNEL_PATH"] = os.path.join(path, "lib")
            os.environ["PPL_KERNEL_PATH"] = os.path.join(path, "lib/libkernel.so")

    if arch == "tpub_7_1" or arch == "tpub_9_0" or arch == "tpub_9_0_rv" or arch == "tpub_7_1_e":
        profile = os.getenv("BMLIB_ENABLE_ALL_PROFILE", default=False)
        if isinstance(profile, str) and (profile.lower() == "true" or profile == "1"):
            os.environ["TPU_KERNEL_PATH"] = os.path.join(
                    path, "lib")
            os.environ["FILE_DUMP_CMD"] = function_name
            profiling_dir = os.path.join(path, "profiling")
            if os.path.exists(profiling_dir):
                shutil.rmtree(profiling_dir)
            os.makedirs(profiling_dir, exist_ok=True)
            os.chdir(profiling_dir)
    if debug == True:
      cmd = ["gdb", "--args"]
    else:
      cmd = []
    cmd.append(os.path.join(path, "test_case"))
    _os_system(cmd)
    files = os.listdir(os.environ["PPL_DATA_PATH"])
    files = [f for f in files if f.endswith(".out")]
    mem_num = len(files)
    tpu_data = {}
    for i in range(mem_num):
        tar_data_file = os.path.join(
                os.environ["PPL_DATA_PATH"], function_name + "_tar_" + str(i) + ".out")
        assert (os.path.exists(tar_data_file))
        tpu_data[str(i)] = np.fromfile(tar_data_file, dtype=np.float32)

    tar_npz = os.path.join(os.environ["PPL_DATA_PATH"], function_name + "_tar.npz")
    np.savez(tar_npz, **tpu_data)
    return

def optimize_ttir(mod, arch, sig_key, path, function_name, build_debug, mode, only_emit_kernel, grid_size, grid_0, grid_1):
    mod = inline_ppl_ir(mod)
    pm = ir.pass_manager(mod.context)
    pm.enable_debug()
    if grid_size == 1:
        pm.add_group_block_pass(grid_0)
    else:
        pm.add_group_block_pass(grid_0, grid_1)
    pm.add_cse_pass()

    pm.add_fe_conversion_pass()
    pm.add_insert_load_coeff_pass()
    pm.add_insert_sync_pass()
    pm.add_canonicalizer_pass()
    pm.add_ppl_cano_pass()
    pm.add_shape_inference_pass()

    pm.add_ppl_cano_pass()
    pm.add_insert_scalar_pass()
    pm.add_cse_pass()
    pm.add_symbol_dce_pass()
    pm.add_simplify_affinestructure_pass()
    pm.add_lower_affine_pass()
    pm.add_set_memref_shape_pass()
    pm.add_loop_motion_pass()

    pm.add_ppl_loop_motion_pass()
    pm.add_tensor_conversion_pass()
    pm.add_combine_ops_pass()
    pm.add_apply_bc_pass()
    pm.add_canonicalizer_pass()
    if only_emit_kernel:
      pm.add_remove_debug_pass()
    pm.add_live_range_pass()
    pm.add_pipeline_pass()
    pm.add_canonicalizer_pass()
    pm.add_ppl_cano_pass()
    pm.add_cse_pass()
    pm.add_symbol_dce_pass()
    pm.add_canonicalizer_pass()
    pm.add_address_assign_pass()
    pm.add_reg_alloc_pass()
    pm.add_dyn_block_pass()
    ret = pm.run(mod)
    if ret:
        if not only_emit_kernel:
            print("[ERROR] codegen failed, generator tpu kernel file failed!")
        return ret
    mlir_path = os.path.join(path, function_name+".mlir")
    with open(mlir_path, 'w') as mlir:
        mlir.write(mod.str())
    mod.translate(path, function_name, only_emit_kernel)
    codegen(path, arch, sig_key, function_name, build_debug, mode, only_emit_kernel)
    # end_time = time.time()
    # print("compile end :{:.6f}s".format(time.time()))
    return mod

# ------------------------------------------------------------------------------
# compiler
# ------------------------------------------------------------------------------
def get_kernel_name(src: str, pattern: str) -> str:
    '''
    Get kernel name from PTX code.
    This Kernel name is required when launching the kernel.
    '''
    # There is a name mangling in PTX codegen, so the original kernel names in Ppl IR are not available in PTX/cubin.
    assert src
    for line in src.split('\n'):
        line = line.strip()
        if line.startswith(pattern):
            return line.split()[-1]


def convert_type_repr(x):
    match = re.search(r'!tt\.ptr<(.*)>', x)
    if match is not None:
        return '*' + convert_type_repr(match.group(1))
    return x


def make_hash(fn, arch, **kwargs):
    if isinstance(fn, JITFunction):
        configs = kwargs["configs"]
        signature = kwargs["signature"]
        constants = kwargs.get("constants", dict())
        num_warps = kwargs.get("num_warps", 4)
        num_stages = kwargs.get("num_stages", 3)
        debug = kwargs.get("debug", False)
        # Get unique key for the compiled code
        get_conf_key = lambda conf: (sorted(conf.divisible_by_16),
                                     sorted(conf.equal_to_1))
        configs_key = [get_conf_key(conf) for conf in configs]
        key = f"{fn.cache_key}-{''.join(signature.values())}-{configs_key}-{constants}-{num_warps}-{num_stages}-{debug}-{arch}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()
    assert isinstance(fn, str)
    return hashlib.md5(
        (Path(fn).read_text() + version_key()).encode("utf-8")).hexdigest()


def parse_mlir_module(path, context):
    module = ir.parse_mlir_module(path, context)
    # module takes ownership of the context
    module.context = context
    return module


instance_descriptor = namedtuple("instance_descriptor",
                                 ["divisible_by_16", "equal_to_1"],
                                 defaults=[set(), set()])

def compile(fn, **kwargs):
    # Get device type to decide which backend should be used
    # print("compile begin :{:.6f}s".format(time.time()))
    arch = get_chip_code(os.getenv("CHIP", default="bm1684x"))
    context = ir.context()
    constants = kwargs.get("constants", dict())
    debug = kwargs.get("debug", False)
    mode = kwargs.get("mode", "cmodel")
    save_dir = kwargs.get("save_dir")
    only_emit_kernel = kwargs.get("only_emit_kernel")
    constexpr_index = kwargs.get("constexpr_index")
    grid_size = kwargs.get("grid_size")
    grid_0 =  kwargs.get("grid_0")
    grid_1 =  kwargs.get("grid_1")
    grid_2 =  kwargs.get("grid_2")
    hash = kwargs.get("hash")
    signature = kwargs["signature"]
    sig_key = kwargs["sig_key"]
    enable_dump_ir = os.getenv("PPL_DUMP", "0") == "1"
    if save_dir is None:
        target_path = os.getcwd() + "/test_" + fn.__name__
    else:
        target_path = save_dir + "/test_" + fn.__name__

    # find out the signature of the function
    if isinstance(fn, JITFunction):
        configs = kwargs.get("configs", None)
        if configs is None:
            configs = [instance_descriptor()]
        assert len(configs) == 1
        kwargs["configs"] = configs
        name = fn.__name__
        first_stage = 0
    else:
        assert False

    fn_cache_manager = get_cache_manager(hash)

    # build compilation stages
    stages = dict()
    stages["ast"] = (lambda path: fn, None)
    stages["ttir"] = (
        lambda path: parse_mlir_module(path, context),
        lambda src: optimize_ttir(
            ast_to_ttir(
                src, signature, configs[0], constants, debug=debug, arch=arch),
            arch, sig_key, fn_cache_manager.get_cache_dir(), fn.__name__, debug, mode, only_emit_kernel, grid_size, grid_0, grid_1))

    so_path = ""
    # determine name and extension type of provided function
    if isinstance(fn, JITFunction):
        name, ext = fn.__name__, "ast"
    else:
        name, ext = os.path.basename(fn).split(".")

    # load metadata if any
    metadata = {"hash": hash}
    metadata_filename = f"{name}.json"
    # The group is addressed by the metadata
    metadata_group = fn_cache_manager.get_group(metadata_filename) or {}
    metadata_path = metadata_group.get(metadata_filename)
    if metadata_path is not None:
        with open(metadata_path, 'r') as file:
            data = json.load(file)
        errorCode = data.get("errorCode")
        if errorCode == 0:
            if enable_dump_ir:
                fn_cache_manager.store(target_path)
        return CompiledKernel(fn, so_path, metadata, dict(), fn_cache_manager.get_cache_dir(),
                              arch, fn.__name__, mode, only_emit_kernel, constexpr_index, grid_size, grid_0, grid_1, grid_2, errorCode)

    first_stage = list(stages.keys()).index(ext)
    asm = dict()
    module = fn
    errorCode = 0
    # run compilation pipeline  and populate metadata
    for ir_name, (parse, compile_kernel) in list(stages.items())[first_stage:]:
        ir_filename = f"{name}.{ir_name}"

        if ir_name == ext:
            next_module = parse(fn)
        else:
            next_module = compile_kernel(module)
            if isinstance(next_module, int):
                errorCode = next_module
        asm[ir_name] = str(next_module)
        module = next_module
    metadata["errorCode"] = errorCode
    metadata_group[metadata_filename] = fn_cache_manager.put(json.dumps(
        metadata, default=vars), metadata_filename, binary=False)
    fn_cache_manager.put_group(metadata_filename, metadata_group)
    if enable_dump_ir and errorCode == 0:
        fn_cache_manager.store(target_path)
    # return handle to compiled kernel
    return CompiledKernel(fn, so_path, metadata, asm,
                          fn_cache_manager.get_cache_dir(),
                          arch, fn.__name__, mode, only_emit_kernel,
                          constexpr_index, grid_size, grid_0, grid_1,
                          grid_2, errorCode)

class CompiledKernel:

    # Hooks for external tools to monitor the execution of ppl kernels
    launch_enter_hook = None
    launch_exit_hook = None

    def __init__(self, fn, so_path, metadata, asm, path, arch, function_name, mode,
                 only_emit_kernel, constexpr_index, grid_size, grid_0, grid_1, grid_2, errorCode, desc=False):
        # initialize launcher
        import importlib.util
        self.fn = fn
        # initialize metadata
        self.num_warps = 1
        self.num_stages = 1
        self.shared = 0
        self.device_type = "cpu"
        # initialize asm dict
        self.asm = asm
        # binaries are lazily initialized
        # because it involves doing runtime things
        # (e.g., checking amount of shared memory on current device)
        self.metadata = metadata
        self.cu_module = None
        self.cu_function = None
        self.path = path
        self.arch = arch
        self.function_name = function_name
        self.mode = mode
        self.only_emit_kernel = only_emit_kernel
        self.desc = desc
        if only_emit_kernel:
            self.so_path = os.path.join(os.path.join(path, "lib"), '{name}.so'.format(name=function_name))
        else:
            self.so_path = ""
        self.constexpr_index = constexpr_index
        self.grid_size = grid_size
        self.grid_0 = grid_0
        self.grid_1 = grid_1
        self.grid_2 = grid_2
        self.errorCode = errorCode

    def _init_handles(self):
        self.run = validate
        return

    def __getattribute__(self, name):
        if name == 'run':
            self._init_handles()
        return super().__getattribute__(name)

    def __getitem__(self, grid):
        self._init_handles()

        def runner(*args):
            self.run(args)

        return runner
