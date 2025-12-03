"""
TSP CLI - Command Line Interface
"""

import argparse
import json
import numpy as np
from tsp_solver import TSPSolver, generate_random_tsp
from tsp_visualizer import TSPVisualizer
import sys


def load_distance_matrix(filepath: str) -> np.ndarray:
    """Load distance matrix from file (JSON, NPY, or CSV)"""
    if filepath.endswith('.json'):
        with open(filepath, 'r') as f:
            data = json.load(f)
            return np.array(data)
    elif filepath.endswith('.npy'):
        return np.load(filepath)
    elif filepath.endswith('.csv'):
        return np.loadtxt(filepath, delimiter=',')
    else:
        raise ValueError(f"Unsupported file format: {filepath}")


def save_solution(tour, cost, filepath: str):
    """Save solution to file"""
    solution = {
        'tour': tour,
        'cost': float(cost)
    }
    with open(filepath, 'w') as f:
        json.dump(solution, f, indent=2)
    print(f"Solution saved to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='TSP Solver - Production-grade Traveling Salesman Problem solver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate random instance and solve
  python tsp_cli.py --random 20 --algorithm christofides
  
  # Load from file and solve
  python tsp_cli.py --input distances.json --algorithm held-karp
  
  # Compare algorithms
  python tsp_cli.py --random 30 --compare
  
  # Solve and visualize
  python tsp_cli.py --random 50 --algorithm 2-opt --visualize --output solution.png
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', '-i', type=str,
                           help='Input file (JSON, NPY, or CSV format)')
    input_group.add_argument('--random', '-r', type=int,
                           help='Generate random instance with N cities')
    
    # Algorithm selection
    parser.add_argument('--algorithm', '-a', type=str, default='auto',
                       choices=['held-karp', 'christofides', 'nearest-neighbor', '2-opt', 'auto'],
                       help='Algorithm to use (default: auto)')
    
    # Comparison mode
    parser.add_argument('--compare', '-c', action='store_true',
                       help='Compare multiple algorithms')
    
    # Visualization
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Visualize the solution')
    
    # Output options
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for solution or visualization')
    
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Load or generate distance matrix
    if args.input:
        print(f"Loading distance matrix from {args.input}...")
        dist_matrix = load_distance_matrix(args.input)
        coords = None
    else:
        print(f"Generating random TSP instance with {args.random} cities...")
        dist_matrix = generate_random_tsp(args.random, seed=args.seed)
        np.random.seed(args.seed)
        coords = np.random.rand(args.random, 2) * 1000
    
    n = len(dist_matrix)
    print(f"Problem size: {n} cities")
    
    # Create solver
    solver = TSPSolver(dist_matrix)
    
    # Solve
    if args.compare:
        print("\n" + "=" * 80)
        print("COMPARING ALGORITHMS")
        print("=" * 80)
        
        algorithms = ['nearest-neighbor', 'christofides', '2-opt']
        if n <= 15:
            algorithms = ['held-karp'] + algorithms
        
        results = []
        for algo in algorithms:
            print(f"\nTesting {algo}...")
            try:
                if algo == '2-opt':
                    nn_result = solver.nearest_neighbor()
                    result = solver.two_opt(nn_result.tour, max_iterations=500)
                else:
                    result = solver.solve(algo)
                
                print(f"  Cost: {result.cost:.2f}")
                print(f"  Time: {result.execution_time:.4f}s")
                if result.approximation_ratio:
                    print(f"  Approximation ratio: {result.approximation_ratio}")
                
                results.append(result)
                
            except Exception as e:
                print(f"  Error: {e}")
        
        # Find best solution
        best_result = min(results, key=lambda r: r.cost)
        print("\n" + "=" * 80)
        print(f"Best solution: {best_result.algorithm}")
        print(f"Cost: {best_result.cost:.2f}")
        
        # Visualize comparison
        if args.visualize and coords is not None:
            visualizer = TSPVisualizer(coords)
            tours = [(r.tour, r.algorithm, r.cost) for r in results]
            visualizer.plot_comparison(tours, save_path=args.output)
    
    else:
        print(f"\nSolving with {args.algorithm}...")
        
        try:
            if args.algorithm == '2-opt':
                nn_result = solver.nearest_neighbor()
                result = solver.two_opt(nn_result.tour, max_iterations=1000)
            else:
                result = solver.solve(args.algorithm)
            
            print("\n" + "=" * 80)
            print("SOLUTION")
            print("=" * 80)
            print(f"Algorithm: {result.algorithm}")
            print(f"Tour: {result.tour}")
            print(f"Cost: {result.cost:.2f}")
            print(f"Execution time: {result.execution_time:.4f}s")
            print(f"Optimal: {result.is_optimal}")
            if result.approximation_ratio:
                print(f"Approximation ratio: {result.approximation_ratio}")
            
            # Save solution
            if args.output and not args.visualize:
                save_solution(result.tour, result.cost, args.output)
            
            # Visualize
            if args.visualize:
                if coords is None:
                    print("\nWarning: Cannot visualize without coordinates")
                    print("Visualization only available for randomly generated instances")
                else:
                    visualizer = TSPVisualizer(coords)
                    save_path = args.output if args.output else "tsp_solution.png"
                    visualizer.plot_tour(result.tour, 
                                       title=f"{result.algorithm}",
                                       cost=result.cost,
                                       save_path=save_path)
        
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
