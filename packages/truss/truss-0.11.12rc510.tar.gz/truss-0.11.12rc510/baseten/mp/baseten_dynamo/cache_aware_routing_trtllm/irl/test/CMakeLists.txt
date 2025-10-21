Include(FetchContent)

FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v3.8.1 # or a later release
)

FetchContent_MakeAvailable(Catch2)

# Individual test executables using a loop
set(TEST_SOURCES test_cpu.cpp test_gpu.cpp)

add_library(
  test_cuda
  test_kernels.cu
)

foreach(TEST_SOURCE ${TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_SOURCE} NAME_WE)
    add_executable(${TEST_NAME} ${TEST_SOURCE})
    target_link_libraries(${TEST_NAME} PRIVATE Catch2::Catch2WithMain test_cuda)
endforeach()

# # Simplified benchmarks
# add_executable(benchmark_latency benchmark_latency.cpp)
# target_link_libraries(benchmark_latency PRIVATE Catch2::Catch2WithMain)

# add_executable(benchmark_memory benchmark_memory.cpp)
# target_link_libraries(benchmark_memory PRIVATE Catch2::Catch2WithMain)

# CUDA benchmark (optional - only built if CUDA is available and CUDA_BENCHMARKS is defined)
# if(CMAKE_CUDA_COMPILER)
#     add_executable(benchmark_latency_cuda benchmark_latency_cuda.cu)
#     target_link_libraries(benchmark_latency_cuda PRIVATE Catch2::Catch2WithMain)
#     target_compile_definitions(benchmark_latency_cuda PRIVATE CUDA_BENCHMARKS)
#     set_property(TARGET benchmark_latency_cuda PROPERTY CUDA_SEPARABLE_COMPILATION ON)
#     target_compile_options(benchmark_latency_cuda PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:--expt-relaxed-constexpr>)
    
#     # CUDA correctness test
#     add_executable(test_cuda_correctness test_cuda_correctness.cu)
#     target_link_libraries(test_cuda_correctness PRIVATE Catch2::Catch2WithMain)
#     target_compile_definitions(test_cuda_correctness PRIVATE CUDA_BENCHMARKS)
#     set_property(TARGET test_cuda_correctness PROPERTY CUDA_SEPARABLE_COMPILATION ON)
#     target_compile_options(test_cuda_correctness PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:--expt-relaxed-constexpr>)
# endif()
