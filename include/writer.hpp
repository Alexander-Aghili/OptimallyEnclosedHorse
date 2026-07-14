#pragma once

#include "solver.hpp"

// Replicate enclose.horse scoring: flood-fill the horse's reachable region
// through non-wall, non-water tiles. Score = size of that region (0 if the
// horse can reach the border), plus 3 per enclosed cherry.
int game_score(Game *game, const Solution &sol);
