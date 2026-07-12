#include "reader.hpp"
#include "solver.hpp"

#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <vector>

std::string read_file(const char *filename) {
  std::ifstream file(filename);
  std::string str;
  if (file.is_open()) {
    std::stringstream buffer;
    buffer << file.rdbuf();
    str = buffer.str();
    file.close();
  }
  return str;
}

Game read_map(const char *filename) {
  return read_map_from_string(read_file(filename).c_str());
}

Game read_map_from_string(const char *input) {
  // first line is the wall budget; the map grid follows on the next line
  int budget = atoi(input);
  const char *newline = strchr(input, '\n');
  const char *map_str = newline ? newline + 1 : input;

  // find out the dimensions of the map
  int rows = 0;
  int cols = 0;

  int map_str_size = strlen(map_str);
  for (int i = 0; i < map_str_size; i++) {
    if (map_str[i] == '\n') {
      cols = i + 1;
      break;
    }
  }
  for (int i = 0; i < map_str_size; i++) {
    if (map_str[i] == '\n') {
      rows++;
    }
  }
  // allocate the map: one contiguous block, row pointers index into it
  int *data = new int[rows * cols];
  int **grid = new int *[rows];
  for (int i = 0; i < rows; i++) {
    grid[i] = data + i * cols;
  }

  std::vector<Position> *cherries = new std::vector<Position>();
  std::vector<Position> *bees = new std::vector<Position>();
  std::vector<Position> *portals = new std::vector<Position>();

  // parse the map
  int horse = -1; // flat index (i * cols + j) of the horse tile
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      char ch = map_str[i * cols + j];
      switch (ch) {
      case '~':
        grid[i][j] = WATER;
        break;
      case '.':
        grid[i][j] = FIELD;
        break;
      case 'H':
        grid[i][j] = HORSE;
        horse = i * cols + j;
        break;
      case 'C':
        cherries->push_back(Position{i, j});
        grid[i][j] = FIELD;
        break;
      default:
        grid[i][j] = FIELD;
      }
    }
  }

  return Game{grid, rows, cols, budget, horse, cherries, bees, portals};
}
