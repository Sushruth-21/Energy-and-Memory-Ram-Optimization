#!/usr/bin/env python3
"""
Test script for the Energy & Memory RAM Optimization Environment.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Mock the he_demo package for testing
import types
he_demo = types.ModuleType('he_demo')

# Import models and add to he_demo
from models import EnergyOptimizationAction, EnergyOptimizationObservation, Task, TaskSummary
he_demo.EnergyOptimizationAction = EnergyOptimizationAction
he_demo.EnergyOptimizationObservation = EnergyOptimizationObservation
he_demo.Task = Task
he_demo.TaskSummary = TaskSummary

# Add to sys.modules
sys.modules['he_demo'] = he_demo
sys.modules['he_demo.models'] = he_demo

# Now import the environment
from he_demo.server.he_demo_environment import EnergyOptimizationEnvironment

def test_environment():
    """Test the energy optimization environment."""
    print("Testing Energy & Memory RAM Optimization Environment")
    print("=" * 60)

    # Create environment
    env = EnergyOptimizationEnvironment()

    # Test reset
    print("\n1. Testing reset...")
    obs = env.reset()
    print(f"Initial RAM usage: {obs.ram_usage:.1f}%")
    print(f"Initial energy consumption: {obs.energy_consumption:.1f} kWh")
    print(f"Initial system load: {obs.system_load:.2f}")
    print(f"Current task: {obs.current_task.name if obs.current_task else 'None'}")
    print(f"Tasks completed: {obs.tasks_completed}")

    # Test different actions
    actions_to_test = [
        ("reduce_ram", 0.8),
        ("optimize_energy", 0.7),
        ("balance_resources", 0.6),
        ("monitor_system", 0.5)
    ]

    print("\n2. Testing actions...")
    for action_type, intensity in actions_to_test:
        action = EnergyOptimizationAction(action_type=action_type, intensity=intensity)
        obs = env.step(action)

        print(f"\nAction: {action_type} (intensity: {intensity})")
        print(f"RAM usage: {obs.ram_usage:.1f}%")
        print(f"Energy consumption: {obs.energy_consumption:.1f} kWh")
        print(f"System load: {obs.system_load:.2f}")
        print(f"Reward: {obs.reward:.2f}")
        print(f"Task progress: {obs.task_progress:.2f}")
        print(f"Efficiency score: {obs.efficiency_score:.2f}")
        print(f"Current task: {obs.current_task.name if obs.current_task else 'None'}")
        print(f"Tasks completed: {obs.tasks_completed}")

        if obs.done:
            print("Episode completed!")
            break

    print("\n3. Testing task progression...")
    # Reset and try to complete a task
    obs = env.reset()
    steps = 0
    max_test_steps = 20

    while not obs.done and steps < max_test_steps:
        # Simple strategy: alternate between RAM reduction and energy optimization
        if steps % 2 == 0:
            action = EnergyOptimizationAction(action_type="reduce_ram", intensity=0.9)
        else:
            action = EnergyOptimizationAction(action_type="optimize_energy", intensity=0.8)

        obs = env.step(action)
        steps += 1

        print(f"Step {steps}: RAM={obs.ram_usage:.1f}%, Energy={obs.energy_consumption:.1f}kWh, Reward={obs.reward:.2f}")

        if obs.current_task and obs.task_progress >= 1.0:
            print(f"Task '{obs.current_task.name}' completed!")
            break

    print("\nTest completed successfully!")
    print(f"Final state: RAM={obs.ram_usage:.1f}%, Energy={obs.energy_consumption:.1f}kWh")
    print(f"Tasks completed: {len(obs.tasks_completed)}")
    print(f"Total steps: {steps}")

if __name__ == "__main__":
    test_environment()