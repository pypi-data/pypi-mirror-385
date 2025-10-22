import os
import platform
import re
import contextlib
import shlex
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import zipfile
import urllib.request
import json
from io import BytesIO
#from distutils.command.clean import clean
from pathlib import Path
from typing import List, NamedTuple, Optional

from setuptools import Extension, setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py
from dataclasses import dataclass

#from distutils.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from wheel.bdist_wheel import bdist_wheel
from setuptools import Command
from setuptools.command.install import install
# ---- package data ---
def get_base_dir():
    return os.path.relpath(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), os.path.dirname(__file__))

def get_cmake_dir():
    plat_name = sysconfig.get_platform()
    python_version = sysconfig.get_python_version()
    dir_name = f"cmake.{plat_name}-{sys.implementation.name}-{python_version}"
    cmake_dir = Path(get_base_dir()) / "python" / "build" / dir_name
    cmake_dir.mkdir(parents=True, exist_ok=True)
    return cmake_dir

class CMakeClean(Command):

    def initialize_options(self):
        clean.initialize_options(self)
        self.build_temp = get_cmake_dir()


class CMakeBuildPy(build_py):

    def run(self) -> None:
        self.run_command('build_ext')
        return super().run()


class CMakeExtension(Extension):

    def __init__(self, name, path, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.relpath(os.path.abspath(sourcedir), os.path.dirname(__file__))
        self.path = path


class CMakeBuild(build_ext):

    user_options = build_ext.user_options + \
        [('base-dir=', None, 'base directory of Triton')]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.base_dir = get_base_dir()

    def finalize_options(self):
        build_ext.finalize_options(self)

    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
      os.chdir(self.base_dir)
      command = f"bash -c 'source envsetup.sh && bash build.sh Release && bash setup_python.sh'"
      os.system(command)
      os.chdir(os.path.join("./", "python"))

class plugin_install(install):
    def run(self):
        install.run(self)


class plugin_develop(develop):
    def run(self):
        develop.run(self)


class plugin_bdist_wheel(bdist_wheel):
    def run(self):
        bdist_wheel.run(self)


class plugin_egginfo(egg_info):
    def run(self):
        egg_info.run(self)

def get_packages():
    return find_packages(include=['ppl*'])

def get_entry_points():
    entry_points = {}
    return entry_points

def get_version():
  ppl_version = "1.0.108"
  PPL_BUILD_PATH = os.getenv("PPL_BUILD_PATH")
  if PPL_BUILD_PATH is None:
    PPL_BUILD_PATH=os.path.join(get_base_dir(), "build")

  command = f"grep PPL_VERSION {PPL_BUILD_PATH}/CMakeCache.txt | cut -d'=' -f2 | cut -d'-' -f1"
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  if process.returncode != 0:
    print(f"Error: {stderr.decode().strip()}")
  else:
    ppl_version = stdout.decode().strip()
  return ppl_version

package_data = {
    'ppl': ["_C/*.so"],
    'ppl': ["3rd/*"],
}

setup(
    name=os.environ.get("PPL_WHEEL_NAME", "tpu_ppl"),
    version=get_version(),
    author="liang.chen",
    author_email="liang.chen@sophgo.com",
    description="A language and compiler for custom Deep Learning operations",
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    packages=get_packages(),
    package_data=package_data,
    include_package_data=True,
    #data_files=[('_C', ['ppl/_C/libppl.so'])],
    entry_points=get_entry_points(),
    ext_modules=[CMakeExtension("ppl", "ppl/_C/")],
    cmdclass={
        "build_ext": CMakeBuild,
        "build_py": CMakeBuildPy,
        "clean": CMakeClean,
        "install": plugin_install,
        "develop": plugin_develop,
        "bdist_wheel": plugin_bdist_wheel,
        "egg_info": plugin_egginfo,
    },
    zip_safe=False,
    # for PyPI
    keywords=["Compiler", "Deep Learning"],
    url="https://github.com/sophgo/PPL/",
    license="2-Clause BSD",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    # install_requires=[
    #     # "torch==2.1.1",
    #     "numpy"
    # ],
    test_suite="tests",
    extras_require={
        "build": [
            "cmake>=3.20",
            "lit"
        ],
    },
)
