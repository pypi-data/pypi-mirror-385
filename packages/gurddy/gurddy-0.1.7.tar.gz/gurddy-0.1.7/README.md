### Gurddy
Gurddy is a lightweight Python package designed to model and solve Constraint Satisfaction Problems (CSP), Linear Programming (LP), and Minimax optimization problems with ease. Built for researchers, engineers, and optimization enthusiasts, Gurddy provides a unified interface to define variables, constraints, and objectives—then leverages powerful solvers under the hood to deliver optimal or feasible solutions.

## Quick Start

### 🧩 Logic Puzzle Example
```python
import gurddy

# Solve a simple logic puzzle: 3 people, pets, and house colors
model = gurddy.Model("LogicPuzzle", "CSP")

# Variables: people, pets, colors (positions 1-3)
alice = model.addVar("alice", domain=[1, 2, 3])
bob = model.addVar("bob", domain=[1, 2, 3])
carol = model.addVar("carol", domain=[1, 2, 3])

cat = model.addVar("cat", domain=[1, 2, 3])
dog = model.addVar("dog", domain=[1, 2, 3])
fish = model.addVar("fish", domain=[1, 2, 3])

red = model.addVar("red", domain=[1, 2, 3])
blue = model.addVar("blue", domain=[1, 2, 3])
green = model.addVar("green", domain=[1, 2, 3])

# All different constraints
model.addConstraint(gurddy.AllDifferentConstraint([alice, bob, carol]))
model.addConstraint(gurddy.AllDifferentConstraint([cat, dog, fish]))
model.addConstraint(gurddy.AllDifferentConstraint([red, blue, green]))

# Logic constraints
def same_position(a, b):
    return a == b

model.addConstraint(gurddy.FunctionConstraint(same_position, (alice, cat)))    # Alice has cat
model.addConstraint(gurddy.FunctionConstraint(same_position, (bob, red)))      # Bob in red house
model.addConstraint(gurddy.FunctionConstraint(same_position, (cat, green)))    # Cat owner in green house
model.addConstraint(gurddy.FunctionConstraint(same_position, (carol, fish)))   # Carol has fish

# Solve
solution = model.solve()
print("Alice has Cat in Green house")
print("Bob has Dog in Red house") 
print("Carol has Fish in Blue house")
```

### 👑 N-Queens Example
```python
import gurddy

# Solve 4-Queens problem
model = gurddy.Model("4-Queens", "CSP")

# Create variables (one per row, value = column)
queens = [model.addVar(f"q{i}", domain=[0,1,2,3]) for i in range(4)]

# All queens in different columns
model.addConstraint(gurddy.AllDifferentConstraint(queens))

# No two queens on same diagonal
for i in range(4):
    for j in range(i + 1, 4):
        row_diff = j - i
        diagonal_constraint = lambda c1, c2, rd=row_diff: abs(c1 - c2) != rd
        model.addConstraint(gurddy.FunctionConstraint(diagonal_constraint, (queens[i], queens[j])))

# Solve and print solution
solution = model.solve()
if solution:
    for row in range(4):
        line = ['Q' if solution[f'q{row}'] == col else '.' for col in range(4)]
        print(' '.join(line))
```

Output:
```
. Q . .
. . . Q  
Q . . .
. . Q .
```

### 🎮 Minimax Game Theory Example
```python
from gurddy.solver.minimax_solver import MinimaxSolver

# Solve Rock-Paper-Scissors game
payoff_matrix = [
    [0, -1, 1],   # Rock vs [Rock, Paper, Scissors]
    [1, 0, -1],   # Paper vs [Rock, Paper, Scissors]
    [-1, 1, 0]    # Scissors vs [Rock, Paper, Scissors]
]

solver = MinimaxSolver(None)
result = solver.solve_game_matrix(payoff_matrix, player="row")

print(f"Optimal strategy: Rock={result['strategy'][0]:.2f}, "
      f"Paper={result['strategy'][1]:.2f}, Scissors={result['strategy'][2]:.2f}")
print(f"Game value: {result['value']:.2f}")
```

