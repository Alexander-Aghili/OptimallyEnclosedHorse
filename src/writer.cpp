#include "writer.hpp"

#include <cmath>
#include <deque>
#include <utility>
#include <vector>

int game_score(Game *game, const Solution &sol) {
  const int R = game->rows, C = game->columns;
  auto wall = [&](int i, int j) { return std::lround(sol.x[i * C + j]) != 0; };

  const int hi = game->horse / C, hj = game->horse % C;

  std::vector<std::vector<char>> seen(R, std::vector<char>(C, 0));
  std::deque<std::pair<int, int>> q;
  seen[hi][hj] = 1;
  q.push_back({hi, hj});
  bool escaped = false;

  while (!q.empty()) {
    auto [i, j] = q.front();
    q.pop_front();
    if (i == 0 || j == 0 || i == R - 1 || j == C - 1) {
      escaped = true;
    }
    for (auto [di, dj] : {std::pair{-1, 0}, {1, 0}, {0, -1}, {0, 1}}) {
      int ni = i + di, nj = j + dj;
      if (ni < 0 || ni >= R || nj < 0 || nj >= C) continue;
      if (seen[ni][nj]) continue;
      if (wall(ni, nj) || game->grid[ni][nj] == WATER) continue;
      seen[ni][nj] = 1;
      q.push_back({ni, nj});
    }
  }

  if (escaped) return 0;

  int area = 0;
  for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j) area += seen[i][j];

  int cherry_bonus = 0;
  for (const auto &c : *game->cherries)
    if (seen[c.i][c.j]) cherry_bonus += 3;

  return area + cherry_bonus;
}
