"""
Task Registry with Explicit Grader Mappings

This module provides a registry of all tasks with their corresponding graders
for easy discovery and validation.
"""

from typing import Dict, Callable, Any
from he_demo.task_graders import (
    task_1_basic_ram_reduction_grader,
    task_2_energy_optimization_grader,
    task_3_balanced_optimization_grader,
    task_4_advanced_efficiency_grader,
    task_5_expert_optimization_grader,
)

# Explicit registry of tasks with graders
TASK_REGISTRY: Dict[str, Dict[str, Any]] = {
    "basic_ram_reduction": {
        "task_name": "basic_ram_reduction",
        "display_name": "Basic RAM Reduction",
        "difficulty": 1,
        "grader": task_1_basic_ram_reduction_grader,
        "grader_name": "task_1_basic_ram_reduction_grader",
        "description": "Reduce RAM usage below 70%"
    },
    "energy_optimization": {
        "task_name": "energy_optimization",
        "display_name": "Energy Optimization",
        "difficulty": 2,
        "grader": task_2_energy_optimization_grader,
        "grader_name": "task_2_energy_optimization_grader",
        "description": "Reduce energy consumption below 6 kWh while maintaining RAM below 75%"
    },
    "balanced_optimization": {
        "task_name": "balanced_optimization",
        "display_name": "Balanced Optimization",
        "difficulty": 3,
        "grader": task_3_balanced_optimization_grader,
        "grader_name": "task_3_balanced_optimization_grader",
        "description": "Balance RAM below 60% and energy below 5 kWh"
    },
    "advanced_efficiency": {
        "task_name": "advanced_efficiency",
        "display_name": "Advanced Efficiency",
        "difficulty": 4,
        "grader": task_4_advanced_efficiency_grader,
        "grader_name": "task_4_advanced_efficiency_grader",
        "description": "Achieve RAM below 50% and energy below 4 kWh"
    },
    "expert_optimization": {
        "task_name": "expert_optimization",
        "display_name": "Expert Optimization",
        "difficulty": 5,
        "grader": task_5_expert_optimization_grader,
        "grader_name": "task_5_expert_optimization_grader",
        "description": "Master level: RAM below 40% and energy below 3 kWh"
    }
}


def get_all_tasks_with_graders() -> Dict[str, Dict[str, Any]]:
    """Get all tasks with their associated graders."""
    return TASK_REGISTRY


def get_task_grader(task_name: str) -> Callable:
    """Get the grader for a specific task."""
    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Unknown task: {task_name}")
    return TASK_REGISTRY[task_name]["grader"]


def get_tasks_count() -> int:
    """Get the total number of tasks with graders."""
    return len(TASK_REGISTRY)


def is_grader_requirement_met() -> bool:
    """Check if minimum grader requirement (3 tasks) is met."""
    return len(TASK_REGISTRY) >= 3


if __name__ == "__main__":
    print(f"Total tasks with graders: {get_tasks_count()}")
    print(f"Requirement met (≥3): {is_grader_requirement_met()}")
    print("\nTasks:")
    for task_name, info in TASK_REGISTRY.items():
        print(f"  - {info['display_name']} (Difficulty {info['difficulty']})")
        print(f"    Grader: {info['grader_name']}")
