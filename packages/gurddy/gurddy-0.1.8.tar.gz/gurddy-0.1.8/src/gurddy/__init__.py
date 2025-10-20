from .model import Model
from .variable import Variable
from .constraint import Constraint, LinearConstraint, AllDifferentConstraint, FunctionConstraint
from .solver.csp_solver import CSPSolver
from .solver.lp_solver import LPSolver
from .solver.minimax_solver import MinimaxSolver

# SciPy integration - import conditionally
try:
    from .solver.scipy_solver import (
        ScipySolver, 
        optimize_portfolio, 
        fit_distribution, 
        design_filter, 
        solve_nonlinear
    )
    SCIPY_AVAILABLE = True
    __all__ = [
        'Model', 'Variable', 'Constraint', 'LinearConstraint', 'AllDifferentConstraint', 
        'FunctionConstraint', 'CSPSolver', 'LPSolver', 'MinimaxSolver',
        'ScipySolver', 'optimize_portfolio', 'fit_distribution', 'design_filter', 'solve_nonlinear'
    ]
except ImportError:
    SCIPY_AVAILABLE = False
    __all__ = [
        'Model', 'Variable', 'Constraint', 'LinearConstraint', 'AllDifferentConstraint', 
        'FunctionConstraint', 'CSPSolver', 'LPSolver', 'MinimaxSolver'
    ]