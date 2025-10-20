#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "dftracer_core" for configuration "Release"
set_property(TARGET dftracer_core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_core PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdftracer_core.so.4.0.0"
  IMPORTED_SONAME_RELEASE "libdftracer_core.so.4.0.0"
  )

list(APPEND _cmake_import_check_targets dftracer_core )
list(APPEND _cmake_import_check_files_for_dftracer_core "${_IMPORT_PREFIX}/lib/libdftracer_core.so.4.0.0" )

# Import target "dftracer_core_dbg" for configuration "Release"
set_property(TARGET dftracer_core_dbg APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_core_dbg PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdftracer_core_dbg.so"
  IMPORTED_SONAME_RELEASE "libdftracer_core_dbg.so"
  )

list(APPEND _cmake_import_check_targets dftracer_core_dbg )
list(APPEND _cmake_import_check_files_for_dftracer_core_dbg "${_IMPORT_PREFIX}/lib/libdftracer_core_dbg.so" )

# Import target "dftracer_service" for configuration "Release"
set_property(TARGET dftracer_service APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_service PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/dftracer_service"
  )

list(APPEND _cmake_import_check_targets dftracer_service )
list(APPEND _cmake_import_check_files_for_dftracer_service "${_IMPORT_PREFIX}/bin/dftracer_service" )

# Import target "dftracer_preload" for configuration "Release"
set_property(TARGET dftracer_preload APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_preload PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdftracer_preload.so"
  IMPORTED_SONAME_RELEASE "libdftracer_preload.so"
  )

list(APPEND _cmake_import_check_targets dftracer_preload )
list(APPEND _cmake_import_check_files_for_dftracer_preload "${_IMPORT_PREFIX}/lib/libdftracer_preload.so" )

# Import target "dftracer_preload_dbg" for configuration "Release"
set_property(TARGET dftracer_preload_dbg APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_preload_dbg PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdftracer_preload_dbg.so"
  IMPORTED_SONAME_RELEASE "libdftracer_preload_dbg.so"
  )

list(APPEND _cmake_import_check_targets dftracer_preload_dbg )
list(APPEND _cmake_import_check_files_for_dftracer_preload_dbg "${_IMPORT_PREFIX}/lib/libdftracer_preload_dbg.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
