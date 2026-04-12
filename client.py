# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""He Demo Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from models import EnergyOptimizationAction, EnergyOptimizationObservation, Task, TaskSummary


class EnergyOptimizationEnv(
    EnvClient[EnergyOptimizationAction, EnergyOptimizationObservation, State]
):
    """
    Client for the Energy & Memory RAM Optimization Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> # Connect to a running server
        >>> with EnergyOptimizationEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(f"RAM: {result.observation.ram_usage:.1f}%, Energy: {result.observation.energy_consumption:.1f} kWh")
        ...
        ...     result = client.step(EnergyOptimizationAction(action_type="reduce_ram", intensity=0.8))
        ...     print(f"Task: {result.observation.current_task.name if result.observation.current_task else 'None'}")

    Example with Docker:
        >>> # Automatically start container and connect
        >>> client = EnergyOptimizationEnv.from_docker_image("energy-optimization-env:latest")
        >>> try:
        ...     result = client.reset()
        ...     result = client.step(EnergyOptimizationAction(action_type="balance_resources", intensity=0.6))
        ... finally:
        ...     client.close()
    """

    def _step_payload(self, action: EnergyOptimizationAction) -> Dict:
        """
        Convert EnergyOptimizationAction to JSON payload for step message.

        Args:
            action: EnergyOptimizationAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "action_type": action.action_type,
            "intensity": action.intensity,
        }

    def _parse_result(self, payload: Dict) -> StepResult[EnergyOptimizationObservation]:
        """
        Parse server response into StepResult[EnergyOptimizationObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with EnergyOptimizationObservation
        """
        obs_data = payload.get("observation", {})

        # Parse current task if present
        current_task = None
        if obs_data.get("current_task"):
            task_data = obs_data["current_task"]
            current_task = TaskSummary(
                name=task_data.get("name", ""),
                description=task_data.get("description", ""),
                difficulty=task_data.get("difficulty", 1),
                ram_target=task_data.get("ram_target", 100.0),
                energy_target=task_data.get("energy_target", 10.0),
                max_steps=task_data.get("max_steps", 10),
                completed=task_data.get("completed", False),
                remaining_steps=task_data.get("remaining_steps"),
                progress=task_data.get("progress", 0.0)
            )

        observation = EnergyOptimizationObservation(
            ram_usage=obs_data.get("ram_usage", 0.0),
            energy_consumption=obs_data.get("energy_consumption", 0.0),
            system_load=obs_data.get("system_load", 0.0),
            current_task=current_task,
            tasks_completed=obs_data.get("tasks_completed", []),
            steps_taken=obs_data.get("steps_taken", 0),
            task_progress=obs_data.get("task_progress", 0.0),
            efficiency_score=obs_data.get("efficiency_score", 0.0),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
