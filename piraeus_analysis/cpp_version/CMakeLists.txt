cmake_minimum_required(VERSION 3.10)
project(preprocess LANGUAGES CXX)

add_executable(preprocess preprocess.c++)

# headers
target_include_directories(preprocess PRIVATE
    "C:/Program Files/CNPY/include"
)

# library
target_link_libraries(preprocess PRIVATE
    "C:/Program Files/CNPY/lib/cnpy.lib"
)