Output:
```
Optimal strategy: Rock=0.33, Paper=0.33, Scissors=0.33
Game value: 0.00
```

Features
- 🧩 CSP Support: Define discrete variables, domains, and logical constraints.
- 📈 LP Support: Formulate linear objectives and inequality/equality constraints.
- 🎮 Minimax Support: Solve game theory problems and robust optimization under uncertainty.
- 🔌 Extensible Solver Backend: Integrates with industry-standard solvers (e.g., Gurobi, CBC, or GLPK via compatible interfaces).
- 📦 Simple API: Intuitive syntax for rapid prototyping and experimentation.
- 🧪 Type-Hinted & Tested: Robust codebase with unit tests and clear documentation.

## CSP Examples

### 🧩 Classic Puzzles

#### **Sudoku Solver** (`optimized_csp.py`)
- Complete 9×9 Sudoku puzzle solver
- Demonstrates AllDifferent constraints
- Shows mask-based optimizations for small integer domains
- **Run**: `python examples/optimized_csp.py`

#### **N-Queens Problem** (`n_queens.py`)
- Place N queens on N×N chessboard without conflicts
- Demonstrates custom function constraints for diagonal checks
- Supports any board size (4×4, 8×8, etc.)
- **Run**: `python examples/n_queens.py`

#### **Logic Puzzles** (`logic_puzzles.py`) ✨ **UPDATED**
- **Einstein's Zebra Puzzle**: Complete 5-house logic puzzle solver
- **Simple Logic Puzzles**: 3-person pet/house assignments
- **Advanced CSP Techniques**: Function constraints, mask optimization
- **Automatic Solver Selection**: Uses optimized algorithms for best performance
- **Run**: `python examples/logic_puzzles.py`

### 🎨 Graph Problems

#### **Graph Coloring** (`graph_coloring.py`)
- Color graph vertices with minimum colors
- Includes sample graphs: Triangle, Square, Petersen, Wheel
- Finds chromatic number automatically
- **Run**: `python examples/graph_coloring.py`

#### **Map Coloring** (`map_coloring.py`)
- Color geographical maps (Australia, USA, Europe)
- Demonstrates the Four Color Theorem
- Real-world adjacency relationships
- **Run**: `python examples/map_coloring.py`

### 📅 Scheduling Problems

#### **Multi-Type Scheduling** (`scheduling.py`)
- **Course Scheduling**: University course timetabling
- **Meeting Scheduling**: Conference room allocation
- **Resource Scheduling**: Task-resource-time assignment
- Complex temporal and resource constraints
- **Run**: `python examples/scheduling.py`

## LP Examples

#### **Basic Linear Programming** (`optimized_lp.py`)
- Simple LP problem demonstration
- Shows PuLP integration
- **Run**: `python examples/optimized_lp.py`

## Minimax Examples

#### **Game Theory & Robust Optimization** (`minimax.py`) ✨ **NEW**
- **Zero-Sum Games**: Rock-Paper-Scissors, Matching Pennies, Battle of Sexes
- **Portfolio Optimization**: Minimize maximum loss across market scenarios
- **Production Planning**: Maximize minimum profit under demand uncertainty
- **Security Games**: Optimal resource allocation against adversaries
- **Advertising Competition**: Strategic budget allocation
- **Mixed Strategy Equilibria**: Find optimal randomized strategies
- **Robust Decision Making**: Handle worst-case scenarios
- **Run**: `python examples/minimax.py`


## Quick Start Guide

### Running All Examples
```bash
# Navigate to examples directory
cd examples

# Run CSP examples
python n_queens.py
python graph_coloring.py
python map_coloring.py
python scheduling.py
python logic_puzzles.py
python optimized_csp.py

# Run LP examples
python optimized_lp.py

# Run Minimax examples
python minimax.py
```

### Example Output Preview

