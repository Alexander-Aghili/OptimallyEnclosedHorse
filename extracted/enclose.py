# copyright 2026 dynomight — available under AGPL-3.0
# https://www.gnu.org/licenses/agpl-3.0.en.html

import numpy as np
from PIL import Image

def readmap(fname, vertical_tiles, horizontal_tiles, horse_position):
    image = np.array(Image.open(fname))[:, :, :3]

    chunk_i = int(np.round(image.shape[0] / vertical_tiles))
    chunk_j = int(np.round(image.shape[1] / horizontal_tiles))
    print(f"{chunk_i=}")
    print(f"{chunk_j=}")

    field = np.array([27, 107, 58])
    water = np.array([6, 47, 72])

    map = np.zeros((vertical_tiles, horizontal_tiles), dtype=int)
    for i in range(vertical_tiles):
        for j in range(horizontal_tiles):
            chunk = image[
                chunk_i * i : chunk_i * (i + 1), chunk_j * j : chunk_j * (j + 1), :
            ]

            close_to_water = np.sum(np.all(chunk == water, axis=-1))
            close_to_field = np.sum(np.all(chunk == field, axis=-1))

            if np.sum(close_to_water) > np.sum(close_to_field):
                map[i, j] = 0
            else:
                map[i, j] = 1

    map[*horse_position] = 2

    return map

def solve_map(map, max_walls):
    from scipy import optimize
    from time import time

    vertical_tiles, horizontal_tiles = map.shape

    W_varnums = np.reshape(
        np.arange(vertical_tiles * horizontal_tiles), (vertical_tiles, horizontal_tiles)
    )
    E_varnums = (
        np.reshape(
            np.arange(vertical_tiles * horizontal_tiles),
            (vertical_tiles, horizontal_tiles),
        )
        + vertical_tiles * horizontal_tiles
    )
    nvars = 2 * vertical_tiles * horizontal_tiles

    c = np.zeros(nvars)
    c[E_varnums.ravel()] = 1

    integrality = np.ones(nvars)

    bounds = optimize.Bounds(np.zeros(nvars), np.ones(nvars))

    constraints = []

    for i in range(vertical_tiles):
        for j in range(horizontal_tiles):
            if map[i, j] == 0:
                lb = 0
                ub = 0
                A = np.zeros(nvars)
                A[E_varnums[i, j]] = 1
                constraints.append(optimize.LinearConstraint(A=A, lb=lb, ub=ub))
            elif (
                i == 0 or j == 0 or i == vertical_tiles - 1 or j == horizontal_tiles - 1
            ):
                lb = 1
                ub = 1
                A = np.zeros(nvars)
                A[E_varnums[i, j]] = 1
                A[W_varnums[i, j]] = 1
                constraints.append(optimize.LinearConstraint(A=A, lb=lb, ub=ub))
            else:
                for i2, j2 in (i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1):
                    if (
                        i2 >= 0
                        and j2 >= 0
                        and i2 < vertical_tiles
                        and j2 < horizontal_tiles
                    ):
                        lb = 0
                        ub = np.inf
                        A = np.zeros(nvars)
                        A[E_varnums[i, j]] = 1
                        A[E_varnums[i2, j2]] = -1
                        A[W_varnums[i, j]] = 1
                        constraints.append(optimize.LinearConstraint(A=A, lb=lb, ub=ub))

    A = np.zeros(nvars)
    A[W_varnums.ravel()] = 1
    constraints.append(optimize.LinearConstraint(A, 0, max_walls))

    horse_var = W_varnums.ravel()[map.ravel().tolist().index(2)]
    A = np.zeros(nvars)
    A[E_varnums.ravel()[horse_var]] = 1
    constraints.append(optimize.LinearConstraint(A, 0, 0))

    A = np.zeros(nvars)
    A[W_varnums.ravel()[horse_var]] = 1
    constraints.append(optimize.LinearConstraint(A, 0, 0))

    t0 = time()
    sol = optimize.milp(
        c, integrality=integrality, bounds=bounds, constraints=constraints
    )
    t1 = time()
    print("solve time:", t1 - t0)

    W_sol = np.round(sol.x[W_varnums]).astype(int)

    map[W_sol == 1] = 5

    return map

map = readmap("map.png", 21, 21, (11, 11))
solve_map(map, 13)
