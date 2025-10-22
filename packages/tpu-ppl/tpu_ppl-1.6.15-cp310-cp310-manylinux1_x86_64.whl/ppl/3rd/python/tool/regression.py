#!/usr/bin/env python3
import os
import argparse
import shutil
from example import full_pl_list, sample_list, python_list
import logging
import argparse
from os_system import _os_subprocess_with_log, _os_subprocess
from tool.config import get_chip_code
from ppl.runtime.cache import default_cache_dir
import time
import multiprocessing
from multiprocessing import Pool, cpu_count
# import psutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s -\n%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

SUCCESS = 0
FAILURE = 1

_lock = None

def _init_lock(l):
    global _lock
    _lock = l

class BaseTestFiles:

    def __init__(self, top_dir, chips, file_list, mode, is_full, time_out):
        self.result_message = ""
        self.top_dir = top_dir
        self.file_list = file_list
        self.chips = chips
        self.test_failed_list = []
        self.vali_failed_list = []
        self.time_out_list = []
        self.dubious_pl_list = {}
        self.file_not_found_list = {}
        self.chip_index_map = {
            'bm1684x': 1,
            'bm1688': 2,
            'bm1690': 3,
            'sg2260e': 4,
            'sg2262': 5,
            'sg2262rv': 6,
            'mars3': 7,
            'bm1684xe': 8,
            'bm1684x2': 9,
            'bm1684x2rv': 10,
        }
        self.mode = mode
        self.is_full = is_full
        self.time_out = time_out
        self.time_cost_list = []
        self.test_type = "Unkown"


    def summarize(self):
        self.result_message = f"\n====================== {str(self.__class__.__name__)} test summarize ======================\n"
        if self.file_not_found_list:
            self.result_message += "\n[WARNING]: File does not exist:\n"
            for fileName, _ in self.file_not_found_list.items():
                self.result_message += f"- {fileName}\n"

        if self.test_failed_list:
            self.result_message += "[FAILED]: These " + self.test_type + " files failed in compilation:\n"
            for chip, fileName in self.test_failed_list:
                self.result_message += f"- {fileName} tested in PLATFORM: {chip}\n"
        else:
            self.result_message += "[SUCCESS]: All " + self.test_type + " files passed compilation\n"

        if self.test_type == "PL":
            if self.vali_failed_list:
                self.result_message += "[FAILED]: These " + self.test_type + " files do not passed the correctness validation:\n"
                for chip, fileName in self.vali_failed_list:
                    self.result_message += f"- {fileName} validated in PLATFORM: {chip}\n"
            else:
                self.result_message += "[SUCCESS]: All correctness validation passed.\n"

        if self.dubious_pl_list:
            self.result_message += "\n[WARNING]: These " + self.test_type + " files do not have correctness validation scripts:\n"
            for fileName, _ in self.dubious_pl_list.items():
                self.result_message += f"- {fileName}\n"

        if self.time_out_list:
            self.result_message += "\n[WARNING]: These " + self.test_type + " files run time out:\n"
            for chip, fileName in self.time_out_list:
                self.result_message += f"- {fileName} tested in PLATFORM: {chip}\n"

        if self.time_cost_list:
            self.result_message += "\n[INFO]: The time consume summary:\n"
            for chip, time_cost, local_time_list in self.time_cost_list:
                self.result_message += f"- run models for {chip}: {time_cost:.1f} seconds\n"
                for file, ret, output_info, local_time_cost in local_time_list:
                    res = 'SUCCESS' if (ret == 0) else 'FAILED'
                    self.result_message += f"---- test {file} ({res}) [{local_time_cost:.1f} seconds]\n"
                    if ret != 0:
                        self.result_message += f"{output_info}\n"
    def check_test_open(self, case):
        flag = 1 if self.is_full else 0
        if type(case) == list:
            return case[flag]
        else:
            return case

    def get_applicable_tests(self, chip):
        applicable_tests = {}
        chip_index = self.chip_index_map[chip]

        for category, tests in self.file_list.items():
            applicable_tests[category] = [
                test[0] for test in tests
                if self.check_test_open(test[chip_index])
            ]

        return applicable_tests

    def check_file_exists(self, path):
        if not os.path.exists(path):
            self.file_not_found_list[path] = ""
            logging.warning(f"[WARNING]: File does not exist - {path}")
            return False
        else:
            return True

    def check_is_rv_chip(self, chip):
        if chip == "sg2260e":
            test_opt = "--gen_ref --opt O3"
        elif chip in ["sg2262rv", "bm1684x2rv"]:
            test_opt = "--gen_ref --opt O3 --rv"
            chip = chip.split("rv")[0]
        else:
            test_opt = "--gen_ref"
        return test_opt, chip

    def test_all(self):
        raise NotImplementedError("Subclasses should implement this method")


