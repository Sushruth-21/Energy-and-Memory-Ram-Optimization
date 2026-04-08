# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Energy & Memory RAM Optimization Environment.

This environment simulates system resource optimization tasks where an AI agent
must optimize RAM usage and energy consumption through various actions.
"""

from typing import List, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


class EnergyOptimizationAction(Action):
    """Action for the Energy & Memory RAM Optimization environment."""

    action_type: str = Field(
        ...,
        description="Type of optimization action: 'reduce_ram', 'optimize_energy', 'balance_resources', 'monitor_system'"
    )
    intensity: float = Field(
        1.0,
        description="Intensity of the action (0.0 to 1.0), affects effectiveness and potential side effects"
    )


class Task(BaseModel):
    """Represents an optimization task with difficulty and requirements."""

    name: str = Field(..., description="Unique name of the task")
    description: str = Field(..., description="Human-readable description of the task")
    difficulty: int = Field(..., description="Difficulty level (1-5)")
    ram_target: float = Field(..., description="Target RAM usage percentage (lower is better)")
    energy_target: float = Field(..., description="Target energy consumption (lower is better)")
    max_steps: int = Field(..., description="Maximum steps allowed to complete the task")
    completed: bool = Field(default=False, description="Whether the task has been completed")

    def check_completion(self, ram_usage: float, energy_consumption: float, steps_taken: int) -> bool:
        """Check if the task is completed based on current system state."""
        if steps_taken > self.max_steps:
            return False
        return ram_usage <= self.ram_target and energy_consumption <= self.energy_target


class TaskSummary(BaseModel):
    """Serializable task summary exposed in observations."""

    name: str = Field(..., description="Task identifier")
    description: str = Field(..., description="Task description")
    difficulty: int = Field(..., description="Task difficulty level")
    ram_target: float = Field(..., description="RAM usage target percentage")
    energy_target: float = Field(..., description="Energy consumption target in kWh")
    max_steps: int = Field(..., description="Maximum allowed steps for the task")
    completed: bool = Field(False, description="Whether the task is completed")
    remaining_steps: Optional[int] = Field(None, description="Remaining steps before the task deadline")
    progress: float = Field(..., description="Estimated progress toward task completion (0-1)")


class EnergyOptimizationObservation(Observation):
    """Observation from the Energy & Memory RAM Optimization environment."""

    ram_usage: float = Field(..., description="Current RAM usage percentage (0-100)")
    energy_consumption: float = Field(..., description="Current energy consumption in kWh")
    system_load: float = Field(..., description="Overall system load (0-1)")
    current_task: Optional[TaskSummary] = Field(None, description="Current optimization task")
    tasks_completed: List[str] = Field(default_factory=list, description="List of completed task names")
    steps_taken: int = Field(..., description="Number of steps taken in current episode")
    task_progress: float = Field(..., description="Progress towards current task completion (0-1)")
    efficiency_score: float = Field(..., description="Overall efficiency score based on optimization")
