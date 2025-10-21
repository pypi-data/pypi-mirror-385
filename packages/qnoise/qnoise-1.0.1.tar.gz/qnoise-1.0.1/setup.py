from setuptools import setup, Extension
import pybind11
import sys
import os

# Get the directory containing setup.py
here = os.path.abspath(os.path.dirname(__file__))

ext_modules = [
    Extension(
        "qnoise._qnoise",
        sources=[
            "qnoise/qNoisePy.cpp",
            "cpp/qNoise.cpp",  
        ],
        include_dirs=[
            pybind11.get_include(),
            "cpp",  
        ],
        language="c++",
        extra_compile_args=["-std=c++11", "-O3", "-Wall", "-fPIC"] if sys.platform != "win32" else ["/std:c++14", "/O2"],
    ),
]

setup(ext_modules=ext_modules, zip_safe=False)