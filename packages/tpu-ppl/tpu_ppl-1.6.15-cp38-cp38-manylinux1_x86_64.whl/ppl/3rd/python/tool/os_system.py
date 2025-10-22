import logging
import argparse
import subprocess
import os
import time
import shlex
import signal
from subprocess import Popen, PIPE

def _os_subprocess(cmd: list, time_out: int = 0):
    cmd_str = ""
    for s in cmd:
        cmd_str += str(s) + " "
    print("[Running]: {}".format(cmd_str))
    process = Popen(shlex.split(cmd_str), stdout=PIPE, stderr=subprocess.STDOUT)
    st = time.time()
    info = ""
    while True:
        output = process.stdout.readline().rstrip().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            info += output.strip() + "\n"

        if time_out > 0 and time.time() - st > time_out:
            os.kill(process.pid, signal.SIGTERM)
            print("[!Warning:TimeOut]: {}".format(cmd_str))
            return 2 , "[!Warning:TimeOut]: {}".format(cmd_str)

    rc = process.poll()
    if rc == 0:
        print("[Success]: {}".format(cmd_str))
        info = " "
    else:
        print("rc: {}, [!Error]: {}".format(rc, cmd_str))
        print(info)
        rc = 1
    return rc, info

def _os_subprocess_with_log(cmd: list, log_name, time_out: int = 0):
    cmd_str = " ".join(map(str, cmd))
    print("[Running]: {}".format(cmd_str))
    cmd_str += f" > {log_name} 2>&1"
    time_out = 0
    err = 0
    rc = 0
    try:
        result = subprocess.run(
            cmd_str,
            text=True,
            check=True,
            shell=True,
            timeout=time_out if time_out > 0 else None
        )
        rc = result.returncode
    except subprocess.TimeoutExpired:
        print("[!Warning:TimeOut]: {}".format(cmd_str))
        time_out = 1
    except Exception as e:
        err = 1
    
    try:
        with open(log_name, "r") as f:
            output = f.read().strip()
    except FileNotFoundError:
        output = ""

    if err:
        print("ret 1, [!Error]: {}".format(cmd_str))
        return 1, output
    if time_out:
        print("[!Warning:TimeOut]: {}".format(cmd_str))
        return 2, output
    if rc:
        print("ret {}, [!Error]: {}".format(rc, cmd_str))
        return rc, output
    else:
        print("[Success]: {}".format(cmd_str))
        return 0, output

def _os_system(cmd: list, time_out: int = 0):
    cmd_str = ""
    for s in cmd:
        cmd_str += str(s) + " "
    print("[Running]: {}".format(cmd_str))
    ret = os.system(cmd_str)
    if ret == 0:
        print("[Success]: {}".format(cmd_str))
    else:
        print("[!Error]: {}".format(cmd_str))
        return 1
    return 0
