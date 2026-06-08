cmake_minimum_required(VERSION 3.20)
project(SimpleFeedKernel VERSION 1.0.0 LANGUAGES CXX)

# Enforce C++20 standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable extreme optimization and AVX-512 Hardware Intrinsics
# Note: For production, ensure the target deployment CPU supports AVX-512 (e.g., AWS C6i instances).
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -mavx512f -mavx512bw -mavx512vl -Wall -Wextra")

# Include directories
include_directories(src)

# We will link this to gRPC in the next phase
# add_executable(kernel_server ...)
