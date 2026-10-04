"""
Local Search operators cho bài toán VRP.
"""
import numpy as np
from typing import List


def two_opt_route(route: List[int], dist_matrix: np.ndarray) -> List[int]:
    route = list(route)
    n = len(route)
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                d_current = (
                    dist_matrix[route[i - 1]][route[i]]
                    + dist_matrix[route[j]][route[j + 1]]
                )
                d_new = (
                    dist_matrix[route[i - 1]][route[j]]
                    + dist_matrix[route[i]][route[j + 1]]
                )

                if d_new < d_current - 1e-10:
                    route[i : j + 1] = route[i : j + 1][::-1]
                    improved = True
    return route


def two_opt_solution(routes: List[List[int]], dist_matrix: np.ndarray) -> List[List[int]]:
    return [two_opt_route(route, dist_matrix) for route in routes]


def or_opt_route(route: List[int], dist_matrix: np.ndarray) -> List[int]:
    route = list(route)
    improved = True

    while improved:
        improved = False
        for seg_len in [1, 2, 3]:
            if improved:
                break
            for i in range(1, len(route) - seg_len):
                if i + seg_len >= len(route):
                    break
                cost_remove = (
                    dist_matrix[route[i - 1]][route[i]]
                    + dist_matrix[route[i + seg_len - 1]][route[i + seg_len]]
                    - dist_matrix[route[i - 1]][route[i + seg_len]]
                )
                best_gain = 0
                best_j = -1
                for j in range(1, len(route) - 1):
                    if i - 1 <= j <= i + seg_len:
                        continue
                    cost_insert = (
                        dist_matrix[route[j]][route[i]]
                        + dist_matrix[route[i + seg_len - 1]][route[j + 1]]
                        - dist_matrix[route[j]][route[j + 1]]
                    )
                    gain = cost_remove - cost_insert
                    if gain > best_gain + 1e-10:
                        best_gain = gain
                        best_j = j
                if best_j >= 0:
                    segment = route[i : i + seg_len]
                    new_route = route[:i] + route[i + seg_len :]
                    insert_pos = best_j if best_j < i else best_j - seg_len
                    new_route = (
                        new_route[: insert_pos + 1]
                        + segment
                        + new_route[insert_pos + 1 :]
                    )
                    route = new_route
                    improved = True
                    break
    return route


def full_local_search(routes: List[List[int]], dist_matrix: np.ndarray) -> List[List[int]]:
    improved_routes = []
    for route in routes:
        route = two_opt_route(route, dist_matrix)
        route = or_opt_route(route, dist_matrix)
        route = two_opt_route(route, dist_matrix)
        improved_routes.append(route)
    return improved_routes
