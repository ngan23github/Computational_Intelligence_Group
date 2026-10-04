"""
Ant Colony Optimization cho CVRP.
"""
import numpy as np
import time
from typing import List, Tuple, Optional, Callable
from vrp_parser import VRPInstance

class ACO_VRP:
    def __init__(self, instance: VRPInstance, n_ants: int = 50, n_iterations: int = 200,
                 alpha: float = 1.0, beta: float = 3.0, rho: float = 0.1, Q: float = 100.0,
                 use_mmas: bool = False, local_search_fn: Optional[Callable] = None,
                 elitist_weight: float = 2.0, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)
        self.instance = instance
        self.dist_matrix = instance.distance_matrix()
        self.n_nodes = instance.dimension
        self.depot = instance.depot
        self.capacity = instance.capacity
        self.demands = instance.demands
        self.n_ants, self.n_iterations = n_ants, n_iterations
        self.alpha, self.beta, self.rho, self.Q = alpha, beta, rho, Q
        self.use_mmas, self.local_search_fn, self.elitist_weight = use_mmas, local_search_fn, elitist_weight

        with np.errstate(divide='ignore'):
            self.eta = 1.0 / self.dist_matrix
        np.fill_diagonal(self.eta, 0)
        self.eta[self.eta == np.inf] = 0

        self.nn_cost = self._nearest_neighbor_cost()
        tau0 = 1.0 / (self.n_nodes * self.nn_cost) if self.nn_cost > 0 else 1.0
        self.pheromone = np.full((self.n_nodes, self.n_nodes), tau0)
        if self.use_mmas:
            self.tau_max = 1.0 / (self.rho * self.nn_cost)
            self.tau_min = self.tau_max / (2.0 * self.n_nodes)
            self.pheromone = np.full((self.n_nodes, self.n_nodes), self.tau_max)

    def _nearest_neighbor_cost(self) -> float:
        unvisited = set(range(self.n_nodes)) - {self.depot}
        total_cost = 0.0
        while unvisited:
            current, load = self.depot, 0
            while unvisited:
                feasible = [j for j in unvisited if self.demands[j] <= self.capacity - load]
                if not feasible: break
                nearest = min(feasible, key=lambda j: self.dist_matrix[current][j])
                total_cost += self.dist_matrix[current][nearest]
                load += self.demands[nearest]
                current = nearest
                unvisited.remove(nearest)
            total_cost += self.dist_matrix[current][self.depot]
        return total_cost

    def solve(self, verbose: bool = True):
        best_solution, best_cost = None, np.inf
        convergence, iteration_bests = [], []
        start_time = time.time()
        for iteration in range(self.n_iterations):
            solutions = []
            for _ in range(self.n_ants):
                solution = self._construct_solution()
                if self.local_search_fn is not None:
                    solution = self.local_search_fn(solution, self.dist_matrix)
                cost = self._solution_cost(solution)
                solutions.append((solution, cost))

            iter_best_sol, iter_best_cost = min(solutions, key=lambda x: x[1])
            iteration_bests.append(iter_best_cost)
            if iter_best_cost < best_cost:
                best_solution = [route[:] for route in iter_best_sol]
                best_cost = iter_best_cost

            self._evaporate_pheromone()
            if self.use_mmas:
                self._deposit_pheromone_single(best_solution, best_cost)
                np.clip(self.pheromone, self.tau_min, self.tau_max, out=self.pheromone)
            else:
                self._deposit_pheromone_all(solutions)
                self._deposit_pheromone_single(best_solution, best_cost, weight=self.elitist_weight)

            convergence.append(best_cost)
            if verbose and (iteration + 1) % max(1, self.n_iterations // 10) == 0:
                print(f"  Iter {iteration+1:4d}/{self.n_iterations} │ Best: {best_cost:>8.2f} │ Routes: {len(best_solution)}")

        stats = {'runtime': time.time() - start_time, 'nn_cost': self.nn_cost}
        if self.instance.optimal_value:
            stats['gap_pct'] = (best_cost / self.instance.optimal_value - 1) * 100
        return best_solution, best_cost, convergence, stats

    def _construct_solution(self) -> List[List[int]]:
        unvisited = set(range(self.n_nodes)) - {self.depot}
        routes = []
        while unvisited:
            route, current_load, current = [self.depot], 0, self.depot
            while unvisited:
                feasible = [j for j in unvisited if self.demands[j] <= self.capacity - current_load]
                if not feasible: break
                next_cust = self._select_next(current, feasible)
                route.append(next_cust)
                current_load += self.demands[next_cust]
                current = next_cust
                unvisited.remove(next_cust)
            route.append(self.depot)
            routes.append(route)
        return routes

    def _select_next(self, current: int, feasible: List[int]) -> int:
        feasible_arr = np.array(feasible)
        attractiveness = (self.pheromone[current][feasible_arr] ** self.alpha) * (self.eta[current][feasible_arr] ** self.beta)
        total = attractiveness.sum()
        if total == 0: return int(np.random.choice(feasible_arr))
        return int(np.random.choice(feasible_arr, p=attractiveness / total))

    def _solution_cost(self, routes: List[List[int]]) -> float:
        return sum(self.dist_matrix[route[i]][route[i+1]] for route in routes for i in range(len(route)-1))

    def _evaporate_pheromone(self):
        self.pheromone *= (1.0 - self.rho)

    def _deposit_pheromone_all(self, solutions):
        for solution, cost in solutions:
            for route in solution:
                for i in range(len(route) - 1):
                    self.pheromone[route[i]][route[i + 1]] += self.Q / cost
                    self.pheromone[route[i + 1]][route[i]] += self.Q / cost

    def _deposit_pheromone_single(self, solution, cost, weight=1.0):
        for route in solution:
            for i in range(len(route) - 1):
                self.pheromone[route[i]][route[i + 1]] += (weight * self.Q / cost)
                self.pheromone[route[i + 1]][route[i]] += (weight * self.Q / cost)
