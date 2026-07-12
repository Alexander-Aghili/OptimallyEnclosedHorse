#include "solver.hpp"
#include "Highs.h"
#include <vector>

Solution solve(Game *game) {
    const int R = game->rows, C = game->columns;
    const int n = R * C; 
    auto W = [&](int i, int j) {return i* C + j; }; // wall var index
    auto E = [&](int i, int j) {return n + i* C + j; }; // escape var index

    HighsModel model;
    HighsLp &lp = model.lp_;
    lp.num_col_ = 2 * n;
    lp.sense_   = ObjSense::kMinimize;

    lp.col_cost_.assign(2 * n, 0.0);
    lp.col_lower_.assign(2 * n, 0.0);
    lp.col_upper_.assign(2 * n, 1.0);
    lp.integrality_.assign(2 * n, HighsVarType::kInteger);
    for (int t = 0; t < n; ++t) {
	lp.col_cost_[n + t] = 1.0;
    } 

    std::vector<int> starts{0};
    std::vector<int> index;
    std::vector<double> value;
    std::vector<double> rlo, rhi;
    auto add_row = [&](std::initializer_list<std::pair<int,double>> terms,
			double lo, double hi) {
	for (auto [col, coef] : terms) { 
	    index.push_back(col); 
	    value.push_back(coef);
	}
	starts.push_back((int)index.size());
	rlo.push_back(lo); 
	rhi.push_back(hi);
    };

    for (int i = 0; i < R; ++i) {
	for (int j = 0; j < C; ++j) {
	    if (game->grid[i][j] == WATER) {
		add_row({{E(i,j), 1}}, 0, 0); // water never escapes
	    } else if (i == 0 || i == R-1 || j == 0 || j == C-1) {
		// border: escapes unless we wall it  ->  E + W = 1
		add_row({{E(i,j), 1}, {W(i,j), 1}}, 1, 1);
	    } else {
		// interior: escapable unless walled or every neighbor is contained
		//   E[t] - E[nb] + W[t] >= 0  for each neighbor nb
		for (auto [di,dj] : {std::pair{-1,0},{1,0},{0,-1},{0,1}}) {
		    add_row({{E(i,j), 1}, {E(i+di,j+dj), -1}, {W(i,j), 1}}, 0, kHighsInf);
		}
	    }
	}
    }

    // Wall budget: sum(W) <= budget
    for (int t = 0; t < n; ++t) { index.push_back(t); value.push_back(1.0); }
    starts.push_back((int)index.size());
    rlo.push_back(0);
    rhi.push_back(game->budget);

    // Horse tile stays enclosed (E=0) and unwalled (W=0).
    const int hi = game->horse / C, hj = game->horse % C;
    add_row({{E(hi,hj), 1}}, 0, 0);
    add_row({{W(hi,hj), 1}}, 0, 0);

    lp.num_row_ = (int)rlo.size();
    lp.row_lower_ = std::move(rlo);
    lp.row_upper_ = std::move(rhi);
    lp.a_matrix_.format_ = MatrixFormat::kRowwise;
    lp.a_matrix_.start_  = std::move(starts);
    lp.a_matrix_.index_  = std::move(index);
    lp.a_matrix_.value_  = std::move(value);

    Highs highs;
    highs.setOptionValue("output_flag", false);
    highs.passModel(model);
    highs.run();

    const std::vector<double> &x = highs.getSolution().col_value;
    return Solution {x, highs.getObjectiveValue() };
}
