# Advanced LLM Inference v2.0
## Token-Based Reward System & Dependent Task Pipeline

## Overview

`inference_v2.py` is an advanced version of the inference script that implements:

1. **Free-Form Message Input** - Accept any natural language command, not just structured action_type,intensity
2. **Token-Level Reward System** - Each token in the message is evaluated (0 < score < 1)
3. **Dependent Task Pipeline** - Tasks depend on each other; failure stops the pipeline
4. **Observation Blocks** - Transparent state tracking at each step
5. **Benchmark Comparison** - Runs benchmarks before full evaluation
6. **Enhanced Graders** - 6+ graders with huge differences between difficulty levels

---

## Architecture

### 1. Token-Based Reward System

Each message is tokenized and scored individually:

```python
message = "aggressively reduce_ram with 0.9 intensity, then optimize_energy"

Token Scoring:
  - "aggressively" → 0.75 (instruction)
  - "reduce_ram" → 0.95 (action, highly optimized)
  - "0.9" → 0.92 (intensity, high reward)
  - "optimize_energy" → 0.90 (action, highly optimized)

Final Message Score: 0.605 (mean of all tokens, 0 < score < 1)
```

**Token Categories:**
- **Action Tokens**: reduce_ram (0.95), optimize_energy (0.90), balance_resources (0.75), monitor_system (0.65)
- **Intensity Tokens**: 0.9 (0.92), 0.8 (0.88), ..., 0.1 (0.25)
- **Instruction Tokens**: "efficiently" (0.78), "optimize" (0.85), "maximum" (0.80), "minimal" (0.85)
- **Default Tokens**: Long words get 0.70, medium 0.60, short 0.50

### 2. Dependent Task Pipeline

Tasks run sequentially with dependencies:

```
Task 1: basic_ram_reduction          (Difficulty 1) - min score: 0.60
   ↓ (must pass)
Task 2: energy_optimization          (Difficulty 2) - min score: 0.65
   ↓ (must pass)
Task 3: balanced_optimization        (Difficulty 3) - min score: 0.70
   ↓ (must pass)
Task 4: advanced_efficiency          (Difficulty 4) - min score: 0.75
   ↓ (must pass)
Task 5: expert_optimization          (Difficulty 5) - min score: 0.80
   ↓ (must pass)
Task 6: quantum_optimization         (Difficulty 6) - min score: 0.85
```

**Pipeline Execution Rules:**
- If a task score < min_grader_score, pipeline STOPS
- Each task must pass to unlock the next task
- No skipping or parallel execution

### 3. Observation Blocks

Real-time state display at each step:

```
╔════════════════════════════════════════════════════════════════╗
║                    OBSERVATION BLOCK - Step 1                     ║
╠════════════════════════════════════════════════════════════════╣
│ Task: basic_ram_reduction                      │
│ Difficulty: 1 | Progress: 45.0% | Steps: 1   │
├────────────────────────────────────────────────────────────────┤
│ RAM Usage:       72.0% │ Energy:    8.0 kWh │
│ Last Action:   reduce_ram,0.8                  │
│ Action Reward:  0.800 │ Total Reward:  0.800 │
│ Timestamp:     2026-04-12T15:04:54.389049               │
╚════════════════════════════════════════════════════════════════╝
```

Information shown:
- Task name and difficulty
- Current progress percentage
- RAM and Energy metrics
- Last action executed
- Reward accumulated
- Timestamp

### 4. Enhanced Graders (6 Levels)

Each task has a unique grader with massive differences:

| Task | Difficulty | Primary Metric | Multiplier | Step Penalty |
|------|-----------|----------------|-----------|-------------|
| Task 1 | 1 (Easy) | RAM Reduction | 0.80x | -10% per step |
| Task 2 | 2 (Medium) | Energy Optimization | 0.95x | -8% per step |
| Task 3 | 3 (Hard) | Balanced (50-50) | 0.92x | -5% per step |
| Task 4 | 4 (Hard+) | Advanced Efficiency | 0.88x | -10% per step |
| Task 5 | 5 (Expert) | Master Optimization | 0.85x | -15% per step |
| Task 6 | 6 (Legendary) | Quantum Optimization | 0.80x | -20% per step + extreme bonus |

