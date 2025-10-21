

####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was dftracer_utilsConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

include(CMakeFindDependencyMacro)

# Find dependencies - handle both CPM-built and system packages

# ZLIB dependency
find_library(ZLIB_LIBRARY_BUNDLED
    NAMES z libz zlib
    PATHS ${_IMPORT_PREFIX}/lib
    NO_DEFAULT_PATH
)

if(ZLIB_LIBRARY_BUNDLED)
    # Found zlib that was built with this package
    find_path(ZLIB_INCLUDE_DIR_BUNDLED
        NAMES zlib.h
        PATHS ${_IMPORT_PREFIX}/include
        NO_DEFAULT_PATH
    )

    if(ZLIB_INCLUDE_DIR_BUNDLED AND NOT TARGET ZLIB::ZLIB)
        add_library(ZLIB::ZLIB UNKNOWN IMPORTED)
        set_target_properties(ZLIB::ZLIB PROPERTIES
            IMPORTED_LOCATION "${ZLIB_LIBRARY_BUNDLED}"
            INTERFACE_INCLUDE_DIRECTORIES "${ZLIB_INCLUDE_DIR_BUNDLED}"
        )
    endif()
else()
    # Fall back to system zlib
    find_dependency(ZLIB REQUIRED)
endif()

# SQLITE3 dependency
find_library(SQLITE3_LIBRARY_BUNDLED
    NAMES sqlite3 libsqlite3
    PATHS ${_IMPORT_PREFIX}/lib
    NO_DEFAULT_PATH
)

if(SQLITE3_LIBRARY_BUNDLED)
    # Found sqlite3 that was built with this package
    find_path(SQLITE3_INCLUDE_DIR_BUNDLED
        NAMES sqlite3.h
        PATHS ${_IMPORT_PREFIX}/include
        NO_DEFAULT_PATH
    )

    if(SQLITE3_INCLUDE_DIR_BUNDLED AND NOT TARGET SQLite::SQLite3)
        add_library(SQLite::SQLite3 UNKNOWN IMPORTED)
        set_target_properties(SQLite::SQLite3 PROPERTIES
            IMPORTED_LOCATION "${SQLITE3_LIBRARY_BUNDLED}"
            INTERFACE_INCLUDE_DIRECTORIES "${SQLITE3_INCLUDE_DIR_BUNDLED}"
        )
    endif()
else()
    # Fall back to system sqlite3 via pkg-config
    find_dependency(PkgConfig REQUIRED)
    pkg_check_modules(SQLITE3 REQUIRED sqlite3)

    if(SQLITE3_FOUND AND NOT TARGET SQLite::SQLite3)
        add_library(SQLite::SQLite3 UNKNOWN IMPORTED)
        set_target_properties(SQLite::SQLite3 PROPERTIES
            IMPORTED_LOCATION "${SQLITE3_LIBRARIES}"
            INTERFACE_INCLUDE_DIRECTORIES "${SQLITE3_INCLUDE_DIRS}"
        )
    endif()
endif()

# SPDLOG dependency
find_library(SPDLOG_LIBRARY_BUNDLED
    NAMES spdlog libspdlog
    PATHS ${_IMPORT_PREFIX}/lib
    NO_DEFAULT_PATH
)

if(SPDLOG_LIBRARY_BUNDLED)
    # Found spdlog that was built with this package
    find_path(SPDLOG_INCLUDE_DIR_BUNDLED
        NAMES spdlog/spdlog.h
        PATHS ${_IMPORT_PREFIX}/include
        NO_DEFAULT_PATH
    )

    if(SPDLOG_INCLUDE_DIR_BUNDLED AND NOT TARGET spdlog::spdlog)
        add_library(spdlog::spdlog UNKNOWN IMPORTED)
        set_target_properties(spdlog::spdlog PROPERTIES
            IMPORTED_LOCATION "${SPDLOG_LIBRARY_BUNDLED}"
            INTERFACE_INCLUDE_DIRECTORIES "${SPDLOG_INCLUDE_DIR_BUNDLED}"
        )
    endif()

    # Also create header-only alias if not exists
    if(NOT TARGET spdlog::spdlog_header_only)
        add_library(spdlog::spdlog_header_only INTERFACE IMPORTED)
        set_target_properties(spdlog::spdlog_header_only PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${SPDLOG_INCLUDE_DIR_BUNDLED}"
        )
    endif()
