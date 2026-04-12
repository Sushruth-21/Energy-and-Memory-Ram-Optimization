# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Energy & Memory RAM Optimization Environment."""

from he_demo.client import EnergyOptimizationEnv
from he_demo.models import EnergyOptimizationAction, EnergyOptimizationObservation, Task
from he_demo.task_graders import (
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
from he_demo.task_registry import (
    TASK_REGISTRY,
    get_all_tasks_with_graders,
    get_task_grader,
    get_tasks_count,
    is_grader_requirement_met,
)
from he_demo.grader_manifest import (
    GRADERS_MANIFEST,
    get_graders_manifest,
    get_active_graders_count,
    get_grader_names,
    is_validator_satisfied,
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
    "GRADERS_MANIFEST",
    "get_graders_manifest",
    "get_active_graders_count",
    "get_grader_names",
    "is_validator_satisfied",
]