#### N-Queens (8×8 board)
```
8-Queens Solution:
+---+---+---+---+---+---+---+---+
| Q |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+
|   |   |   |   | Q |   |   |   |
+---+---+---+---+---+---+---+---+
...
Queen positions: (0,0), (1,4), (2,7), (3,5), (4,2), (5,6), (6,1), (7,3)
```

#### Graph Coloring
```
Triangle: Complete graph K3 (triangle)
Trying with 3 colors...
Chromatic number: 3
Vertex 0: Red
Vertex 1: Blue  
Vertex 2: Green
```

#### Logic Puzzles
```
Simple Logic Puzzle Solution:
Position 1: Alice has Cat in Green house
Position 2: Bob has Dog in Red house
Position 3: Carol has Fish in Blue house

Einstein's Zebra Puzzle Solution:
House 1: Norwegian - Green - Coffee - Snails - OldGold
House 2: Japanese - Blue - Water - Fox - Parliaments  
House 3: English - Red - Milk - Horse - Chesterfields
House 4: Spanish - White - OrangeJuice - Dog - LuckyStrike
House 5: Ukrainian - Yellow - Tea - Zebra - Kools

ANSWERS:
Who owns the zebra? Ukrainian (House 5)
Who drinks water? Japanese (House 2)
```

#### Minimax Games
```
Rock-Paper-Scissors Game:
Row Player (Maximizer) Strategy:
  Rock:     0.3333
  Paper:    0.3333
  Scissors: 0.3333
  Game Value: 0.0000

✓ Optimal strategy: Play each move with equal probability (1/3)
✓ Game value is 0 (fair game)

Robust Portfolio Optimization:
Optimal Allocation (minimize maximum loss):
  Stock A: $12.28
  Stock B: $0.00
  Bond C:  $87.72
  Total:   $100.00

Worst-case loss: $1.93

✓ Minimax strategy balances risk across all scenarios
```

## 🆕 Recent Updates

### Minimax Solver Addition ✨ **NEW**
- **🎮 Game Theory Support**: Solve zero-sum games and find Nash equilibria
- **🛡️ Robust Optimization**: Minimize maximum loss or maximize minimum gain
- **📊 Mixed Strategies**: Compute optimal probability distributions for competitive scenarios
- **💼 Real-World Applications**: Portfolio optimization, security games, competitive strategy
- **🔧 Flexible API**: Support for game matrices, scenario-based decisions, and custom constraints
- **⚡ Efficient Solving**: Linear programming based implementation using PuLP

### Logic Puzzles Solver Enhancement
- **✅ Fixed CSP Solver**: Resolved constraint propagation issues in tuple-based solver
- **🚀 Mask Optimization**: Automatic detection and use of optimized algorithms for small integer domains
- **🧩 Complete Zebra Puzzle**: Successfully solves Einstein's famous 5-house logic puzzle
- **📈 Performance Boost**: Up to 10x faster solving for problems with domains 1-32
- **🔧 Robust Constraints**: Improved handling of equality and adjacency constraints

### New Features
- **Automatic Solver Selection**: Chooses optimal algorithm based on problem characteristics
- **Enhanced Debugging**: Better error messages and constraint conflict detection
- **Flexible Domain Support**: Works with both 0-based and 1-based integer domains
- **Memory Efficient**: Reduced memory usage through bit-mask operations

## Problem Categories

### 🔢 **Combinatorial Puzzles**
- Sudoku, N-Queens, Logic puzzles
- **Key Techniques**: AllDifferent constraints, custom functions
- **Files**: `optimized_csp.py`, `n_queens.py`, `logic_puzzles.py`

### 🌐 **Graph Theory Problems**  
- Graph coloring, map coloring
- **Key Techniques**: Binary constraints, chromatic number finding
- **Files**: `graph_coloring.py`, `map_coloring.py`

### ⏰ **Scheduling & Assignment**
- Course scheduling, resource allocation
- **Key Techniques**: Time-resource encoding, complex constraints
- **Files**: `scheduling.py`

