cmake_minimum_required(VERSION 3.16)
project(OptimalEncloseHorse CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

find_package(HiGHS CONFIG QUIET)

if(NOT HiGHS_FOUND)
  message(STATUS "HiGHS not found locally; fetching via FetchContent")
  include(FetchContent)
  FetchContent_Declare(
    highs
    GIT_REPOSITORY https://github.com/ERGO-Code/HiGHS.git
    GIT_TAG        v1.11.0
  )
  # Build just the library, skip HiGHS' own tests/executable.
  set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
  set(FAST_BUILD ON CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(highs)
endif()

add_executable(enclose
  src/main.cpp
  src/reader.cpp
  src/solver.cpp
  src/writer.cpp
)

target_include_directories(enclose PRIVATE include)
target_link_libraries(enclose PRIVATE highs::highs)