**HUGE Differences:**
- Difficulty 1 multiplier: 0.80
- Difficulty 6 multiplier: 0.60 (with step penalties)
- Ratio: ~33% difference between easiest and hardest

All scores strictly bounded: **0.001 ≤ score ≤ 0.999**

### 5. Benchmark Comparison

Before running tasks, pipeline shows baseline performance:

```
✓ Baseline (Random):    Reward=1.737, Score=0.347
✓ Baseline (Heuristic): Reward=2.080, Score=0.999
✓ Expected (LLM):       Reward=5.0, Score=0.940
```

Used as reference for LLM performance evaluation.

---

## Usage

### Basic Execution

```powershell
cd "d:\Projects\Pytorch x hugging face\he_demo"
python inference_v2.py
```

### With HF Token (for LLM)

```powershell
$env:HF_TOKEN = "hf_YOUR_TOKEN_HERE"
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"  # Optional
python inference_v2.py
```

### Without HF Token (Local Actions Only)

```powershell
python inference_v2.py
# Will use default action sequences without LLM
```

### Specify Custom Model

```powershell
$env:HF_TOKEN = "hf_YOUR_TOKEN"
$env:MODEL_NAME = "meta-llama/Llama-2-70b-chat-hf"
python inference_v2.py
```

---

## Output

### Pipeline Results File

Generated as `pipeline_results.json`:

```json
{
  "timestamp": "2026-04-12T15:04:54.389049",
  "benchmark": {
    "baseline_random": {"reward": 1.737, "score": 0.347},
    "baseline_heuristic": {"reward": 2.08, "score": 0.999},
    "expected_llm": {"reward": 5.0, "score": 0.94}
  },
  "tasks": [
    {
      "task_name": "basic_ram_reduction",
      "difficulty": 1,
      "total_reward": 2.08,
      "final_grader_score": 0.8,
      "total_steps": 10,
      "passed": true,
      "steps": [...]
    },
    ...
  ],
  "pipeline_status": "STOPPED",
  "total_tasks_attempted": 3,
  "total_tasks_completed": 2,
  "failure_point": "balanced_optimization"
}
```

### Console Output

Shows:
- Benchmark comparison
- Each task's progress
- Token-based reward analysis
- Observation blocks for each step
- Final grader score and pass/fail
- Pipeline summary

---

## Examples

### Example 1: Successful Pipeline (All Tasks Pass)

```
RUNNING BENCHMARK COMPARISON
✓ Baseline (Random):    Reward=1.737, Score=0.347
✓ Baseline (Heuristic): Reward=2.08, Score=0.999
✓ Expected (LLM):       Reward=5.0, Score=0.94

✓ Environment initialized...

TASK 1: BASIC_RAM_REDUCTION
...
✅ TASK PASSED: Grader Score 0.75 >= 0.60

TASK 2: ENERGY_OPTIMIZATION
...
✅ TASK PASSED: Grader Score 0.82 >= 0.65

... (Tasks 3-6)

PIPELINE SUMMARY
✅ ALL TASKS COMPLETED SUCCESSFULLY!
Tasks Completed: 6/6
```

### Example 2: Pipeline Failure (Stops at Task 3)

```
TASK 1: BASIC_RAM_REDUCTION
✅ TASK PASSED: Grader Score 0.75 >= 0.60

TASK 2: ENERGY_OPTIMIZATION
✅ TASK PASSED: Grader Score 0.82 >= 0.65

TASK 3: BALANCED_OPTIMIZATION
❌ TASK FAILED: Grader Score 0.55 < 0.70
Pipeline halted at: balanced_optimization

PIPELINE SUMMARY
Tasks Attempted: 3
Tasks Completed: 2
Pipeline Status: STOPPED
Failed at: balanced_optimization
```