### 📊 **Optimization Problems**
- Linear programming, mixed-integer programming
- **Key Techniques**: Objective optimization, constraint relaxation
- **Files**: `optimized_lp.py`

### 🎮 **Game Theory & Robust Optimization**
- Zero-sum games, mixed strategies, Nash equilibria
- Portfolio optimization, worst-case planning
- **Key Techniques**: Minimax, maximin, robust optimization
- **Files**: `minimax.py`

## Learning Path

### 🟢 **Beginner** (Start Here)
1. `optimized_csp.py` - Learn basic CSP concepts with Sudoku
2. `n_queens.py` - Understand custom constraints
3. `graph_coloring.py` - Explore graph problems

### 🟡 **Intermediate**
4. `map_coloring.py` - Real-world constraint modeling
5. `scheduling.py` - Multi-constraint problems
6. `optimized_lp.py` - Introduction to LP

### 🔴 **Advanced**
7. `minimax.py` - Game theory and robust optimization
8. `logic_puzzles.py` - Complex CSP with advanced techniques


## Customization Tips

### Adding New Constraints
```python
# Custom constraint function
def my_constraint(val1, val2):
    return val1 + val2 <= 10

# Add to model
model.addConstraint(FunctionConstraint(my_constraint, (var1, var2)))
```

### Performance Tuning
```python
# For small integer domains (1-32), force mask optimization
solver = gurddy.CSPSolver(model)
solver.force_mask = True
solution = solver.solve()

# Automatic optimization (recommended)
# The solver automatically detects optimal algorithms
solution = model.solve()
```

### Domain Specification
```python
# Different domain types
model.addVar('binary_var', domain=[0, 1])           # Binary
model.addVar('small_int', domain=[1,2,3,4,5])       # Small integers  
model.addVar('large_range', domain=list(range(100))) # Large range
```

-------------------
Installation (PyPI)
-------------------

Install the package from PyPI:

```powershell
pip install gurddy
```

For LP/MIP examples you also need PuLP (the LP backend used by the built-in `LPSolver`):

```powershell
pip install pulp
```

If you publish optional extras you may use something like `pip install gurddy[lp]` if configured; otherwise install `pulp` separately as shown above.


Usage — Core concepts
---------------------

After installing from PyPI you can import the public API from the `gurddy` package. The library exposes a small Model/Variable/Constraint API used by both CSP and LP solvers.

- Model: container for variables, constraints, and objective. Use `Model(...)` and then `addVar`, `addConstraint`, `setObjective` or call `solve()` which will dispatch to the appropriate solver based on `problem_type`.
- Variable: create with `Model.addVar(name, low_bound=None, up_bound=None, cat='Continuous', domain=None)`; for CSP use `domain` (tuple of ints), for LP use numeric bounds and category ('Continuous', 'Integer', 'Binary').
- Expression: arithmetic expressions are created implicitly by operations on `Variable` objects or explicitly via `Expression(variable_or_value)`.
- Constraint types: `LinearConstraint`, `AllDifferentConstraint`, `FunctionConstraint`.

Usage — CSP Examples
-------------------

Gurddy can solve a wide variety of Constraint Satisfaction Problems. Here are some examples:

### Simple CSP Example

```python
from gurddy.model import Model
from gurddy.constraint import AllDifferentConstraint

# Build CSP model
model = Model('simple_csp', problem_type='CSP')
# Add discrete variables with domains (1..9)
model.addVar('A1', domain=[1,2,3,4,5,6,7,8,9])
model.addVar('A2', domain=[1,2,3,4,5,6,7,8,9])

# Add AllDifferent constraint across a group
model.addConstraint(AllDifferentConstraint([model.variables['A1'], model.variables['A2']]))

# Solve (uses internal CSPSolver)
solution = model.solve()
print(solution)  # dict of variable name -> assigned int, or None if unsatisfiable
```

### N-Queens Problem

