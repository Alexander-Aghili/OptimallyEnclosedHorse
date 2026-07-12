#include "reader.hpp"
#include "solver.hpp"
#include "writer.hpp"

#include <iostream>

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <map_filename>" << std::endl;
    return 1;
  }
  Game game = read_map(argv[1]);

  for (int i = 0; i < game.rows; i++) {
    for (int j = 0; j < game.columns; j++) {
      std::cout << game.grid[i][j] << " ";
    }
    std::cout << std::endl;
  }

  std::cout << game.rows << std::endl;
  std::cout << game.columns << std::endl;

  std::cout << game.cherries->size() << std::endl;
  for (int i = 0; i < game.cherries->size(); i++) {
    std::cout << game.cherries->at(i).i << " " << game.cherries->at(i).j
              << std::endl;
  }

  Solution sol = solve(&game);

  for (int i = 0; i < sol.x.size(); i++) {
    std::cout << sol.x[i] << " ";
  }
  std::cout << std::endl;
  std::cout << sol.objective << std::endl;

  return 0;
}