### Example 3: Token-Based Reward Analysis

```
LLM Response: "aggressively reduce RAM usage while optimizing energy consumption"

📊 Token-Based Reward Analysis:
   Message Score: 0.72
   Tokens analyzed: 10
     - 'aggressively': 0.75 (instruction)
     - 'reduce': 0.60 (instruction)
     - 'ram': 0.50 (instruction)
     - 'usage': 0.50 (instruction)
     - 'optimize': 0.85 (instruction)
```

---

## Key Features

✅ **Free-Form Input**: Accept any message, not just structured commands
✅ **Token Rewards**: Each word/action gets individual score (0<score<1)
✅ **Dependent Tasks**: Tasks must be completed in order
✅ **Stop on Failure**: One failure stops entire pipeline
✅ **Transparent State**: Observation blocks show current state
✅ **Benchmarks**: Compare against baselines before evaluation
✅ **Enhanced Graders**: 6 levels with huge differences
✅ **JSON Export**: Complete results saved for analysis

---

## Grader Scoring Details

### Grader 1: Basic RAM Reduction (0.80x multiplier)
```
RAM Score: (100 - current_ram) / (100 - 70) = normalized
Final Score = RAM_Score * 0.80
```

### Grader 2: Energy Optimization (0.95x multiplier)
```
Energy Score: (10 - current_energy) / (10 - 6) = normalized
Final Score = Energy_Score * 0.95
```

### Grader 3: Balanced (0.92x multiplier)
```
Balance Score = (RAM_Score + Energy_Score) / 2
Final Score = Balance_Score * 0.92
```

### Grader 4: Advanced (0.88x multiplier, step penalty)
```
Efficiency = RAM_Score * 0.6 + Energy_Score * 0.4
Step Penalty = max(0.0, 1.0 - (steps - 25) * 0.05)
Final Score = Efficiency * 0.88 * Step_Penalty
```

### Grader 5: Expert (0.85x multiplier, aggressive step penalty)
```
Expert = RAM_Score * 0.6 + Energy_Score * 0.4
Step Penalty = max(0.1, 1.0 - (steps - 30) * 0.08)
Final Score = Expert * 0.85 * Step_Penalty
```

### Grader 6: Quantum (0.80x multiplier, extreme penalties + bonus)
```
Quantum = RAM_Score * 0.5 + Energy_Score * 0.5
Step Penalty = max(0.05, 1.0 - (steps - 35) * 0.15)
Speed Bonus = 1.0 + (steps <= 15) * 0.10
Final Score = Quantum * 0.80 * Step_Penalty * Speed_Bonus
```

All final scores clamped: **0.001 ≤ score ≤ 0.999**

---

## Troubleshooting

### Port Error: "error while attempting to bind"
```
Make sure server is running:
python -m uvicorn he_demo.server.app:app --host 0.0.0.0 --port 8000
```

### HF Token Not Set
```
Set environment variable:
$env:HF_TOKEN = "your_token_here"
```

### LLM Call Failed
```
Script continues with default actions
Check if HF_TOKEN is valid
Check internet connectivity
```

### Observation Block Not Showing
```
Check console output - should appear after each step
May be truncated in some terminals
Check pipeline_results.json for complete data
```

---

## Next Steps

1. Run the pipeline with your HF token
2. Monitor observation blocks for state changes
3. Check pipeline_results.json for detailed metrics
4. Analyze token rewards to optimize message format
5. Adjust task difficulty targets as needed

---

## Files Modified

- `inference_v2.py` - New advanced inference script
- `task_graders.py` - Already has 5-6 graders with proper scoring
- `server/app.py` - Server supports task tracking
- `models.py` - Observation model compatible

All changes are **backwards compatible** with existing system.