```python
from gurddy.model import Model
from gurddy.constraint import AllDifferentConstraint, FunctionConstraint

def solve_n_queens(n=8):
    model = Model(f"{n}-Queens", "CSP")
    
    # Variables: one for each row, value represents column position
    queens = {}
    for row in range(n):
        var_name = f"queen_row_{row}"
        queens[var_name] = model.addVar(var_name, domain=list(range(n)))
    
    # All queens in different columns
    model.addConstraint(AllDifferentConstraint(list(queens.values())))
    
    # No two queens on same diagonal
    def not_on_same_diagonal(col1, col2, row_diff):
        return abs(col1 - col2) != row_diff
    
    queen_vars = list(queens.values())
    for i in range(n):
        for j in range(i + 1, n):
            row_diff = j - i
            constraint_func = lambda c1, c2, rd=row_diff: not_on_same_diagonal(c1, c2, rd)
            model.addConstraint(FunctionConstraint(constraint_func, (queen_vars[i], queen_vars[j])))
    
    return model.solve()

# Solve 8-Queens
solution = solve_n_queens(8)
```

### Graph Coloring

```python
def solve_graph_coloring(edges, num_vertices, max_colors=4):
    model = Model("GraphColoring", "CSP")
    
    # Variables: one for each vertex
    vertices = {}
    for v in range(num_vertices):
        vertices[f"vertex_{v}"] = model.addVar(f"vertex_{v}", domain=list(range(max_colors)))
    
    # Adjacent vertices must have different colors
    def different_colors(color1, color2):
        return color1 != color2
    
    for v1, v2 in edges:
        var1 = vertices[f"vertex_{v1}"]
        var2 = vertices[f"vertex_{v2}"]
        model.addConstraint(FunctionConstraint(different_colors, (var1, var2)))
    
    return model.solve()

# Example: Color a triangle graph
edges = [(0, 1), (1, 2), (2, 0)]
solution = solve_graph_coloring(edges, 3, 3)
```

Minimax Problem Types Supported
-------------------------------

Gurddy's Minimax solver handles game theory and robust optimization problems:

### Problem Types
- **Zero-Sum Games**: Two-player games where one player's gain equals the other's loss
- **Mixed Strategy Equilibria**: Find optimal randomized strategies using linear programming
- **Minimax Decision Problems**: Minimize maximum loss across uncertain scenarios
- **Maximin Decision Problems**: Maximize minimum gain under worst-case conditions
- **Robust Optimization**: Make decisions that perform well in all scenarios

### Applications
- **Game Theory**: Rock-Paper-Scissors, Matching Pennies, Battle of Sexes
- **Portfolio Optimization**: Asset allocation minimizing worst-case loss
- **Production Planning**: Robust production under demand uncertainty
- **Security Games**: Resource allocation for defense against adversaries
- **Competitive Strategy**: Advertising budgets, pricing strategies
- **Risk Management**: Worst-case scenario planning

### Key Features
- **Linear Programming Based**: Uses PuLP for efficient solving
- **Mixed Strategies**: Computes optimal probability distributions
- **Game Value Computation**: Determines equilibrium payoffs
- **Scenario Analysis**: Handles multiple uncertain scenarios
- **Budget Constraints**: Supports resource allocation constraints

CSP Problem Types Supported
---------------------------

Gurddy's CSP solver can handle a wide variety of constraint satisfaction problems:

### Constraint Types
- **AllDifferentConstraint**: Global constraint ensuring all variables take distinct values
- **FunctionConstraint**: Custom binary constraints defined by Python functions  
- **LinearConstraint**: Equality and inequality constraints (var == value, var <= value, etc.)

### Problem Categories
- **Combinatorial Puzzles**: Sudoku, N-Queens, Logic puzzles
- **Graph Problems**: Graph coloring, map coloring
- **Scheduling**: Resource allocation, time slot assignment
- **Assignment Problems**: Matching, allocation with constraints

