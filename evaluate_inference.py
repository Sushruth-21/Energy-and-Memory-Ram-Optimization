#!/usr/bin/env python
"""
Language Model Inference Evaluation Script

This script runs the LLM through the Energy & Memory RAM Optimization environment
and evaluates its performance including:
- Action quality and validity
- Reward progression
- Task completion
- Model decision-making efficiency
- Benchmark comparison across tasks
"""

import os
import sys
import json
from typing import Dict, List, Tuple
from datetime import datetime

# Set environment variables for the inference script
os.environ.setdefault("API_BASE_URL", "https://router.huggingface.co/v1")
os.environ.setdefault("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
os.environ.setdefault("LOCAL_SERVER_URL", "http://localhost:8000")

# Import after setting environment variables
from he_demo.client import EnergyOptimizationEnv
from he_demo.models import EnergyOptimizationAction, EnergyOptimizationObservation
from he_demo.task_graders import get_grader, get_grader_metadata, TASK_GRADERS

print("=" * 80)
print("LLM INFERENCE EVALUATION SCRIPT")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Available tasks: {list(TASK_GRADERS.keys())}")
print()

# ============================================================================
# EVALUATION METRICS
# ============================================================================

class EvaluationMetrics:
    """Track and calculate evaluation metrics for LLM performance."""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.task_meta = get_grader_metadata(task_name)
        
        # Tracking variables
        self.steps: List[int] = []
        self.actions: List[str] = []
        self.rewards: List[float] = []
        self.ram_usage: List[float] = []
        self.energy_consumption: List[float] = []
        self.task_progress: List[float] = []
        
        # Final metrics
        self.total_steps = 0
        self.total_reward = 0.0
        self.avg_reward = 0.0
        self.max_reward = 0.0
        self.min_reward = 0.0
        self.grader_score = 0.0
        self.task_completed = False
        self.action_validity_rate = 0.0
        self.valid_actions = 0
        self.invalid_actions = 0
        
    def add_step(self, step: int, action: str, reward: float, obs: EnergyOptimizationObservation):
        """Record a step in the episode."""
        self.steps.append(step)
        self.actions.append(action)
        self.rewards.append(reward)
        self.ram_usage.append(obs.ram_usage)
        self.energy_consumption.append(obs.energy_consumption)
        self.task_progress.append(obs.task_progress)
        
        self.total_steps = step
        self.total_reward += reward
        if reward > self.max_reward:
            self.max_reward = reward
        if self.min_reward == 0.0 or reward < self.min_reward:
            self.min_reward = reward
    
    def mark_action_validity(self, valid: bool):
        """Mark whether an action was valid."""
        if valid:
            self.valid_actions += 1
        else:
            self.invalid_actions += 1
    
    def finalize(self, final_obs: EnergyOptimizationObservation, grader_score: float):
        """Finalize metrics after episode completes."""
        self.grader_score = grader_score
        self.task_completed = final_obs.current_task.completed if final_obs.current_task else False
        
        if self.total_steps > 0:
            self.avg_reward = self.total_reward / self.total_steps
            self.action_validity_rate = self.valid_actions / (self.valid_actions + self.invalid_actions) if (self.valid_actions + self.invalid_actions) > 0 else 0.0
    
    def print_summary(self):
        """Print detailed evaluation summary."""
        print("\n" + "=" * 80)
        print(f"EVALUATION SUMMARY - Task: {self.task_name.upper()}")
        print("=" * 80)
        print(f"\nTask Metadata:")
        print(f"  Difficulty: {self.task_meta['difficulty']}")
        print(f"  Description: {self.task_meta['description']}")
        print(f"  RAM Target: {self.task_meta['target_ram']}% | Energy Target: {self.task_meta['target_energy']} kWh")
        print(f"  Max Steps Allowed: {self.task_meta['max_steps']}")
        
        print(f"\nPerformance Metrics:")
        print(f"  ✓ Total Steps Taken: {self.total_steps}")
        print(f"  ✓ Total Reward Accumulated: {self.total_reward:.3f}")
        print(f"  ✓ Average Reward per Step: {self.avg_reward:.3f}")
        print(f"  ✓ Reward Range: [{self.min_reward:.3f}, {self.max_reward:.3f}]")
        
        print(f"\nAction Quality:")
        print(f"  ✓ Valid Actions: {self.valid_actions}")
        print(f"  ✓ Invalid Actions: {self.invalid_actions}")
        print(f"  ✓ Action Validity Rate: {self.action_validity_rate*100:.1f}%")
        
        print(f"\nResource Optimization:")
        print(f"  ✓ Initial RAM: {self.ram_usage[0]:.1f}% → Final RAM: {self.ram_usage[-1]:.1f}%")
        print(f"    RAM Reduction: {self.ram_usage[0] - self.ram_usage[-1]:.1f}%")
        print(f"  ✓ Initial Energy: {self.energy_consumption[0]:.1f} kWh → Final Energy: {self.energy_consumption[-1]:.1f} kWh")
        print(f"    Energy Reduction: {self.energy_consumption[0] - self.energy_consumption[-1]:.1f} kWh")
        
        print(f"\nTask Completion:")
        print(f"  ✓ Task Completed: {'YES ✓' if self.task_completed else 'NO ✗'}")
        print(f"  ✓ Final Task Progress: {self.task_progress[-1]*100:.1f}%")
        
        print(f"\nGrader Evaluation:")
        print(f"  ✓ Grader Score: {self.grader_score:.3f} (Scale: 0.001-0.999)")
        print(f"  ✓ Score Quality: ", end="")
        if self.grader_score > 0.8:
            print("EXCELLENT ★★★★★")
        elif self.grader_score > 0.6:
            print("GOOD ★★★★")
        elif self.grader_score > 0.4:
            print("FAIR ★★★")
        elif self.grader_score > 0.2:
            print("POOR ★★")
        else:
            print("VERY POOR ★")
        
        print("\n" + "=" * 80)
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "task_name": self.task_name,
            "difficulty": self.task_meta['difficulty'],
            "total_steps": self.total_steps,
            "total_reward": round(self.total_reward, 3),
            "avg_reward": round(self.avg_reward, 3),
            "reward_range": [round(self.min_reward, 3), round(self.max_reward, 3)],
            "valid_actions": self.valid_actions,
            "invalid_actions": self.invalid_actions,
            "action_validity_rate": round(self.action_validity_rate, 3),
            "initial_ram": round(self.ram_usage[0], 1) if self.ram_usage else 0,
            "final_ram": round(self.ram_usage[-1], 1) if self.ram_usage else 0,
            "initial_energy": round(self.energy_consumption[0], 1) if self.energy_consumption else 0,
            "final_energy": round(self.energy_consumption[-1], 1) if self.energy_consumption else 0,
            "task_completed": self.task_completed,
            "final_task_progress": round(self.task_progress[-1], 3) if self.task_progress else 0,
            "grader_score": round(self.grader_score, 3)
        }


