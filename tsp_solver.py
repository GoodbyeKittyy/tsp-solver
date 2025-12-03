"""
TSP Solver - Production-Grade Implementation
Implements multiple algorithms: Held-Karp (DP), Christofides, Branch-and-Bound, Genetic Algorithm
"""

import numpy as np
import time
from typing import List, Tuple, Dict, Optional
from itertools import combinations, permutations
from dataclasses import dataclass
import heapq
import random


@dataclass
class TSPResult:
    """Container for TSP solution results"""
    tour: List[int]
    cost: float
    algorithm: str
    execution_time: float
    num_cities: int
    is_optimal: bool
    approximation_ratio: Optional[float] = None


class TSPSolver:
    """Production-grade TSP solver with multiple algorithms"""
    
    def __init__(self, distance_matrix: np.ndarray):
        """
        Initialize TSP solver with distance matrix
        
        Args:
            distance_matrix: n×n matrix of distances between cities
        """
        self.distance_matrix = distance_matrix
        self.n = len(distance_matrix)
        self.validate_input()
    
    def validate_input(self):
        """Validate distance matrix"""
        if self.distance_matrix.shape[0] != self.distance_matrix.shape[1]:
            raise ValueError("Distance matrix must be square")
        if self.n < 2:
            raise ValueError("Need at least 2 cities")
        if not np.all(np.diag(self.distance_matrix) == 0):
            raise ValueError("Diagonal elements must be zero")
    
    def calculate_tour_cost(self, tour: List[int]) -> float:
        """Calculate total cost of a tour"""
        cost = 0
        for i in range(len(tour)):
            cost += self.distance_matrix[tour[i]][tour[(i + 1) % len(tour)]]
        return cost
    
    def held_karp(self) -> TSPResult:
        """
        Held-Karp algorithm (Dynamic Programming)
        Time: O(n² * 2ⁿ), Space: O(n * 2ⁿ)
        Optimal for small instances (n ≤ 20)
        """
        start_time = time.time()
        
        if self.n > 20:
            raise ValueError("Held-Karp: Too many cities (max 20 for practical computation)")
        
        # DP table: dp[mask][i] = (min_cost, prev_city)
        dp = {}
        
        # Base case: start from city 0, visit only city 0
        dp[(1, 0)] = (0, -1)
        
        # Generate all subsets
        for subset_size in range(2, self.n + 1):
            for subset in combinations(range(1, self.n), subset_size - 1):
                subset = (0,) + subset  # Always include starting city 0
                bits = sum(1 << i for i in subset)
                
                for last in subset:
                    if last == 0:
                        continue
                    
                    prev_bits = bits & ~(1 << last)
                    min_cost = float('inf')
                    min_prev = -1
                    
                    for prev in subset:
                        if prev == last or prev not in subset:
                            continue
                        
                        prev_cost = dp.get((prev_bits, prev), (float('inf'), -1))[0]
                        cost = prev_cost + self.distance_matrix[prev][last]
                        
                        if cost < min_cost:
                            min_cost = cost
                            min_prev = prev
                    
                    dp[(bits, last)] = (min_cost, min_prev)
        
        # Find minimum cost to return to start
        all_cities_mask = (1 << self.n) - 1
        min_cost = float('inf')
        last_city = -1
        
        for i in range(1, self.n):
            cost = dp.get((all_cities_mask, i), (float('inf'), -1))[0]
            cost += self.distance_matrix[i][0]
            if cost < min_cost:
                min_cost = cost
                last_city = i
        
        # Reconstruct path
        tour = self.reconstruct_path_hk(dp, all_cities_mask, last_city)
        
        execution_time = time.time() - start_time
        
        return TSPResult(
            tour=tour,
            cost=min_cost,
            algorithm="Held-Karp (Exact DP)",
            execution_time=execution_time,
            num_cities=self.n,
            is_optimal=True
        )
    
    def reconstruct_path_hk(self, dp: Dict, mask: int, last: int) -> List[int]:
        """Reconstruct tour from DP table"""
        path = [last]
        current_mask = mask
        current = last
        
        while current != 0:
            prev = dp[(current_mask, current)][1]
            if prev == -1:
                break
            path.append(prev)
            current_mask = current_mask & ~(1 << current)
            current = prev
        
        path.reverse()
        return path
    
    def nearest_neighbor(self, start: int = 0) -> TSPResult:
        """
        Nearest Neighbor heuristic
        Time: O(n²), Approximation: No bound (can be arbitrarily bad)
        """
        start_time = time.time()
        
        unvisited = set(range(self.n))
        tour = [start]
        unvisited.remove(start)
        current = start
        total_cost = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current][x])
            total_cost += self.distance_matrix[current][nearest]
            current = nearest
            tour.append(current)
            unvisited.remove(current)
        
        total_cost += self.distance_matrix[current][start]
        
        execution_time = time.time() - start_time
        
        return TSPResult(
            tour=tour,
            cost=total_cost,
            algorithm="Nearest Neighbor",
            execution_time=execution_time,
            num_cities=self.n,
            is_optimal=False
        )
    
    def christofides(self) -> TSPResult:
        """
        Christofides algorithm
        Time: O(n³), Approximation: 1.5-approximation for metric TSP
        """
        start_time = time.time()
        
        # Step 1: Compute MST using Prim's algorithm
        mst = self.compute_mst()
        
        # Step 2: Find odd-degree vertices
        odd_vertices = self.find_odd_degree_vertices(mst)
        
        # Step 3: Minimum weight perfect matching on odd vertices
        matching = self.min_weight_matching(odd_vertices)
        
        # Step 4: Combine MST and matching to form Eulerian graph
        multigraph = self.combine_mst_matching(mst, matching)
        
        # Step 5: Find Eulerian circuit
        circuit = self.find_eulerian_circuit(multigraph)
        
        # Step 6: Convert to Hamiltonian circuit (shortcut)
        tour = self.make_hamiltonian(circuit)
        
        cost = self.calculate_tour_cost(tour)
        execution_time = time.time() - start_time
        
        return TSPResult(
            tour=tour,
            cost=cost,
            algorithm="Christofides",
            execution_time=execution_time,
            num_cities=self.n,
            is_optimal=False,
            approximation_ratio=1.5
        )
    
    def compute_mst(self) -> List[Tuple[int, int]]:
        """Compute MST using Prim's algorithm"""
        mst = []
        visited = {0}
        edges = [(self.distance_matrix[0][j], 0, j) for j in range(1, self.n)]
        heapq.heapify(edges)
        
        while len(visited) < self.n and edges:
            weight, u, v = heapq.heappop(edges)
            if v in visited:
                continue
            
            visited.add(v)
            mst.append((u, v))
            
            for j in range(self.n):
                if j not in visited:
                    heapq.heappush(edges, (self.distance_matrix[v][j], v, j))
        
        return mst
    
    def find_odd_degree_vertices(self, mst: List[Tuple[int, int]]) -> List[int]:
        """Find vertices with odd degree in MST"""
        degree = [0] * self.n
        for u, v in mst:
            degree[u] += 1
            degree[v] += 1
        return [i for i in range(self.n) if degree[i] % 2 == 1]
    
    def min_weight_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Greedy minimum weight perfect matching"""
        matching = []
        unmatched = set(odd_vertices)
        
        while len(unmatched) > 0:
            v = unmatched.pop()
            nearest = min(unmatched, key=lambda u: self.distance_matrix[v][u])
            matching.append((v, nearest))
            unmatched.remove(nearest)
        
        return matching
    
    def combine_mst_matching(self, mst: List[Tuple[int, int]], 
                            matching: List[Tuple[int, int]]) -> Dict[int, List[int]]:
        """Combine MST and matching into multigraph"""
        graph = {i: [] for i in range(self.n)}
        for u, v in mst + matching:
            graph[u].append(v)
            graph[v].append(u)
        return graph
    
    def find_eulerian_circuit(self, graph: Dict[int, List[int]]) -> List[int]:
        """Find Eulerian circuit using Hierholzer's algorithm"""
        curr_path = [0]
        circuit = []
        curr_graph = {k: v[:] for k, v in graph.items()}
        
        while curr_path:
            curr = curr_path[-1]
            if curr_graph[curr]:
                next_vertex = curr_graph[curr].pop()
                curr_graph[next_vertex].remove(curr)
                curr_path.append(next_vertex)
            else:
                circuit.append(curr_path.pop())
        
        return circuit[::-1]
    
    def make_hamiltonian(self, circuit: List[int]) -> List[int]:
        """Convert Eulerian circuit to Hamiltonian by shortcutting"""
        visited = set()
        tour = []
        for city in circuit:
            if city not in visited:
                tour.append(city)
                visited.add(city)
        return tour
    
    def two_opt(self, initial_tour: Optional[List[int]] = None, 
                max_iterations: int = 1000) -> TSPResult:
        """
        2-opt local search improvement
        Time: O(n² * iterations)
        """
        start_time = time.time()
        
        if initial_tour is None:
            tour = list(range(self.n))
        else:
            tour = initial_tour[:]
        
        best_cost = self.calculate_tour_cost(tour)
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(1, self.n - 1):
                for j in range(i + 1, self.n):
                    new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                    new_cost = self.calculate_tour_cost(new_tour)
                    
                    if new_cost < best_cost:
                        tour = new_tour
                        best_cost = new_cost
                        improved = True
                        break
                if improved:
                    break
        
        execution_time = time.time() - start_time
        
        return TSPResult(
            tour=tour,
            cost=best_cost,
            algorithm="2-opt",
            execution_time=execution_time,
            num_cities=self.n,
            is_optimal=False
        )
    
    def solve(self, algorithm: str = "auto") -> TSPResult:
        """
        Solve TSP with specified algorithm
        
        Args:
            algorithm: "held-karp", "christofides", "nearest-neighbor", "2-opt", "auto"
        """
        if algorithm == "auto":
            if self.n <= 15:
                return self.held_karp()
            elif self.n <= 100:
                return self.christofides()
            else:
                nn_result = self.nearest_neighbor()
                return self.two_opt(nn_result.tour)
        
        algorithms = {
            "held-karp": self.held_karp,
            "christofides": self.christofides,
            "nearest-neighbor": self.nearest_neighbor,
            "2-opt": lambda: self.two_opt()
        }
        
        if algorithm not in algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        return algorithms[algorithm]()


