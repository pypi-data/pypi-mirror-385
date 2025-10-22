#!/usr/bin/env python3
import os
import argparse
import shutil
import subprocess
from example_hw import sample_list
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s -\n%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

SUCCESS = 0
FAILURE = 1


class BaseTestFiles:

    def __init__(self, top_dir, chips, file_list, mode, is_full):
        self.result_message = ""
        self.top_dir = top_dir
        self.file_list = file_list
        self.chips = chips
        self.test_failed_list = []
        self.vali_failed_list = []
        self.dubious_pl_list = {}
        self.file_not_found_list = {}
        self.chip_index_map = {
            'bm1684x': 1,
            'bm1688': 2,
            'bm1690': 3,
            'sg2380': 4,
        }
        self.mode = mode
        self.is_full = is_full

    def summarize(self):
        self.result_message = f"\n====================== {str(self.__class__.__name__)} test summarize ======================\n"
        if self.file_not_found_list:
            self.result_message += "\n[WARNING]: File does not exist:\n"
            for fileName, _ in self.file_not_found_list.items():
                self.result_message += f"- {fileName}\n"

        if self.test_failed_list:
            self.result_message += "[FAILED]: These PL files failed in compilation:\n"
            for chip, fileName in self.test_failed_list:
                self.result_message += f"- {fileName} tested in PLATFORM: {chip}\n"
        else:
            self.result_message += "[SUCCESS]: All PL files passed compilation\n"

        if self.vali_failed_list:
            self.result_message += "[FAILED]: These PL files do not passed the correctness validation:\n"
            for chip, fileName in self.vali_failed_list:
                self.result_message += f"- {fileName} validated in PLATFORM: {chip}\n"
        else:
            self.result_message += "[SUCCESS]: All correctness validation passed.\n"

        if self.dubious_pl_list:
            self.result_message += "\n[WARNING]: These PL files do not have correctness validation scripts:\n"
            for fileName, _ in self.dubious_pl_list.items():
                self.result_message += f"- {fileName}\n"

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

    def test_all(self):
        raise NotImplementedError("Subclasses should implement this method")

class TestSampleFiles(BaseTestFiles):
    def __init__(self, sample_dir, chips, file_list, mode):
        super().__init__(sample_dir, chips, file_list, mode, True)

    def verify_one(self, script_name, chip, filePath):
        cmd = [script_name, chip, self.mode]
        ret = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
        if ret.stdout:
            logging.info(f"Output from {script_name}: {ret.stdout}")
        if "FAILED" in ret.stdout or ret.returncode:
            logging.error(f"Error from {script_name}: {ret.stderr}")
            self.test_failed_list.append((chip, filePath))

    def test_one(self, filePath, chip):
        self.check_file_exists(filePath)
        os.chdir(filePath)
        self.verify_one("./build.sh", chip, filePath)
        #self.verify_one("./run.sh", chip, filePath)

    def test_all(self):
        for chip in self.chips:
            applicable_tests = self.get_applicable_tests(chip)
            for sub_dir, files in applicable_tests.items():
                if len(files):
                    filePath = os.path.join(self.top_dir, sub_dir)
                    self.test_one(filePath, chip)
        self.summarize()
        return FAILURE if (len(self.file_not_found_list) or
                           len(self.test_failed_list)) else SUCCESS

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
                        default="bm1684x,bm1690,bm1688",
                        help="chip platform name")
    parser.add_argument("--mode",
                        default='cmodel',
                        help="target building & running mode")
    args = parser.parse_args()
    if os.path.exists(args.reg_save_dir):
        shutil.rmtree(args.reg_save_dir)
    os.makedirs(args.reg_save_dir)
    os.chdir(args.reg_save_dir)
    ppl_dir = os.getenv('PPL_PROJECT_ROOT')
    chips = args.chip.split(",")
    is_full = True if args.reg_mode == "full" else False

    sampleTest = TestSampleFiles(ppl_dir, chips, sample_list, args.mode)
    exit_status = 0
    testers = [sampleTest]
    result_message = ""
    for test_runner in testers:
        if not isinstance(test_runner, BaseTestFiles):
            continue
        exit_status = test_runner.test_all() or exit_status
        result_message += test_runner.result_message

    logging.critical(result_message)
    exit(exit_status)