# ============================================================================
# DIRECT ENVIRONMENT TEST
# ============================================================================

async def run_random_actions_baseline():
    """Run baseline test with random actions for comparison."""
    print("\n" + "=" * 80)
    print("BASELINE TEST: Random Actions")
    print("=" * 80)
    
    # Test on the easiest task
    task_name = "basic_ram_reduction"
    env = EnergyOptimizationEnv(base_url="http://localhost:8000")
    
    try:
        result = await env.reset()
        obs = result.observation
        
        print(f"Initial State:")
        print(f"  RAM: {obs.ram_usage:.1f}%")
        print(f"  Energy: {obs.energy_consumption:.1f} kWh")
        
        total_reward = 0.0
        for step in range(1, 6):
            # Random action
            import random
            action_type = random.choice(["reduce_ram", "optimize_energy", "balance_resources"])
            intensity = random.uniform(0.3, 0.9)
            
            action = EnergyOptimizationAction(action_type=action_type, intensity=intensity)
            result = await env.step(action)
            obs = result.observation
            reward = result.reward or 0.0
            total_reward += reward
            
            print(f"\nStep {step}:")
            print(f"  Action: {action_type}, Intensity: {intensity:.2f}")
            print(f"  Reward: {reward:.3f}")
            print(f"  RAM: {obs.ram_usage:.1f}% | Energy: {obs.energy_consumption:.1f} kWh")
        
        print(f"\nBaseline Total Reward: {total_reward:.3f}")
        print(f"Baseline Avg Reward: {total_reward/5:.3f}")
        
    except Exception as e:
        print(f"Error running baseline: {e}")


