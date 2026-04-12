# Grader Configuration Guide

## Overview
This environment includes **5 task-specific graders** for the Energy & Memory RAM Optimization tasks.

## Available Graders

All graders are:
- ✅ Properly exported from `task_graders` module
- ✅ Callable functions that take `EnergyOptimizationObservation` and return float score (0.0-1.0)
- ✅ Registered in `TASK_GRADERS` dictionary
- ✅ Configured in `openenv.yaml`

### Grader List

| Task | Function | Difficulty | Min/Max Steps | Target RAM | Target Energy |
|------|----------|------------|---------------|-----------|---------------|
| Basic RAM Reduction | `task_1_basic_ram_reduction_grader` | 1 | 10 | < 70% | < 7.5 kWh |
| Energy Optimization | `task_2_energy_optimization_grader` | 2 | 15 | < 75% | < 6.0 kWh |
| Balanced Optimization | `task_3_balanced_optimization_grader` | 3 | 20 | < 60% | < 5.0 kWh |
| Advanced Efficiency | `task_4_advanced_efficiency_grader` | 4 | 25 | < 50% | < 4.0 kWh |
| Expert Optimization | `task_5_expert_optimization_grader` | 5 | 30 | < 40% | < 3.0 kWh |

## How to Access Graders

### Method 1: Direct Import
```python
from task_graders import (
    task_1_basic_ram_reduction_grader,
    task_2_energy_optimization_grader,
    task_3_balanced_optimization_grader,
    task_4_advanced_efficiency_grader,
    task_5_expert_optimization_grader,
)

# Use grader
obs = ...
score = task_1_basic_ram_reduction_grader(obs)
```

### Method 2: Via Registry
```python
from task_graders import get_grader, TASK_GRADERS

# Get specific grader
grader = get_grader("basic_ram_reduction")
score = grader(observation)

# Get all graders
all_graders = TASK_GRADERS  # Dict with grader functions
```

### Method 3: Via Task Registry
```python
from task_registry import get_task_grader, get_tasks_count

print(f"Total tasks: {get_tasks_count()}")  # 5
grader = get_task_grader("basic_ram_reduction")
```

### Method 4: String-based Import (OpenEnV Format)
```python
# Pattern used in openenv.yaml: module:function
module_name, func_name = "task_graders", "task_1_basic_ram_reduction_grader"
module = __import__(module_name)
grader = getattr(module, func_name)
score = grader(observation)
```

### Method 5: Via Server Endpoints (FastAPI)
```bash
# Get all graders metadata
GET http://localhost:8000/graders

# Get specific grader info
GET http://localhost:8000/graders/{task_name}

# Get grader manifest
GET http://localhost:8000/graders/manifest

# Get grader discovery info
GET http://localhost:8000/graders/discovery
```

## Validation

All graders are validated to:
- ✅ Return float scores in valid range (0.001 - 0.999)
- ✅ Accept `EnergyOptimizationObservation` objects
- ✅ Implement scoring logic based on RAM/energy targets
- ✅ Be callable and importable
- ✅ Meet hackathon requirement (≥3 graders required, we have 5)

## openenv.yaml Configuration

Tasks are configured with grader paths as:
```yaml
tasks:
  - name: basic_ram_reduction
    grader: task_graders:task_1_basic_ram_reduction_grader
    ...
```

The format `module:function_name` allows OpenEnV validator to:
1. Parse the reference
2. Import `task_graders` module
3. Get the function by name using `getattr()`
4. Verify it's callable
5. Register it as the grader for that task

## Verification Commands

```bash
# Test grader imports
python -c "from task_graders import *; print('✅ All imports OK')"

# Test grader callable
python -c "import task_graders; print(callable(task_graders.task_1_basic_ram_reduction_grader))"

# Test grader execution
python -c "
from task_graders import task_1_basic_ram_reduction_grader
from models import EnergyOptimizationObservation
obs = EnergyOptimizationObservation(ram_usage=80, energy_consumption=8, current_task='test', step=1, done=False)
score = task_1_basic_ram_reduction_grader(obs)
print(f'Score: {score}')
"

# Run full validation
python validate.py
```

## Requirements Met ✅

- Minimum 3 graders: ✅ **5 graders**
- Grader score range: ✅ **0.001-0.999**
- OpenEnV compatibility: ✅ **Verified**
- Multi-mode deployment: ✅ **Ready**