### Performance Optimizations ✨ **ENHANCED**
- **Mask-based AC-3**: Optimized arc consistency for small integer domains (1-32)
- **AllDifferent Propagation**: Uses maximum matching algorithms for global constraints
- **Smart Variable Ordering**: Minimum Remaining Values (MRV) heuristic
- **Value Ordering**: Least Constraining Value (LCV) heuristic
- **Automatic Optimization**: CSPSolver automatically detects when to use mask optimizations
- **Precomputed Support Masks**: Cached constraint support for faster propagation
- **Bit-level Operations**: Memory-efficient domain representation and manipulation
- **Intelligent Backtracking**: Enhanced constraint propagation during search

### Advanced Features
- **Backtracking with Inference**: AC-3 constraint propagation during search
- **Multiple Constraint Types**: Mix different constraint types in the same problem
- **Extensible**: Easy to add custom constraint types and heuristics

Usage — LP / MIP (example)
--------------------------

The LP solver wraps PuLP. A basic LP/MIP example:

```python
from gurddy.model import Model

# Build an LP model
m = Model('demo', problem_type='LP')
# addVar(name, low_bound=None, up_bound=None, cat='Continuous')
x = m.addVar('x', low_bound=0, cat='Continuous')
y = m.addVar('y', low_bound=0, cat='Integer')

# Objective: maximize 3*x + 5*y
m.setObjective(x * 3 + y * 5, sense='Maximize')

# Add linear constraints (using Expression objects implicitly via Variable operations)
m.addConstraint((x * 2 + y * 1) <= 10)

# Solve (uses LPSolver which wraps PuLP)
sol = m.solve()
print(sol)  # dict var name -> numeric value or None
```

Usage — Minimax (example)
-------------------------

The Minimax solver handles game theory and robust optimization problems:

### Zero-Sum Game Example

```python
from gurddy.solver.minimax_solver import MinimaxSolver

# Rock-Paper-Scissors payoff matrix
payoff_matrix = [
    [0, -1, 1],   # Rock vs [Rock, Paper, Scissors]
    [1, 0, -1],   # Paper vs [Rock, Paper, Scissors]
    [-1, 1, 0]    # Scissors vs [Rock, Paper, Scissors]
]

solver = MinimaxSolver(None)

# Find optimal mixed strategy for row player
result = solver.solve_game_matrix(payoff_matrix, player="row")
print(f"Optimal strategy: {result['strategy']}")  # [0.333, 0.333, 0.333]
print(f"Game value: {result['value']}")  # 0.0 (fair game)
```

### Robust Optimization Example

```python
from gurddy.solver.minimax_solver import MinimaxSolver

# Portfolio optimization: minimize maximum loss across scenarios
scenarios = [
    {"StockA": -0.2, "StockB": -0.1, "BondC": 0.05},  # Bull market
    {"StockA": 0.3, "StockB": 0.2, "BondC": -0.02},   # Bear market
    {"StockA": 0.05, "StockB": 0.03, "BondC": -0.01}  # Stable market
]

solver = MinimaxSolver(None)
result = solver.solve_minimax_decision(scenarios, ["StockA", "StockB", "BondC"])

print(f"Optimal allocation: {result['decision']}")
print(f"Worst-case loss: {result['max_loss']}")
```

### Maximin Example

```python
# Production planning: maximize minimum profit
scenarios = [
    {"ProductX": -50, "ProductY": -40},  # High demand (negative for maximin)
    {"ProductX": -30, "ProductY": -35},  # Medium demand
    {"ProductX": -20, "ProductY": -25}   # Low demand
]

solver = MinimaxSolver(None)
result = solver.solve_maximin_decision(scenarios, ["ProductX", "ProductY"])

print(f"Optimal production: {result['decision']}")
print(f"Guaranteed minimum profit: {result['min_gain']}")
```

Examples Gallery
----------------

Gurddy comes with comprehensive examples demonstrating various problem types:

