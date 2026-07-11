#pragma once

#include "solver.hpp"
#include <string>

Game read_map(const char *filename);
Game read_map_from_string(const char *map_str);
std::string read_file(const char *filename);
