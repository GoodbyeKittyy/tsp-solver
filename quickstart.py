"""
TSP Solver - Quick Start Demo
Run this file to see all features in action
"""

from tsp_solver import TSPSolver, generate_random_tsp
from tsp_visualizer import TSPVisualizer
import numpy as np


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_basic_usage():
    """Demo 1: Basic usage with small instance"""
    print_section("DEMO 1: Basic Usage - Exact Solution")
    
    # Create small problem
    print("Creating 5-city TSP instance...")
    dist_matrix = np.array([
        [0, 10, 15, 20, 25],
        [10, 0, 35, 25, 30],
        [15, 35, 0, 30, 20],
        [20, 25, 30, 0, 15],
        [25, 30, 20, 15, 0]
    ])
    
    solver = TSPSolver(dist_matrix)
    
    # Solve with exact algorithm
    print("Solving with Held-Karp (exact algorithm)...")
    result = solver.held_karp()
    
    print(f"\n✓ Solution found!")
    print(f"  Algorithm: {result.algorithm}")
    print(f"  Tour: {result.tour}")
    print(f"  Cost: {result.cost:.2f}")
    print(f"  Time: {result.execution_time:.4f} seconds")
    print(f"  Optimal: {result.is_optimal}")


def demo_algorithm_comparison():
    """Demo 2: Compare different algorithms"""
    print_section("DEMO 2: Algorithm Comparison")
    
    # Generate random instance
    n = 20
    print(f"Generating random {n}-city instance...")
    dist_matrix = generate_random_tsp(n, seed=42)
    solver = TSPSolver(dist_matrix)
    
    algorithms = [
        ('nearest-neighbor', 'Nearest Neighbor'),
        ('christofides', 'Christofides'),
        ('2-opt', '2-opt Improvement')
    ]
    
    results = []
    
    for algo, name in algorithms:
        print(f"\nTesting {name}...")
        
        if algo == '2-opt':
            # 2-opt needs initial tour
            nn_result = solver.nearest_neighbor()
            result = solver.two_opt(nn_result.tour, max_iterations=200)
        else:
            result = solver.solve(algo)
        
        results.append(result)
        
        print(f"  Cost: {result.cost:.2f}")
        print(f"  Time: {result.execution_time:.4f}s")
        if result.approximation_ratio:
            print(f"  Approximation: {result.approximation_ratio}×")
    
    # Summary
    best = min(results, key=lambda r: r.cost)
    print(f"\n✓ Best solution: {best.algorithm} with cost {best.cost:.2f}")


def demo_scaling():
    """Demo 3: Performance scaling"""
    print_section("DEMO 3: Scalability Test")
    
    sizes = [10, 20, 50, 100, 200]
    
    print("Testing performance across different problem sizes...")
    print(f"\n{'Size':<8} {'Algorithm':<20} {'Cost':<12} {'Time':<10}")
    print("-" * 60)
    
    for n in sizes:
        dist_matrix = generate_random_tsp(n, seed=42)
        solver = TSPSolver(dist_matrix)
        
        # Use appropriate algorithm for size
        if n <= 15:
            result = solver.held_karp()
        elif n <= 100:
            result = solver.christofides()
        else:
            result = solver.nearest_neighbor()
        
        print(f"{n:<8} {result.algorithm:<20} {result.cost:<12.2f} {result.execution_time:<10.4f}s")
    
    print("\n✓ Scaling test complete!")


def demo_visualization():
    """Demo 4: Visualization"""
    print_section("DEMO 4: Solution Visualization")
    
    n = 25
    print(f"Creating visualization for {n}-city problem...")
    
    # Generate instance with coordinates
    dist_matrix = generate_random_tsp(n, seed=42)
    np.random.seed(42)
    coords = np.random.rand(n, 2) * 1000
    
    solver = TSPSolver(dist_matrix)
    
    # Solve with different algorithms
    print("Solving with multiple algorithms...")
    nn_result = solver.nearest_neighbor()
    chris_result = solver.christofides()
    improved_result = solver.two_opt(nn_result.tour, max_iterations=200)
    
    # Create visualizations
    print("Generating plots...")
    visualizer = TSPVisualizer(coords)
    
    tours = [
        (nn_result.tour, "Nearest Neighbor", nn_result.cost),
        (chris_result.tour, "Christofides", chris_result.cost),
        (improved_result.tour, "2-opt Improved", improved_result.cost)
    ]
    
    try:
        visualizer.plot_comparison(tours, save_path="demo_comparison.png")
        print("✓ Visualization saved to 'demo_comparison.png'")
    except Exception as e:
        print(f"Note: Visualization requires display. Error: {e}")


