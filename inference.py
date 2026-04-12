"""
Energy & Memory RAM Optimization Inference Script
=================================================
This script demonstrates how an AI agent can learn to optimize energy consumption
and RAM usage through reinforcement learning in the Energy Optimization Environment.

The agent uses an LLM to make strategic decisions about resource optimization actions.

Required Environment Variables:
- API_BASE_URL: The API endpoint for the LLM (for Hugging Face router, use https://router.huggingface.co/v1)
- MODEL_NAME: The model identifier to use for inference
- HF_TOKEN: Your Hugging Face API key with inference permissions
- LOCAL_IMAGE_NAME: The name of the local image to use for the environment (optional)

Example setup:
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="OpenAssistant/oasst-sft-1-pythia-12b"
export HF_TOKEN="hf_..."
export LOCAL_IMAGE_NAME="your-docker-image"  # Optional
"""

import asyncio
import os
import subprocess
import textwrap
from typing import List, Optional, Dict, Any, Callable

from openai import OpenAI, OpenAIError

from he_demo.client import EnergyOptimizationEnv
from he_demo.models import EnergyOptimizationAction, EnergyOptimizationObservation


# ============================================================================
# TASK GRADERS - Integrated from task_graders.py
# ============================================================================
# All grader functions for evaluating agent performance (0.0-1.0 scale)

def task_1_basic_ram_reduction_grader(observation: EnergyOptimizationObservation) -> float:
    """Grade Task 1: Basic RAM Reduction (Difficulty 1)"""
    ram_target = 70.0
    energy_target = 7.5
    max_steps = 10
    
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    if observation.steps_taken <= max_steps:
        step_efficiency = 1.0
    else:
        step_efficiency = max(0.0, 1.0 - (observation.steps_taken - max_steps) * 0.1)
    
    composite_score = (ram_score * 0.4) + (energy_score * 0.4) + (step_efficiency * 0.2)
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


def task_2_energy_optimization_grader(observation: EnergyOptimizationObservation) -> float:
    """Grade Task 2: Energy Optimization (Difficulty 2)"""
    ram_constraint = 75.0
    energy_target = 6.0
    max_steps = 15
    
    energy_baseline = 10.0
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    if observation.ram_usage <= ram_constraint:
        ram_constraint_score = 1.0
    else:
        overage = observation.ram_usage - ram_constraint
        ram_constraint_score = max(0.0, 1.0 - (overage / 5.0))
    
    if observation.steps_taken <= max_steps:
        step_efficiency = 1.0
    else:
        step_efficiency = max(0.0, 1.0 - (observation.steps_taken - max_steps) * 0.08)
    
    composite_score = (energy_score * 0.5) + (ram_constraint_score * 0.25) + (step_efficiency * 0.25)
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


def task_3_balanced_optimization_grader(observation: EnergyOptimizationObservation) -> float:
    """Grade Task 3: Balanced Optimization (Difficulty 3)"""
    ram_target = 60.0
    energy_target = 5.0
    max_steps = 20
    
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    balance_score = (ram_score + energy_score) / 2.0
    
    if observation.steps_taken <= max_steps:
        step_bonus = min(0.1, (max_steps - observation.steps_taken) / max_steps * 0.1)
    else:
        step_bonus = max(-0.2, -(observation.steps_taken - max_steps) * 0.05)
    
    composite_score = max(0.0, min(1.0, (balance_score * 0.9) + step_bonus))
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


def task_4_advanced_efficiency_grader(observation: EnergyOptimizationObservation) -> float:
    """Grade Task 4: Advanced Efficiency (Difficulty 4)"""
    ram_target = 50.0
    energy_target = 4.0
    max_steps = 25
    
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    balance_score = (ram_score + energy_score) / 2.0
    
    if observation.steps_taken <= max_steps:
        step_bonus = min(0.1, (max_steps - observation.steps_taken) / max_steps * 0.1)
    else:
        step_bonus = max(-0.2, -(observation.steps_taken - max_steps) * 0.05)
        
    composite_score = max(0.0, min(1.0, (balance_score * 0.9) + step_bonus))
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


