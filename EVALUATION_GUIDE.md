# LLM Inference Evaluation Guide

## Overview

This project evaluates how well a Language Model (LLM) can interact with the Energy & Memory RAM Optimization environment to achieve reward signals.

---

## What Gets Evaluated

When you run the LLM inference, these components are judged:

### 1. **Action Quality**
- **What**: Whether the LLM produces valid actions in format: `action_type,intensity`
- **How**: Parser validates action_type ∈ ["reduce_ram", "optimize_energy", "balance_resources", "monitor_system"] and intensity ∈ [0.0, 1.0]
- **Grade**: Action validity rate (% of valid vs invalid actions)
- **Example Good**: `reduce_ram,0.8` (valid)
- **Example Bad**: `invalid_action,2.5` (invalid - gets converted to `monitor_system,0.5`)

### 2. **Reward Accumulation**
- **What**: Total reward achieved across all steps
- **How**: Each action generates reward = intensity × 0.1
  - Plus task completion bonus (difficulty × 0.5)
  - Clamped to 0-1 range
- **Grade Metrics**:
  - Total reward (sum of all step rewards)
  - Average reward per step
  - Reward trend (increasing/decreasing)
  - Max and min rewards achieved

### 3. **Resource Optimization**
- **What**: How much RAM and Energy the LLM actually reduced
- **How**: Compare initial vs final state
- **Grade Metrics**:
  - RAM reduction: Initial 80% → Final X%
  - Energy reduction: Initial 8.0 kWh → Final X kWh
  - Efficiency: Resources saved ÷ Steps taken

### 4. **Task Completion**
- **What**: Whether the LLM completed the assigned task
- **How**: Environment checks if current state meets task targets within max_steps
- **Example Task**: Task 1 (basic_ram_reduction)
  - Target: RAM < 70%, Energy < 7.5 kWh
  - Deadline: 10 steps max
  - Success: If both targets met within 10 steps → Reward bonus + task marked complete

### 5. **Grader Score (0.001 - 0.999)**
- **What**: Task-specific evaluation score from the grader
- **How**: Grader function evaluates final observation against task targets
- **Formula Example** (Task 1):
  ```
  RAM score = (100 - final_RAM) / (100 - 70)  [0-1]
  Energy score = (10 - final_energy) / (10 - 7.5)  [0-1]
  Efficiency = bonus for steps taken within limit
  Final = (RAM_score × 0.4) + (Energy_score × 0.4) + (Efficiency × 0.2)
  Clamped to [0.001, 0.999]
  ```

### 6. **Decision-Making Efficiency**
- **What**: How quickly and thoughtfully the LLM makes good decisions
- **How**: Track history of actions and rewards
- **Grade Metrics**:
  - Time-to-first-good-action
  - Convergence speed (steps to reach target)
  - Backtracking frequency (bad decision reversals)
  - Adaptive behavior (does agent improve over time?)

---

## Understanding the Tasks & Difficulty

Each task has explicit graders that measure performance:

| Task | Difficulty | RAM Target | Energy Target | Max Steps | Grader Name |
|------|-----------|-----------|---------------|-----------|------------|
| basic_ram_reduction | 1 | < 70% | < 7.5 kWh | 10 | task_1_basic_ram_reduction_grader |
| energy_optimization | 2 | < 75% | < 6.0 kWh | 15 | task_2_energy_optimization_grader |
| balanced_optimization | 3 | < 60% | < 5.0 kWh | 20 | task_3_balanced_optimization_grader |
| advanced_efficiency | 4 | < 50% | < 4.0 kWh | 25 | task_4_advanced_efficiency_grader |
| expert_optimization | 5 | < 40% | < 3.0 kWh | 30 | task_5_expert_optimization_grader |

---

## How to Run Evaluation

### Step 1: Start the Environment Server
```bash
cd d:\Projects\Pytorch\ x\ hugging\ face\he_demo
python -m uvicorn he_demo.server.app:app --host 0.0.0.0 --port 8000
```

### Step 2A: Quick Baseline Test
Run the heuristic agent to establish a baseline:
```bash
python evaluate_inference.py
```

**Output you'll see:**
```
BASELINE TEST: Random Actions
Initial RAM: 80.0%, Energy: 8.0 kWh

Step 1: optimize_energy, Intensity: 0.65      | Reward: +0.065 | RAM: 80.0% | Energy:  6.7 kWh
Step 2: balance_resources, Intensity: 0.42    | Reward: +0.042 | RAM: 77.9% | Energy:  6.3 kWh
...
Baseline Total Reward: 0.341
Baseline Avg Reward: 0.068
```

### Step 2B: Run Full LLM Evaluation
```bash
# Set your LLM credentials
$env:HF_TOKEN = "your_hf_token_here"
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"  # or your preferred model

# Run inference on Task 1
$env:ENERGY_TASK = "basic_ram_reduction"
python inference.py
```

**Output you'll see:**
```
[CONFIG] Task-specific grader configured: task=basic_ram_reduction difficulty=1 description='Reduce RAM usage below 70%'

Step 1: LLM chooses → reduce_ram,0.7
  Reward: +0.070
  RAM: 80% → 73%
  Energy: 8.0 kWh

Step 2: LLM chooses → reduce_ram,0.6
  Reward: +0.060
  RAM: 73% → 67.0%
  Energy: 8.0 kWh

Step 3: LLM chooses → monitor_system,0.5
  Reward: +0.050
  RAM: 67% (already optimized)
  Energy: 8.0 kWh

[Task Completed!]
Task Completion Bonus: +0.5 reward

GRADER EVALUATION:
  Task: basic_ram_reduction
  Final State: RAM=67.0%, Energy=8.0kWh, Steps=3/10
  Grader Score: 0.782 ✓

EPISODE SUMMARY:
  Total Reward: 0.680
  Average Reward/Step: 0.227
  Task Completed: YES
  Grader Score: 0.782
```