def demo_real_world_example():
    """Demo 5: Real-world application"""
    print_section("DEMO 5: Real-World Application - Delivery Route")
    
    # Simulate delivery locations
    print("Simulating delivery route optimization...")
    print("\nScenario: Delivery truck must visit 15 customer locations")
    print("Starting from depot at location 0\n")
    
    # Generate locations
    np.random.seed(123)
    locations = np.random.rand(15, 2) * 100  # 100km x 100km area
    
    # Calculate distances (Euclidean)
    n = len(locations)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = np.linalg.norm(locations[i] - locations[j])
    
    solver = TSPSolver(dist_matrix)
    
    # Find optimal route
    result = solver.christofides()
    
    print(f"✓ Optimal route found:")
    print(f"  Delivery sequence: {' → '.join(map(str, result.tour))} → 0")
    print(f"  Total distance: {result.cost:.2f} km")
    print(f"  Estimated time: {result.cost / 60:.1f} hours @ 60 km/h")
    print(f"  Algorithm: {result.algorithm}")
    print(f"  Computation time: {result.execution_time:.4f}s")
    
    # Compare with naive approach
    naive_tour = list(range(n))
    naive_cost = solver.calculate_tour_cost(naive_tour)
    savings = (naive_cost - result.cost) / naive_cost * 100
    
    print(f"\n  Savings vs naive route: {savings:.1f}%")
    print(f"  Distance saved: {naive_cost - result.cost:.2f} km")


def demo_api_usage():
    """Demo 6: Programmatic API usage"""
    print_section("DEMO 6: API Usage Examples")
    
    print("Example 1: Auto algorithm selection")
    print("-" * 40)
    
    dist_matrix = generate_random_tsp(30, seed=42)
    solver = TSPSolver(dist_matrix)
    result = solver.solve("auto")  # Automatically chooses best algorithm
    
    print(f"Auto-selected: {result.algorithm}")
    print(f"Cost: {result.cost:.2f}, Time: {result.execution_time:.4f}s\n")
    
    print("Example 2: Custom distance matrix")
    print("-" * 40)
    
    # Custom distances between 4 locations
    custom_matrix = np.array([
        [0, 100, 200, 150],
        [100, 0, 120, 180],
        [200, 120, 0, 90],
        [150, 180, 90, 0]
    ])
    
    custom_solver = TSPSolver(custom_matrix)
    custom_result = custom_solver.solve("held-karp")
    
    print(f"Optimal tour: {custom_result.tour}")
    print(f"Total distance: {custom_result.cost:.2f}\n")
    
    print("Example 3: Iterative improvement")
    print("-" * 40)
    
    # Start with fast heuristic, then improve
    quick = solver.nearest_neighbor()
    print(f"Quick solution: {quick.cost:.2f}")
    
    improved = solver.two_opt(quick.tour, max_iterations=500)
    improvement = (quick.cost - improved.cost) / quick.cost * 100
    print(f"After 2-opt: {improved.cost:.2f}")
    print(f"Improvement: {improvement:.1f}%")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  TSP SOLVER - QUICK START DEMONSTRATION")
    print("  Production-grade Traveling Salesman Problem solver")
    print("=" * 80)
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Algorithm Comparison", demo_algorithm_comparison),
        ("Scalability", demo_scaling),
        ("Visualization", demo_visualization),
        ("Real-World Application", demo_real_world_example),
        ("API Usage", demo_api_usage)
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all demos...\n")
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n⚠ Warning: Demo '{name}' encountered an error: {e}")
            continue
    
    print("\n" + "=" * 80)
    print("  DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Try modifying the examples above")
    print("  2. Read the full documentation in README.md")
    print("  3. Explore the CLI: python tsp_cli.py --help")
    print("  4. Run the API server: python tsp_api.py")
    print("  5. Run tests: pytest tests/")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
