cmake_minimum_required(VERSION 3.20)

include(packages.cmake)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CUDA_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror -Wall -Wextra -Wno-lto-type-mismatch -Wno-odr")
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} --expt-relaxed-constexpr")
set(CMAKE_CUDA_ARCHITECTURES "native")

if (NOT SKBUILD)
  project(irl LANGUAGES CXX)
  # debug
  # set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -g -lineinfo")
else()
  project(irl_ext LANGUAGES CXX)
endif()

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(src)

enable_language(CUDA)

# export compile_commands.json
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_library(
  irl_cuda
  src/runner_split_1.cu
  src/runner_split_2.cu
  src/runner_split_3.cu
  src/runner_split_4.cu
  src/globals.cu
  src/memory.cu
  src/metrics.cu
  src/metrics.cpp
  src/cuda_api.cpp
)

set_property(TARGET irl_cuda PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
link_libraries(irl_cuda)

# TODO add compile guards for torch in .cu files
# if (SKBUILD)
    find_package(Python
                REQUIRED COMPONENTS Interpreter Development.Module
                OPTIONAL_COMPONENTS Development.SABIModule)
    # find_package(nanobind CONFIG REQUIRED)

    set(CMAKE_PREFIX_PATH "/usr/local/lib/python3.12/dist-packages/torch/share/cmake/Torch")
    include_directories("/usr/local/lib/python3.12/dist-packages/torch/include")
    find_package(Torch REQUIRED)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
    link_libraries("${TORCH_LIBRARIES}")

    find_package(OpenMP REQUIRED)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")

    nanobind_add_module(
        _irl_ext_impl
        STABLE_ABI
        src/irl_ext.cpp
    )

    set_property(TARGET _irl_ext_impl PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)

    target_link_libraries(
        _irl_ext_impl
        PRIVATE
        irl_cuda
        OpenMP::OpenMP_CXX
    )

    install(TARGETS _irl_ext_impl LIBRARY DESTINATION irl_ext)
# endif()

if (NOT SKBUILD)
add_subdirectory(test)
endif()
