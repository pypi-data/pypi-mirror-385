cmake_minimum_required(VERSION 3.24)
project(localcartesian_bindings LANGUAGES CXX)

# Silence the pybind11 FindPython deprecation warning
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Toggle system vs vendored GeographicLib (default: vendored OFF -> system ON for conda, or ON for PyPI static)
option(USE_SYSTEM_GEOGRAPHICLIB "Use system GeographicLib" OFF)

if(USE_SYSTEM_GEOGRAPHICLIB)
  find_package(GeographicLib CONFIG QUIET)
  if(NOT GeographicLib_FOUND)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(GEOGRAPHICLIB REQUIRED geographiclib)
  endif()
else()
  include(FetchContent)
  FetchContent_Declare(
    geolib
    GIT_REPOSITORY https://github.com/geographiclib/geographiclib.git # Or the C++ version
    GIT_TAG v2.6 # Or a specific tag/commit hash
  )
  set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
  set(GEOGRAPHICLIB_DOCUMENTATION OFF CACHE BOOL "" FORCE)
  set(GEOGRAPHICLIB_LINK_PROGRAMS OFF CACHE BOOL "" FORCE)
  set(GEOGRAPHICLIB_LINK_MATLAB OFF CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(geolib)
endif()

pybind11_add_module(_core localcartesian_bindings.cpp)
target_compile_features(_core PRIVATE cxx_std_17)
target_compile_options(_core PRIVATE -O3 -fvisibility=hidden)

if(USE_SYSTEM_GEOGRAPHICLIB)
  if(GeographicLib_FOUND)
    target_link_libraries(_core PRIVATE GeographicLib::GeographicLib)
  else()
    target_include_directories(_core PRIVATE ${GEOGRAPHICLIB_INCLUDE_DIRS})
    target_link_libraries(_core PRIVATE ${GEOGRAPHICLIB_LIBRARIES})
  endif()
else()
  target_link_libraries(_core PRIVATE GeographicLib)  # static target from vendored build
endif()

# Install the extension into the Python package inside the wheel
install(TARGETS _core LIBRARY DESTINATION localcartesian)

# Install typing files (if present)
install(FILES
  ${CMAKE_SOURCE_DIR}/../src/localcartesian/py.typed
  ${CMAKE_SOURCE_DIR}/../src/localcartesian/_core.pyi
  DESTINATION localcartesian
)