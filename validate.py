#!/usr/bin/env python3
"""
Final validation script for the Energy & Memory RAM Optimization Environment.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Mock the he_demo package
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
from server.he_demo_environment import EnergyOptimizationEnvironment

def main():
    print("🔋 Energy & Memory RAM Optimization Environment - Final Validation")
    print("=" * 70)

    try:
        # Create environment
        env = EnergyOptimizationEnvironment()
        print("✅ Environment created successfully")

        # Test reset
        obs = env.reset()
        print("✅ Environment reset successfully")
        print(f"   Initial RAM: {obs.ram_usage:.1f}%")
        print(f"   Initial Energy: {obs.energy_consumption:.1f} kWh")
        print(f"   Current Task: {obs.current_task.name if obs.current_task else 'None'}")

        # Test a few actions
        actions = [
            ("reduce_ram", 0.8),
            ("optimize_energy", 0.7),
            ("balance_resources", 0.6)
        ]

        for action_type, intensity in actions:
            action = EnergyOptimizationAction(action_type=action_type, intensity=intensity)
            obs = env.step(action)
            print(f"✅ Action '{action_type}' executed: RAM={obs.ram_usage:.1f}%, Energy={obs.energy_consumption:.1f}kWh, Reward={obs.reward:.2f}")

        print("\n🎉 All validation tests passed!")
        print("🚀 The Energy & Memory RAM Optimization Environment is ready for deployment!")

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()