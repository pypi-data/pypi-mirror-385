cmake_minimum_required(VERSION 3.16)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Treat warnings as errors
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror -Wall -Wextra")

set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=gold")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -fuse-ld=gold")

# Explicitly set architectures and add -real suffix to only genreate native cubin code
# This avoids PTX JIT issues when running across driver versions
set(CMAKE_CUDA_ARCHITECTURES "80-real;86-real;89-real;90-real;100-real")

project(Briton LANGUAGES CXX CUDA)

set(BUILD_DEPS ON)

# External libraries Briton depends on.
include(packages.cmake)

# Directories with includes that Briton needs.
include(includes.cmake)

file(GLOB LIB_SOURCES src/*.cpp src/*.cu)

set(COMMON_LIBS
  gRPC::grpc++_reflection
  protobuf::libprotobuf
  /usr/local/briton/libs/libtokenizer.a
  OpenSSL::SSL
  OpenSSL::Crypto
  nlohmann_json::nlohmann_json
)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/include ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_library(bproto SHARED ${briton_proto_srcs} ${briton_grpc_srcs})
target_link_libraries(bproto ${COMMON_LIBS})

############################################################
# Briton library.
add_library(
  briton
  SHARED
  ${LIB_SOURCES}
)
target_link_libraries(briton ${COMMON_LIBS} ${MPI_LIBRARIES} ${CUDA_LIBRARIES} ${TRTLLM_LIBS} bproto)
link_libraries(briton)

# Briton main application.
add_executable(
  ${PROJECT_NAME}
  app/main.cpp
)

#############################################################
# Briton client.
add_executable(
  client
  client/client.cpp
  ${briton_proto_srcs}
  ${briton_grpc_srcs}
)
set_target_properties(client PROPERTIES EXCLUDE_FROM_ALL TRUE)
#############################################################
# Trace aggregator.
add_executable(
  trace_aggregator
  src/tracer/trace_aggregator.cpp
)
target_include_directories(trace_aggregator PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

#############################################################
# Trace to CSV converter.
add_executable(
  trace_to_csv
  src/tracer/trace_to_csv.cpp
)
target_include_directories(trace_to_csv PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(trace_to_csv PROPERTIES EXCLUDE_FROM_ALL TRUE)

#############################################################
# Briton Python bindings.
find_package(Python 3.10 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module(briton_bind pybind/pybind.cpp)
add_custom_command(TARGET briton_bind POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:briton_bind>
    ${CMAKE_SOURCE_DIR}/python/briton/briton
  COMMENT "Copying briton_bind to python package directory")


############################################################
# TRTLLM hooks
add_library(hot_reload SHARED experimental/hot_reload.cpp)
target_include_directories(hot_reload PUBLIC src/include)
set_target_properties(hot_reload PROPERTIES
    POSITION_INDEPENDENT_CODE ON
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
    OUTPUT_NAME "hot_reload"          # Generates libhot_reload.so
)

add_library(customtrt SHARED experimental/customtrt.cpp)
target_link_libraries(customtrt hot_reload)

add_library(empty_for_test SHARED experimental/empty_for_test.cpp)
target_link_libraries(empty_for_test hot_reload)
set_target_properties(empty_for_test PROPERTIES EXCLUDE_FROM_ALL TRUE)

############################################################
# Briton tests.
file(GLOB TEST_SOURCES "tests/*.cpp" "tests/*.cu")
add_executable(test ${TEST_SOURCES})

find_package(GTest REQUIRED)
target_link_libraries(test
  gtest_main
  briton
  ${COMMON_LIBS}
  ${TRTLLM_LIBS}
  ${GTEST_LIBRARIES}
)

set_target_properties(test PROPERTIES EXCLUDE_FROM_ALL TRUE)
