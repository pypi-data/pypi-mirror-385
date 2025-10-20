def _cmake_to_bool(s):
    return s.upper() not in ['', '0','FALSE','OFF','N','NO','IGNORE','NOTFOUND']

is_python_package    = _cmake_to_bool("TRUE")

BUILD_FOR_CONDA     = _cmake_to_bool("ON")
BUILD_STUB_FILES    = _cmake_to_bool("ON")
CHECK_RANGE         = _cmake_to_bool("OFF")
DEBUG_LOG           = _cmake_to_bool("OFF")
ENABLE_CPP_CORE_GUIDELINES_CHECK  = _cmake_to_bool("OFF")
ENABLE_UNIT_TESTS   = _cmake_to_bool("OFF")
INSTALL_PROFILES    = _cmake_to_bool("OFF")
INTEL_MIC           = _cmake_to_bool("OFF")
TRACE_MEMORY        = _cmake_to_bool("OFF")
USE_CCACHE          = _cmake_to_bool("ON")
USE_CGNS            = _cmake_to_bool("OFF")
USE_GUI             = _cmake_to_bool("ON")
USE_INTERNAL_TCL    = _cmake_to_bool("ON")
USE_JPEG            = _cmake_to_bool("OFF")
USE_MPEG            = _cmake_to_bool("OFF")
USE_MPI             = _cmake_to_bool("OFF")
USE_MPI4PY          = _cmake_to_bool("")
USE_NATIVE_ARCH     = _cmake_to_bool("OFF")
USE_NUMA            = _cmake_to_bool("OFF")
USE_OCC             = _cmake_to_bool("ON")
USE_PYTHON          = _cmake_to_bool("ON")
USE_SPDLOG          = _cmake_to_bool("")

CMAKE_INSTALL_PREFIX  = "C:/gitlabci/tools/builds/3zsqG5ns/0/ngsolve/netgen/_skbuild/win-amd64-3.13/cmake-install"
NG_INSTALL_DIR_PYTHON   = "."
NG_INSTALL_DIR_BIN      = "netgen"
NG_INSTALL_DIR_LIB      = "netgen/lib"
NG_INSTALL_DIR_INCLUDE  = "netgen/include"
NG_INSTALL_DIR_CMAKE    = "netgen/cmake"
NG_INSTALL_DIR_RES      = "share"

NETGEN_PYTHON_RPATH_BIN = "netgen"
NETGEN_PYTHON_RPATH     = "netgen"
NETGEN_PYTHON_PACKAGE_NAME = "netgen-mesher"

NG_COMPILE_FLAGS           = "/arch:AVX2"
ngcore_compile_options     = "/arch:AVX2;/bigobj;$<BUILD_INTERFACE:/MP;/W1;/wd4068>"
ngcore_compile_definitions = "NETGEN_PYTHON;NG_PYTHON;PYBIND11_SIMPLE_GIL_MANAGEMENT;_WIN32_WINNT=0x1000;WNT;WNT_WINDOW;NOMINMAX;MSVC_EXPRESS;_CRT_SECURE_NO_WARNINGS;HAVE_STRUCT_TIMESPEC;WIN32"

NETGEN_VERSION = "6.2.2506-20-gcd974c3b"
NETGEN_VERSION_GIT = "v6.2.2506-20-gcd974c3b"
NETGEN_VERSION_PYTHON = "6.2.2506.post20.dev0"

NETGEN_VERSION_MAJOR = "6"
NETGEN_VERSION_MINOR = "2"
NETGEN_VERSION_TWEAK = "20"
NETGEN_VERSION_PATCH = "2506"
NETGEN_VERSION_HASH = "gcd974c3b"

PYTHON_VERSION       = "3.13.2"
PYTHON_VERSION_MAJOR = "3"
PYTHON_VERSION_MINOR = "13"

version = NETGEN_VERSION_GIT

def get_cmake_dir():
    import os.path as p
    d_python = p.dirname(p.dirname(p.dirname(__file__)))
    py_to_cmake = p.relpath(
            NG_INSTALL_DIR_CMAKE,
            NG_INSTALL_DIR_PYTHON
            )
    return p.normpath(p.join(d_python,py_to_cmake))