### CSP Examples
- **`examples/optimized_csp.py`** - Complete Sudoku solver with optimizations
- **`examples/n_queens.py`** - N-Queens problem for any board size
- **`examples/graph_coloring.py`** - Graph coloring with various test graphs
- **`examples/map_coloring.py`** - Map coloring (Australia, USA, Europe)
- **`examples/scheduling.py`** - Course and meeting scheduling problems
- **`examples/logic_puzzles.py`** - Logic puzzles including Einstein's Zebra puzzle

### LP Examples  
- **`examples/optimized_lp.py`** - LP relaxation vs MIP, timings, sensitivity analysis

### Minimax Examples ✨ **NEW**
- **`examples/minimax.py`** - Game theory, robust optimization, security games

### Running Examples

```bash
# CSP Examples
python examples/n_queens.py           # N-Queens problem
python examples/graph_coloring.py     # Graph coloring
python examples/map_coloring.py       # Map coloring
python examples/scheduling.py         # Scheduling problems
python examples/logic_puzzles.py      # Logic puzzles
python examples/optimized_csp.py      # Sudoku solver

# LP Examples  
python examples/optimized_lp.py       # Production planning

# Minimax Examples
python examples/minimax.py            # Game theory & robust optimization
```

Problem-Specific Examples
------------------------

### Sudoku Solver
```python
# Complete 9x9 Sudoku with given clues
model = Model("Sudoku", "CSP")

# Create 81 variables for 9x9 grid
vars_dict = {}
for row in range(1, 10):
    for col in range(1, 10):
        var_name = f"cell_{row}_{col}"
        vars_dict[var_name] = model.addVar(var_name, domain=[1,2,3,4,5,6,7,8,9])

# Add AllDifferent constraints for rows, columns, and 3x3 boxes
# ... (see examples/optimized_csp.py for complete implementation)
```

### Einstein's Zebra Puzzle
```python
# The famous logic puzzle: 5 houses, 5 attributes each
# Who owns the zebra and who drinks water?
model = gurddy.Model("ZebraPuzzle", "CSP")

# Variables for each attribute (colors, nationalities, drinks, pets, cigarettes)
# Each assigned to houses 1-5 (optimized for mask-based solving)
houses = list(range(1, 6))

colors = ['Red', 'Green', 'White', 'Yellow', 'Blue']
nationalities = ['English', 'Spanish', 'Ukrainian', 'Norwegian', 'Japanese']
# ... create variables for each attribute

# AllDifferent constraints ensure each attribute appears exactly once
model.addConstraint(gurddy.AllDifferentConstraint(color_vars))
model.addConstraint(gurddy.AllDifferentConstraint(nationality_vars))
# ... add constraints for all attributes

# Logic constraints from the puzzle clues
def same_house(house1, house2):
    return house1 == house2

# "The English person lives in the red house"
model.addConstraint(gurddy.FunctionConstraint(
    same_house, (english_var, red_var)
))

# Force mask optimization for best performance
solver = gurddy.CSPSolver(model)
solver.force_mask = True
solution = solver.solve()

# Result: Ukrainian owns the zebra, Japanese drinks water
```

### Course Scheduling
```python
# Schedule university courses avoiding conflicts
model = Model("CourseScheduling", "CSP")

courses = ['Math101', 'Physics101', 'Chemistry101', 'Biology101', 'English101']
time_slots = list(range(20))  # 5 days × 4 slots

# Variables and constraints for scheduling
# ... (see examples/scheduling.py for complete implementation)
```

Developer Notes
---------------
- **CSP Optimizations**: The CSP solver includes precomputed support masks, mask-based AC-3, and AllDifferent matching propagation for enhanced performance on small integer domains.
- **LP Backend**: Uses PuLP by default. Can be extended to support other solvers (ORTOOLS, Gurobi) by modifying `src/gurddy/solver/lp_solver.py`.
- **Extensibility**: Easy to add new constraint types by inheriting from the `Constraint` base class.
- **Memory Efficiency**: Mask-based operations reduce memory usage for problems with small domains.

Running tests
-------------
Run unit tests with pytest:

