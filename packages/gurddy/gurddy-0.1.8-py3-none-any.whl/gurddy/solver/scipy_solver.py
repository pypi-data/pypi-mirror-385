"""
SciPy Integration Solver for Gurddy

This module provides seamless integration between Gurddy and SciPy for advanced optimization.
Users can access SciPy functionality through Gurddy's unified interface.
"""

from typing import Dict, List, Tuple, Optional, Callable, Any, Union
import numpy as np

try:
    import scipy.optimize
    import scipy.stats
    import scipy.signal
    import scipy.integrate
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ScipySolver:
    """
    SciPy integration solver that provides advanced optimization capabilities.
    
    This solver acts as a bridge between Gurddy's constraint system and SciPy's
    numerical optimization routines.
    """
    
    def __init__(self, model=None):
        self.model = model
        if not SCIPY_AVAILABLE:
            raise ImportError(
                "SciPy is required for ScipySolver. Install with: pip install scipy"
            )
    
    def solve_nonlinear_optimization(
        self,
        objective: Callable,
        x0: Union[List[float], np.ndarray],
        method: str = 'SLSQP',
        bounds: Optional[List[Tuple[float, float]]] = None,
        constraints: Optional[List[Dict]] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Solve nonlinear optimization problem using SciPy.
        
        Args:
            objective: Objective function to minimize
            x0: Initial guess
            method: Optimization method ('SLSQP', 'L-BFGS-B', etc.)
            bounds: Variable bounds [(min, max), ...]
            constraints: List of constraint dictionaries
            options: Solver options
            
        Returns:
            Dictionary with optimization results
        """
        if options is None:
            options = {'maxiter': 1000}
        
        result = scipy.optimize.minimize(
            objective, x0, method=method,
            bounds=bounds, constraints=constraints,
            options=options
        )
        
        return {
            'success': result.success,
            'x': result.x,
            'fun': result.fun,
            'message': result.message,
            'nit': result.nit,
            'nfev': result.nfev,
            'raw_result': result
        }
    
    def solve_portfolio_optimization(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.02,
        bounds: Optional[List[Tuple[float, float]]] = None,
        constraints: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Solve portfolio optimization problem (maximize Sharpe ratio).
        
        Args:
            expected_returns: Expected returns for each asset
            covariance_matrix: Asset covariance matrix
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
            bounds: Weight bounds for each asset
            constraints: Additional constraints
            
        Returns:
            Dictionary with optimal portfolio weights and metrics
        """
        n_assets = len(expected_returns)
        
        def objective(weights):
            """Minimize negative Sharpe ratio"""
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
            portfolio_std = np.sqrt(portfolio_variance)
            
            if portfolio_std < 1e-8:
                return 1e6
            
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
            return -sharpe_ratio
        
        # Default constraints: weights sum to 1
        default_constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}
        ]
        
        if constraints:
            default_constraints.extend(constraints)
        
        # Default bounds: 0 to 1 for each weight
        if bounds is None:
            bounds = [(0, 1) for _ in range(n_assets)]
        
        # Initial guess: equal weights
        x0 = np.ones(n_assets) / n_assets
        
        result = self.solve_nonlinear_optimization(
            objective, x0, bounds=bounds, constraints=default_constraints
        )
        
        if result['success']:
            optimal_weights = result['x']
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_variance = np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights))
            portfolio_std = np.sqrt(portfolio_variance)
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
            
            result.update({
                'weights': optimal_weights,
                'expected_return': portfolio_return,
                'volatility': portfolio_std,
                'sharpe_ratio': sharpe_ratio
            })
        
        return result
    
    def fit_distribution_parameters(
        self,
        data: np.ndarray,
        distribution: str = 'gamma',
        bounds: Optional[List[Tuple[float, float]]] = None,
        method: str = 'mle'
    ) -> Dict[str, Any]:
        """
        Fit distribution parameters with optional constraints.
        
        Args:
            data: Sample data
            distribution: Distribution name ('gamma', 'weibull_min', 'norm', etc.)
            bounds: Parameter bounds
            method: Fitting method ('mle' or 'quantile')
            
        Returns:
            Dictionary with fitted parameters and goodness-of-fit statistics
        """
        if not hasattr(scipy.stats, distribution):
            raise ValueError(f"Unknown distribution: {distribution}")
        
        dist = getattr(scipy.stats, distribution)
        
        if method == 'mle':
            # Standard MLE
            initial_params = dist.fit(data)
            
            if bounds is None:
                params = initial_params
            else:
                # Constrained MLE using optimization
                def negative_log_likelihood(params):
                    try:
                        return -np.sum(dist.logpdf(data, *params))
                    except:
                        return 1e6
                
                # Ensure bounds match parameter dimensions
                if len(bounds) != len(initial_params):
                    # Adjust bounds to match parameter count
                    if len(bounds) < len(initial_params):
                        # Extend bounds with default values
                        default_bounds = [(0.01, 100.0) for _ in range(len(initial_params) - len(bounds))]
                        bounds = list(bounds) + default_bounds
                    else:
                        # Truncate bounds to match parameter count
                        bounds = bounds[:len(initial_params)]
                
                result = self.solve_nonlinear_optimization(
                    negative_log_likelihood, initial_params, bounds=bounds
                )
                
                if result['success']:
                    params = result['x']
                else:
                    params = initial_params
        
        elif method == 'quantile':
            # Quantile matching method
            quantile_levels = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
            empirical_quantiles = np.quantile(data, quantile_levels)
            
            def objective(params):
                try:
                    theoretical_quantiles = dist.ppf(quantile_levels, *params)
                    return np.sum((empirical_quantiles - theoretical_quantiles)**2)
                except:
                    return 1e6
            
            initial_params = dist.fit(data)
            
            # Ensure bounds match parameter dimensions
            if bounds is not None:
                if len(bounds) != len(initial_params):
                    if len(bounds) < len(initial_params):
                        default_bounds = [(0.01, 100.0) for _ in range(len(initial_params) - len(bounds))]
                        bounds = list(bounds) + default_bounds
                    else:
                        bounds = bounds[:len(initial_params)]
            
            result = self.solve_nonlinear_optimization(
                objective, initial_params, bounds=bounds
            )
            
            if result['success']:
                params = result['x']
            else:
                params = initial_params
        
        else:
            raise ValueError(f"Unknown fitting method: {method}")
        
        # Goodness of fit test
        ks_stat, p_value = scipy.stats.kstest(data, lambda x: dist.cdf(x, *params))
        
        return {
            'parameters': params,
            'distribution': distribution,
            'ks_statistic': ks_stat,
            'p_value': p_value,
            'log_likelihood': np.sum(dist.logpdf(data, *params)),
            'aic': 2 * len(params) - 2 * np.sum(dist.logpdf(data, *params))
        }
    
    def design_fir_filter(
        self,
        num_taps: int,
        cutoff_freq: float,
        sampling_freq: float,
        filter_type: str = 'lowpass',
        optimize: bool = True,
        desired_response: Optional[np.ndarray] = None,
        freq_grid: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Design FIR filter with optional optimization.
        
        Args:
            num_taps: Number of filter taps
            cutoff_freq: Cutoff frequency
            sampling_freq: Sampling frequency
            filter_type: Filter type ('lowpass', 'highpass', 'bandpass')
            optimize: Whether to optimize coefficients
            desired_response: Desired frequency response (for optimization)
            freq_grid: Frequency grid for response evaluation
            
        Returns:
            Dictionary with filter coefficients and performance metrics
        """
        # Initial filter design using SciPy
        initial_filter = scipy.signal.firwin(
            num_taps, cutoff_freq, fs=sampling_freq, 
            pass_zero=(filter_type == 'lowpass')
        )
        
        if not optimize:
            w, h = scipy.signal.freqz(initial_filter, fs=sampling_freq)
            return {
                'coefficients': initial_filter,
                'frequency_response': (w, h),
                'optimized': False
            }
        
        # Optimization setup
        if freq_grid is None:
            freq_grid = np.linspace(0, sampling_freq/2, 512)
        
        if desired_response is None:
            if filter_type == 'lowpass':
                desired_response = np.where(freq_grid <= cutoff_freq, 1.0, 0.0)
            elif filter_type == 'highpass':
                desired_response = np.where(freq_grid >= cutoff_freq, 1.0, 0.0)
            else:
                raise ValueError("Desired response must be provided for bandpass filters")
        
        def objective(coeffs):
            """Minimize frequency response error"""
            w, h = scipy.signal.freqz(coeffs, fs=sampling_freq)
            h_interp = np.interp(freq_grid, w, np.abs(h))
            mse = np.mean((h_interp - desired_response)**2)
            
            # L2 regularization
            l2_penalty = 0.01 * np.sum(coeffs**2)
            return mse + l2_penalty
        
        # Symmetry constraint for linear phase
        def symmetry_constraint(coeffs):
            n = len(coeffs)
            mid = n // 2
            errors = []
            for i in range(mid):
                errors.append(coeffs[i] - coeffs[n-1-i])
            return np.array(errors)
        
        constraints = [{'type': 'eq', 'fun': symmetry_constraint}]
        bounds = [(-2.0, 2.0) for _ in range(num_taps)]
        
        result = self.solve_nonlinear_optimization(
            objective, initial_filter, bounds=bounds, constraints=constraints
        )
        
        if result['success']:
            optimized_filter = result['x']
        else:
            optimized_filter = initial_filter
        
        # Performance evaluation
        w_opt, h_opt = scipy.signal.freqz(optimized_filter, fs=sampling_freq)
        
        return {
            'coefficients': optimized_filter,
            'initial_coefficients': initial_filter,
            'frequency_response': (w_opt, h_opt),
            'optimization_result': result,
            'optimized': True,
            'improvement': objective(initial_filter) - objective(optimized_filter)
        }
    
    def solve_hybrid_problem(
        self,
        discrete_model,
        continuous_objective: Callable,
        continuous_variables: List[str],
        x0: Optional[np.ndarray] = None,
        bounds: Optional[List[Tuple[float, float]]] = None,
        constraints: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Solve hybrid discrete-continuous optimization problem.
        
        Args:
            discrete_model: Gurddy model for discrete decisions
            continuous_objective: Objective function for continuous variables
            continuous_variables: Names of continuous variables
            x0: Initial guess for continuous variables
            bounds: Bounds for continuous variables
            constraints: Constraints for continuous variables
            
        Returns:
            Dictionary with discrete and continuous solutions
        """
        # Step 1: Solve discrete problem
        discrete_solution = discrete_model.solve()
        
        if discrete_solution is None:
            return {
                'success': False,
                'message': 'Discrete problem infeasible',
                'discrete_solution': None,
                'continuous_solution': None
            }
        
        # Step 2: Solve continuous problem given discrete solution
        if x0 is None:
            x0 = np.zeros(len(continuous_variables))
        
        # Create objective function that uses discrete solution
        def hybrid_objective(x_continuous):
            return continuous_objective(x_continuous, discrete_solution)
        
        continuous_result = self.solve_nonlinear_optimization(
            hybrid_objective, x0, bounds=bounds, constraints=constraints
        )
        
        return {
            'success': continuous_result['success'],
            'discrete_solution': discrete_solution,
            'continuous_solution': {
                var: continuous_result['x'][i] 
                for i, var in enumerate(continuous_variables)
            } if continuous_result['success'] else None,
            'objective_value': continuous_result['fun'] if continuous_result['success'] else None,
            'message': continuous_result['message']
        }
    
    def solve(self):
        """
        Generic solve method for model-based problems.
        This method can be extended to handle different problem types.
        """
        if self.model is None:
            raise ValueError("No model provided to ScipySolver")
        
        # This is a placeholder - specific implementations would depend on
        # how the model is structured for SciPy problems
        raise NotImplementedError(
            "Generic solve method not implemented. Use specific methods like "
            "solve_nonlinear_optimization, solve_portfolio_optimization, etc."
        )


# Convenience functions that can be imported directly
def optimize_portfolio(
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    risk_free_rate: float = 0.02,
    bounds: Optional[List[Tuple[float, float]]] = None,
    constraints: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Convenience function for portfolio optimization.
    """
    solver = ScipySolver()
    return solver.solve_portfolio_optimization(
        expected_returns, covariance_matrix, risk_free_rate, bounds, constraints
    )


def fit_distribution(
    data: np.ndarray,
    distribution: str = 'gamma',
    bounds: Optional[List[Tuple[float, float]]] = None,
    method: str = 'mle'
) -> Dict[str, Any]:
    """
    Convenience function for distribution fitting.
    """
    solver = ScipySolver()
    return solver.fit_distribution_parameters(data, distribution, bounds, method)


def design_filter(
    num_taps: int,
    cutoff_freq: float,
    sampling_freq: float,
    filter_type: str = 'lowpass',
    optimize: bool = True
) -> Dict[str, Any]:
    """
    Convenience function for FIR filter design.
    """
    solver = ScipySolver()
    return solver.design_fir_filter(
        num_taps, cutoff_freq, sampling_freq, filter_type, optimize
    )


def solve_nonlinear(
    objective: Callable,
    x0: Union[List[float], np.ndarray],
    method: str = 'SLSQP',
    bounds: Optional[List[Tuple[float, float]]] = None,
    constraints: Optional[List[Dict]] = None,
    options: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Convenience function for nonlinear optimization.
    """
    solver = ScipySolver()
    return solver.solve_nonlinear_optimization(
        objective, x0, method, bounds, constraints, options
    )