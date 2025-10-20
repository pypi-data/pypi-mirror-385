#ifndef __DFTRACER_UTILS_CONFIG_H
#define __DFTRACER_UTILS_CONFIG_H
// clang-format off
/* Version string for DFTRACER_UTILS */
#define DFTRACER_UTILS_PACKAGE_VERSION "0.1.0"
/* #undef DFTRACER_UTILS_GIT_VERSION */
#define DFTRACER_UTILS_GET_VERSION(MAJOR, MINOR, PATCH) (MAJOR * 100000 + MINOR * 100 + PATCH)
#define DFTRACER_UTILS_VERSION (DFTRACER_UTILS_GET_VERSION 0.1.0)
#define DFTRACER_UTILS_VERSION_MAJOR (DFTRACER_UTILS_VERSION / 100000)
#define DFTRACER_UTILS_VERSION_MINOR ((DFTRACER_UTILS_VERSION / 100) % 1000)
#define DFTRACER_UTILS_VERSION_PATCH (DFTRACER_UTILS_VERSION % 100)

/* Compiler used */
/* #undef DFTRACER_UTILS_CMAKE_BUILD_TYPE */

/* #undef DFTRACER_UTILS_CMAKE_C_COMPILER */
/* #undef DFTRACER_UTILS_CMAKE_C_FLAGS */
/* #undef DFTRACER_UTILS_CMAKE_C_FLAGS_DEBUG */
/* #undef DFTRACER_UTILS_CMAKE_C_FLAGS_RELWITHDEBINFO */
/* #undef DFTRACER_UTILS_CMAKE_C_FLAGS_RELEASE */

/* #undef DFTRACER_UTILS_CMAKE_CXX_COMPILER */
/* #undef DFTRACER_UTILS_CMAKE_CXX_FLAGS */
/* #undef DFTRACER_UTILS_CMAKE_CXX_FLAGS_DEBUG */
/* #undef DFTRACER_UTILS_CMAKE_CXX_FLAGS_RELWITHDEBINFO */
/* #undef DFTRACER_UTILS_CMAKE_CXX_FLAGS_RELEASE */

/* #undef DFTRACER_UTILS_CMAKE_C_SHARED_LIBRARY_FLAGS */
/* #undef DFTRACER_UTILS_CMAKE_CXX_SHARED_LIBRARY_FLAGS */

/* Macro flags */
/* #undef DFTRACER_UTILS_HAS_STD_FILESYSTEM */

#define DFTRACER_UTILS_LOGGER_CPP_LOGGER 1
#define DFTRACER_UTILS_LOGGER_LEVEL_TRACE 0
#define DFTRACER_UTILS_LOGGER_LEVEL_DEBUG 0
#define DFTRACER_UTILS_LOGGER_LEVEL_INFO 1
#define DFTRACER_UTILS_LOGGER_LEVEL_WARN 1
#define DFTRACER_UTILS_LOGGER_LEVEL_ERROR 1

//==========================
// Common include
//==========================

#include <dftracer/utils/common/platform_compat.h>

//==========================
// Common macro definitions
//==========================

// Detect VAR_OPT
// https://stackoverflow.com/questions/48045470/portably-detect-va-opt-support
#if __cplusplus <= 201703 && defined __GNUC__ && !defined __clang__ && \
    !defined __EDG__
#define VA_OPT_SUPPORTED false
#else
#define PP_THIRD_ARG(a, b, c, ...) c
#define VA_OPT_SUPPORTED_I(...) PP_THIRD_ARG(__VA_OPT__(, ), true, false, )
#define VA_OPT_SUPPORTED VA_OPT_SUPPORTED_I(?)
#endif

#if !defined(DFTRACER_UTILS_HASH_SEED) || (DFTRACER_UTILS_HASH_SEED <= 0)
#define DFTRACER_UTILS_SEED 104723u
#endif
// clang-format on
#endif // __DFTRACER_UTILS_CONFIG_H