---

## Evaluating Model Performance

### Quality Levels (by Grader Score)

| Score Range | Rating | Interpretation |
|------------|--------|----------------|
| 0.9 - 0.999 | ★★★★★ EXCELLENT | Model solved task optimally, excellent resource optimization |
| 0.7 - 0.9 | ★★★★ GOOD | Model completed task efficiently, minor suboptimality |
| 0.5 - 0.7 | ★★★ FAIR | Model made good progress, some inefficiency |
| 0.3 - 0.5 | ★★ POOR | Model struggled, significant suboptimality |
| 0.001 - 0.3 | ★ VERY POOR | Model barely optimized or failed task |

### Expected Performance Baselines

Based on environment design:

**Random Agent:**
- Avg Reward: ~0.05 per step
- Task Completion: ~10% chance
- Grader Score: ~0.2-0.3
- Insight: No structure, just luck

**Heuristic Agent** (simple if-else rules):
- Avg Reward: ~0.1 per step
- Task Completion: ~60% chance (easy tasks only)
- Grader Score: ~0.5-0.6
- Insight: Follows simple logic, decent for easy tasks

**Competent LLM Agent** (Qwen, GPT, etc.):
- Avg Reward: ~0.12-0.15 per step
- Task Completion: ~70-80% (easy-medium tasks)
- Grader Score: ~0.65-0.80
- Insight: Understands environment, makes reasonable decisions

**Expert LLM Agent** (with few-shot examples):
- Avg Reward: ~0.16-0.20 per step
- Task Completion: ~85-95% (even hard tasks)
- Grader Score: ~0.80-0.95
- Insight: Optimized strategy, efficient resource management

---

## Detailed Metrics Collected

The `evaluate_inference.py` script tracks:

```python
{
    "task_name": "basic_ram_reduction",
    "difficulty": 1,
    "total_steps": 5,
    "total_reward": 0.482,           # Sum of all step rewards
    "avg_reward": 0.0964,             # Average per step
    "reward_range": [0.05, 0.12],    # Min to max reward
    "valid_actions": 5,               # Actions that parsed correctly
    "invalid_actions": 0,             # Actions that failed parsing
    "action_validity_rate": 1.0,      # % of valid actions
    "initial_ram": 80.0,
    "final_ram": 50.0,                # Resource improvement
    "initial_energy": 8.0,
    "final_energy": 4.5,              # Resource improvement
    "task_completed": True,            # Did it hit targets?
    "final_task_progress": 1.0,       # 0.0 = no progress, 1.0 = complete
    "grader_score": 0.782             # Task-specific grader evaluation
}
```

---

## What Makes a Good LLM Agent

1. **Prompt Understanding**: Parses the observation correctly
2. **Action Validity**: Produces valid actions in correct format
3. **Resource Awareness**: Tracks RAM/Energy trade-offs
4. **Goal Orientation**: Works toward task targets, not random
5. **Efficiency**: Achieves targets in fewer steps when possible
6. **Adaptability**: Adjusts strategy if initial approach fails

---

## How Task Graders Work

Each task has a **task_N_..._grader()** function that:

1. Takes the final observation
2. Calculates how close you are to targets
3. Considers step efficiency
4. Returns score in [0.001, 0.999]

**Example: Task 1 Grader Logic**

```python
def task_1_basic_ram_reduction_grader(observation):
    # RAM reduction from baseline 80% to target < 70%
    ram_score = (100 - observation.ram_usage) / (100 - 70)  # 0=bad, 1=good
    
    # Energy reduction from baseline 8.0 to target < 7.5
    energy_score = (10 - observation.energy_consumption) / (10 - 7.5)
    
    # Step efficiency (bonus for using few steps)
    if observation.steps_taken <= 10:
        efficiency = 1.0
    else:
        efficiency = max(0, 1.0 - (steps - 10) * 0.08)
    
    # Combine with weights
    composite = (ram_score × 0.4) + (energy_score × 0.4) + (efficiency × 0.2)
    
    # Clamp to valid range and return
    return max(0.001, min(0.999, composite))
```

---

## Commands Reference

```bash
# View available graders
python -c "from he_demo import TASK_GRADERS; print(list(TASK_GRADERS.keys()))"

# Run evaluation on specific task
$env:ENERGY_TASK="basic_ram_reduction"
$env:MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
$env:HF_TOKEN="hf_xxx"
python inference.py

# Check grader metadata
python -c "from he_demo import get_grader_metadata; import json; print(json.dumps(get_grader_metadata(), indent=2))"

# Test environment directly
python test_env_direct.py

# Run HTTP endpoint tests
curl http://localhost:8000/graders
curl http://localhost:8000/validate
curl http://localhost:8000/tasks
```

---

## Interpreting Results

**Good Sign:**
- ✅ Grader score > 0.6
- ✅ Action validity rate = 100%
- ✅ Task completed = True
- ✅ Avg reward increasing over steps
- ✅ Resource reduction matches task targets

**Bad Sign:**
- ❌ Grader score < 0.3
- ❌ Many invalid actions
- ❌ Task not completed
- ❌ Random action patterns
- ❌ Resources not improving

---

## Summary

The LLM is evaluated on:
1. **Can it parse observations?** (Action validity)
2. **Can it make good decisions?** (Reward accumulation)
3. **Can it complete tasks?** (Task targets met)
4. **How efficiently?** (Steps taken, resource optimization)
5. **What's the final score?** (Grader evaluation)

An excellent LLM agent should exceed baseline performance and consistently achieve grader scores > 0.75.
