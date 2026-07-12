cmake_minimum_required(VERSION 3.16)
# Enable C (not just CXX) up front: HiGHS prefers clang for C, which would
# mix a clang thin-LTO C build with our GCC C++ build and fail to link.
# Resolving C here pins it to the same default toolchain as CXX (gcc/g++).
project(OptimalEncloseHorse C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# --- HiGHS (vendored as a git submodule in ./HiGHS) ---------------------
# Run `git submodule update --init --recursive` before configuring.
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/HiGHS/CMakeLists.txt")
  message(FATAL_ERROR
    "HiGHS submodule not initialized. Run:\n"
    "  git submodule update --init --recursive")
endif()

# Build just the library, skip HiGHS' own tests/executable.
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(FAST_BUILD ON CACHE BOOL "" FORCE)
add_subdirectory(HiGHS)
# ------------------------------------------------------------------------

add_executable(enclose
  src/main.cpp
  src/reader.cpp
  src/solver.cpp
  src/writer.cpp
)

target_include_directories(enclose PRIVATE include)
target_link_libraries(enclose PRIVATE highs::highs)
