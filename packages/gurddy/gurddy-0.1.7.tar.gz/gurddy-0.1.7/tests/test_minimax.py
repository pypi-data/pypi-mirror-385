"""
Unit tests for Minimax solver
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from gurddy.solver.minimax_solver import MinimaxSolver


class TestMinimaxSolver(unittest.TestCase):
    """Test cases for MinimaxSolver"""
    
    def test_rock_paper_scissors(self):
        """Test Rock-Paper-Scissors game"""
        payoff_matrix = [
            [0, -1, 1],   # Rock
            [1, 0, -1],   # Paper
            [-1, 1, 0]    # Scissors
        ]
        
        solver = MinimaxSolver(None)
        result = solver.solve_game_matrix(payoff_matrix, player="row")
        
        # Check that strategy is approximately uniform (1/3, 1/3, 1/3)
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'optimal')
        self.assertAlmostEqual(result['strategy'][0], 1/3, places=2)
        self.assertAlmostEqual(result['strategy'][1], 1/3, places=2)
        self.assertAlmostEqual(result['strategy'][2], 1/3, places=2)
        
        # Game value should be 0 (fair game)
        self.assertAlmostEqual(result['value'], 0.0, places=2)
    
    def test_matching_pennies(self):
        """Test Matching Pennies game"""
        payoff_matrix = [
            [1, -1],   # Heads
            [-1, 1]    # Tails
        ]
        
        solver = MinimaxSolver(None)
        result_row = solver.solve_game_matrix(payoff_matrix, player="row")
        result_col = solver.solve_game_matrix(payoff_matrix, player="col")
        
        # Both players should play 50-50
        self.assertAlmostEqual(result_row['strategy'][0], 0.5, places=2)
        self.assertAlmostEqual(result_row['strategy'][1], 0.5, places=2)
        self.assertAlmostEqual(result_col['strategy'][0], 0.5, places=2)
        self.assertAlmostEqual(result_col['strategy'][1], 0.5, places=2)
        
        # Game value should be 0
        self.assertAlmostEqual(result_row['value'], 0.0, places=2)
        self.assertAlmostEqual(result_col['value'], 0.0, places=2)
    
    def test_minimax_decision_with_budget(self):
        """Test minimax decision problem with budget constraint"""
        scenarios = [
            {"A": 1, "B": 2},
            {"A": 3, "B": 1},
            {"A": 2, "B": 2}
        ]
        
        solver = MinimaxSolver(None)
        result = solver.solve_minimax_decision(scenarios, ["A", "B"], budget=10)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'optimal')
        
        # Check budget constraint is satisfied
        total = result['decision']['A'] + result['decision']['B']
        self.assertAlmostEqual(total, 10.0, places=2)
        
        # Check that max_loss is computed
        self.assertIsNotNone(result['max_loss'])
    
    def test_maximin_decision_with_budget(self):
        """Test maximin decision problem with budget constraint"""
        scenarios = [
            {"X": -10, "Y": -5},  # Negative for maximin (profit)
            {"X": -8, "Y": -6},
            {"X": -5, "Y": -8}
        ]
        
        solver = MinimaxSolver(None)
        result = solver.solve_maximin_decision(scenarios, ["X", "Y"], budget=100)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'optimal')
        
        # Check budget constraint is satisfied
        total = result['decision']['X'] + result['decision']['Y']
        self.assertAlmostEqual(total, 100.0, places=2)
        
        # Check that min_gain is computed
        self.assertIsNotNone(result['min_gain'])
    
    def test_pure_strategy_game(self):
        """Test game with pure strategy equilibrium"""
        # Simple game where row player should always choose first strategy
        payoff_matrix = [
            [2, 2],
            [0, 0]
        ]
        
        solver = MinimaxSolver(None)
        result = solver.solve_game_matrix(payoff_matrix, player="row")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'optimal')
        # Row player should play first strategy with probability 1
        self.assertAlmostEqual(result['strategy'][0], 1.0, places=2)
        self.assertAlmostEqual(result['value'], 2.0, places=2)
    
    def test_minimax_without_budget(self):
        """Test minimax decision without budget constraint"""
        scenarios = [
            {"A": 1, "B": 2},
            {"A": 3, "B": 1}
        ]
        
        solver = MinimaxSolver(None)
        result = solver.solve_minimax_decision(scenarios, ["A", "B"], budget=None)
        
        # Without budget, optimal is to set all variables to 0
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'optimal')


if __name__ == '__main__':
    unittest.main()
