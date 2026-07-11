#pragma once

#include <vector>

typedef enum { WATER, FIELD, HORSE, WALL } TileType;

typedef enum { CHERRY, BEE, PORTAL } FieldType;

typedef struct {
  int i;
  int j;
} Position;

typedef struct {
  int **grid;
  int rows;
  int columns;
  std::vector<Position> *cherries;
  std::vector<Position> *bees;
  std::vector<Position> *portals;
} Game;

void solve(Game *game);

