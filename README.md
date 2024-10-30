# Industrial Workforce Scheduler

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Theory and Algorithms](#theory-and-algorithms)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Visualization](#visualization)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

## Overview
The Industrial Workforce Scheduler is a Python-based optimization system designed for 24/7 industrial operations. It combines discrete event simulation with mathematical optimization to generate efficient staff schedules while considering various constraints such as skills, break times, and coverage requirements.

## Features
- **Schedule Optimization**
  - Fair rotation of shifts
  - Skill-based task assignment
  - Break time optimization
  - Coverage requirements satisfaction
  
- **Visualization & Analysis**
  - Interactive Gantt charts
  - Staff coverage heatmaps
  - Skill distribution analysis
  - Excel reports generation

- **Constraints Handling**
  - Maximum working hours per day/week
  - Required rest periods
  - Skill requirements
  - Minimum staffing levels

## Theory and Algorithms

## Mathematical Model

The scheduler uses Mixed Integer Linear Programming (MILP) to optimize the workforce schedule.

### Decision Variables

For each employee $e$ and time slot $t$:

$x_{e,t} = \begin{cases} 
1 & \text{if employee } e \text{ works at time } t \\
0 & \text{otherwise}
\end{cases}$

$b_{e,t} = \begin{cases}
1 & \text{if employee } e \text{ takes break at time } t \\
0 & \text{otherwise}
\end{cases}$

### Objective Function

Minimize total working hours while ensuring coverage:

$\min \sum_{e \in E} \sum_{t \in T} x_{e,t}$

### Constraints

1. **Daily Hours Limit**:
   For each employee $e$ and day $d$:
   
   $\sum_{t \in T_d} x_{e,t} \leq 8$ 
   
   where $T_d$ represents the time slots in day $d$

2. **Weekly Hours Limit**:
   For each employee $e$:
   
   $\sum_{t \in T_w} x_{e,t} \leq 40$
   
   where $T_w$ represents the time slots in a week

3. **Minimum Coverage Requirement**:
   For each time slot $t$:
   
   $\sum_{e \in E} x_{e,t} \geq 1$

4. **Rest Period**:
   For each employee $e$ and time $t$:
   
   $\sum_{k=t}^{t+11} x_{e,k} \leq 8$
   
   Ensures at least 12 hours rest in any 24-hour period

5. **Break Assignment**:
   For each employee $e$ and shift $s$:
   
   $\sum_{t \in T_s} b_{e,t} = 1$
   
   where $T_s$ represents the time slots in shift $s$

6. **Skill Coverage**:
   For each skill $k$ and time $t$:
   
   $\sum_{e \in E_k} x_{e,t} \geq c_k$
   
   where $E_k$ is the set of employees with skill $k$ and $c_k$ is the minimum coverage required for skill $k$

### Additional Constraints

7. **Break Continuity**:
   For each employee $e$ and time $t$:
   
   $b_{e,t} + b_{e,t+1} \leq 1$
   
   Prevents split breaks

8. **Work-Break Relationship**:
   For each employee $e$ and time $t$:
   
   $b_{e,t} \leq x_{e,t}$
   
   Breaks can only be assigned during working hours

### Sets and Parameters

- $E$: Set of all employees
- $T$: Set of all time slots
- $T_d$: Set of time slots in day $d$
- $T_w$: Set of time slots in week $w$
- $K$: Set of all skills
- $E_k$: Set of employees with skill $k$
- $c_k$: Minimum coverage requirement for skill $k$

### Solution Method

The problem is solved using the CBC (COIN-OR Branch and Cut) solver with the following approach:

1. **Preprocessing**:
   $P(x,b) = \{(x,b) \in \{0,1\}^{|E| \times |T|} : \text{constraints } 1-8\}$

2. **Branch and Bound**:
   Solve using branch and bound with cutting planes:
   
   $z^* = \min\{cx : x \in P(x,b)\}$

3. **Post-processing**:
   Handle any remaining soft constraints and generate break schedule:
   
   $f(x^*) = \text{argmin}_{b \in B} \|b - b^*\|$

### Discrete Event Simulation
The system uses SimPy for discrete event simulation to:
1. Model task arrivals
2. Handle dynamic resource allocation
3. Track employee availability
4. Manage break schedules

## Installation

### Using Conda (Recommended)
```bash
# Create new conda environment
conda create -n workforce python=3.10

# Activate environment
conda activate workforce

# Clone repository
git clone https://github.com/daggbt/industrial-workforce-scheduler.git
cd industrial-workforce-scheduler

# Install required packages
conda install -c conda-forge pyomo simpy pandas numpy matplotlib seaborn plotly xlsxwriter

# Install CBC solver
# For Ubuntu/Debian:
sudo apt-get install coinor-cbc

# For macOS:
brew install coin-or-tools/coinor/cbc

# For Windows:
# Download CBC binary from COIN-OR website
```

### Using pip
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```python
from simulator.workforce_simulator import WorkforceSimulator
from visualization.visualizer import ScheduleVisualizer

# Initialize simulator
env = simpy.Environment()
simulator = WorkforceSimulator(env)

# Add employees
simulator.add_employees_from_matrix(SKILLS_MATRIX)

# Generate schedule
simulator.generate_schedule()

# Visualize results
visualizer = ScheduleVisualizer(simulator)
visualizer.generate_all_visualizations()
```

### Running from Command Line
```bash
python main.py
```

### Customizing Parameters
Edit `config/settings.py` to modify:
- Simulation horizon
- Working hour limits
- Break durations
- Skill requirements
- Visualization preferences

## Project Structure
```
workforce_scheduler/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration parameters
├── models/
│   ├── __init__.py
│   └── entities.py          # Data models
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   └── helpers.py          # Utility functions
├── visualization/
│   ├── __init__.py
│   └── visualizer.py       # Visualization tools
├── simulator/
│   ├── __init__.py
│   └── workforce_simulator.py # Core simulation logic
├── main.py                 # Entry point
├── requirements.txt
└── README.md
```

## Configuration
The system can be configured through `config/settings.py`:

```python
SIMULATION_SETTINGS = {
    'horizon_days': 7,
    'max_hours_per_day': 8,
    'max_hours_per_week': 40,
    'min_rest_hours': 12,
    'min_staff_per_shift': 1
}

VISUALIZATION_SETTINGS = {
    'output_dir': 'schedule_output',
    'plot_width': 15,
    'plot_height': 6
}
```

## Visualization

### Generated Outputs
1. **Interactive Gantt Chart** (`schedule_gantt.html`)
   - Shows employee schedules
   - Break times
   - Skill allocations
   
2. **Coverage Heatmap** (`coverage_heatmap.png`)
   - Staff levels by hour and day
   - Color-coded coverage intensity
   
3. **Skill Distribution** (`skill_coverage.png`)
   - Skill availability over time
   - Coverage gaps analysis

4. **Excel Report** (`schedule_report.xlsx`)
   - Detailed schedule breakdown
   - Employee assignments
   - Coverage statistics

## Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## Troubleshooting

### Common Issues

1. **CBC Solver Not Found**
   ```bash
   sudo apt-get update
   sudo apt-get install coinor-cbc
   ```

2. **Infeasible Solution**
   - Check constraint values in settings.py
   - Ensure minimum staffing requirements are achievable
   - Verify skill matrix coverage

3. **Memory Issues**
   - Reduce simulation horizon
   - Decrease the number of employees
   - Optimize constraint matrix

## Technical Details

### Performance Optimization
The system employs several optimization techniques:
1. Constraint preprocessing
2. Progressive horizon optimization
3. Parallel task processing
4. Memory-efficient data structures

### Solver Configuration
The CBC solver can be tuned through parameters:
```python
solver.options['seconds'] = 300  # Time limit
solver.options['ratio'] = 0.1    # Gap tolerance
solver.options['cuts'] = 'on'    # Cut generation
```

### Output Formats
1. **Schedule Data**
   - JSON for raw data
   - Excel for reports
   - HTML for interactive visualizations
   - PNG for static plots

2. **Logs**
   - INFO: Basic operation logging
   - DEBUG: Detailed solver information
   - ERROR: Exception handling

### Dependencies
- Python ≥ 3.8
- Pyomo ≥ 6.7.0
- SimPy ≥ 4.0.1
- CBC Solver ≥ 2.10
- Pandas ≥ 2.0.0
- Numpy ≥ 1.24.0
- Matplotlib ≥ 3.7.0
- Plotly ≥ 5.18.0

