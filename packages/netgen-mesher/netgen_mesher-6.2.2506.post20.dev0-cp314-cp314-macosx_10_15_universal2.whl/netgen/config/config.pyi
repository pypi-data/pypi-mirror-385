from __future__ import annotations
__all__: list[str] = ['BUILD_FOR_CONDA', 'BUILD_STUB_FILES', 'CHECK_RANGE', 'CMAKE_INSTALL_PREFIX', 'DEBUG_LOG', 'ENABLE_CPP_CORE_GUIDELINES_CHECK', 'ENABLE_UNIT_TESTS', 'INSTALL_PROFILES', 'INTEL_MIC', 'NETGEN_PYTHON_PACKAGE_NAME', 'NETGEN_PYTHON_RPATH', 'NETGEN_PYTHON_RPATH_BIN', 'NETGEN_VERSION', 'NETGEN_VERSION_GIT', 'NETGEN_VERSION_HASH', 'NETGEN_VERSION_MAJOR', 'NETGEN_VERSION_MINOR', 'NETGEN_VERSION_PATCH', 'NETGEN_VERSION_PYTHON', 'NETGEN_VERSION_TWEAK', 'NG_COMPILE_FLAGS', 'NG_INSTALL_DIR_BIN', 'NG_INSTALL_DIR_CMAKE', 'NG_INSTALL_DIR_INCLUDE', 'NG_INSTALL_DIR_LIB', 'NG_INSTALL_DIR_PYTHON', 'NG_INSTALL_DIR_RES', 'PYTHON_VERSION', 'PYTHON_VERSION_MAJOR', 'PYTHON_VERSION_MINOR', 'TRACE_MEMORY', 'USE_CCACHE', 'USE_CGNS', 'USE_GUI', 'USE_INTERNAL_TCL', 'USE_JPEG', 'USE_MPEG', 'USE_MPI', 'USE_MPI4PY', 'USE_NATIVE_ARCH', 'USE_NUMA', 'USE_OCC', 'USE_PYTHON', 'USE_SPDLOG', 'get_cmake_dir', 'is_python_package', 'ngcore_compile_definitions', 'ngcore_compile_options', 'version']
def _cmake_to_bool(s):
    ...
def get_cmake_dir():
    ...
BUILD_FOR_CONDA: bool = True
BUILD_STUB_FILES: bool = True
CHECK_RANGE: bool = False
CMAKE_INSTALL_PREFIX: str = '/Users/gitlab-runner/builds/builds/rL7WHzyj/0/ngsolve/netgen/_skbuild/macosx-10.15-universal2-3.14/cmake-install'
DEBUG_LOG: bool = False
ENABLE_CPP_CORE_GUIDELINES_CHECK: bool = False
ENABLE_UNIT_TESTS: bool = False
INSTALL_PROFILES: bool = False
INTEL_MIC: bool = False
NETGEN_PYTHON_PACKAGE_NAME: str = 'netgen-mesher'
NETGEN_PYTHON_RPATH: str = 'netgen'
NETGEN_PYTHON_RPATH_BIN: str = 'bin'
NETGEN_VERSION: str = '6.2.2506-20-gcd974c3b'
NETGEN_VERSION_GIT: str = 'v6.2.2506-20-gcd974c3b'
NETGEN_VERSION_HASH: str = 'gcd974c3b'
NETGEN_VERSION_MAJOR: str = '6'
NETGEN_VERSION_MINOR: str = '2'
NETGEN_VERSION_PATCH: str = '2506'
NETGEN_VERSION_PYTHON: str = '6.2.2506.post20.dev0'
NETGEN_VERSION_TWEAK: str = '20'
NG_COMPILE_FLAGS: str = '-Xarch_x86_64;-march=core-avx2'
NG_INSTALL_DIR_BIN: str = 'bin'
NG_INSTALL_DIR_CMAKE: str = 'netgen/cmake'
NG_INSTALL_DIR_INCLUDE: str = 'netgen/include'
NG_INSTALL_DIR_LIB: str = 'netgen'
NG_INSTALL_DIR_PYTHON: str = '.'
NG_INSTALL_DIR_RES: str = 'share'
PYTHON_VERSION: str = '3.14.0'
PYTHON_VERSION_MAJOR: str = '3'
PYTHON_VERSION_MINOR: str = '14'
TRACE_MEMORY: bool = False
USE_CCACHE: bool = True
USE_CGNS: bool = False
USE_GUI: bool = True
USE_INTERNAL_TCL: bool = True
USE_JPEG: bool = False
USE_MPEG: bool = False
USE_MPI: bool = True
USE_MPI4PY: bool = False
USE_NATIVE_ARCH: bool = False
USE_NUMA: bool = False
USE_OCC: bool = True
USE_PYTHON: bool = True
USE_SPDLOG: bool = False
is_python_package: bool = True
ngcore_compile_definitions: str = 'NETGEN_PYTHON;NG_PYTHON;PYBIND11_SIMPLE_GIL_MANAGEMENT;PARALLEL;NG_MPI_WRAPPER'
ngcore_compile_options: str = '-Xarch_x86_64;-march=core-avx2'
version: str = 'v6.2.2506-20-gcd974c3b'