def task_5_expert_optimization_grader(observation: EnergyOptimizationObservation) -> float:
    """Grade Task 5: Expert Optimization (Difficulty 5)"""
    ram_target = 40.0
    energy_target = 3.0
    max_steps = 30
    
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    balance_score = (ram_score * 0.6) + (energy_score * 0.4)
    
    if observation.steps_taken <= max_steps:
        step_bonus = min(0.1, (max_steps - observation.steps_taken) / max_steps * 0.1)
    else:
        step_bonus = max(-0.3, -(observation.steps_taken - max_steps) * 0.05)
        
    composite_score = max(0.0, min(1.0, (balance_score * 0.9) + step_bonus))
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


# Explicit task grader mapping for validator tool detection
TASK_GRADERS: Dict[str, Dict[str, Any]] = {
    "basic_ram_reduction": {
        "grader": task_1_basic_ram_reduction_grader,
        "name": "basic_ram_reduction",
        "display_name": "Basic RAM Reduction",
        "difficulty": 1,
        "description": "Reduce RAM usage below 70%",
        "target_ram": 70.0,
        "target_energy": 7.5,
        "max_steps": 10,
        "category": "easy",
        "real_world_application": "Memory optimization for resource-constrained devices and edge computing"
    },
    "energy_optimization": {
        "grader": task_2_energy_optimization_grader,
        "name": "energy_optimization",
        "display_name": "Energy Optimization",
        "difficulty": 2,
        "description": "Reduce energy consumption below 6 kWh while maintaining RAM below 75%",
        "target_ram": 75.0,
        "target_energy": 6.0,
        "max_steps": 15,
        "category": "medium",
        "real_world_application": "Energy efficiency for data centers and cloud infrastructure"
    },
    "balanced_optimization": {
        "grader": task_3_balanced_optimization_grader,
        "name": "balanced_optimization",
        "display_name": "Balanced Optimization",
        "difficulty": 3,
        "description": "Balance RAM below 60% and energy below 5 kWh",
        "target_ram": 60.0,
        "target_energy": 5.0,
        "max_steps": 20,
        "category": "hard",
        "real_world_application": "Production system optimization with dual constraints"
    },
    "advanced_efficiency": {
        "grader": task_4_advanced_efficiency_grader,
        "name": "advanced_efficiency",
        "display_name": "Advanced Efficiency",
        "difficulty": 4,
        "description": "Achieve RAM below 50% and energy below 4 kWh",
        "target_ram": 50.0,
        "target_energy": 4.0,
        "max_steps": 25,
        "category": "hard",
        "real_world_application": "Highly constrained embedded systems and IoT devices"
    },
    "expert_optimization": {
        "grader": task_5_expert_optimization_grader,
        "name": "expert_optimization",
        "display_name": "Expert Optimization",
        "difficulty": 5,
        "description": "Master level: RAM below 40% and energy below 3 kWh",
        "target_ram": 40.0,
        "target_energy": 3.0,
        "max_steps": 30,
        "category": "expert",
        "real_world_application": "Mission-critical space, deep-sea probes, and highly scaled edge clusters"
    }
}


def get_grader(task_name: str) -> Callable:
    """Get the grader function for a specific task."""
    if task_name not in TASK_GRADERS:
        raise ValueError(f"Unknown task: {task_name}. Available tasks: {list(TASK_GRADERS.keys())}")
    return TASK_GRADERS[task_name]["grader"]


def get_all_graders() -> Dict[str, Callable]:
    """Get all available graders."""
    return {name: metadata["grader"] for name, metadata in TASK_GRADERS.items()}


def get_grader_metadata(task_name: str = None) -> Dict[str, Any]:
    """Get metadata about graders."""
    if task_name:
        if task_name not in TASK_GRADERS:
            raise ValueError(f"Unknown task: {task_name}")
        return {k: v for k, v in TASK_GRADERS[task_name].items() if k != "grader"}
    else:
        return {name: {k: v for k, v in metadata.items() if k != "grader"} 
                for name, metadata in TASK_GRADERS.items()}

# Environment configuration variables
# Default endpoint uses Hugging Face's router; set API_BASE_URL explicitly if needed.
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
LOCAL_SERVER_URL = os.getenv("LOCAL_SERVER_URL", "http://localhost:8000")

# Use HF_TOKEN as API key for OpenAI client
API_KEY = HF_TOKEN

