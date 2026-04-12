# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Energy & Memory RAM Optimization Environment."""

from .client import EnergyOptimizationEnv
from .models import EnergyOptimizationAction, EnergyOptimizationObservation, Task
from .task_graders import (
    TASK_GRADERS,
    get_grader,
    get_all_graders,
    get_grader_metadata,
    task_1_basic_ram_reduction_grader,
    task_2_energy_optimization_grader,
    task_3_balanced_optimization_grader,
    task_4_advanced_efficiency_grader,
    task_5_expert_optimization_grader,
)
from .task_registry import (
    TASK_REGISTRY,
    get_all_tasks_with_graders,
    get_task_grader,
    get_tasks_count,
    is_grader_requirement_met,
)

__all__ = [
    "EnergyOptimizationAction",
    "EnergyOptimizationObservation",
    "Task",
    "EnergyOptimizationEnv",
    "TASK_GRADERS",
    "get_grader",
    "get_all_graders",
    "get_grader_metadata",
    "task_1_basic_ram_reduction_grader",
    "task_2_energy_optimization_grader",
    "task_3_balanced_optimization_grader",
    "task_4_advanced_efficiency_grader",
    "task_5_expert_optimization_grader",
    "TASK_REGISTRY",
    "get_all_tasks_with_graders",
    "get_task_grader",
    "get_tasks_count",
    "is_grader_requirement_met",
]
