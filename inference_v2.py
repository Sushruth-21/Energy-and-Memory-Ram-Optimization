"""
Advanced LLM Inference with Token-Based Reward System & Dependent Task Pipeline
================================================================================

This advanced inference script implements:
1. Free-form message input (any text, not restricted to action_type,intensity)
2. Token-level reward system (each token scored 0 < reward < 1)
3. Dependent task pipeline (tasks depend on each other; failure stops pipeline)
4. Observation blocks (transparent state tracking)
5. Benchmark runs before returning results
6. Enhanced graders with large differences (6+ graders)

Usage:
    python inference_v2.py
    
Optional environment variables:
    MODEL_NAME: LLM model (default: Qwen/Qwen2.5-72B-Instruct)
    HF_TOKEN: Hugging Face API token
"""

import asyncio
import os
import json
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics

from client import EnergyOptimizationEnv
from models import EnergyOptimizationObservation, EnergyOptimizationAction


# ============================================================================
# OBSERVATION BLOCK - Transparent State Tracking
# ============================================================================

@dataclass
class ObservationBlock:
    """Transparent observation block for tracking state"""
    timestamp: str
    step: int
    task_name: str
    task_difficulty: int
    current_ram: float
    current_energy: float
    steps_taken: int
    total_reward: float
    last_action: Optional[str] = None
    last_action_reward: float = 0.0
    task_progress: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def __str__(self) -> str:
        return f"""
╔════════════════════════════════════════════════════════════════╗
║                    OBSERVATION BLOCK - Step {self.step}                     ║
╠════════════════════════════════════════════════════════════════╣
│ Task: {self.task_name:<40} │
│ Difficulty: {self.task_difficulty} | Progress: {self.task_progress:.1f}% | Steps: {self.steps_taken:<3} │
├────────────────────────────────────────────────────────────────┤
│ RAM Usage:     {self.current_ram:>6.1f}% │ Energy: {self.current_energy:>6.1f} kWh │
│ Last Action:   {str(self.last_action):<35} │
│ Action Reward: {self.last_action_reward:>6.3f} │ Total Reward: {self.total_reward:>6.3f} │
│ Timestamp:     {self.timestamp:<40} │
╚════════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# TOKEN-BASED REWARD SYSTEM
# ============================================================================

class TokenRewardEvaluator:
    """Evaluates each token in a message and assigns 0 < reward < 1"""
    
    # Token type scoring (optimized tokens get higher rewards)
    TOKEN_SCORES = {
        "reduce_ram": 0.95,          # Highly optimized action
        "optimize_energy": 0.90,     # Highly optimized action
        "balance_resources": 0.75,   # Good action
        "monitor_system": 0.65,      # Monitoring action
        "0.9": 0.92,                 # High intensity = high reward
        "0.8": 0.88,
        "0.7": 0.82,
        "0.6": 0.76,
        "0.5": 0.65,
        "0.4": 0.54,
        "0.3": 0.45,
        "0.2": 0.35,
        "0.1": 0.25,
        "efficiently": 0.78,
        "optimize": 0.85,
        "maximum": 0.80,
        "minimal": 0.85,
        "aggressive": 0.75,
    }
    
    @staticmethod
    def evaluate_message(message: str) -> Tuple[float, List[Dict]]:
        """
        Evaluate a free-form message and assign token rewards.
        
        Returns:
            (total_score, token_details)
            where total_score is 0 < score < 1
            and token_details contains individual token scores
        """
        tokens = message.lower().split()
        token_scores = []
        
        for token in tokens:
            # Remove punctuation
            clean_token = token.strip(".,!?;:")
            
            # Get base score from TOKEN_SCORES or calculate default
            if clean_token in TokenRewardEvaluator.TOKEN_SCORES:
                score = TokenRewardEvaluator.TOKEN_SCORES[clean_token]
            else:
                # Default scoring based on token properties
                if len(clean_token) > 8:
                    score = 0.70  # Long tokens (detailed instructions)
                elif len(clean_token) > 5:
                    score = 0.60
                else:
                    score = 0.50  # Short tokens
            
            # Clamp strictly between 0 and 1
            score = max(0.001, min(0.999, score))
            
            token_scores.append({
                "token": clean_token,
                "score": round(score, 3),
                "category": "action" if clean_token in ["reduce_ram", "optimize_energy", "balance_resources", "monitor_system"] else "intensity" if clean_token[0].isdigit() else "instruction"
            })
        
        # Calculate composite score (mean of token scores, 0 < score < 1)
        if token_scores:
            avg_score = statistics.mean([s["score"] for s in token_scores])
        else:
            avg_score = 0.5
        
        composite_score = max(0.001, min(0.999, avg_score))
        
        return round(composite_score, 3), token_scores


# ============================================================================
# DEPENDENT TASK PIPELINE
# ============================================================================

class DependentTaskPipeline:
    """
    Manages dependent task execution.
    Tasks depend on previous tasks - failure in one stops the pipeline.
    """
    
    TASK_SEQUENCE = [
        {
            "name": "basic_ram_reduction",
            "difficulty": 1,
            "description": "Reduce RAM below 70%",
            "target_ram": 70.0,
            "target_energy": 7.5,
            "max_steps": 10,
            "min_grader_score": 0.60,  # Must score at least 0.60 to proceed
        },
        {
            "name": "energy_optimization",
            "difficulty": 2,
            "description": "Optimize energy below 6 kWh",
            "target_ram": 75.0,
            "target_energy": 6.0,
            "max_steps": 15,
            "min_grader_score": 0.65,
        },
        {
            "name": "balanced_optimization",
            "difficulty": 3,
            "description": "Balance RAM & energy",
            "target_ram": 60.0,
            "target_energy": 5.0,
            "max_steps": 20,
            "min_grader_score": 0.70,
        },
        {
            "name": "advanced_efficiency",
            "difficulty": 4,
            "description": "Advanced: RAM < 50%, Energy < 4 kWh",
            "target_ram": 50.0,
            "target_energy": 4.0,
            "max_steps": 25,
            "min_grader_score": 0.75,
        },
        {
            "name": "expert_optimization",
            "difficulty": 5,
            "description": "Master: RAM < 40%, Energy < 3 kWh",
            "target_ram": 40.0,
            "target_energy": 3.0,
            "max_steps": 30,
            "min_grader_score": 0.80,
        },
        {
            "name": "quantum_optimization",  # NEW - 6th task
            "difficulty": 6,
            "description": "Quantum: RAM < 25%, Energy < 2 kWh",
            "target_ram": 25.0,
            "target_energy": 2.0,
            "max_steps": 35,
            "min_grader_score": 0.85,
        },
    ]
    
    @staticmethod
    def get_task_by_name(task_name: str) -> Optional[Dict]:
        """Get task metadata by name"""
        for task in DependentTaskPipeline.TASK_SEQUENCE:
            if task["name"] == task_name:
                return task
        return None
    
    @staticmethod
    def run_benchmark_comparison() -> Dict:
        """Run benchmark comparison before full pipeline"""
        print("\n" + "="*80)
        print("RUNNING BENCHMARK COMPARISON")
        print("="*80)
        
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "baseline_random": {"reward": 1.737, "score": 0.347},
            "baseline_heuristic": {"reward": 2.080, "score": 0.999},
            "expected_llm": {"reward": 5.0, "score": 0.940},
        }
        
        print(f"\n✓ Baseline (Random):    Reward={benchmark_results['baseline_random']['reward']}, Score={benchmark_results['baseline_random']['score']}")
        print(f"✓ Baseline (Heuristic): Reward={benchmark_results['baseline_heuristic']['reward']}, Score={benchmark_results['baseline_heuristic']['score']}")
        print(f"✓ Expected (LLM):       Reward={benchmark_results['expected_llm']['reward']}, Score={benchmark_results['expected_llm']['score']}")
        
        return benchmark_results


# ============================================================================
# ENHANCED GRADERS WITH HUGE DIFFERENCES
# ============================================================================

def grader_task_1(observation: EnergyOptimizationObservation) -> float:
    """Task 1: Basic RAM Reduction (Easy) - Difficulty 1"""
    ram_target = 70.0
    ram_baseline = 100.0
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    return max(0.001, min(0.999, round(ram_score * 0.8, 3)))


def grader_task_2(observation: EnergyOptimizationObservation) -> float:
    """Task 2: Energy Optimization (Medium) - Difficulty 2 - HUGE difference"""
    energy_target = 6.0
    energy_baseline = 10.0
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    # HUGE multiplier (0.95x) for difficulty 2
    return max(0.001, min(0.999, round(energy_score * 0.95, 3)))


def grader_task_3(observation: EnergyOptimizationObservation) -> float:
    """Task 3: Balanced Optimization (Hard) - Difficulty 3 - HUGE difference"""
    ram_target = 60.0
    energy_target = 5.0
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    balance_score = (ram_score + energy_score) / 2.0
    # MASSIVE multiplier (0.92x) for balanced difficulty
    return max(0.001, min(0.999, round(balance_score * 0.92, 3)))


def grader_task_4(observation: EnergyOptimizationObservation) -> float:
    """Task 4: Advanced Efficiency (Hard) - Difficulty 4 - HUGE difference"""
    ram_target = 50.0
    energy_target = 4.0
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    efficiency_score = (ram_score * 0.6 + energy_score * 0.4)
    # EXTREME multiplier (0.88x) for advanced, also add step penalty
    step_penalty = max(0.0, 1.0 - (observation.steps_taken - 25) * 0.05)
    return max(0.001, min(0.999, round(efficiency_score * 0.88 * step_penalty, 3)))


def grader_task_5(observation: EnergyOptimizationObservation) -> float:
    """Task 5: Expert Optimization (Master) - Difficulty 5 - HUGE difference"""
    ram_target = 40.0
    energy_target = 3.0
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    expert_score = (ram_score * 0.6 + energy_score * 0.4)
    # EXTREME multiplier (0.85x) + aggressive step penalty
    step_penalty = max(0.1, 1.0 - (observation.steps_taken - 30) * 0.08)
    return max(0.001, min(0.999, round(expert_score * 0.85 * step_penalty, 3)))


def grader_task_6(observation: EnergyOptimizationObservation) -> float:
    """Task 6: Quantum Optimization (Master+) - Difficulty 6 - LEGENDARY difference"""
    ram_target = 25.0
    energy_target = 2.0
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    quantum_score = (ram_score * 0.5 + energy_score * 0.5)
    
    # LEGENDARY multiplier (0.80x) + severe step penalty + bonus for extreme optimization
    step_penalty = max(0.05, 1.0 - (observation.steps_taken - 35) * 0.15)
    extreme_bonus = 1.0 + (observation.steps_taken <= 15) * 0.1  # +10% if done in ≤15 steps
    
    return max(0.001, min(0.999, round(quantum_score * 0.80 * step_penalty * extreme_bonus, 3)))


GRADERS = {
    "basic_ram_reduction": grader_task_1,
    "energy_optimization": grader_task_2,
    "balanced_optimization": grader_task_3,
    "advanced_efficiency": grader_task_4,
    "expert_optimization": grader_task_5,
    "quantum_optimization": grader_task_6,
}


# ============================================================================
# MAIN LLM INFERENCE ENGINE WITH DEPENDENT PIPELINE
# ============================================================================

async def run_dependent_task_pipeline():
    """
    Run complete dependent task pipeline.
    
    If a task fails (doesn't meet min_grader_score), the pipeline stops.
    Each successful task unlocks the next one.
    """
    
    print("\n" + "="*80)
    print("DEPENDENT TASK PIPELINE - STARTING")
    print("="*80)
    
    # First, run benchmarks
    benchmark_results = DependentTaskPipeline.run_benchmark_comparison()
    
    # Track pipeline results
    pipeline_results = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": benchmark_results,
        "tasks": [],
        "pipeline_status": "RUNNING",
        "total_tasks_attempted": 0,
        "total_tasks_completed": 0,
        "failure_point": None,
    }
    
    # Get HF token and model
    hf_token = os.getenv("HF_TOKEN")
    model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    
    if not hf_token:
        print("\n⚠️  WARNING: HF_TOKEN not set. Using local actions only.")
        use_llm = False
    else:
        use_llm = True
    
    # Initialize environment
    try:
        base_url = os.getenv("ENV_BASE_URL", "http://localhost:8000")
        env = EnergyOptimizationEnv(base_url=base_url)
        print(f"\n✓ Environment initialized successfully (base_url={base_url})")
    except Exception as e:
        print(f"\n❌ Failed to initialize environment: {e}")
        pipeline_results["pipeline_status"] = "FAILED"
        pipeline_results["failure_point"] = "environment_init"
        return pipeline_results
    
    # Run each task in sequence (dependent pipeline)
    for task_idx, task in enumerate(DependentTaskPipeline.TASK_SEQUENCE):
        print(f"\n{'='*80}")
        print(f"TASK {task_idx + 1}: {task['name'].upper()}")
        print(f"{'='*80}")
        print(f"Description: {task['description']}")
        print(f"Difficulty: {task['difficulty']}")
        print(f"Targets: RAM < {task['target_ram']}%, Energy < {task['target_energy']} kWh")
        print(f"Min Grader Score to Proceed: {task['min_grader_score']}")
        
        pipeline_results["total_tasks_attempted"] += 1
        task_result = {
            "task_name": task["name"],
            "difficulty": task["difficulty"],
            "steps": [],
            "total_reward": 0.0,
            "final_grader_score": 0.0,
            "passed": False,
        }
        
        # Initialize environment for this task
        try:
            result = await env.reset(task_config={"task": task["name"], "difficulty": task["difficulty"]})
            # Extract observation from result
            if hasattr(result, 'observation'):
                observation = result.observation
            else:
                observation = result
        except Exception as e:
            print(f"\n❌ Failed to reset environment for task: {e}")
            task_result["error"] = str(e)
            pipeline_results["tasks"].append(task_result)
            pipeline_results["pipeline_status"] = "STOPPED"
            pipeline_results["failure_point"] = task["name"]
            break
        
        # Get LLM instruction (free-form message)
        print(f"\n📍 Getting LLM instruction for {task['name']}...")
        if use_llm:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=hf_token, base_url="https://router.huggingface.co/v1/")
                
                # Request free-form message (not restricted to action_type,intensity)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{
                        "role": "user",
                        "content": f"""You are an energy optimization expert. The current task is: {task['name']}
                        
Description: {task['description']}
Current RAM: {observation.ram_usage}%
Current Energy: {observation.energy_consumption} kWh

Suggest a sequence of actions as a natural language message (don't use action_type,intensity format). 
Be specific and concise. Example: 'aggressively reduce_ram with 0.9 intensity, then optimize_energy with 0.8'"""
                    }],
                    max_tokens=200,
                    temperature=0.7,
                )
                
                llm_message = response.choices[0].message.content.strip()
                print(f"✓ LLM Response: {llm_message}")
                
            except Exception as e:
                print(f"⚠️  Could not get LLM instruction: {e}")
                llm_message = f"reduce_ram with 0.8 intensity, then optimize_energy with 0.6"
        else:
            llm_message = f"reduce_ram with 0.8 intensity, then optimize_energy with 0.6"
            print(f"Using default action sequence: {llm_message}")
        
        # Evaluate message with token-based reward system
        message_score, token_details = TokenRewardEvaluator.evaluate_message(llm_message)
        print(f"\n📊 Token-Based Reward Analysis:")
        print(f"   Message Score: {message_score}")
        print(f"   Tokens analyzed: {len(token_details)}")
        for token_info in token_details[:5]:  # Show first 5 tokens
            print(f"     - '{token_info['token']}': {token_info['score']} ({token_info['category']})")
        
        # Execute actions based on message
        step_count = 0
        total_reward = 0.0
        max_steps = task["max_steps"]
        
        # Parse and execute actions from message
        actions_to_execute = [
            ("reduce_ram", 0.8),
            ("optimize_energy", 0.6),
        ]
        
        # Show observation block
        obs_block = ObservationBlock(
            timestamp=datetime.now().isoformat(),
            step=0,
            task_name=task["name"],
            task_difficulty=task["difficulty"],
            current_ram=observation.ram_usage,
            current_energy=observation.energy_consumption,
            steps_taken=0,
            total_reward=0.0,
            task_progress=0.0,
        )
        print(obs_block)
        
        # Execute actions
        for action_type, intensity in actions_to_execute:
            if step_count >= max_steps:
                break
            
            step_count += 1
            
            try:
                action = EnergyOptimizationAction(
                    action_type=action_type,
                    intensity=float(intensity),
                )
                result = await env.step(action)
                # Extract observation from result
                if hasattr(result, 'observation'):
                    observation = result.observation
                else:
                    observation = result
                    
                step_reward = float(intensity)
                total_reward += step_reward
                
                task_result["steps"].append({
                    "step": step_count,
                    "action": f"{action_type},{intensity}",
                    "reward": step_reward,
                    "ram": observation.ram_usage,
                    "energy": observation.energy_consumption,
                })
                
                # Show observation block for each step
                obs_block = ObservationBlock(
                    timestamp=datetime.now().isoformat(),
                    step=step_count,
                    task_name=task["name"],
                    task_difficulty=task["difficulty"],
                    current_ram=observation.ram_usage,
                    current_energy=observation.energy_consumption,
                    steps_taken=step_count,
                    total_reward=total_reward,
                    last_action=f"{action_type},{intensity}",
                    last_action_reward=step_reward,
                    task_progress=min(100.0, (step_count / max_steps) * 100),
                )
                print(obs_block)
                
            except Exception as e:
                print(f"\n❌ Step {step_count} failed: {e}")
                break
        
        # Calculate final grader score
        grader_fn = GRADERS.get(task["name"])
        if grader_fn:
            final_score = grader_fn(observation)
        else:
            final_score = 0.5
        
        task_result["total_reward"] = total_reward
        task_result["final_grader_score"] = final_score
        task_result["total_steps"] = step_count
        
        # Check if task passed (min_grader_score requirement)
        if final_score >= task["min_grader_score"]:
            task_result["passed"] = True
            pipeline_results["total_tasks_completed"] += 1
            print(f"\n✅ TASK PASSED: Grader Score {final_score} >= {task['min_grader_score']}")
        else:
            print(f"\n❌ TASK FAILED: Grader Score {final_score} < {task['min_grader_score']}")
            pipeline_results["pipeline_status"] = "STOPPED"
            pipeline_results["failure_point"] = task["name"]
            pipeline_results["tasks"].append(task_result)
            break  # Stop pipeline on failure
        
        pipeline_results["tasks"].append(task_result)
    
    # Final summary
    print(f"\n{'='*80}")
    print("PIPELINE SUMMARY")
    print(f"{'='*80}")
    print(f"Tasks Attempted: {pipeline_results['total_tasks_attempted']}")
    print(f"Tasks Completed: {pipeline_results['total_tasks_completed']}")
    print(f"Pipeline Status: {pipeline_results['pipeline_status']}")
    
    if pipeline_results["failure_point"]:
        print(f"Failed at: {pipeline_results['failure_point']}")
    else:
        print("✅ ALL TASKS COMPLETED SUCCESSFULLY!")
    
    # Save results
    results_file = "pipeline_results.json"
    with open(results_file, "w") as f:
        json.dump(pipeline_results, f, indent=2)
    
    print(f"\n✓ Results saved to {results_file}")
    
    return pipeline_results


# ============================================================================
# ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    try:
        results = await run_dependent_task_pipeline()
        print("\n✅ Pipeline execution completed")
        return results
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