class TestPLFiles(BaseTestFiles):
    def __init__(self, pl_file_dir, chips, file_list, mode, is_full, time_out):
        super().__init__(pl_file_dir, chips, file_list, mode, is_full, time_out)
        self.is_full = is_full
        self.test_type = "PL"

    def test_one(self, fileName, chip):
        self.check_file_exists(fileName)
        logging.info(f"+++++++++++ testing {fileName} in {chip} +++++++++++")
        test_opt, chip = self.check_is_rv_chip(chip)
        cmd = [
            "ppl_compile.py", "--src", fileName, "--chip", chip, test_opt,
            "--mode", self.mode
        ]
        ret, output_info = _os_subprocess(cmd, self.time_out)

        if ret != 0:
            logging.error(f"ppl_compile failed with return code {ret}")
            if ret == 1:
                self.test_failed_list.append((chip, fileName))
            if ret == 2:
                self.time_out_list.append((chip, fileName))
        return ret, output_info

    def verify_one(self, fileName, chip):
        _, chip = self.check_is_rv_chip(chip)
        testFile = fileName.replace(".pl", ".py")
        if os.path.exists(testFile):
            cmd = ["python", testFile, "--chip", chip]
            ret, output_info = _os_subprocess(cmd, self.time_out)
            if ret != 0:
                logging.error(f"verify failed with return code {ret}")
                self.vali_failed_list.append((chip, fileName))
                return ret, output_info
        else:
            logging.warning("File does not exist at the specified path.")
            self.dubious_pl_list[fileName] = ""
        return 0, ""

    def thread_test_and_verify(self, pl_file, chip, file):
        st_local = time.time()
        os.makedirs(file)
        os.chdir(file)

        # check verify file (.py)
        verifyFile = pl_file.replace(".pl", ".py")
        verifyFile_exist = os.path.exists(verifyFile)

        # apply ppl_compile.py
        logging.info(f"+++++++++++ testing {pl_file} in {chip} +++++++++++")
        test_opt, chip = self.check_is_rv_chip(chip)
        cmd = [
            "ppl_compile.py", "--src", pl_file, "--chip", chip, test_opt,
            "--mode", self.mode, "--disable_auto_run"
        ]
        log_name = "output_" + pl_file.split('/')[-1].split('.')[0] + ".log"
        test_ret, test_output_info = _os_subprocess_with_log(cmd, log_name, self.time_out)
        run_fle = "./test_" + pl_file.split('/')[-1].split('.')[0] + "/run.sh"
        if os.path.exists(run_fle):
            with _lock:
                cmd = ["bash", run_fle]
                log_name = log_name.replace(".log", "_run.log")
                run_ret, run_output_info = _os_subprocess_with_log(cmd, log_name, self.time_out)
                test_ret = test_ret | run_ret
                test_output_info = test_output_info + run_output_info
        else:
            test_ret = 1
            print("Error:", run_fle, "do not exist!")
        if test_ret != 0:
            logging.error(f"ppl_compile failed with return code {test_ret}")
            verify_ret, verify_output_info = 0, ''

        else:
            if verifyFile_exist:
                cmd = ["python", verifyFile, "--chip", chip]
                verify_ret, verify_output_info = _os_subprocess(cmd, self.time_out)
                if verify_ret != 0:
                    logging.error(f"verify failed with return code {verify_ret}")
                    print(verify_output_info)
            else:
                logging.warning("File does not exist at the specified path.")
                verify_ret, verify_output_info = 0, ""
        os.chdir("..")
        cost_time = time.time() - st_local
        return [pl_file, test_ret, test_output_info, verifyFile_exist, verify_ret, verify_output_info, cost_time]

    def test_all(self, thread_nums=0):
        logging.info(f"+++++++++++ Start Testing PL Files +++++++++++")
        if thread_nums == 1:
            return self.test_all_old() # if threads == 1, use test_all_old
        lock = multiprocessing.Lock()
        for chip in self.chips:
            local_time_cost_list = []
            # change to chip dir
            if not os.path.exists(chip):
                os.makedirs(chip)
            os.chdir(chip)
            input_list = []
            st = time.time()
            applicable_tests = self.get_applicable_tests(chip)
            for sub_dir, files in applicable_tests.items():
                for file in files:
                    pl_file = os.path.join(self.top_dir, sub_dir, file)
                    if self.check_file_exists(pl_file):
                        # only append whtn pl_file exists
                        input_list.append([pl_file, chip, file.split('.')[0]])
            # multi processing and collect all results
            with Pool(thread_nums, initializer=_init_lock, initargs=(lock,)) as p:
                result_list = p.starmap(self.thread_test_and_verify, input_list)
            # analyse the results
            for res in result_list:
                pl_file, test_ret, test_output_info, verifyFile_exist, verify_ret, verify_output_info, cost_time = res
                if test_ret:
                    # ppl_compile error
                    local_time_cost_list.append([pl_file, test_ret, test_output_info, cost_time])
                else:
                    # ppl_compile pass
                    local_time_cost_list.append([pl_file, verify_ret, verify_output_info, cost_time])
                if test_ret == 1:
                    # ppl_compile error
                    self.test_failed_list.append((chip, pl_file))
                if test_ret == 2:
                    # ppl_compile time out
                    self.time_out_list.append((chip, pl_file))
                if verify_ret != 0:
                    # verify error
                    self.vali_failed_list.append((chip, pl_file))
                if verifyFile_exist == 0:
                    # verify files not found
                    self.dubious_pl_list[pl_file] = ""

            self.time_cost_list.append((chip, time.time()-st, local_time_cost_list))
            os.chdir("..")
        self.summarize()
        return FAILURE if (len(self.file_not_found_list) or len(
            self.vali_failed_list) or len(self.test_failed_list)) else SUCCESS

    def test_all_old(self):
        for chip in self.chips:
            local_time_cost_list = []
            st = time.time()
            applicable_tests = self.get_applicable_tests(chip)
            for sub_dir, files in applicable_tests.items():
                for file in files:
                    pl_file = os.path.join(self.top_dir, sub_dir, file)
                    st_local = time.time()
                    ret, output_info = self.test_one(pl_file, chip)
                    if ret == 0:
                        ret, output_info = self.verify_one(pl_file, chip)
                    local_time_cost_list.append((pl_file, ret, output_info, time.time()-st_local))
            self.time_cost_list.append((chip, time.time()-st, local_time_cost_list))
        self.summarize()
        return FAILURE if (len(self.file_not_found_list) or len(
            self.vali_failed_list) or len(self.test_failed_list)) else SUCCESS

