# enclose.horse solver — IP model from dynomight (2026), available under AGPL-3.0
# https://www.gnu.org/licenses/agpl-3.0.en.html

import json
import re
import urllib.request
from collections import deque
from time import time

import numpy as np

WATER, FIELD, HORSE = 0, 1, 2
WALL = 5

BASE_URL = "https://enclose.horse"
_UA = {"User-Agent": "Mozilla/5.0 (enclose-solver)"}


def _get(url):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def fetch_level(level_id):
    """Fetch a single level and return its raw dict (map string, budget, ...)."""
    html = _get(f"{BASE_URL}/play/{level_id}")
    m = re.search(r"window\.__LEVEL__ = (\{.*?\});", html)
    if not m:
        raise RuntimeError(f"could not find __LEVEL__ for {level_id}")
    return json.loads(m.group(1))


def fetch_daily_levels():
    """Return the list of daily puzzles (id, dayNumber, optimalScore, ...)."""
    html = _get(f"{BASE_URL}/play/E03KkY")
    m = re.search(r"window\.__DAILY_LEVELS__ = (\[.*?\]);", html)
    if not m:
        raise RuntimeError("could not find __DAILY_LEVELS__")
    return json.loads(m.group(1))


def parse_map(map_str):
    print(map_str)
    """Text grid -> (numpy terrain array, set of cherry (i,j), horse (i,j)).

    Cherries are passable field tiles, so they become FIELD in the terrain
    array and are tracked separately for scoring.
    """
    rows = map_str.split("\n")
    h = len(rows)
    w = max(len(r) for r in rows)
    grid = np.full((h, w), WATER, dtype=int)
    cherries = set()
    horse = None
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch == "~":
                grid[i, j] = WATER
            elif ch == ".":
                grid[i, j] = FIELD
            elif ch == "H":
                grid[i, j] = HORSE
                horse = (i, j)
            elif ch == "C":
                grid[i, j] = FIELD
                cherries.add((i, j))
            else:
                grid[i, j] = FIELD
    if horse is None:
        raise RuntimeError("no horse ('H') found in map")
    return grid, cherries, horse


def solve_map(grid, max_walls):
    """Place <= max_walls walls to minimize the number of escapable tiles.

    Returns (walls_array, objective_value, solve_time).
    """
    from scipy import optimize

    vertical_tiles, horizontal_tiles = grid.shape
    n_tiles = vertical_tiles * horizontal_tiles

    W_varnums = np.arange(n_tiles).reshape(grid.shape)
    E_varnums = np.arange(n_tiles).reshape(grid.shape) + n_tiles
    nvars = 2 * n_tiles

    c = np.zeros(nvars)
    c[E_varnums.ravel()] = 1

    integrality = np.ones(nvars)
    bounds = optimize.Bounds(np.zeros(nvars), np.ones(nvars))

    constraints = []
    for i in range(vertical_tiles):
        for j in range(horizontal_tiles):
            if grid[i, j] == WATER:
                A = np.zeros(nvars)
                A[E_varnums[i, j]] = 1
                constraints.append(optimize.LinearConstraint(A, 0, 0))
            elif i in (0, vertical_tiles - 1) or j in (0, horizontal_tiles - 1):
                A = np.zeros(nvars)
                A[E_varnums[i, j]] = 1
                A[W_varnums[i, j]] = 1
                constraints.append(optimize.LinearConstraint(A, 1, 1))
            else:
                for i2, j2 in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                    A = np.zeros(nvars)
                    A[E_varnums[i, j]] = 1
                    A[E_varnums[i2, j2]] = -1
                    A[W_varnums[i, j]] = 1
                    constraints.append(optimize.LinearConstraint(A, 0, np.inf))

    A = np.zeros(nvars)
    A[W_varnums.ravel()] = 1
    constraints.append(optimize.LinearConstraint(A, 0, max_walls))

    horse_flat = int(np.argmax(grid.ravel() == HORSE))
    A = np.zeros(nvars)
    A[E_varnums.ravel()[horse_flat]] = 1
    constraints.append(optimize.LinearConstraint(A, 0, 0))
    A = np.zeros(nvars)
    A[W_varnums.ravel()[horse_flat]] = 1
    constraints.append(optimize.LinearConstraint(A, 0, 0))

    t0 = time()
    sol = optimize.milp(
        c, integrality=integrality, bounds=bounds, constraints=constraints
    )
    dt = time() - t0

    walls = np.round(sol.x[W_varnums]).astype(int)
    return walls, int(round(sol.fun)), dt


def game_score(grid, cherries, horse, walls):
    """Replicate enclose.horse scoring: flood-fill the horse's reachable region.

    Score = size of that region (0 if the horse can reach the boundary),
    plus 3 per enclosed cherry. Returns (score, escaped, area).
    """
    h, w = grid.shape
    seen = {horse}
    q = deque([horse])
    escaped = False
    while q:
        i, j = q.popleft()
        if i == 0 or j == 0 or i == h - 1 or j == w - 1:
            escaped = True
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ni, nj = i + di, j + dj
            if not (0 <= ni < h and 0 <= nj < w):
                continue
            if (ni, nj) in seen:
                continue
            if walls[ni, nj] or grid[ni, nj] == WATER:
                continue
            seen.add((ni, nj))
            q.append((ni, nj))
    if escaped:
        return 0, True, 0
    area = len(seen)
    score = area + 3 * sum(1 for t in cherries if t in seen)
    return score, False, area


def run_first_n(n):
    dailies = fetch_daily_levels()
    dailies = sorted(dailies, key=lambda d: d["dayNumber"])[:n]

    print(
        f"{'day':>3}  {'name':<22} {'walls':>5} {'solve(s)':>9} "
        f"{'ip_obj':>6} {'score':>6} {'optimal':>7}  ok"
    )
    print("-" * 78)
    for d in dailies:
        lvl = fetch_level(d["id"])
        grid, cherries, horse = parse_map(lvl["map"])
        walls, obj, dt = solve_map(grid, lvl["budget"])
        score, escaped, _ = game_score(grid, cherries, horse, walls)
        opt = d["optimalScore"]
        ok = "yes" if score == opt else ("ESC" if escaped else "no")
        print(
            f"{d['dayNumber']:>3}  {d['name'][:22]:<22} {lvl['budget']:>5} "
            f"{dt:>9.3f} {obj:>6} {score:>6} {opt:>7}  {ok}"
        )


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    run_first_n(n)