else()
    # Try to find system spdlog
    find_dependency(spdlog QUIET)
    if(NOT spdlog_FOUND)
        # If spdlog is not found, create an interface target for header-only usage
        if(NOT TARGET spdlog::spdlog_header_only)
            add_library(spdlog::spdlog_header_only INTERFACE IMPORTED)
            # Try to find the library in system locations
            find_library(SPDLOG_LIB spdlog)
            if(SPDLOG_LIB)
                set_target_properties(spdlog::spdlog_header_only PROPERTIES
                    INTERFACE_LINK_LIBRARIES "${SPDLOG_LIB}"
                )
            else()
                # Fallback to just the library name for header-only usage
                set_target_properties(spdlog::spdlog_header_only PROPERTIES
                    INTERFACE_COMPILE_DEFINITIONS "SPDLOG_HEADER_ONLY"
                )
            endif()
        endif()

        if(NOT TARGET spdlog::spdlog)
            add_library(spdlog::spdlog ALIAS spdlog::spdlog_header_only)
        endif()
    endif()
endif()

# YYJSON dependency
find_library(YYJSON_LIBRARY_BUNDLED
    NAMES yyjson libyyjson
    PATHS ${_IMPORT_PREFIX}/lib
    NO_DEFAULT_PATH
)

if(YYJSON_LIBRARY_BUNDLED)
    # Found yyjson that was built with this package
    find_path(YYJSON_INCLUDE_DIR_BUNDLED
        NAMES yyjson.h
        PATHS ${_IMPORT_PREFIX}/include
        NO_DEFAULT_PATH
    )

    if(YYJSON_INCLUDE_DIR_BUNDLED)
        # Create shared target if not exists
        if(NOT TARGET yyjson::yyjson)
            add_library(yyjson::yyjson UNKNOWN IMPORTED)
            set_target_properties(yyjson::yyjson PROPERTIES
                IMPORTED_LOCATION "${YYJSON_LIBRARY_BUNDLED}"
                INTERFACE_INCLUDE_DIRECTORIES "${YYJSON_INCLUDE_DIR_BUNDLED}"
            )
        endif()

        # Also look for static version
        find_library(YYJSON_STATIC_LIBRARY_BUNDLED
            NAMES yyjson_static libyyjson_static
            PATHS ${_IMPORT_PREFIX}/lib
            NO_DEFAULT_PATH
        )

        if(YYJSON_STATIC_LIBRARY_BUNDLED AND NOT TARGET yyjson::yyjson_static)
            add_library(yyjson::yyjson_static UNKNOWN IMPORTED)
            set_target_properties(yyjson::yyjson_static PROPERTIES
                IMPORTED_LOCATION "${YYJSON_STATIC_LIBRARY_BUNDLED}"
                INTERFACE_INCLUDE_DIRECTORIES "${YYJSON_INCLUDE_DIR_BUNDLED}"
            )
        endif()
    endif()
else()
    # Try to find system yyjson
    find_dependency(yyjson QUIET)
endif()

# GHC_FILESYSTEM dependency (header-only)
find_path(GHC_FILESYSTEM_INCLUDE_DIR_BUNDLED
    NAMES ghc/filesystem.hpp
    PATHS ${_IMPORT_PREFIX}/include
    NO_DEFAULT_PATH
)

if(GHC_FILESYSTEM_INCLUDE_DIR_BUNDLED AND NOT TARGET ghc_filesystem)
    add_library(ghc_filesystem INTERFACE IMPORTED)
    set_target_properties(ghc_filesystem PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${GHC_FILESYSTEM_INCLUDE_DIR_BUNDLED}"
    )
else()
    # Try to find system ghc_filesystem
    find_dependency(ghc_filesystem QUIET)
endif()

# PICOSHA2 dependency (header-only)
find_path(PICOSHA2_INCLUDE_DIR_BUNDLED
    NAMES picosha2.h
    PATHS ${_IMPORT_PREFIX}/include
    NO_DEFAULT_PATH
)

if(PICOSHA2_INCLUDE_DIR_BUNDLED AND NOT TARGET picosha2)
    add_library(picosha2 INTERFACE IMPORTED)
    set_target_properties(picosha2 PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${PICOSHA2_INCLUDE_DIR_BUNDLED}"
    )
endif()

# Include the targets file
include("${CMAKE_CURRENT_LIST_DIR}/dftracer_utilsTargets.cmake")

# Main target (no namespace): dftracer_utils -> points to static
if(TARGET dftracer_utils::dftracer_utils AND NOT TARGET dftracer_utils)
    add_library(dftracer_utils ALIAS dftracer_utils::dftracer_utils)
endif()

# Static alias: dftracer_utils::static -> points to main static target
if(TARGET dftracer_utils::dftracer_utils AND NOT TARGET dftracer_utils::static)
    add_library(dftracer_utils::static ALIAS dftracer_utils::dftracer_utils)
endif()

# Shared alias: dftracer_utils::shared -> points to shared target (if it exists)
if(TARGET dftracer_utils::shared AND NOT TARGET dftracer_utils::shared)
    # Target already exists, no alias needed
elseif(TARGET dftracer_utils::dft_reader_shared AND NOT TARGET dftracer_utils::shared)
    add_library(dftracer_utils::shared ALIAS dftracer_utils::dft_reader_shared)
endif()

check_required_components(dftracer_utils)
