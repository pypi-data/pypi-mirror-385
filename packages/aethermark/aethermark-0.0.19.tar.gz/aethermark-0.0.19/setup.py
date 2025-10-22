from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "_aethermark",
        sources=[
            "bindings/aethermark_py.cpp",
            "src/aethermark.cpp",  # include your main library
        ],
        include_dirs=[
            "include",
            pybind11.get_include(),
        ],
        language="c++",
        extra_compile_args=["-std=c++17"],
    ),
]

setup(
    name="aethermark",
    version="0.0.19",
    ext_modules=ext_modules,
)
