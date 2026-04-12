# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Task Graders for Energy & Memory RAM Optimization Environment.

This module defines explicit graders for each task that evaluate agent performance
on a 0.0-1.0 scale. Each grader calculates scores based on:
- RAM usage optimization (percentage reduction from baseline)
- Energy consumption optimization (kWh reduction)
- Efficiency within step limits
- Real-world optimization metrics

The graders are exposed through the TASK_GRADERS registry for easy discovery.
"""

from typing import Callable, Dict, Any
from models import EnergyOptimizationObservation


# Explicit exports for validator tool discovery
__all__ = [
    'task_1_basic_ram_reduction_grader',
    'task_2_energy_optimization_grader',
    'task_3_balanced_optimization_grader',
    'task_4_advanced_efficiency_grader',
    'task_5_expert_optimization_grader',
    'TASK_GRADERS',
    'get_grader',
    'get_all_graders',
    'get_grader_metadata',
]


# ============================================================================
# TASK 1: Basic RAM Reduction (Easy Level - Difficulty 1)
# ============================================================================

def task_1_basic_ram_reduction_grader(observation: EnergyOptimizationObservation) -> float:
    """
    Grade Task 1: Basic RAM Reduction
    
    Target: Reduce RAM usage below 70%, Energy below 7.5 kWh within 10 steps.
    
    Real-world application: Reducing memory footprint is critical for:
    - Running applications on resource-constrained devices
    - Improving system responsiveness during high loads
    - Preventing out-of-memory errors on edge devices
    
    Scoring:
    - RAM Score: 0.0 (80% baseline) → 1.0 (70% target)
    - Energy Score: 0.0 (8.0 kWh baseline) → 1.0 (7.5 kWh target)
    - Step Efficiency: Penalty if exceeding 10 steps
    
    Args:
        observation: Current environment observation
        
    Returns:
        Score from 0.0 (worst) to 1.0 (best)
    """
    # Target thresholds
    ram_target = 70.0
    energy_target = 7.5
    max_steps = 10
    
    # Baseline values for scoring normalization
    ram_baseline = 100.0  # Maximum possible RAM
    energy_baseline = 10.0  # Maximum possible energy
    
    # Calculate RAM score: how close we are to the target (lower is better)
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    
    # Calculate Energy score: how close we are to the target (lower is better)
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    # Step efficiency penalty: agent should complete within max_steps
    if observation.steps_taken <= max_steps:
        step_efficiency = 1.0
    else:
        # Penalty of 10% per step over limit
        step_efficiency = max(0.0, 1.0 - (observation.steps_taken - max_steps) * 0.1)
    
    # Combined score: 40% RAM, 40% Energy, 20% Step Efficiency
    composite_score = (ram_score * 0.4) + (energy_score * 0.4) + (step_efficiency * 0.2)
    
    # Clamp strictly between 0 and 1 (not including endpoints)
    # Validator requires 0 < score < 1
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


# ============================================================================
# TASK 2: Energy Optimization (Medium Level - Difficulty 2)
# ============================================================================

def task_2_energy_optimization_grader(observation: EnergyOptimizationObservation) -> float:
    """
    Grade Task 2: Energy Optimization
    
    Target: Reduce energy consumption below 6 kWh while keeping RAM below 75% within 15 steps.
    
    Real-world application: Energy optimization is essential for:
    - Data centers reducing operational costs and carbon footprint
    - Mobile/IoT devices extending battery life
    - Cloud providers meeting sustainability goals
    
    Scoring:
    - Energy Score: 0.0 (8.0 kWh) → 1.0 (6.0 kWh target) [Primary focus - 50%]
    - RAM Constraint Score: Penalty if RAM > 75% [Constraint - 25%]
    - Step Efficiency: Bonus for completing within 15 steps [Efficiency - 25%]
    
    Args:
        observation: Current environment observation
        
    Returns:
        Score from 0.0 (worst) to 1.0 (best)
    """
    # Target thresholds
    ram_constraint = 75.0  # Must stay below this
    energy_target = 6.0  # Primary optimization target
    max_steps = 15
    
    # Baseline values
    energy_baseline = 10.0
    
    # Primary objective: Energy reduction
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    # Constraint: RAM must not exceed threshold
    if observation.ram_usage <= ram_constraint:
        ram_constraint_score = 1.0
    else:
        # Penalty for every 1% over constraint (max 1%)
        overage = observation.ram_usage - ram_constraint
        ram_constraint_score = max(0.0, 1.0 - (overage / 5.0))  # 5% buffer before full penalty
    
    # Step efficiency
    if observation.steps_taken <= max_steps:
        step_efficiency = 1.0
    else:
        step_efficiency = max(0.0, 1.0 - (observation.steps_taken - max_steps) * 0.08)
    
    # Combined: Energy (50%), RAM Constraint (25%), Step Efficiency (25%)
    composite_score = (energy_score * 0.5) + (ram_constraint_score * 0.25) + (step_efficiency * 0.25)
    
    # Clamp strictly between 0 and 1 (not including endpoints)
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


# ============================================================================
# TASK 3: Balanced Optimization (Hard Level - Difficulty 3)
# ============================================================================

def task_3_balanced_optimization_grader(observation: EnergyOptimizationObservation) -> float:
    """
    Grade Task 3: Balanced Optimization
    
    Target: Balance RAM below 60% and energy below 5 kWh within 20 steps.
    
    Real-world application: Balanced optimization is required for:
    - Production systems requiring both memory and energy efficiency
    - Cloud services managing multi-tenant workloads
    - Edge computing with dual constraints
    
    Scoring:
    - RAM Score: 0.0 (100%) → 1.0 (60% target) [50%]
    - Energy Score: 0.0 (10 kWh) → 1.0 (5 kWh target) [50%]
    - Step Efficiency Bonus: Extra credit for quick completion
    
    Args:
        observation: Current environment observation
        
    Returns:
        Score from 0.0 (worst) to 1.0 (best)
    """
    # Target thresholds
    ram_target = 60.0
    energy_target = 5.0
    max_steps = 20
    
    # Baseline values
    ram_baseline = 100.0
    energy_baseline = 10.0
    
    # Equal weighting for both objectives
    ram_score = max(0.0, min(1.0, (ram_baseline - observation.ram_usage) / (ram_baseline - ram_target)))
    energy_score = max(0.0, min(1.0, (energy_baseline - observation.energy_consumption) / (energy_baseline - energy_target)))
    
    # Balance score: both must be optimized equally
    balance_score = (ram_score + energy_score) / 2.0
    
    # Step efficiency bonus
    if observation.steps_taken <= max_steps:
        step_bonus = min(0.1, (max_steps - observation.steps_taken) / max_steps * 0.1)  # Up to 10% bonus
    else:
        step_bonus = max(-0.2, -(observation.steps_taken - max_steps) * 0.05)  # Up to -20% penalty
    
    # Combined: Balance (90%) + Step Bonus (10%)
    composite_score = (balance_score * 0.9) + step_bonus
    
    # Clamp strictly between 0 and 1 (not including endpoints)
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


# ============================================================================
# TASK 4: Advanced Efficiency (Hard Level - Difficulty 4)
# ============================================================================

def task_4_advanced_efficiency_grader(observation: EnergyOptimizationObservation) -> float:
    """
    Grade Task 4: Advanced Efficiency
    
    Target: Achieve RAM below 50% and energy below 4 kWh within 25 steps.
    """
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
        
    composite_score = (balance_score * 0.9) + step_bonus
    
    # Clamp strictly between 0 and 1 (not including endpoints)
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


# ============================================================================
# TASK 5: Expert Optimization (Master Level - Difficulty 5)
# ============================================================================

def task_5_expert_optimization_grader(observation: EnergyOptimizationObservation) -> float:
    """
    Grade Task 5: Expert Optimization
    
    Target: Master level: RAM below 40% and energy below 3 kWh within 30 steps.
    """
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
        
    composite_score = (balance_score * 0.9) + step_bonus
    
    # Clamp strictly between 0 and 1 (not including endpoints)
    clamped_score = max(0.001, min(0.999, composite_score))
    return round(clamped_score, 3)


# ============================================================================
# Registry and Metadata
# ============================================================================

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
    """
    Get the grader function for a specific task.
    
    Args:
        task_name: Name of the task
        
    Returns:
        Grader function that takes an observation and returns a float score (0.0-1.0)
    """
    if task_name not in TASK_GRADERS:
        raise ValueError(f"Unknown task: {task_name}. Available tasks: {list(TASK_GRADERS.keys())}")
    return TASK_GRADERS[task_name]["grader"]


def get_all_graders() -> Dict[str, Callable]:
    """
    Get all available graders.
    
    Returns:
        Dictionary mapping task names to grader functions
    """
    return {name: metadata["grader"] for name, metadata in TASK_GRADERS.items()}


def get_grader_metadata(task_name: str = None) -> Dict[str, Any]:
    """
    Get metadata about graders.
    
    Args:
        task_name: Specific task name, or None for all tasks
        
    Returns:
        Metadata dictionary for the task(s)
    """
    if task_name:
        if task_name not in TASK_GRADERS:
            raise ValueError(f"Unknown task: {task_name}")
        # Return metadata without the grader function (for JSON serialization)
        return {k: v for k, v in TASK_GRADERS[task_name].items() if k != "grader"}
    else:
        # Return all metadata
        return {name: {k: v for k, v in metadata.items() if k != "grader"} 
                for name, metadata in TASK_GRADERS.items()}


if __name__ == "__main__":
    # Example usage and testing
    print("Available Task Graders:")
    print("=" * 80)
    for task_name, metadata in TASK_GRADERS.items():
        print(f"\n{metadata['display_name']} (Difficulty {metadata['difficulty']})")
        print(f"  Name: {task_name}")
        print(f"  Description: {metadata['description']}")
        print(f"  Targets: RAM < {metadata['target_ram']}%, Energy < {metadata['target_energy']} kWh")
        print(f"  Max Steps: {metadata['max_steps']}")
        print(f"  Real-world: {metadata['real_world_application']}")
