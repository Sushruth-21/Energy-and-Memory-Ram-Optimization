"""
Grader Manifest - Explicit declaration of all available task graders.

This module provides a manifest that makes graders discoverable by validator tools.
"""

# Explicit list of graders for validator detection
GRADERS_MANIFEST = {
    "graders": [
        {
            "id": "task_1_basic_ram_reduction_grader",
            "name": "basic_ram_reduction",
            "type": "task_grader",
            "version": "1.0",
            "score_range": (0.001, 0.999),
            "enabled": True
        },
        {
            "id": "task_2_energy_optimization_grader",
            "name": "energy_optimization",
            "type": "task_grader",
            "version": "1.0",
            "score_range": (0.001, 0.999),
            "enabled": True
        },
        {
            "id": "task_3_balanced_optimization_grader",
            "name": "balanced_optimization",
            "type": "task_grader",
            "version": "1.0",
            "score_range": (0.001, 0.999),
            "enabled": True
        },
        {
            "id": "task_4_advanced_efficiency_grader",
            "name": "advanced_efficiency",
            "type": "task_grader",
            "version": "1.0",
            "score_range": (0.001, 0.999),
            "enabled": True
        },
        {
            "id": "task_5_expert_optimization_grader",
            "name": "expert_optimization",
            "type": "task_grader",
            "version": "1.0",
            "score_range": (0.001, 0.999),
            "enabled": True
        }
    ],
    "validation": {
        "requirement": "At least 3 tasks with graders",
        "minimum_required": 3,
        "actual_count": 5,
        "status": "PASS"
    },
    "metadata": {
        "environment": "Energy & Memory RAM Optimization",
        "description": "RL environment for optimizing system resources",
        "total_graders": 5,
        "all_enabled": True
    }
}


def get_graders_manifest():
    """Get the graders manifest for validator detection."""
    return GRADERS_MANIFEST


def get_active_graders_count():
    """Get count of active graders."""
    return sum(1 for g in GRADERS_MANIFEST["graders"] if g.get("enabled", True))


def get_grader_names():
    """Get list of all grader names."""
    return [g["name"] for g in GRADERS_MANIFEST["graders"]]


def is_validator_satisfied():
    """Check if grader requirements are satisfied."""
    return get_active_graders_count() >= GRADERS_MANIFEST["validation"]["minimum_required"]
