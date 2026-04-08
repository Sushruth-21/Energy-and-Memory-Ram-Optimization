#!/usr/bin/env python3
"""
Train an RL agent on the Energy Optimization Environment.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock the he_demo package for direct testing
import types
he_demo = types.ModuleType('he_demo')
from models import EnergyOptimizationAction, EnergyOptimizationObservation, Task, TaskSummary
he_demo.EnergyOptimizationAction = EnergyOptimizationAction
he_demo.EnergyOptimizationObservation = EnergyOptimizationObservation
he_demo.Task = Task
he_demo.TaskSummary = TaskSummary
sys.modules['he_demo'] = he_demo
sys.modules['he_demo.models'] = he_demo

from gym_wrapper import EnergyOptimizationGymEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

def train_agent():
    """Train a PPO agent on the energy optimization environment."""

    print("🚀 Training PPO Agent on Energy Optimization Environment")
    print("=" * 60)

    # Create vectorized environment for better training
    def make_env():
        return EnergyOptimizationGymEnv()

    env = make_vec_env(make_env, n_envs=4)

    # Create PPO agent
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        vf_coef=0.5,
        max_grad_norm=0.5,
    )

    # Train the agent
    print("Training for 10,000 timesteps...")
    model.learn(total_timesteps=10000)

    # Save the trained model
    model.save("energy_optimization_ppo")
    print("✅ Model saved as 'energy_optimization_ppo.zip'")

    # Test the trained agent
    print("\n🧪 Testing trained agent...")
    test_env = EnergyOptimizationGymEnv()
    obs, _ = test_env.reset()

    total_reward = 0
    steps = 0

    while steps < 50:
        # Get action from trained model
        action, _ = model.predict(obs, deterministic=True)

        # Execute action
        obs, reward, done, _, _ = test_env.step(action)

        total_reward += reward
        steps += 1

        # Convert action back to readable format
        action_type_index = int(action[0])
        intensity = float(action[1])
        action_types = ["reduce_ram", "optimize_energy", "balance_resources", "monitor_system"]
        action_type = action_types[action_type_index]

        print(f"Step {steps}: {action_type}({intensity:.1f}) -> RAM={obs[0]:.1f}%, Energy={obs[1]:.1f}kWh, Reward={reward:.2f}")

        if done:
            break

if __name__ == "__main__":
    train_agent()