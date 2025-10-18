import sys
import os
import subprocess
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

here = os.path.abspath(os.path.dirname(__file__))

def _brew_prefix(pkg: str) -> str | None:
    try:
        return subprocess.check_output(["brew", "--prefix", pkg], text=True).strip()
    except Exception:
        return None

def _openblas_paths():
    # Prefer explicit env if set (works cross-platform)
    ob_dir = os.environ.get("OPENBLAS_DIR")
    if ob_dir:
        return os.path.join(ob_dir, "include"), os.path.join(ob_dir, "lib")

    # macOS Homebrew OpenBLAS
    if sys.platform == "darwin":
        p = _brew_prefix("openblas")
        if p:
            return os.path.join(p, "include"), os.path.join(p, "lib")

    # Fallback: nothing found
    return None, None

class BuildExt(build_ext):
    def build_extension(self, ext):
        """Override to handle per-file compilation flags"""
        # Save original flags
        original_compile_args = ext.extra_compile_args or []
        
        # Separate sources by type
        c_sources = [s for s in ext.sources if s.endswith('.c')]
        cpp_sources = [s for s in ext.sources if s.endswith(('.cpp', '.cc', '.cxx'))]
        
        # Build C files with C flags
        if c_sources:
            ext.sources = c_sources
            ext.extra_compile_args = self._get_c_flags()
            super().build_extension(ext)
        
        # Build C++ files with C++ flags
        if cpp_sources:
            ext.sources = cpp_sources
            ext.extra_compile_args = self._get_cpp_flags()
            super().build_extension(ext)
        
        # Restore for linking
        ext.sources = c_sources + cpp_sources
        ext.extra_compile_args = original_compile_args
    
    def _get_c_flags(self):
        """Get flags appropriate for C compilation"""
        compiler = self.compiler.compiler_type
        
        if compiler == "msvc":
            flags = []
        else:
            flags = []
            if sys.platform == "darwin":
                flags.extend(["-arch", "arm64"])
        
        return flags
    
    def _get_cpp_flags(self):
        """Get flags appropriate for C++ compilation"""
        compiler = self.compiler.compiler_type
        
        if compiler == "msvc":
            flags = ["/std:c++20"]
        else:
            flags = ["-std=c++20"]
            if sys.platform == "darwin":
                flags.extend(["-stdlib=libc++", "-arch", "arm64"])
        
        return flags
    
    def build_extensions(self):
        compiler = self.compiler.compiler_type
        print(f"Detected compiler: {compiler}")
        
        if sys.platform == "darwin":
            print("Building for ARM64 only (Apple Silicon)")

        # --- OpenBLAS wiring ---
        ob_inc, ob_lib = _openblas_paths()
        if ob_inc and ob_lib:
            print(f"Using OpenBLAS include: {ob_inc}")
            print(f"Using OpenBLAS libdir: {ob_lib}")
            for ext in self.extensions:
                # Preserve order: add OpenBLAS at the end to not interfere with project includes
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
            print("  e.g., brew install openblas")

        # Set link flags for all extensions
        for ext in self.extensions:
            existing_link = getattr(ext, "extra_link_args", []) or []
            
            if compiler == "msvc":
                link_args = []
            else:
                link_args = []
                if sys.platform == "darwin":
                    link_args.extend(["-stdlib=libc++", "-arch", "arm64"])
            
            ext.extra_link_args = existing_link + link_args

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
            "src/matrix/structures/ndarray.c"
        ],
        include_dirs=[
            os.path.join(here, "src"),
            os.path.join(here, "src", "pybinding"),
            os.path.join(here, "src", "matrix", "structures"),  # Add this for ndarray.h
        ],
        language="c++",
    ),
]

setup(
    name="pypearl",
    version="0.6.9",
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