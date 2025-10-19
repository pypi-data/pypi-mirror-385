#!python3  # noqa: EXE001

import shutil
from pathlib import Path

import numpy as np
import setuptools._distutils.ccompiler
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

sund_folder = Path("src") / "_core"
sundials_dir = Path("src") / "third_party" / "sundials"

# Check if sundials directory exists
if not sundials_dir.is_dir():
    msg = f"Sundials directory not found at {sundials_dir}. This likely means you need to update git submodules. Try running: git submodule update --init --recursive"  # noqa: E501
    raise FileNotFoundError(
        msg,
    )
elif not any(sundials_dir.iterdir()):  # Check if directory is empty
    msg = f"Sundials directory at {sundials_dir} is empty. This likely means you need to update git submodules. Try running: git submodule update --init --recursive"  # noqa: E501
    raise FileNotFoundError(
        msg,
    )


class CustomBuildExt(build_ext):
    def build_extension(self, ext):
        compiler = setuptools._distutils.ccompiler.new_compiler()  # noqa: SLF001
        compiler_type = compiler.compiler_type

        # Store original compile method to restore later
        orig_compile = self.compiler.compile

        # Override the compile method to handle different file types
        def specialized_compile(sources, **kwargs):
            c_sources = []
            cpp_sources = []

            for source in sources:
                if Path(source).suffix == ".c":
                    c_sources.append(source)
                else:
                    cpp_sources.append(source)

            # Backup existing compile args
            original_compile_args = kwargs.get("extra_preargs", [])

            # Compile C++ files with C++20
            if cpp_sources:
                cpp_compile_args = list(original_compile_args)
                if compiler_type == "msvc":
                    cpp_compile_args += ["/std:c++20"]
                elif compiler_type == "unix":
                    cpp_compile_args += ["-std=c++20"]

                kwargs["extra_preargs"] = cpp_compile_args
                cpp_objects = orig_compile(cpp_sources, **kwargs)
            else:
                cpp_objects = []

            # Compile C files with C11 or appropriate C standard
            if c_sources:
                c_compile_args = list(original_compile_args)
                if compiler_type == "msvc":
                    # MSVC doesn't use /std for C
                    pass
                elif compiler_type == "unix":
                    c_compile_args += ["-std=c11"]  # Use C11 standard for C files

                kwargs["extra_preargs"] = c_compile_args
                c_objects = orig_compile(c_sources, **kwargs)
            else:
                c_objects = []

            return cpp_objects + c_objects

        # Replace compile method with our specialized version
        self.compiler.compile = specialized_compile

        try:
            super().build_extension(ext)
        finally:
            # Restore original compile method
            self.compiler.compile = orig_compile


# Copy files needed for building the models later to the sund/_model_deps folder
dst_dir = Path("src") / "sund" / "_model_deps"
(dst_dir / "_include").mkdir(parents=True, exist_ok=True)
(dst_dir / "_src").mkdir(parents=True, exist_ok=True)

header_files = [
    sund_folder / "ExtraFormulas" / "mathaddon.h",
    sund_folder / "ExtraFormulas" / "mathaddon.cpp",
    sund_folder / "_Models" / "Models_M_API.h",
    sund_folder / "_Models" / "model_structure.h",
    sund_folder / "sund_sundials" / "sund_sundials_flags.h",
    sund_folder / "include" / "pyarraymacros.h",
    sund_folder / "include" / "timescales.h",
]

for header_file in header_files:
    if header_file.exists():
        target_dir = "_include" if header_file.suffix == ".h" else "_src"
        shutil.copy(header_file, dst_dir / target_dir / header_file.name)


# Define includes
include = [
    Path(np.get_include()),
    sund_folder / "sund_sundials",
    sund_folder / "include",
    sund_folder / "_Activity",
    sund_folder / "_debug",
    sund_folder / "_Models",
    sund_folder / "_Simulation",
    sund_folder / "_StringList",
]

# Debug module source
debug_source = sund_folder / "_debug" / "debug.cpp"

_Activity = Extension(
    name="sund._Activity",
    include_dirs=include,
    sources=[sund_folder / "_Activity" / "Activity.cpp", debug_source],
)

_debug = Extension(name="sund._debug", include_dirs=include, sources=[debug_source])

_Models = Extension(
    name="sund._Models",
    include_dirs=include,
    sources=[sund_folder / "_Models" / "Models.cpp", debug_source],
)

# Get all sund_sundials source files
sund_sundials_files = [
    sund_folder / "sund_sundials" / "sund_cvode.cpp",
    sund_folder / "sund_sundials" / "sund_ida.cpp",
]

