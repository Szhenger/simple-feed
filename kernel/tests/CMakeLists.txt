cmake_minimum_required(VERSION 3.14)
project(EngineKernelTests)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Force architecture flags for vector register access
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mavx512f -mavx512bw -march=native")

include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
# For Windows/MSVC safety
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(kernel_tests
    test_main.cpp
    test_buffer_safety.cpp
    test_avx_scanner.cpp
)

target_link_libraries(kernel_tests gtest_main)
include(GoogleTest)
gtest_discover_tests(kernel_tests)
