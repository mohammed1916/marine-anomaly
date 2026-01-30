cmake_minimum_required(VERSION 3.20)
project(preprocess_piraeus LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)

find_package(CUDAToolkit REQUIRED)

# Attempt to find cudf and rmm
# Note: These usually require CMAKE_PREFIX_PATH to be set if not in standard locations
find_package(cudf REQUIRED)
find_package(rmm REQUIRED)

# cnpy setup
set(CNPY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../cnpy")
include_directories(${CNPY_DIR})

# Find the library manually to be safe on Windows
find_library(CNPY_LIB cnpy PATHS "${CNPY_DIR}/build/Release" "${CNPY_DIR}/build" NO_DEFAULT_PATH)

if(NOT CNPY_LIB)
    message(FATAL_ERROR "Could not find cnpy library in ${CNPY_DIR}/build/Release or ${CNPY_DIR}/build")
endif()

add_executable(preprocess preprocess.cpp)

target_link_libraries(preprocess PRIVATE
    CUDA::cudart
    cudf::cudf
    rmm::rmm
    ${CNPY_LIB}
)