class TestSampleFiles(BaseTestFiles):
    def __init__(self, sample_dir, chips, file_list, mode, time_out):
        super().__init__(sample_dir, chips, file_list, mode, True, time_out)
        self.test_type = "Sample"

    def verify_one(self, script_name, chip, filePath):
        _, chip = self.check_is_rv_chip(chip)
        cmd = [script_name, chip, self.mode]
        ret, output_info = _os_subprocess(cmd, self.time_out)
        if ret != 0:
            logging.error(f"Error from {script_name}: {ret}")
            if ret == 1:
                self.test_failed_list.append((chip, filePath))
            if ret == 2:
                self.time_out_list.append((chip, filePath))
        else:
            logging.info(f"Output from {script_name}: {ret}")
        return ret, output_info

    def test_one(self, filePath, chip):
        logging.info(f"+++++++++++ testing {filePath} in {chip} +++++++++++")
        self.check_file_exists(filePath)
        os.chdir(filePath)
        arch = get_chip_code(chip)
        ret, output_info = self.verify_one("./build.sh", arch, filePath)
        if ret == 0:
            self.verify_one("./run.sh", arch, filePath)
        return ret, output_info

    def test_all(self, thread_nums=0):
        logging.info(f"+++++++++++ Start Testing Sample Files +++++++++++")
        for chip in self.chips:
            local_time_cost_list = []
            st = time.time()
            applicable_tests = self.get_applicable_tests(chip)
            for sub_dir, files in applicable_tests.items():
                if len(files):
                    filePath = os.path.join(self.top_dir, sub_dir)
                    st_local = time.time()
                    ret, output_info = self.test_one(filePath, chip)
                    local_time_cost_list.append((filePath, ret, output_info, time.time()-st_local))
            self.time_cost_list.append((chip, time.time()-st, local_time_cost_list))
        self.summarize()
        return FAILURE if (len(self.file_not_found_list) or
                           len(self.test_failed_list)) else SUCCESS

