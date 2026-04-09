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

    def grade(self, ram_usage: float, energy_consumption: float, steps_taken: int) -> float:
        """Grade the task performance with a score from 0.0 to 1.0."""
        if steps_taken > self.max_steps:
            return 0.0
        
        # Calculate RAM score (0-1, higher is better for lower RAM)
        ram_score = max(0.0, min(1.0, (100.0 - ram_usage) / (100.0 - self.ram_target)))
        
        # Calculate energy score (0-1, higher is better for lower energy)
        energy_score = max(0.0, min(1.0, (10.0 - energy_consumption) / (10.0 - self.energy_target)))
        
        # Combine scores with equal weighting
        return (ram_score + energy_score) / 2.0


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


# Task graders that return scores from 0.0 to 1.0
def grade_basic_ram_reduction(observation: EnergyOptimizationObservation) -> float:
    """Grade performance on basic RAM reduction task."""
    task = Task(
        name="basic_ram_reduction",
        description="Reduce RAM usage below 70%",
        difficulty=1,
        ram_target=70.0,
        energy_target=7.5,
        max_steps=10
    )
    return task.grade(observation.ram_usage, observation.energy_consumption, observation.steps_taken)


def grade_energy_optimization(observation: EnergyOptimizationObservation) -> float:
    """Grade performance on energy optimization task."""
    task = Task(
        name="energy_optimization", 
        description="Reduce energy consumption below 6 kWh while maintaining RAM below 75%",
        difficulty=2,
        ram_target=75.0,
        energy_target=6.0,
        max_steps=15
    )
    return task.grade(observation.ram_usage, observation.energy_consumption, observation.steps_taken)


def grade_balanced_optimization(observation: EnergyOptimizationObservation) -> float:
    """Grade performance on balanced optimization task."""
    task = Task(
        name="balanced_optimization",
        description="Balance RAM below 60% and energy below 5 kWh",
        difficulty=3,
        ram_target=60.0,
        energy_target=5.0,
        max_steps=20
    )
    return task.grade(observation.ram_usage, observation.energy_consumption, observation.steps_taken)


def grade_advanced_efficiency(observation: EnergyOptimizationObservation) -> float:
    """Grade performance on advanced efficiency task."""
    task = Task(
        name="advanced_efficiency",
        description="Achieve RAM below 50% and energy below 4 kWh",
        difficulty=4,
        ram_target=50.0,
        energy_target=4.0,
        max_steps=25
    )
    return task.grade(observation.ram_usage, observation.energy_consumption, observation.steps_taken)


def grade_expert_optimization(observation: EnergyOptimizationObservation) -> float:
    """Grade performance on expert optimization task."""
    task = Task(
        name="expert_optimization",
        description="Master level: RAM below 40% and energy below 3 kWh",
        difficulty=5,
        ram_target=40.0,
        energy_target=3.0,
        max_steps=30
    )
    return task.grade(observation.ram_usage, observation.energy_consumption, observation.steps_taken)