sundials_files = [
    sundials_dir / "src" / "cvode" / "cvode.c",
    sundials_dir / "src" / "cvode" / "cvode_bandpre.c",
    sundials_dir / "src" / "cvode" / "cvode_bbdpre.c",
    sundials_dir / "src" / "cvode" / "cvode_diag.c",
    # sundials_dir / "src" / "cvode" / "cvode_direct.c", # Removed between sundials 5.5.0 to 7.0.0
    # sundials_dir / "src" / "cvode" / "cvode_fused_gpu.cpp", # GPU support, not implemented
    sundials_dir / "src" / "cvode" / "cvode_fused_stubs.c",
    sundials_dir / "src" / "cvode" / "cvode_io.c",
    sundials_dir / "src" / "cvode" / "cvode_ls.c",
    # sundials_dir / "src" / "cvode" / "cvode_spils.c",  # Removed between sundials 5.5.0 to 7.0.0
    sundials_dir / "src" / "cvode" / "cvode_nls.c",
    sundials_dir / "src" / "cvode" / "cvode_proj.c",
    sundials_dir / "src" / "ida" / "ida.c",
    sundials_dir / "src" / "ida" / "ida_bbdpre.c",
    # sundials_dir / "src" / "ida" / "ida_direct.c",  # Removed between sundials 5.5.0 to 7.0.0
    sundials_dir / "src" / "ida" / "ida_ic.c",
    sundials_dir / "src" / "ida" / "ida_io.c",
    sundials_dir / "src" / "ida" / "ida_ls.c",
    sundials_dir / "src" / "ida" / "ida_nls.c",
    sundials_dir / "src" / "nvector" / "serial" / "nvector_serial.c",
    sundials_dir / "src" / "sundials" / "sundials_band.c",
    sundials_dir / "src" / "sundials" / "sundials_context.c",
    sundials_dir / "src" / "sundials" / "sundials_dense.c",
    sundials_dir / "src" / "sundials" / "sundials_direct.c",
    sundials_dir / "src" / "sundials" / "sundials_errors.c",
    sundials_dir / "src" / "sundials" / "sundials_hashmap.c",
    sundials_dir / "src" / "sundials" / "sundials_iterative.c",
    sundials_dir / "src" / "sundials" / "sundials_linearsolver.c",
    sundials_dir / "src" / "sundials" / "sundials_logger.c",
    sundials_dir / "src" / "sundials" / "sundials_math.c",
    sundials_dir / "src" / "sundials" / "sundials_matrix.c",
    sundials_dir / "src" / "sundials" / "sundials_nonlinearsolver.c",
    sundials_dir / "src" / "sundials" / "sundials_nvector.c",
    sundials_dir / "src" / "sundials" / "sundials_nvector_senswrapper.c",
    sundials_dir / "src" / "sundials" / "sundials_version.c",
    sundials_dir / "src" / "sunlinsol" / "band" / "sunlinsol_band.c",
    sundials_dir / "src" / "sunlinsol" / "dense" / "sunlinsol_dense.c",
    sundials_dir / "src" / "sunlinsol" / "pcg" / "sunlinsol_pcg.c",
    sundials_dir / "src" / "sunlinsol" / "spbcgs" / "sunlinsol_spbcgs.c",
    sundials_dir / "src" / "sunlinsol" / "spfgmr" / "sunlinsol_spfgmr.c",
    sundials_dir / "src" / "sunlinsol" / "spgmr" / "sunlinsol_spgmr.c",
    sundials_dir / "src" / "sunlinsol" / "sptfqmr" / "sunlinsol_sptfqmr.c",
    sundials_dir / "src" / "sunmatrix" / "band" / "sunmatrix_band.c",
    sundials_dir / "src" / "sunmatrix" / "dense" / "sunmatrix_dense.c",
    sundials_dir / "src" / "sunmatrix" / "sparse" / "sunmatrix_sparse.c",
    sundials_dir / "src" / "sunnonlinsol" / "newton" / "sunnonlinsol_newton.c",
    sundials_dir / "src" / "sunnonlinsol" / "fixedpoint" / "sunnonlinsol_fixedpoint.c",
]

sundials_includes = [
    sundials_dir / "include",
    sundials_dir / "src",
    sundials_dir / "src" / "sundials",
]

_Simulation = Extension(
    name="sund._Simulation",
    include_dirs=include + sundials_includes,
    sources=[
        sund_folder / "_Simulation" / "_Simulation.cpp",
        debug_source,
        *sund_sundials_files,
        *sundials_files,
    ],
)

_StringList = Extension(
    name="sund._StringList",
    include_dirs=include,
    sources=[sund_folder / "_StringList" / "_StringList.cpp", debug_source],
)

setup(
    cmdclass={"build_ext": CustomBuildExt},
    ext_modules=[_Activity, _debug, _Models, _Simulation, _StringList],
)