class TestPythonFiles(BaseTestFiles):

    def __init__(self, ppl_dir, chips, file_list, mode, time_out):
        super().__init__(ppl_dir, chips, file_list, mode, True, time_out)
        self.test_type = "Python"
        self.cache_dir = os.environ.get('PPL_CACHE_PATH', default_cache_dir())
        self.clear_cache()

    def clear_cache(self):
        # clear cache dir
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def test_one(self, fileName, chip):
        self.check_file_exists(fileName)
        env = os.environ.copy()
        env['DEBUG'] = '1'
        env['CHIP'] = chip
        env['MODE'] = self.mode
        env['SAVE_DIR'] = os.getcwd()
        os.environ.update(env)
        cmd = ["python3", fileName]
        cmd_str = " ".join(map(str, cmd))
        logging.info("[Running]: {}".format(cmd_str))
        ret, output_info = _os_subprocess(cmd, self.time_out)
        if ret != 0:
            logging.error(f"[Failed]: {cmd_str}")
            if ret == 1:
                self.test_failed_list.append((chip, fileName))
            if ret == 2:
                self.time_out_list.append((chip, fileName))
        else:
            logging.info(f"[Success]: {cmd_str}")
        return ret, output_info

    def thread_test_and_verify(self, py_file, chip):
        st_local = time.time()
        env = os.environ.copy()
        env['DEBUG'] = '1'
        env['CHIP'] = chip
        env['MODE'] = self.mode
        env['SAVE_DIR'] = os.getcwd()
        os.environ.update(env)
        cmd = ["python3", py_file]
        cmd_str = " ".join(map(str, cmd))
        logging.info("[Running]: {}".format(cmd_str))
        ret, output_info = _os_subprocess(cmd, self.time_out)
        if ret != 0:
            logging.error(f"[Failed]: {cmd_str}")
        else:
            logging.info(f"[Success]: {cmd_str}")
        cost_time = time.time() - st_local
        return [py_file, ret, output_info, cost_time]

    def test_all(self, thread_nums=0):
        thread_nums = 1 # todo: use multi threads
        logging.info(f"+++++++++++ Start Testing Python Files +++++++++++")
        if thread_nums == 1:
            return self.test_all_old()
        for chip in self.chips:
            local_time_cost_list = []
            # change to chip dir
            if not os.path.exists(chip):
                os.makedirs(chip)
            os.chdir(chip)
            input_list = []
            st = time.time()
            applicable_tests = self.get_applicable_tests(chip)
            for sub_dir, files in applicable_tests.items():
                for file in files:
                    py_file = os.path.join(self.top_dir, sub_dir, file)
                    if self.check_file_exists(py_file):
                        input_list.append([py_file, chip])
            with Pool(thread_nums) as p:
                result_list = p.starmap(self.thread_test_and_verify, input_list)
            # analyse results
            for res in result_list:
                py_file, ret, output_info, cost_time = res
                if ret == 1:
                    self.test_failed_list.append((chip, py_file))
                if ret == 2:
                    self.time_out_list.append((chip, py_file))
                local_time_cost_list.append([py_file, ret, output_info, cost_time])

            self.time_cost_list.append((chip, time.time()-st, local_time_cost_list))
            os.chdir("..")
        self.summarize()
        return FAILURE if (len(self.file_not_found_list)
                           or len(self.test_failed_list)) else SUCCESS
    def test_all_old(self):
        for chip in self.chips:
            local_time_cost_list = []
            st = time.time()
            applicable_tests = self.get_applicable_tests(chip)
            for sub_dir, files in applicable_tests.items():
                for file in files:
                    py_file = os.path.join(self.top_dir, sub_dir, file)
                    st_local = time.time()
                    ret, output_info = self.test_one(py_file, chip)
                    local_time_cost_list.append((py_file, ret, output_info, time.time()-st_local))
            self.time_cost_list.append((chip, time.time()-st, local_time_cost_list))
            self.clear_cache()
        self.summarize()
        return FAILURE if (len(self.file_not_found_list)
                           or len(self.test_failed_list)) else SUCCESS