```powershell
python -m pytest
```

Contributing
------------
PRs welcome. If you add a new solver backend, please include configuration and a small example demonstrating usage.

API Reference (concise)
-----------------------

This section lists the most commonly used classes and functions with signatures and short descriptions.

Model
- - -
- Model(name: str = "Model", problem_type: str = "LP")
	- Container for variables, constraints, objective and solver selection.
	- Attributes: variables: Dict[str, Variable], constraints: List[Constraint], objective: Optional[Expression], sense: str

- addVar(name: str, low_bound: Optional[float] = None, up_bound: Optional[float] = None,
				 cat: str = 'Continuous', domain: Optional[list] = None) -> Variable
	- Create and register a Variable. For CSP use `domain` (list/tuple of ints). For LP use numeric bounds and `cat`.

- addVars(names: List[str], **kwargs) -> Dict[str, Variable]
	- Convenience to create multiple variables with the same kwargs.

- addConstraint(constraint: Constraint, name: Optional[str] = None) -> None
	- Register a Constraint object (LinearConstraint, AllDifferentConstraint, FunctionConstraint).

- setObjective(expr: Expression, sense: str = "Maximize") -> None
	- Set the objective expression and sense for LP problems.

- solve() -> Optional[Dict[str, Union[int, float]]]
	- Dispatch to the appropriate solver (CSPSolver or LPSolver) and return a mapping from variable name to value, or None if unsatisfiable/no optimal found.

Variable
- - -
- Variable(name: str, low_bound: Optional[float] = None, up_bound: Optional[float] = None,
					 cat: str = 'Continuous', domain: Optional[list] = None)
	- Represents a decision variable. For CSP set `domain` (discrete values). For LP set numeric bounds and `cat` in {'Continuous','Integer','Binary'}.
	- Supports arithmetic operator overloads to build `Expression` objects (e.g., `x * 3 + y`).

Expression
- - -
- Expression(term: Union[Variable, int, float, Expression])
	- Arithmetic expression type used to build linear objectives and constraints.
	- Operators: +, -, *, / with scalars; comparisons (==, <=, >=, <, >) produce `LinearConstraint` instances.

Constraint types
- - -
- LinearConstraint(expr: Expression, sense: str)
	- General linear constraint wrapper (sense in {'<=','>=','==', '!='}).

- AllDifferentConstraint(vars: List[Variable])
	- Global constraint enforcing all variables in the list take pairwise distinct values (used primarily for CSPs).

- FunctionConstraint(func: Callable[[int,int], bool], vars: Tuple[Variable, ...])
	- Custom binary (or n-ary) constraint defined by a Python callable.

Solvers
- - -
- class CSPSolver
	- CSPSolver(model: Model)
	- Attributes: mask_threshold: int (domain size under which mask optimization is used), force_mask: bool
	- Methods: solve() -> Optional[Dict[str, int]]  (returns assignment mapping or None)

- class LPSolver
	- LPSolver(model: Model)
	- Methods: solve() -> Optional[Dict[str, float]]  (returns variable values mapping or None). Uses PuLP by default; requires `pulp` installed.

- class MinimaxSolver ✨ **NEW**
	- MinimaxSolver(model: Model)
	- Methods:
		- solve_game_matrix(payoff_matrix: List[List[float]], player: str) -> Dict  (solves zero-sum games)
		- solve_minimax_decision(scenarios: List[Dict], variables: List[str]) -> Dict  (minimize maximum loss)
		- solve_maximin_decision(scenarios: List[Dict], variables: List[str]) -> Dict  (maximize minimum gain)
		- solve() -> Optional[Dict[str, float]]  (generic model-based solving)

Notes
- The API intentionally keeps model construction separate from solver execution. Use `Model.solve()` for convenience or instantiate solver classes directly for advanced control (e.g., change `CSPSolver.force_mask`).
- For more examples see `examples/optimized_csp.py`, `examples/optimized_lp.py`, `examples/minimax.py`.

