# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Task graders for the Energy & Memory RAM Optimization Environment.

Each grader function evaluates agent performance on a specific task,
returning a score from 0.0 (worst) to 1.0 (best).

This module is intentionally self-contained with NO external dependencies
beyond the Python standard library, so it can always be imported by the
OpenEnv validator regardless of whether openenv-core or other packages
are installed in the validation environment.
"""

# Explicit exports for validator discovery
__all__ = [
    'grade_basic_ram_reduction',
    'grade_energy_optimization',
    'grade_balanced_optimization',
    'grade_advanced_efficiency',
    'grade_expert_optimization',
]


def grade_basic_ram_reduction(observation) -> float:
    """Grade performance on basic RAM reduction task: Reduce RAM usage below 70%."""
    ram_usage = getattr(observation, 'ram_usage', 100.0)
    energy_consumption = getattr(observation, 'energy_consumption', 10.0)
    steps_taken = getattr(observation, 'steps_taken', 0)

    # Target: RAM <= 70%, Energy <= 7.5 kWh, within 10 steps
    ram_score = max(0.0, min(1.0, (100.0 - ram_usage) / (100.0 - 70.0)))
    energy_score = max(0.0, min(1.0, (10.0 - energy_consumption) / (10.0 - 7.5)))
    step_penalty = 1.0 if steps_taken <= 10 else max(0.0, 1.0 - (steps_taken - 10) * 0.1)

    return (ram_score + energy_score) / 2.0 * step_penalty


def grade_energy_optimization(observation) -> float:
    """Grade performance on energy optimization task: Reduce energy below 6 kWh while maintaining RAM below 75%."""
    ram_usage = getattr(observation, 'ram_usage', 100.0)
    energy_consumption = getattr(observation, 'energy_consumption', 10.0)
    steps_taken = getattr(observation, 'steps_taken', 0)

    # Target: RAM <= 75%, Energy <= 6.0 kWh, within 15 steps
    ram_score = max(0.0, min(1.0, (100.0 - ram_usage) / (100.0 - 75.0)))
    energy_score = max(0.0, min(1.0, (10.0 - energy_consumption) / (10.0 - 6.0)))
    step_penalty = 1.0 if steps_taken <= 15 else max(0.0, 1.0 - (steps_taken - 15) * 0.1)

    return (ram_score + energy_score) / 2.0 * step_penalty


def grade_balanced_optimization(observation) -> float:
    """Grade performance on balanced optimization task: Balance RAM below 60% and energy below 5 kWh."""
    ram_usage = getattr(observation, 'ram_usage', 100.0)
    energy_consumption = getattr(observation, 'energy_consumption', 10.0)
    steps_taken = getattr(observation, 'steps_taken', 0)

    # Target: RAM <= 60%, Energy <= 5.0 kWh, within 20 steps
    ram_score = max(0.0, min(1.0, (100.0 - ram_usage) / (100.0 - 60.0)))
    energy_score = max(0.0, min(1.0, (10.0 - energy_consumption) / (10.0 - 5.0)))
    step_penalty = 1.0 if steps_taken <= 20 else max(0.0, 1.0 - (steps_taken - 20) * 0.1)

    return (ram_score + energy_score) / 2.0 * step_penalty


def grade_advanced_efficiency(observation) -> float:
    """Grade performance on advanced efficiency task: Achieve RAM below 50% and energy below 4 kWh."""
    ram_usage = getattr(observation, 'ram_usage', 100.0)
    energy_consumption = getattr(observation, 'energy_consumption', 10.0)
    steps_taken = getattr(observation, 'steps_taken', 0)

    # Target: RAM <= 50%, Energy <= 4.0 kWh, within 25 steps
    ram_score = max(0.0, min(1.0, (100.0 - ram_usage) / (100.0 - 50.0)))
    energy_score = max(0.0, min(1.0, (10.0 - energy_consumption) / (10.0 - 4.0)))
    step_penalty = 1.0 if steps_taken <= 25 else max(0.0, 1.0 - (steps_taken - 25) * 0.1)

    return (ram_score + energy_score) / 2.0 * step_penalty


def grade_expert_optimization(observation) -> float:
    """Grade performance on expert optimization task: Master level - RAM below 40% and energy below 3 kWh."""
    ram_usage = getattr(observation, 'ram_usage', 100.0)
    energy_consumption = getattr(observation, 'energy_consumption', 10.0)
    steps_taken = getattr(observation, 'steps_taken', 0)

    # Target: RAM <= 40%, Energy <= 3.0 kWh, within 30 steps
    ram_score = max(0.0, min(1.0, (100.0 - ram_usage) / (100.0 - 40.0)))
    energy_score = max(0.0, min(1.0, (10.0 - energy_consumption) / (10.0 - 3.0)))
    step_penalty = 1.0 if steps_taken <= 30 else max(0.0, 1.0 - (steps_taken - 30) * 0.1)

    return (ram_score + energy_score) / 2.0 * step_penalty