def thread_num_generator(threads, min_free_mem=4):
    # keep at least 4GB free memory
    cpu_num = cpu_count()
    # mem_free = psutil.virtual_memory().free / 1000000000 # detect free memory
    # print("cpu core num:", cpu_num, "free memory:", mem_free)
    print("cpu core num:", cpu_num)
    if threads != 0:
        return threads
    cpu_max_threads = int(cpu_num / 2)
    # mem_max_threads = int((mem_free - min_free_mem) / 1.25)
    # threads = min(cpu_max_threads, mem_max_threads)
    threads = cpu_max_threads
    print("calculated thread num is", threads)
    return threads


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--reg_save_dir",
                        type=str,
                        default="./regression_out",
                        help="dir to save the test result")
    parser.add_argument("--reg_mode",
                        type=str.lower,
                        default="basic",
                        choices=["basic", "full"],
                        help="chip platform name")
    parser.add_argument("--chip",
                        type=str.lower,
                        default="bm1684x,bm1688,bm1690,sg2262,mars3,bm1684xe,sg2260e,sg2262rv,bm1684x2,bm1684x2rv",
                        help="chip platform name")
    parser.add_argument("--mode",
                        default='cmodel',
                        help="target building & running mode")
    parser.add_argument("--time_out",
                        type=int,
                        default = 0,
                        help="timeout")
    parser.add_argument("--threads",
                        type = int,
                        default = 0,
                        help="num of threads used")
    parser.add_argument("--tester",
                        type = str,
                        default="pl,sample,py",
                        help="regression test list")
    t0 = time.time()
    args = parser.parse_args()
    if os.path.exists(args.reg_save_dir):
        shutil.rmtree(args.reg_save_dir)
    os.makedirs(args.reg_save_dir)
    os.chdir(args.reg_save_dir)
    ppl_dir = os.getenv('PPL_PROJECT_ROOT')
    chips = args.chip.split(",")
    is_full = True if args.reg_mode == "full" else False
    multiprocessing.set_start_method("spawn", force=True)
    testers = []
    reg_tester_list = args.tester.split(',')
    for t in reg_tester_list:
        if t.strip() == "pl":
            tester = TestPLFiles(ppl_dir, chips, full_pl_list, args.mode, is_full, args.time_out)
        elif t.strip() == "sample":
            tester = TestSampleFiles(ppl_dir, chips, sample_list, args.mode, args.time_out)
        elif t.strip() == "py":
            tester = TestPythonFiles(ppl_dir, chips, python_list, args.mode, args.time_out)
        testers.append(tester)

    exit_status = 0
    result_message = ""

    thread_nums = thread_num_generator(args.threads)

    for test_runner in testers:
        if not isinstance(test_runner, BaseTestFiles):
            continue
        exit_status = test_runner.test_all(thread_nums) or exit_status
        result_message += test_runner.result_message

    logging.critical(result_message)
    print("total cost time:", time.time() - t0, "seconds")
    print(result_message)
    print("exit_status: ", exit_status)
    exit(exit_status)
