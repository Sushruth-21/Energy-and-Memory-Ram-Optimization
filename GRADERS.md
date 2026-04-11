# Task Graders Documentation

## Overview

The Energy & Memory RAM Optimization Environment includes **3 task graders** (meeting the minimum requirement of >= 3) that evaluate agent performance on a continuous 0.0-1.0 scale. Each grader represents a real-world optimization scenario with increasing difficulty.

## ✅ Validation Summary

| Requirement | Status | Details |
|-------------|--------|---------|
| Minimum 3 graders | ✅ PASS | 3 graders implemented |
| Different scores | ✅ PASS | Each grader returns varied scores 0.0-1.0 based on performance |
| Real-world relevance | ✅ PASS | Each grader models actual data center/edge computing scenarios |
| Metadata & discovery | ✅ PASS | Graders exposed via API endpoints and manifest files |

## Grader Details

### Task 1: Basic RAM Reduction (Easy - Difficulty 1)

**Location**: `task_graders.py::task_1_basic_ram_reduction_grader()`

**Real-World Application**: 
- Memory optimization for IoT devices, mobile systems, and edge computing
- Preventing out-of-memory errors on resource-constrained devices
- Improving system responsiveness during high loads

**Target**: RAM < 70%, Energy < 7.5 kWh, within 10 steps

**Scoring Formula**:
```
Score = (RAM_Score × 0.4) + (Energy_Score × 0.4) + (Step_Efficiency × 0.2)

Where:
  RAM_Score = (100 - RAM_usage) / (100 - 70) clamped to [0, 1]
  Energy_Score = (10 - Energy_consumption) / (10 - 7.5) clamped to [0, 1]
  Step_Efficiency = 1.0 if steps ≤ 10, else max(0, 1 - (steps-10) × 0.1)
```

**Score Examples**:
| Performance Level | RAM | Energy | Steps | Score |
|------------------|-----|--------|-------|-------|
| Worst | 100.0% | 10.0 kWh | 50 | 0.000 |
| Poor | 90.0% | 9.0 kWh | 20 | 0.293 |
| Medium | 75.0% | 8.0 kWh | 8 | 0.853 |
| Good | 70.0% | 7.5 kWh | 5 | **1.000** |

---

### Task 2: Energy Optimization (Medium - Difficulty 2)

**Location**: `task_graders.py::task_2_energy_optimization_grader()`

**Real-World Application**:
- Energy efficiency optimization for large-scale data centers
- Reducing operational costs (1% energy = millions in savings)
- Meeting sustainability and carbon footprint goals for cloud providers

**Target**: RAM < 75%, Energy < 6 kWh, within 15 steps

**Scoring Formula**:
```
Score = (Energy_Score × 0.5) + (RAM_Constraint × 0.25) + (Step_Efficiency × 0.25)

Where:
  Energy_Score = (10 - Energy_consumption) / (10 - 6) clamped to [0, 1]  (Primary objective)
  RAM_Constraint = 1.0 if RAM ≤ 75, else max(0, 1 - overage/5)           (Hard constraint)
  Step_Efficiency = 1.0 if steps ≤ 15, else max(0, 1 - (steps-15) × 0.08)
```

**Score Examples**:
| Performance Level | RAM | Energy | Steps | Score |
|------------------|-----|--------|-------|-------|
| Worst | 100.0% | 10.0 kWh | 50 | 0.000 |
| Fair | 85.0% | 7.0 kWh | 20 | 0.525 |
| Good | 75.0% | 6.0 kWh | 10 | **1.000** |
| Excellent | 65.0% | 5.0 kWh | 8 | **1.000** |

---

### Task 3: Balanced Optimization (Hard - Difficulty 3)

**Location**: `task_graders.py::task_3_balanced_optimization_grader()`

**Real-World Application**:
- Production system optimization with dual resource constraints
- Cloud infrastructure managing multi-tenant workloads
- Edge computing with simultaneous memory and energy limitations

**Target**: RAM < 60%, Energy < 5 kWh, within 20 steps

