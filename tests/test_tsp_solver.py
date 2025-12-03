"""
Unit tests for TSP Solver
Run with: pytest test_tsp_solver.py
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tsp_solver import TSPSolver, generate_random_tsp, TSPResult


class TestTSPSolver:
    """Test suite for TSP Solver"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Small 4-city instance
        self.small_matrix = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        
        # Symmetric 5-city instance
        self.medium_matrix = np.array([
            [0, 10, 15, 20, 25],
            [10, 0, 35, 25, 30],
            [15, 35, 0, 30, 20],
            [20, 25, 30, 0, 15],
            [25, 30, 20, 15, 0]
        ])
    
    def test_initialization(self):
        """Test solver initialization"""
        solver = TSPSolver(self.small_matrix)
        assert solver.n == 4
        assert solver.distance_matrix.shape == (4, 4)
    
    def test_invalid_matrix(self):
        """Test validation of invalid matrices"""
        # Non-square matrix
        with pytest.raises(ValueError):
            TSPSolver(np.array([[1, 2], [3, 4], [5, 6]]))
        
        # Non-zero diagonal
        invalid = self.small_matrix.copy()
        invalid[0, 0] = 5
        with pytest.raises(ValueError):
            TSPSolver(invalid)
        
        # Too few cities
        with pytest.raises(ValueError):
            TSPSolver(np.array([[0]]))
    
    def test_tour_cost_calculation(self):
        """Test tour cost calculation"""
        solver = TSPSolver(self.small_matrix)
        tour = [0, 1, 2, 3]
        expected_cost = 10 + 35 + 30 + 20  # 0→1→2→3→0
        assert solver.calculate_tour_cost(tour) == expected_cost
    
    def test_held_karp_small(self):
        """Test Held-Karp on small instance"""
        solver = TSPSolver(self.small_matrix)
        result = solver.held_karp()
        
        assert isinstance(result, TSPResult)
        assert result.is_optimal
        assert len(result.tour) == 4
        assert result.cost > 0
        assert result.algorithm == "Held-Karp (Exact DP)"
    
    def test_held_karp_too_large(self):
        """Test Held-Karp fails gracefully on large instances"""
        large_matrix = generate_random_tsp(25, seed=42)
        solver = TSPSolver(large_matrix)
        
        with pytest.raises(ValueError, match="Too many cities"):
            solver.held_karp()
    
    def test_nearest_neighbor(self):
        """Test Nearest Neighbor heuristic"""
        solver = TSPSolver(self.medium_matrix)
        result = solver.nearest_neighbor()
        
        assert isinstance(result, TSPResult)
        assert not result.is_optimal
        assert len(result.tour) == 5
        assert result.cost > 0
        assert result.algorithm == "Nearest Neighbor"
    
    def test_christofides(self):
        """Test Christofides algorithm"""
        solver = TSPSolver(self.medium_matrix)
        result = solver.christofides()
        
        assert isinstance(result, TSPResult)
        assert not result.is_optimal
        assert result.approximation_ratio == 1.5
        assert len(result.tour) == 5
        assert result.cost > 0
        assert result.algorithm == "Christofides"
    
    def test_two_opt(self):
        """Test 2-opt improvement"""
        solver = TSPSolver(self.medium_matrix)
        
        # Get initial tour
        initial_tour = list(range(5))
        initial_cost = solver.calculate_tour_cost(initial_tour)
        
        # Improve with 2-opt
        result = solver.two_opt(initial_tour, max_iterations=100)
        
        assert isinstance(result, TSPResult)
        assert len(result.tour) == 5
        assert result.cost <= initial_cost  # Should not worsen
        assert result.algorithm == "2-opt"
    
    def test_auto_algorithm_selection(self):
        """Test automatic algorithm selection"""
        # Small instance should use Held-Karp
        small_solver = TSPSolver(self.small_matrix)
        result = small_solver.solve("auto")
        assert "Held-Karp" in result.algorithm
        
        # Medium instance should use Christofides
        medium_matrix = generate_random_tsp(30, seed=42)
        medium_solver = TSPSolver(medium_matrix)
        result = medium_solver.solve("auto")
        assert "Christofides" in result.algorithm
    
    def test_tour_validity(self):
        """Test that tours visit all cities exactly once"""
        solver = TSPSolver(self.medium_matrix)
        
        for algo in ['nearest-neighbor', 'christofides']:
            result = solver.solve(algo)
            
            # Check all cities visited
            assert len(result.tour) == 5
            
            # Check no duplicates
            assert len(set(result.tour)) == 5
            
            # Check valid city indices
            assert all(0 <= city < 5 for city in result.tour)
    
    def test_cost_consistency(self):
        """Test that reported cost matches calculated cost"""
        solver = TSPSolver(self.medium_matrix)
        
        for algo in ['nearest-neighbor', 'christofides', '2-opt']:
            if algo == '2-opt':
                result = solver.two_opt()
            else:
                result = solver.solve(algo)
            
            calculated_cost = solver.calculate_tour_cost(result.tour)
            assert abs(result.cost - calculated_cost) < 1e-6
    
    def test_performance_metrics(self):
        """Test that performance metrics are recorded"""
        solver = TSPSolver(self.medium_matrix)
        result = solver.nearest_neighbor()
        
        assert result.execution_time > 0
        assert result.num_cities == 5
        assert result.tour is not None
        assert result.cost > 0
    
    def test_generate_random_tsp(self):
        """Test random TSP generation"""
        n = 10
        dist_matrix = generate_random_tsp(n, seed=42)
        
        assert dist_matrix.shape == (n, n)
        assert np.all(np.diag(dist_matrix) == 0)  # Diagonal is zero
        assert np.all(dist_matrix >= 0)  # Non-negative distances
        
        # Test reproducibility
        dist_matrix2 = generate_random_tsp(n, seed=42)
        np.testing.assert_array_equal(dist_matrix, dist_matrix2)
    
    def test_different_starting_cities(self):
        """Test nearest neighbor from different starting points"""
        solver = TSPSolver(self.medium_matrix)
        
        costs = []
        for start in range(5):
            result = solver.nearest_neighbor(start=start)
            costs.append(result.cost)
        
        # Not all costs should be identical (different starting points)
        assert len(set(costs)) > 1
    
    def test_large_instance(self):
        """Test solver handles larger instances"""
        large_matrix = generate_random_tsp(100, seed=42)
        solver = TSPSolver(large_matrix)
        
        # Should complete without error
        result = solver.nearest_neighbor()
        assert len(result.tour) == 100
        assert result.execution_time < 1.0  # Should be fast


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_two_cities(self):
        """Test with minimum number of cities"""
        matrix = np.array([
            [0, 10],
            [10, 0]
        ])
        solver = TSPSolver(matrix)
        result = solver.nearest_neighbor()
        
        assert len(result.tour) == 2
        assert result.cost == 20  # Go and return
    
    def test_identical_distances(self):
        """Test with all identical distances"""
        n = 5
        matrix = np.ones((n, n)) * 10
        np.fill_diagonal(matrix, 0)
        
        solver = TSPSolver(matrix)
        result = solver.nearest_neighbor()
        
        assert len(result.tour) == n
        assert result.cost == n * 10  # All edges same cost
    
    def test_very_asymmetric(self):
        """Test with highly asymmetric distances"""
        matrix = np.array([
            [0, 1, 100],
            [100, 0, 1],
            [1, 100, 0]
        ])
        solver = TSPSolver(matrix)
        result = solver.nearest_neighbor()
        
        assert len(result.tour) == 3
        assert result.cost > 0


class TestAlgorithmComparison:
    """Test relative performance of algorithms"""
    
    def test_optimal_vs_heuristic(self):
        """Compare optimal solution with heuristics"""
        matrix = generate_random_tsp(12, seed=42)
        solver = TSPSolver(matrix)
        
        # Get optimal solution
        optimal = solver.held_karp()
        
        # Get heuristic solutions
        nn = solver.nearest_neighbor()
        chris = solver.christofides()
        
        # Heuristics should be close to optimal
        assert nn.cost >= optimal.cost  # Can't beat optimal
        assert chris.cost >= optimal.cost
        
        # Christofides should be within 1.5x for metric TSP
        # (Not always guaranteed for random instances, but should be close)
        assert chris.cost < optimal.cost * 2.0
    
    def test_2opt_improvement(self):
        """Test that 2-opt improves solution"""
        matrix = generate_random_tsp(20, seed=42)
        solver = TSPSolver(matrix)
        
        # Get initial solution
        initial = solver.nearest_neighbor()
        
        # Improve with 2-opt
        improved = solver.two_opt(initial.tour, max_iterations=100)
        
        # Should not worsen
        assert improved.cost <= initial.cost


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
