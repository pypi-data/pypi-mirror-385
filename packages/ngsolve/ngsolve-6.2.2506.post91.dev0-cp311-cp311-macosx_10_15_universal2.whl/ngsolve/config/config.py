def _cmake_to_bool(s):
    return s.upper() not in ['', '0','FALSE','OFF','N','NO','IGNORE','NOTFOUND']

is_python_package    = _cmake_to_bool("TRUE")

BUILD_STUB_FILES     = _cmake_to_bool("ON")
BUILD_UMFPACK        = _cmake_to_bool("")
ENABLE_UNIT_TESTS    = _cmake_to_bool("OFF")
INSTALL_DEPENDENCIES = _cmake_to_bool("OFF")
USE_CCACHE           = _cmake_to_bool("ON")
USE_HYPRE            = _cmake_to_bool("OFF")
USE_LAPACK           = _cmake_to_bool("ON")
USE_MKL              = _cmake_to_bool("OFF")
USE_MUMPS            = _cmake_to_bool("OFF")
USE_PARDISO          = _cmake_to_bool("OFF")
USE_UMFPACK          = _cmake_to_bool("ON")

NETGEN_DIR = "/Users/gitlab-runner/Library/Python/3.11/lib/python/site-packages"

NGSOLVE_COMPILE_DEFINITIONS         = "HAVE_NETGEN_SOURCES;HAVE_DLFCN_H;HAVE_CXA_DEMANGLE;USE_TIMEOFDAY;MSG_NOSIGNAL=0;TCL;LAPACK;NGS_PYTHON;USE_UMFPACK"
NGSOLVE_COMPILE_DEFINITIONS_PRIVATE = ""
NGSOLVE_COMPILE_INCLUDE_DIRS        = ""
NGSOLVE_COMPILE_OPTIONS             = "$<$<COMPILE_LANGUAGE:CXX>:-std=c++17>;$<$<COMPILE_LANGUAGE:CXX>:-Wno-undefined-var-template;-Wno-vla-extension>;-DMAX_SYS_DIM=3"

NGSOLVE_INSTALL_DIR_PYTHON   = "."
NGSOLVE_INSTALL_DIR_BIN      = "bin"
NGSOLVE_INSTALL_DIR_LIB      = "netgen"
NGSOLVE_INSTALL_DIR_INCLUDE  = "netgen/include"
NGSOLVE_INSTALL_DIR_CMAKE    = "ngsolve/cmake"
NGSOLVE_INSTALL_DIR_RES      = "share"

NGSOLVE_VERSION = "6.2.2506-91-g125cf2190"
NGSOLVE_VERSION_GIT = "v6.2.2506-91-g125cf2190"
NGSOLVE_VERSION_PYTHON = "6.2.2506.post91.dev0"

NGSOLVE_VERSION_MAJOR = "6"
NGSOLVE_VERSION_MINOR = "2"
NGSOLVE_VERSION_TWEAK = "91"
NGSOLVE_VERSION_PATCH = "2506"
NGSOLVE_VERSION_HASH = "g125cf2190"

CMAKE_CXX_COMPILER           = "/Library/Developer/CommandLineTools/usr/bin/c++"
CMAKE_CUDA_COMPILER          = ""
CMAKE_C_COMPILER             = "/Library/Developer/CommandLineTools/usr/bin/cc"
CMAKE_LINKER                 = "/Library/Developer/CommandLineTools/usr/bin/ld"
CMAKE_INSTALL_PREFIX         = "/Users/gitlab-runner/builds/builds/rL7WHzyj/0/ngsolve/ngsolve/_skbuild/macosx-10.15-universal2-3.11/cmake-install"
CMAKE_CXX_COMPILER_LAUNCHER  = "/usr/local/bin/ccache"

version = NGSOLVE_VERSION_GIT

MKL_LINK = ""

def get_cmake_dir():
    import os.path as p
    d_python = p.dirname(p.dirname(p.dirname(__file__)))
    py_to_cmake = p.relpath(
            NGSOLVE_INSTALL_DIR_CMAKE,
            NGSOLVE_INSTALL_DIR_PYTHON
            )
    return p.normpath(p.join(d_python,py_to_cmake))