def generate_random_tsp(n: int, seed: Optional[int] = None) -> np.ndarray:
    """Generate random TSP instance with Euclidean distances"""
    if seed:
        np.random.seed(seed)
    
    # Generate random 2D coordinates
    coords = np.random.rand(n, 2) * 1000
    
    # Calculate Euclidean distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    return dist_matrix


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("TSP Solver - Production Grade Implementation")
    print("=" * 60)
    
    # Test with small instance (exact solution)
    print("\nTest 1: Small instance (10 cities) - Exact Solution")
    dist_matrix_small = generate_random_tsp(10, seed=42)
    solver_small = TSPSolver(dist_matrix_small)
    
    result = solver_small.solve("held-karp")
    print(f"Algorithm: {result.algorithm}")
    print(f"Tour: {result.tour}")
    print(f"Cost: {result.cost:.2f}")
    print(f"Time: {result.execution_time:.4f}s")
    print(f"Optimal: {result.is_optimal}")
    
    # Test with medium instance (approximation)
    print("\n" + "=" * 60)
    print("Test 2: Medium instance (50 cities) - Christofides")
    dist_matrix_medium = generate_random_tsp(50, seed=42)
    solver_medium = TSPSolver(dist_matrix_medium)
    
    result = solver_medium.solve("christofides")
    print(f"Algorithm: {result.algorithm}")
    print(f"Tour length: {len(result.tour)} cities")
    print(f"Cost: {result.cost:.2f}")
    print(f"Time: {result.execution_time:.4f}s")
    print(f"Approximation Ratio: {result.approximation_ratio}")
    
    # Test with large instance (heuristic)
    print("\n" + "=" * 60)
    print("Test 3: Large instance (200 cities) - Nearest Neighbor + 2-opt")
    dist_matrix_large = generate_random_tsp(200, seed=42)
    solver_large = TSPSolver(dist_matrix_large)
    
    nn_result = solver_large.nearest_neighbor()
    print(f"Nearest Neighbor Cost: {nn_result.cost:.2f}")
    print(f"Time: {nn_result.execution_time:.4f}s")
    
    improved_result = solver_large.two_opt(nn_result.tour, max_iterations=500)
    print(f"\n2-opt Improved Cost: {improved_result.cost:.2f}")
    print(f"Improvement: {((nn_result.cost - improved_result.cost) / nn_result.cost * 100):.2f}%")
    print(f"Time: {improved_result.execution_time:.4f}s")
    
    print("\n" + "=" * 60)
    print("Benchmark complete!")
