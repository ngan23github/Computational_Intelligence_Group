"""
Parser cho file CVRPLIB (.vrp) theo chuẩn TSPLIB.
"""
import numpy as np
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class VRPInstance:
    name: str
    dimension: int
    capacity: int
    coords: np.ndarray
    demands: np.ndarray
    depot: int
    optimal_value: Optional[float] = None

    def distance_matrix(self) -> np.ndarray:
        diff = self.coords[:, np.newaxis, :] - self.coords[np.newaxis, :, :]
        return np.sqrt((diff ** 2).sum(axis=-1))

    def customer_indices(self):
        return [i for i in range(self.dimension) if i != self.depot]

    def min_vehicles(self) -> int:
        total_demand = sum(self.demands[i] for i in self.customer_indices())
        return int(np.ceil(total_demand / self.capacity))

    def __str__(self):
        customers = self.dimension - 1
        total_demand = sum(self.demands[i] for i in self.customer_indices())
        min_v = self.min_vehicles()
        s = f"═══ VRP Instance: {self.name} ═══\n"
        s += f"  Số node:         {self.dimension} ({customers} khách hàng + 1 depot)\n"
        s += f"  Sức chứa xe:     {self.capacity}\n"
        s += f"  Tổng demand:     {total_demand}\n"
        s += f"  Xe tối thiểu:    ≥ {min_v}\n"
        s += f"  Depot:           node {self.depot}"
        if self.optimal_value:
            s += f"\n  Best Known (BKS): {self.optimal_value}"
        return s


def parse_vrp_file(filepath: str) -> VRPInstance:
    with open(filepath, 'r') as f:
        content = f.read()

    name_match = re.search(r'NAME\s*:\s*(.+)', content)
    name = name_match.group(1).strip() if name_match else "unknown"

    dimension = int(re.search(r'DIMENSION\s*:\s*(\d+)', content).group(1))
    capacity = int(re.search(r'CAPACITY\s*:\s*(\d+)', content).group(1))

    optimal_value = None
    comment_match = re.search(r'COMMENT\s*:\s*(.+)', content)
    if comment_match:
        opt_match = re.search(r'[Oo]ptimal\s+value\s*:\s*(\d+)', comment_match.group(1))
        if opt_match:
            optimal_value = float(opt_match.group(1))

    coords = np.zeros((dimension, 2))
    coord_match = re.search(
        r'NODE_COORD_SECTION\s*\n(.*?)(?=\n[A-Z_]+_SECTION|\nEOF)',
        content, re.DOTALL
    )
    if coord_match:
        for line in coord_match.group(1).strip().split('\n'):
            parts = line.split()
            if len(parts) >= 3:
                idx = int(parts[0]) - 1
                coords[idx] = [float(parts[1]), float(parts[2])]

    demands = np.zeros(dimension, dtype=int)
    demand_match = re.search(
        r'DEMAND_SECTION\s*\n(.*?)(?=\n[A-Z_]+_SECTION|\nEOF)',
        content, re.DOTALL
    )
    if demand_match:
        for line in demand_match.group(1).strip().split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                idx = int(parts[0]) - 1
                demands[idx] = int(parts[1])

    depot = 0
    depot_match = re.search(
        r'DEPOT_SECTION\s*\n(.*?)(?=\n[A-Z_]+_SECTION|\nEOF|\Z)',
        content, re.DOTALL
    )
    if depot_match:
        for line in depot_match.group(1).strip().split('\n'):
            val = line.strip()
            if val and val != '-1':
                depot = int(val) - 1
                break

    return VRPInstance(
        name=name, dimension=dimension, capacity=capacity,
        coords=coords, demands=demands, depot=depot, optimal_value=optimal_value
    )

def parse_sol_file(filepath: str, depot: int = 0) -> list:
    routes = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.lower().startswith('route'):
                parts = line.strip().split(':')
                if len(parts) == 2:
                    customers = [int(x) - 1 for x in parts[1].split()]
                    route = [depot] + customers + [depot]
                    routes.append(route)
    return routes