TASK_NAME = os.getenv("ENERGY_TASK", "energy_optimization")
BENCHMARK = os.getenv("ENERGY_BENCHMARK", "energy_optimization")
MAX_STEPS = 50  # More steps for complex optimization tasks
TEMPERATURE = 0.3  # Lower temperature for more consistent optimization decisions
MAX_TOKENS = 100
SUCCESS_SCORE_THRESHOLD = 0.5  # Higher threshold for meaningful optimization

# Max possible reward: task completion bonuses + efficiency improvements
MAX_TOTAL_REWARD = 100.0  # Estimated maximum possible reward

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an AI system optimization agent. Your goal is to optimize computer system resources:
    - Reduce RAM usage (target: below 40%)
    - Minimize energy consumption (target: below 3 kWh)
    - Complete optimization tasks efficiently

    Available actions:
    - reduce_ram: Focus on RAM optimization (intensity 0.0-1.0)
    - optimize_energy: Focus on energy reduction (intensity 0.0-1.0)
    - balance_resources: Balanced approach to both resources
    - monitor_system: Gather system information

    Action format: action_type,intensity
    Example: reduce_ram,0.8

    Consider current system state, task requirements, and potential trade-offs.
    Reply with exactly one action in the format: action_type,intensity
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int, action: str, reward: float, done: bool, error: Optional[str]
) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def build_user_prompt(
    step: int, observation, last_reward: float, history: List[str]
) -> str:
    current_task_info = ""
    if observation.current_task:
        task = observation.current_task
        current_task_info = f"""
        Current Task: {task.name}
        Description: {task.description}
        Targets: RAM < {task.ram_target}%, Energy < {task.energy_target} kWh
        Max Steps: {task.max_steps}
        """

    history_block = "\n".join(history[-3:]) if history else "None"

    return textwrap.dedent(
        f"""
        Step: {step}
        System State:
        - RAM Usage: {observation.ram_usage:.1f}%
        - Energy Consumption: {observation.energy_consumption:.1f} kWh
        - System Load: {observation.system_load:.2f}
        - Efficiency Score: {observation.efficiency_score:.2f}
        - Task Progress: {observation.task_progress:.2f}
        - Steps Taken: {observation.steps_taken}

        {current_task_info}
        Tasks Completed: {', '.join(observation.tasks_completed) if observation.tasks_completed else 'None'}

        Last Reward: {last_reward:.2f}
        Recent Actions:
        {history_block}

        Choose your next optimization action (action_type,intensity):
        """
    ).strip()


def parse_action(action_str: str) -> EnergyOptimizationAction:
    """Parse action string into EnergyOptimizationAction."""
    try:
        parts = action_str.strip().split(',')
        if len(parts) != 2:
            raise ValueError("Invalid action format")

        action_type = parts[0].strip()
        intensity = float(parts[1].strip())

        # Validate action type
        valid_actions = ["reduce_ram", "optimize_energy", "balance_resources", "monitor_system"]
        if action_type not in valid_actions:
            action_type = "monitor_system"  # Default fallback

        # Clamp intensity to valid range
        intensity = max(0.0, min(1.0, intensity))

        return EnergyOptimizationAction(action_type=action_type, intensity=intensity)
    except Exception:
        # Return safe default action
        return EnergyOptimizationAction(action_type="monitor_system", intensity=0.5)


