import sys
import os
import subprocess
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.unixccompiler import UnixCCompiler

here = os.path.abspath(os.path.dirname(__file__))

def _brew_prefix(pkg: str) -> str | None:
    try:
        return subprocess.check_output(["brew", "--prefix", pkg], text=True).strip()
    except Exception:
        return None

def _openblas_paths():
    ob_dir = os.environ.get("OPENBLAS_DIR")
    if ob_dir:
        return os.path.join(ob_dir, "include"), os.path.join(ob_dir, "lib")

    if sys.platform == "darwin":
        p = _brew_prefix("openblas")
        if p:
            return os.path.join(p, "include"), os.path.join(p, "lib")

    return None, None

class BuildExt(build_ext):
    def build_extensions(self):
        # Monkey-patch the compiler to treat .c files as C++
        if isinstance(self.compiler, UnixCCompiler):
            original_compile = self.compiler._compile
            
            def _compile_wrapper(obj, src, ext, cc_args, extra_postargs, pp_opts):
                # Force C++ compilation for .c files by using the C++ compiler
                if src.endswith('.c'):
                    # Replace C compiler with C++ compiler
                    original_compiler_so = self.compiler.compiler_so
                    self.compiler.compiler_so = self.compiler.compiler_cxx
                    try:
                        return original_compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
                    finally:
                        self.compiler.compiler_so = original_compiler_so
                else:
                    return original_compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
            
            self.compiler._compile = _compile_wrapper
        
        compiler = self.compiler.compiler_type
        print(f"Detected compiler: {compiler}")
        
        if sys.platform == "darwin":
            print("Building for ARM64 only (Apple Silicon)")

        # OpenBLAS setup
        ob_inc, ob_lib = _openblas_paths()
        if ob_inc and ob_lib:
            print(f"Using OpenBLAS include: {ob_inc}")
            print(f"Using OpenBLAS libdir: {ob_lib}")
            for ext in self.extensions:
                if ob_inc not in (ext.include_dirs or []):
                    ext.include_dirs = (ext.include_dirs or []) + [ob_inc]
                if ob_lib not in (ext.library_dirs or []):
                    ext.library_dirs = (ext.library_dirs or []) + [ob_lib]
                if "openblas" not in (ext.libraries or []):
                    ext.libraries = (ext.libraries or []) + ["openblas"]
                if sys.platform == "darwin":
                    rpath_flag = f"-Wl,-rpath,{ob_lib}"
                    existing_link = getattr(ext, "extra_link_args", []) or []
                    if rpath_flag not in existing_link:
                        ext.extra_link_args = existing_link + [rpath_flag]
        else:
            print("WARNING: OpenBLAS not found. Set OPENBLAS_DIR or install via Homebrew.")

        # Apply C++ flags to all extensions
        for ext in self.extensions:
            if compiler == "msvc":
                cpp_args = ["/std:c++20"]
                link_args = []
            else:
                cpp_args = ["-std=c++20"]
                link_args = []
                if sys.platform == "darwin":
                    cpp_args.extend(["-stdlib=libc++", "-arch", "arm64"])
                    link_args.extend(["-stdlib=libc++", "-arch", "arm64"])
            
            ext.extra_compile_args = (ext.extra_compile_args or []) + cpp_args
            ext.extra_link_args = (ext.extra_link_args or []) + link_args

        super().build_extensions()

ext_modules = [
    Extension(
        name="pypearl._pypearl",
        sources=[
            "src/pybinding/binding.cpp",
            "src/pybinding/layerbinding.cpp",
            "src/pybinding/matrixbinding.cpp",
            "src/pybinding/activationbinding/relubinding.cpp",
            "src/pybinding/activationbinding/softmaxbinding.cpp",
            "src/pybinding/lossbinding/ccebinding.cpp",
            "src/pybinding/optimizerbinding/sgdbinding.cpp",
            "src/pybinding/modelbinding/modelbinding.cpp",
            # ndarray.c is included by binding.cpp, not compiled separately
        ],
        include_dirs=[
            os.path.join(here, "src"),
            os.path.join(here, "src", "pybinding"),
            os.path.join(here, "src", "matrix", "structures"),
        ],
        language="c++",
    ),
]

setup(
    name="pypearl",
    version="0.6.12",
    author="Brody Massad",
    author_email="brodymassad@gmail.com",
    description="An efficient Machine Learning Library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
    packages=find_packages(),
    package_data={"pypearl": ["*.pyi", "py.typed"]},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)