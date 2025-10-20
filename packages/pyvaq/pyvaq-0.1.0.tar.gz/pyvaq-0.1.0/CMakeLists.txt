cmake_minimum_required(VERSION 3.13)

project(BitVecEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_FLAGS "-Wall -Wextra -Wpedantic -Wno-psabi -Wno-sign-compare")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopt-info")

IF (NOT OPTIMIZATION_LEVEL)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -ffast-math -mfma")
  add_definitions(-DVAQ_OPTIMIZE)
  add_definitions(-march=haswell)
  add_definitions(-mavx -mavx2)
ELSEIF (OPTIMIZATION_LEVEL STREQUAL "full")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")
ELSEIF (OPTIMIZATION_LEVEL STREQUAL "aggressive")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
ELSEIF (OPTIMIZATION_LEVEL STREQUAL "generic")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
ENDIF()

include_directories(external/eigen)
if (DEFINED ENV{CONDA_PREFIX})
  include_directories($ENV{CONDA_PREFIX}/include)
  link_directories($ENV{CONDA_PREFIX}/lib)
endif()

find_package(Armadillo REQUIRED)
find_library(GLPK_LIBRARY glpk REQUIRED)

add_subdirectory(bitvecengine)
add_subdirectory(examples)

target_link_libraries(VAQ PRIVATE -larmadillo)
target_link_libraries(VAQ PRIVATE -lglpk)

IF (BUILD_TESTING)
  add_subdirectory(test)
  add_custom_target(test COMMAND Test --durations yes)
ENDIF(BUILD_TESTING)

add_definitions(-DEIGEN_USE_BLAS -DEIGEN_USE_LAPACKE)
add_definitions(-DEIGEN_DONT_PARALLELIZE)

FIND_PACKAGE(OpenMP)
IF(OPENMP_FOUND)
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
ENDIF()

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module(pyvaq bitvecengine/VAQ_binding.cpp)
target_link_libraries(pyvaq PRIVATE VAQ FPGrowth)

install(TARGETS pyvaq DESTINATION pyvaq)
