#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "dftracer_utils::dftracer_utils" for configuration "Release"
set_property(TARGET dftracer_utils::dftracer_utils APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::dftracer_utils PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libdftracer_utils.a"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::dftracer_utils )
list(APPEND _cmake_import_check_files_for_dftracer_utils::dftracer_utils "${_IMPORT_PREFIX}/dftracer/lib/libdftracer_utils.a" )

# Import target "dftracer_utils::shared" for configuration "Release"
set_property(TARGET dftracer_utils::shared APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::shared PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "dftracer_utils::sqlite3"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libdftracer_utils.so.0.1.0"
  IMPORTED_SONAME_RELEASE "libdftracer_utils.so.0"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::shared )
list(APPEND _cmake_import_check_files_for_dftracer_utils::shared "${_IMPORT_PREFIX}/dftracer/lib/libdftracer_utils.so.0.1.0" )

# Import target "dftracer_utils::sqlite3" for configuration "Release"
set_property(TARGET dftracer_utils::sqlite3 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::sqlite3 PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libsqlite3.so"
  IMPORTED_SONAME_RELEASE "libsqlite3.so"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::sqlite3 )
list(APPEND _cmake_import_check_files_for_dftracer_utils::sqlite3 "${_IMPORT_PREFIX}/dftracer/lib/libsqlite3.so" )

# Import target "dftracer_utils::sqlite3_static" for configuration "Release"
set_property(TARGET dftracer_utils::sqlite3_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::sqlite3_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libsqlite3_static.a"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::sqlite3_static )
list(APPEND _cmake_import_check_files_for_dftracer_utils::sqlite3_static "${_IMPORT_PREFIX}/dftracer/lib/libsqlite3_static.a" )

# Import target "dftracer_utils::xxhash" for configuration "Release"
set_property(TARGET dftracer_utils::xxhash APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::xxhash PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libxxhash.so"
  IMPORTED_SONAME_RELEASE "libxxhash.so"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::xxhash )
list(APPEND _cmake_import_check_files_for_dftracer_utils::xxhash "${_IMPORT_PREFIX}/dftracer/lib/libxxhash.so" )

# Import target "dftracer_utils::xxhash_static" for configuration "Release"
set_property(TARGET dftracer_utils::xxhash_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::xxhash_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libxxhash_static.a"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::xxhash_static )
list(APPEND _cmake_import_check_files_for_dftracer_utils::xxhash_static "${_IMPORT_PREFIX}/dftracer/lib/libxxhash_static.a" )

# Import target "dftracer_utils::yyjson" for configuration "Release"
set_property(TARGET dftracer_utils::yyjson APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::yyjson PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libyyjson.so.0.1.0"
  IMPORTED_SONAME_RELEASE "libyyjson.so.0"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::yyjson )
list(APPEND _cmake_import_check_files_for_dftracer_utils::yyjson "${_IMPORT_PREFIX}/dftracer/lib/libyyjson.so.0.1.0" )

# Import target "dftracer_utils::yyjson_static" for configuration "Release"
set_property(TARGET dftracer_utils::yyjson_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::yyjson_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libyyjson_static.a"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::yyjson_static )
list(APPEND _cmake_import_check_files_for_dftracer_utils::yyjson_static "${_IMPORT_PREFIX}/dftracer/lib/libyyjson_static.a" )

# Import target "dftracer_utils::cpp-logger" for configuration "Release"
set_property(TARGET dftracer_utils::cpp-logger APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_utils::cpp-logger PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/dftracer/lib/libcpp-logger.so.1.1.0"
  IMPORTED_SONAME_RELEASE "libcpp-logger.so.1"
  )

list(APPEND _cmake_import_check_targets dftracer_utils::cpp-logger )
list(APPEND _cmake_import_check_files_for_dftracer_utils::cpp-logger "${_IMPORT_PREFIX}/dftracer/lib/libcpp-logger.so.1.1.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
