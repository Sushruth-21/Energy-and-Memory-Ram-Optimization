# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Energy & Memory RAM Optimization Environment Implementation.

An RL environment for training AI agents to optimize system resources including
RAM usage and energy consumption through various optimization strategies.
"""

import random
from typing import List
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from he_demo.models import EnergyOptimizationAction, EnergyOptimizationObservation, Task, TaskSummary
from he_demo.task_graders import TASK_GRADERS, get_grader, get_all_graders, get_grader_metadata


class EnergyOptimizationEnvironment(Environment):
    """
    Energy & Memory RAM Optimization Environment.

    This environment simulates a computer system where an AI agent must optimize
    RAM usage and energy consumption. The agent faces tasks of increasing difficulty
    and receives rewards based on optimization efficiency.

    Tasks include:
    - Basic RAM reduction
    - Energy optimization
    - Resource balancing
    - Advanced multi-objective optimization

    The environment includes automated graders that verify task completion and
    provide detailed feedback on optimization performance.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the energy optimization environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0

        # System state
        self.ram_usage = 80.0  # Starting RAM usage %
        self.energy_consumption = 8.0  # Starting energy consumption kWh
        self.system_load = 0.7  # Starting system load

        # Task management
        self.tasks = self._create_tasks()
        self.current_task_index = 0
        self.tasks_completed = []

        # Performance tracking
        self.baseline_ram = self.ram_usage
        self.baseline_energy = self.energy_consumption

    def _create_tasks(self) -> List[Task]:
        """Create tasks with increasing difficulty."""
        return [
            Task(
                name="basic_ram_reduction",
                description="Reduce RAM usage below 70%",
                difficulty=1,
                ram_target=70.0,
                energy_target=7.5,  # Slightly below initial 8.0
                max_steps=10
            ),
            Task(
                name="energy_optimization",
                description="Reduce energy consumption below 6 kWh while maintaining RAM below 75%",
                difficulty=2,
                ram_target=75.0,
                energy_target=6.0,
                max_steps=15
            ),
            Task(
                name="balanced_optimization",
                description="Balance RAM below 60% and energy below 5 kWh",
                difficulty=3,
                ram_target=60.0,
                energy_target=5.0,
                max_steps=20
            ),
            Task(
                name="advanced_efficiency",
                description="Achieve RAM below 50% and energy below 4 kWh",
                difficulty=4,
                ram_target=50.0,
                energy_target=4.0,
                max_steps=25
            ),
            Task(
                name="expert_optimization",
                description="Master level: RAM below 40% and energy below 3 kWh",
                difficulty=5,
                ram_target=40.0,
                energy_target=3.0,
                max_steps=30
            )
        ]

    def _get_current_task(self) -> Task:
        """Get the current task, cycling through available tasks."""
        if self.current_task_index >= len(self.tasks):
            self.current_task_index = 0
        return self.tasks[self.current_task_index]

    def _calculate_reward(self, action: EnergyOptimizationAction) -> float:
        """Calculate reward based on action effectiveness and task progress."""
        base_reward = 0.0

        # Action effectiveness rewards
        if action.action_type == "reduce_ram":
            ram_reduction = min(5.0 * action.intensity, self.ram_usage * 0.1)
            self.ram_usage = max(0.0, self.ram_usage - ram_reduction)
            base_reward += ram_reduction * 0.5  # Reward for RAM reduction

            # Penalty for excessive RAM reduction (system instability)
            if action.intensity > 0.8:
                base_reward -= 2.0

        elif action.action_type == "optimize_energy":
            energy_reduction = min(1.0 * action.intensity, self.energy_consumption * 0.15)
            self.energy_consumption = max(0.0, self.energy_consumption - energy_reduction)
            base_reward += energy_reduction * 2.0  # Higher reward for energy savings

            # Penalty for aggressive energy optimization (performance impact)
            if action.intensity > 0.9:
                self.system_load = min(1.0, self.system_load + 0.1)
                base_reward -= 1.0

        elif action.action_type == "balance_resources":
            # Balanced approach: moderate improvements to both
            ram_reduction = min(2.0 * action.intensity, self.ram_usage * 0.05)
            energy_reduction = min(0.5 * action.intensity, self.energy_consumption * 0.1)

            self.ram_usage = max(0.0, self.ram_usage - ram_reduction)
            self.energy_consumption = max(0.0, self.energy_consumption - energy_reduction)

            base_reward += (ram_reduction * 0.3 + energy_reduction * 1.5)

        elif action.action_type == "monitor_system":
            # Monitoring action: small reward for gathering information
            base_reward += 0.1
            # Slight natural system load reduction from monitoring
            self.system_load = max(0.0, self.system_load - 0.02)

        # Natural system changes (simulate real system behavior)
        self._apply_system_dynamics()

        # Task completion bonus
        current_task = self._get_current_task()
        if not current_task.completed and current_task.check_completion(
            self.ram_usage, self.energy_consumption, self._state.step_count
        ):
            current_task.completed = True
            self.tasks_completed.append(current_task.name)
            base_reward += current_task.difficulty * 10.0  # Bonus for task completion
            self.current_task_index += 1  # Move to next task

        # Efficiency bonus
        efficiency_improvement = (
            (self.baseline_ram - self.ram_usage) / self.baseline_ram +
            (self.baseline_energy - self.energy_consumption) / self.baseline_energy
        ) * 0.5
        base_reward += efficiency_improvement

        return base_reward

    def _apply_system_dynamics(self):
        """Apply natural system dynamics and external factors."""
        # Random external load changes
        if random.random() < 0.1:  # 10% chance each step
            load_change = random.uniform(-0.05, 0.05)
            self.system_load = max(0.0, min(1.0, self.system_load + load_change))

            # Load affects RAM and energy
            ram_impact = load_change * 10.0
            energy_impact = load_change * 0.5

            self.ram_usage = max(0.0, min(100.0, self.ram_usage + ram_impact))
            self.energy_consumption = max(0.0, self.energy_consumption + energy_impact)

    def _calculate_task_progress(self) -> float:
        """Calculate progress towards current task completion."""
        current_task = self._get_current_task()
        if current_task.completed:
            return 1.0

        # Calculate RAM progress (0-1 scale)
        ram_progress = max(0.0, min(1.0, (100.0 - self.ram_usage) / (100.0 - current_task.ram_target)))

        # Calculate energy progress (0-1 scale)
        energy_range = 10.0 - current_task.energy_target  # Total possible energy reduction
        if energy_range > 0:
            energy_progress = max(0.0, min(1.0, (8.0 - self.energy_consumption) / energy_range))
        else:
            energy_progress = 1.0 if self.energy_consumption <= current_task.energy_target else 0.0

        return min(1.0, (ram_progress + energy_progress) / 2.0)

    def _calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score."""
        ram_efficiency = max(0.0, (100.0 - self.ram_usage) / 100.0)
        energy_efficiency = max(0.0, (10.0 - self.energy_consumption) / 10.0)
        return (ram_efficiency + energy_efficiency) / 2.0

    def _task_to_summary(self, task: Task, steps_taken: int) -> TaskSummary:
        """Convert a Task to a TaskSummary for observations."""
        remaining_steps = max(0, task.max_steps - steps_taken) if not task.completed else 0
        progress = self._calculate_task_progress() if not task.completed else 1.0

        return TaskSummary(
            name=task.name,
            description=task.description,
            difficulty=task.difficulty,
            ram_target=task.ram_target,
            energy_target=task.energy_target,
            max_steps=task.max_steps,
            completed=task.completed,
            remaining_steps=remaining_steps,
            progress=progress
        )

    def reset(self) -> EnergyOptimizationObservation:
        """
        Reset the environment to initial state.

        Returns:
            EnergyOptimizationObservation with initial system state
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1

        # Reset system state
        self.ram_usage = 80.0
        self.energy_consumption = 8.0
        self.system_load = 0.7

        # Reset tasks
        for task in self.tasks:
            task.completed = False
        self.current_task_index = 0
        self.tasks_completed = []

        # Reset baselines
        self.baseline_ram = self.ram_usage
        self.baseline_energy = self.energy_consumption

        current_task = self._get_current_task()

        return EnergyOptimizationObservation(
            ram_usage=self.ram_usage,
            energy_consumption=self.energy_consumption,
            system_load=self.system_load,
            current_task=self._task_to_summary(current_task, 0) if current_task else None,
            tasks_completed=self.tasks_completed.copy(),
            steps_taken=0,
            task_progress=self._calculate_task_progress(),
            efficiency_score=self._calculate_efficiency_score(),
            done=False,
            reward=0.0,
        )

    def step(self, action: EnergyOptimizationAction) -> EnergyOptimizationObservation:
        """
        Execute an optimization action in the environment.

        Args:
            action: EnergyOptimizationAction containing the optimization strategy

        Returns:
            EnergyOptimizationObservation with updated system state and reward
        """
        self._state.step_count += 1

        # Calculate reward for the action
        reward = self._calculate_reward(action)

        # Check if episode should end
        done = self._state.step_count >= 100 or self.current_task_index >= len(self.tasks)

        current_task = self._get_current_task()

        return EnergyOptimizationObservation(
            ram_usage=self.ram_usage,
            energy_consumption=self.energy_consumption,
            system_load=self.system_load,
            current_task=self._task_to_summary(current_task, self._state.step_count) if current_task else None,
            tasks_completed=self.tasks_completed.copy(),
            steps_taken=self._state.step_count,
            task_progress=self._calculate_task_progress(),
            efficiency_score=self._calculate_efficiency_score(),
            done=done,
            reward=reward,
            metadata={
                "action_taken": action.action_type,
                "action_intensity": action.intensity,
                "episode_step": self._state.step_count,
                "current_task_name": current_task.name if current_task else None
            },
        )

    @property
    def state(self) -> State:
        """
        Get the current environment state.

        Returns:
            Current State with episode_id and step_count
        """
        return self._state

    @property
    def graders(self):
        """
        Get all task graders for this environment.
        
        Returns:
            Dictionary mapping task names to grader functions
        """
        return get_all_graders()
    
    @property
    def grader_metadata(self):
        """
        Get metadata about all available graders.
        
        Returns:
            Dictionary with metadata for each task grader
        """
        return get_grader_metadata()
    
    def grade_task(self, task_name: str, observation: EnergyOptimizationObservation) -> float:
        """
        Grade performance on a specific task.
        
        Args:
            task_name: Name of the task to grade
            observation: Observation to grade
            
        Returns:
            Score from 0.0 (worst) to 1.0 (best)
        """
        grader = get_grader(task_name)
        return grader(observation)