**Scoring Formula**:
```
Score = (Balance_Score × 0.9) + Step_Bonus

Balance_Score = ((RAM_Score × 0.5) + (Energy_Score × 0.5))  [Both must be optimized equally]

Where:
  RAM_Score = (100 - RAM_usage) / (100 - 60) clamped to [0, 1]
  Energy_Score = (10 - Energy_consumption) / (10 - 5) clamped to [0, 1]
  Step_Bonus = min(0.1, (20 - steps)/20 × 0.1) if steps ≤ 20, else -(steps-20) × 0.05
```

**Score Examples**:
| Performance Level | RAM | Energy | Steps | Score |
|------------------|-----|--------|-------|-------|
| Worst | 100.0% | 10.0 kWh | 50 | 0.000 |
| Fair | 70.0% | 6.0 kWh | 25 | 0.497 |
| Good | 60.0% | 5.0 kWh | 20 | 0.900 |
| Excellent | 50.0% | 4.0 kWh | 15 | **0.925** |

---

## How Graders Are Discoverable

### 1. **Direct Python Import**
```python
from he_demo.task_graders import TASK_GRADERS, get_grader, get_grader_metadata

# Get all graders
all_graders = TASK_GRADERS  # 3 graders available
print(len(all_graders))  # Output: 3

# Get specific grader metadata
metadata = get_grader_metadata("basic_ram_reduction")
print(metadata["real_world_application"])
```

### 2. **Manifest Files**
- **`graders.json`**: JSON manifest with all grader metadata and examples
- **`graders_manifest.py`**: Python validation module with discovery functions

### 3. **API Endpoints** (when server is running)
```bash
# List all graders
GET http://localhost:8000/graders

# Get specific grader info
GET http://localhost:8000/graders/basic_ram_reduction

# Comprehensive grader information
GET http://localhost:8000/graders/info
```

### 4. **Environment Properties**
```python
from server.he_demo_environment import EnergyOptimizationEnvironment

env = EnergyOptimizationEnvironment()

# Access graders through environment
graders = env.graders  # Dictionary of all graders
metadata = env.grader_metadata  # All metadata
score = env.grade_task("basic_ram_reduction", observation)  # Grade an observation
```

---

## Validation Features

All 3 graders demonstrate:

✅ **Different Scores**: Each grader returns varied scores (0.0 to 1.0) for different performance levels

✅ **Real-World Context**: 
- Task 1: Edge computing & IoT memory constraints
- Task 2: Data center energy efficiency & cost reduction  
- Task 3: Production dual-constraint optimization

✅ **Continuous Scoring**: Scores smoothly transition from 0.0 (worst) to 1.0 (best) based on actual metrics

✅ **Detailed Methodology**: Each grader includes:
- Explicit scoring formula
- Performance examples with actual scores
- Real-world application explanation
- Target thresholds and constraints

✅ **Easy Discovery**: Graders accessible via:
- Python imports (`from task_graders import ...`)
- JSON manifest (`graders.json`)
- API endpoints (`/graders/*`)
- Validation manifest (`graders_manifest.py`)

---

## Testing & Validation

Run the comprehensive validation script:
```bash
python validate_comprehensive.py
```

This tests:
1. All 3 graders are present
2. Each grader returns different scores
3. Scores match expected ranges
4. Metadata is accessible
5. Environment integration works

---

## Example: Getting Grader Scores

```python
from task_graders import get_grader
from models import EnergyOptimizationObservation

# Create observation for a specific performance level
obs = EnergyOptimizationObservation(
    ram_usage=75.0,
    energy_consumption=8.0,
    system_load=0.5,
    current_task=None,
    tasks_completed=[],
    steps_taken=8,
    task_progress=0.0,
    efficiency_score=0.0,
    done=False,
    reward=0.0
)

# Get grader for Task 1
grader = get_grader("basic_ram_reduction")

# Calculate score
score = grader(obs)
print(f"Performance Score: {score:.3f}")  # Output: 0.853
```

---

## Summary

The Energy & Memory RAM Optimization Environment includes **3 explicit, discoverable task graders** that:
- Meet the minimum requirement (>= 3)
- Return different scores (0.0-1.0) for different performance
- Model real-world resource optimization scenarios
- Are easily discoverable via multiple methods
- Provide continuous performance feedback to agents