def get_model_action(
    client: OpenAI, step: int, observation, last_reward: float, history: List[str]
) -> EnergyOptimizationAction:
    """Get optimization action from the language model."""
    user_prompt = build_user_prompt(step, observation, last_reward, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        action_text = (completion.choices[0].message.content or "").strip()
        return parse_action(action_text)
    except OpenAIError as exc:
        error_text = str(exc)
        print(f"[DEBUG] Model request failed: {error_text}", flush=True)
        status_code = getattr(exc, 'status_code', None)

        if status_code == 403 or "403" in error_text or "insufficient permissions" in error_text.lower():
            raise RuntimeError(
                "Hugging Face authentication failed: your token does not have sufficient inference permissions. "
                "Use a token with inference access or switch to an active model/endpoint you are authorized for. "
                "If you are using the Hugging Face router, ensure HF_TOKEN has the `inference` scope and that MODEL_NAME is accessible."
            ) from exc

        return EnergyOptimizationAction(action_type="monitor_system", intensity=0.5)
    except Exception as exc:
        print(f"[DEBUG] Unexpected model request failure: {exc}", flush=True)
        return EnergyOptimizationAction(action_type="monitor_system", intensity=0.5)


async def main() -> None:
    # Validate required environment variables
    if not API_BASE_URL or API_BASE_URL == "<your-active-endpoint>":
        raise ValueError("API_BASE_URL environment variable must be set to your active LLM endpoint")

    if not MODEL_NAME or MODEL_NAME == "<your-active-model>":
        raise ValueError("MODEL_NAME environment variable must be set to your active model identifier")

    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable must be set to your Hugging Face API key")

    # ===== GRADER CONFIGURATION (Per Hackathon Rules) =====
    # Validate that the specified task has a grader configured
    if TASK_NAME not in TASK_GRADERS:
        available_tasks = list(TASK_GRADERS.keys())
        raise ValueError(
            f"Task '{TASK_NAME}' not found. Available tasks with graders: {available_tasks}. "
            f"Set ENERGY_TASK environment variable to one of these task names."
        )
    
    task_metadata = get_grader_metadata(TASK_NAME)
    print(
        f"[CONFIG] Task-specific grader configured: task={TASK_NAME} "
        f"difficulty={task_metadata['difficulty']} "
        f"description='{task_metadata['description']}'",
        flush=True,
    )

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    async def local_image_exists(image_name: str) -> bool:
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
                capture_output=True,
                text=True,
                check=True,
            )
            return image_name in result.stdout.splitlines()
        except Exception:
            return False

    if LOCAL_IMAGE_NAME:
        if await local_image_exists(LOCAL_IMAGE_NAME):
            env = await EnergyOptimizationEnv.from_docker_image(LOCAL_IMAGE_NAME)
        else:
            print(
                f"[WARN] Docker image '{LOCAL_IMAGE_NAME}' not found locally. Falling back to local server at {LOCAL_SERVER_URL}",
                flush=True,
            )
            env = EnergyOptimizationEnv(base_url=LOCAL_SERVER_URL)
    else:
        env = EnergyOptimizationEnv(base_url=LOCAL_SERVER_URL)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset()
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            # Get action from model
            action = get_model_action(client, step, result.observation, last_reward, history)

            # Execute action
            result = await env.step(action)
            obs = result.observation

            reward = result.reward or 0.0
            done = result.done
            error = None

            # Format action for logging
            action_str = f"{action.action_type},{action.intensity:.1f}"

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

            # Update history
            history.append(f"Step {step}: {action_str} -> reward {reward:+.2f}")

            if done:
                break

        # ===== GRADER INTEGRATION (Per Hackathon Rules) =====
        # Apply the task-specific grader to evaluate performance
        try:
            grader_func = get_grader(TASK_NAME)
            grader_score = grader_func(result.observation)
            grader_metadata = get_grader_metadata(TASK_NAME)
        except Exception as e:
            print(f"[DEBUG] Grader error for task {TASK_NAME}: {e}", flush=True)
            grader_score = 0.0
            grader_metadata = None

        # Calculate final score using grader logic
        # Grader provides task-specific evaluation (0.0-1.0)
        score = grader_score

        # Log grader details
        if grader_metadata:
            print(
                f"[GRADER] task={TASK_NAME} difficulty={grader_metadata.get('difficulty', 'unknown')} "
                f"target_ram={grader_metadata.get('target_ram', 'n/a')}% "
                f"target_energy={grader_metadata.get('target_energy', 'n/a')}kWh "
                f"grader_score={grader_score:.3f}",
                flush=True,
            )

        success = score >= SUCCESS_SCORE_THRESHOLD

        # Additional logging of completions and efficiency
        total_reward = sum(rewards)
        tasks_completed = len(result.observation.tasks_completed) if result.observation.tasks_completed else 0
        efficiency_score = result.observation.efficiency_score

        print(
            f"[METRICS] total_reward={total_reward:.2f} tasks_completed={tasks_completed} "
            f"efficiency_score={efficiency_score:.3f} final_grader_score={score:.3f}",
            flush=True,
        )

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error (container cleanup): {e}", flush=True)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
