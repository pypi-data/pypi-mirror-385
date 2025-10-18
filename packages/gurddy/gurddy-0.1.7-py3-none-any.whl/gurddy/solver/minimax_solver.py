# gurddy/solver/minimax_solver.py
"""
Minimax solver for game theory and decision problems.
Supports zero-sum games, decision trees, and adversarial search.
"""
import pulp
from typing import List, Dict, Optional, Tuple
from ..model import Model
from ..constraint import LinearConstraint


class MinimaxSolver:
    """
    Solver for minimax optimization problems.
    
    Supports:
    - Zero-sum two-player games (find optimal mixed strategy)
    - Minimax decision problems (minimize maximum loss)
    - Maximin problems (maximize minimum gain)
    """
    
    def __init__(self, model: Model):
        self.model = model
        self.pulp_model = None
        self.var_map = {}
        
    def solve_game_matrix(self, payoff_matrix: List[List[float]], 
                         player: str = "row") -> Dict:
        """
        Solve a zero-sum game using linear programming.
        
        Args:
            payoff_matrix: Payoff matrix (row player's perspective)
            player: "row" or "col" - which player to optimize for
            
        Returns:
            Dictionary with optimal strategy and game value
        """
        m = len(payoff_matrix)  # row player strategies
        n = len(payoff_matrix[0])  # col player strategies
        
        if player == "row":
            # Row player maximizes minimum expected payoff
            # max v subject to: sum_i p_i * a_ij >= v for all j, sum_i p_i = 1, p_i >= 0
            prob = pulp.LpProblem("Minimax_Row", pulp.LpMaximize)
            
            # Variables: probabilities for each row strategy + game value
            p = [pulp.LpVariable(f"p_{i}", lowBound=0, upBound=1) for i in range(m)]
            v = pulp.LpVariable("v", lowBound=None)
            
            # Objective: maximize game value
            prob += v
            
            # Constraints: expected payoff against each column strategy >= v
            for j in range(n):
                prob += pulp.lpSum([p[i] * payoff_matrix[i][j] for i in range(m)]) >= v
            
            # Probabilities sum to 1
            prob += pulp.lpSum(p) == 1
            
            # Solve
            status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
            
            if status == pulp.LpStatusOptimal:
                strategy = [p[i].varValue for i in range(m)]
                return {
                    "strategy": strategy,
                    "value": v.varValue,
                    "player": "row",
                    "status": "optimal"
                }
        
        else:  # player == "col"
            # Column player minimizes maximum expected loss
            # min u subject to: sum_j q_j * a_ij <= u for all i, sum_j q_j = 1, q_j >= 0
            prob = pulp.LpProblem("Minimax_Col", pulp.LpMinimize)
            
            # Variables: probabilities for each column strategy + game value
            q = [pulp.LpVariable(f"q_{j}", lowBound=0, upBound=1) for j in range(n)]
            u = pulp.LpVariable("u", lowBound=None)
            
            # Objective: minimize game value
            prob += u
            
            # Constraints: expected payoff for each row strategy <= u
            for i in range(m):
                prob += pulp.lpSum([q[j] * payoff_matrix[i][j] for j in range(n)]) <= u
            
            # Probabilities sum to 1
            prob += pulp.lpSum(q) == 1
            
            # Solve
            status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
            
            if status == pulp.LpStatusOptimal:
                strategy = [q[j].varValue for j in range(n)]
                return {
                    "strategy": strategy,
                    "value": u.varValue,
                    "player": "col",
                    "status": "optimal"
                }
        
        return {"status": "infeasible"}
    
    def solve_minimax_decision(self, scenarios: List[Dict[str, float]], 
                              variables: List[str],
                              budget: float = None) -> Dict:
        """
        Solve minimax decision problem: minimize maximum loss across scenarios.
        
        Args:
            scenarios: List of dicts mapping variable names to coefficients
            variables: List of decision variable names
            budget: Optional budget constraint (sum of variables)
            
        Returns:
            Dictionary with optimal decision and worst-case value
        """
        prob = pulp.LpProblem("Minimax_Decision", pulp.LpMinimize)
        
        # Decision variables
        x = {var: pulp.LpVariable(var, lowBound=0) for var in variables}
        
        # Auxiliary variable for maximum
        z = pulp.LpVariable("max_loss", lowBound=None)
        
        # Objective: minimize maximum loss
        prob += z
        
        # Constraints: loss in each scenario <= z
        for scenario in scenarios:
            loss = pulp.lpSum([scenario.get(var, 0) * x[var] for var in variables])
            prob += loss <= z
        
        # Budget constraint if specified
        if budget is not None:
            prob += pulp.lpSum([x[var] for var in variables]) == budget
        
        # Solve
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        if status == pulp.LpStatusOptimal:
            return {
                "decision": {var: x[var].varValue for var in variables},
                "max_loss": z.varValue,
                "status": "optimal"
            }
        
        return {"status": "infeasible"}
    
    def solve_maximin_decision(self, scenarios: List[Dict[str, float]], 
                              variables: List[str],
                              budget: float = None) -> Dict:
        """
        Solve maximin decision problem: maximize minimum gain across scenarios.
        
        Args:
            scenarios: List of dicts mapping variable names to coefficients
            variables: List of decision variable names
            budget: Optional budget constraint (sum of variables)
            
        Returns:
            Dictionary with optimal decision and worst-case value
        """
        prob = pulp.LpProblem("Maximin_Decision", pulp.LpMaximize)
        
        # Decision variables
        x = {var: pulp.LpVariable(var, lowBound=0) for var in variables}
        
        # Auxiliary variable for minimum
        z = pulp.LpVariable("min_gain", lowBound=None)
        
        # Objective: maximize minimum gain
        prob += z
        
        # Constraints: gain in each scenario >= z
        for scenario in scenarios:
            gain = pulp.lpSum([scenario.get(var, 0) * x[var] for var in variables])
            prob += gain >= z
        
        # Budget constraint if specified
        if budget is not None:
            prob += pulp.lpSum([x[var] for var in variables]) == budget
        
        # Solve
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        if status == pulp.LpStatusOptimal:
            return {
                "decision": {var: x[var].varValue for var in variables},
                "min_gain": z.varValue,
                "status": "optimal"
            }
        
        return {"status": "infeasible"}
    
    def solve(self) -> Optional[Dict]:
        """
        Generic solve method for model-based minimax problems.
        Uses the model's constraints and objective.
        """
        # Create PuLP problem (minimax typically minimizes maximum)
        self.pulp_model = pulp.LpProblem(self.model.name, pulp.LpMinimize)
        
        # Map variables
        for var_name, var in self.model.variables.items():
            cat = pulp.LpContinuous if var.cat == 'Continuous' else pulp.LpInteger if var.cat == 'Integer' else pulp.LpBinary
            self.var_map[var_name] = pulp.LpVariable(var_name, lowBound=var.low_bound, 
                                                     upBound=var.up_bound, cat=cat)
        
        # Objective
        if self.model.objective:
            obj_terms = [coeff * self.var_map[var.name] for var, coeff in self.model.objective.terms.items()]
            obj_expr = pulp.lpSum(obj_terms)
            if isinstance(self.model.objective.constant, (int, float)):
                obj_expr += self.model.objective.constant
            self.pulp_model += obj_expr
        
        # Constraints
        for constr in self.model.constraints:
            if isinstance(constr, LinearConstraint):
                lhs_terms = [coeff * self.var_map[var.name] for var, coeff in constr.expr.terms.items()]
                lhs = pulp.lpSum(lhs_terms)
                if isinstance(constr.expr.constant, (int, float)):
                    lhs += constr.expr.constant
                
                if constr.sense == '<=':
                    self.pulp_model += lhs <= 0
                elif constr.sense == '>=':
                    self.pulp_model += lhs >= 0
                elif constr.sense == '==':
                    self.pulp_model += lhs == 0
        
        status = self.pulp_model.solve(pulp.PULP_CBC_CMD(msg=False))
        
        if status == pulp.LpStatusOptimal:
            return {var_name: v.varValue for var_name, v in self.var_map.items()}
        
        return None
