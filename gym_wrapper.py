#!/usr/bin/env python3
"""
Gym wrapper for the Energy Optimization Environment.
"""

import sys
import os
import gymnasium as gym
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))

# Import from root level modules
from models import EnergyOptimizationAction, EnergyOptimizationObservation, Task, TaskSummary
from server.he_demo_environment import EnergyOptimizationEnvironment

class EnergyOptimizationGymEnv(gym.Env):
    """Gym wrapper for the Energy Optimization Environment."""

    def __init__(self):
        super().__init__()

        # Create the underlying environment
        self.env = EnergyOptimizationEnvironment()

        # Define action and observation spaces
        # Actions: [action_type_index, intensity]
        # action_type_index: 0=reduce_ram, 1=optimize_energy, 2=balance_resources, 3=monitor_system
        self.action_space = gym.spaces.Box(
            low=np.array([0, 0.0]),
            high=np.array([3, 1.0]),
            dtype=np.float32
        )

        # Observations: [ram_usage, energy_consumption, system_load, task_progress, efficiency_score, steps_taken]
        self.observation_space = gym.spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0]),
            high=np.array([100.0, 10.0, 1.0, 1.0, 1.0, 100]),
            dtype=np.float32
        )

    def reset(self, **kwargs):
        """Reset the environment."""
        obs = self.env.reset()
        return self._obs_to_array(obs), {}

    def step(self, action):
        """Execute an action in the environment."""
        # Convert action array to EnergyOptimizationAction
        action_type_index = int(action[0])
        intensity = float(action[1])

        action_types = ["reduce_ram", "optimize_energy", "balance_resources", "monitor_system"]
        action_type = action_types[action_type_index]

        action_obj = EnergyOptimizationAction(action_type=action_type, intensity=intensity)
        obs = self.env.step(action_obj)

        # Convert observation to array
        obs_array = self._obs_to_array(obs)

        # Check if episode is done
        done = obs.done

        # Return reward
        reward = obs.reward

        return obs_array, reward, done, False, {}

    def _obs_to_array(self, obs):
        """Convert EnergyOptimizationObservation to numpy array."""
        return np.array([
            obs.ram_usage,
            obs.energy_consumption,
            obs.system_load,
            obs.task_progress,
            obs.efficiency_score,
            obs.steps_taken
        ], dtype=np.float32)

    def render(self, mode="human"):
        """Render the environment."""
        obs = self.env._get_current_observation()
        if obs:
            print(f"RAM: {obs.ram_usage:.1f}%, Energy: {obs.energy_consumption:.1f}kWh, "
                  f"Task: {obs.current_task.name if obs.current_task else 'None'}, "
                  f"Progress: {obs.task_progress:.2f}")

    def close(self):
        """Close the environment."""
        pass