# ============================================================================
# SIMPLE HEURISTIC AGENT TEST
# ============================================================================

async def run_heuristic_agent():
    """Run evaluation with a simple heuristic agent (not LLM)."""
    print("\n" + "=" * 80)
    print("HEURISTIC AGENT TEST: Rule-Based Decision Making")
    print("=" * 80)
    
    task_name = "basic_ram_reduction"
    env = EnergyOptimizationEnv(base_url="http://localhost:8000")
    metrics = EvaluationMetrics(task_name)
    
    try:
        result = await env.reset()
        obs = result.observation
        
        print(f"Task: {task_name}")
        print(f"Initial RAM: {obs.ram_usage:.1f}%, Energy: {obs.energy_consumption:.1f} kWh\n")
        
        for step in range(1, 11):
            # Heuristic: If RAM > target, reduce RAM. Otherwise optimize energy.
            ram_target = 70.0
            energy_target = 7.5
            
            if obs.ram_usage > ram_target:
                action_type = "reduce_ram"
                intensity = 0.8  # High intensity for RAM reduction
                metrics.mark_action_validity(True)
            else:
                action_type = "optimize_energy"
                intensity = 0.6
                metrics.mark_action_validity(True)
            
            action = EnergyOptimizationAction(action_type=action_type, intensity=intensity)
            action_str = f"{action_type},{intensity:.1f}"
            
            result = await env.step(action)
            obs = result.observation
            reward = result.reward or 0.0
            
            metrics.add_step(step, action_str, reward, obs)
            
            print(f"Step {step}: {action_str:30} | Reward: {reward:+.3f} | RAM: {obs.ram_usage:5.1f}% | Energy: {obs.energy_consumption:5.1f} kWh")
            
            if result.done:
                break
        
        # Apply grader
        grader_func = get_grader(task_name)
        grader_score = grader_func(obs)
        metrics.finalize(obs, grader_score)
        
        metrics.print_summary()
        
        print(f"\nHeuristic Agent Performance:")
        print(f"  - Complexity: Simple rule-based")
        print(f"  - Decision Speed: Instant")
        print(f"  - Generalization: Limited (task-specific)")
        print(f"  - Final Score: {grader_score:.3f}")
        
    except Exception as e:
        print(f"Error running heuristic agent: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Run all evaluation tests."""
    print("\nStarting evaluation tests...\n")
    
    # Test 1: Baseline with random actions
    try:
        await run_random_actions_baseline()
    except Exception as e:
        print(f"Could not run baseline test: {e}")
    
    # Test 2: Heuristic agent
    try:
        await run_heuristic_agent()
    except Exception as e:
        print(f"Could not run heuristic agent: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    print("\nKey Insights:")
    print("- Baseline (Random): Shows what untrained agent achieves")
    print("- Heuristic Agent: Shows what simple rules can achieve")
    print("- LLM Inference: Should exceed both baselines with intelligent reasoning")
    print("\nNext Step: Run `python inference.py` to evaluate the actual LLM")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
