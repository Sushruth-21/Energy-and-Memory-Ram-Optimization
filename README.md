---
title: Energy & Memory RAM Optimization Environment
emoji: ⚡
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - reinforcement-learning
  - energy-optimization
  - resource-management
---

# Energy & Memory RAM Optimization RL Environment

An OpenEnv-based reinforcement learning environment for training AI agents to optimize energy consumption and RAM usage in computer systems. The environment features tasks of increasing difficulty, automated graders for task completion verification, and sophisticated reward logic.

## Features

### AI Agent Capabilities
- **Resource Detection**: Real-time monitoring of RAM usage and energy consumption
- **Optimization Strategies**: Multiple action types for different optimization approaches
- **Adaptive Learning**: Agents learn to balance competing objectives (RAM vs energy efficiency)

### Task Progression
Tasks increase in difficulty from basic resource reduction to advanced multi-objective optimization:

1. **Basic RAM Reduction**: Reduce RAM usage below 70%
2. **Energy Optimization**: Reduce energy consumption below 6 kWh while maintaining RAM below 75%
3. **Balanced Optimization**: Balance RAM below 60% and energy below 5 kWh
4. **Advanced Efficiency**: Achieve RAM below 50% and energy below 4 kWh
5. **Expert Optimization**: Master level: RAM below 40% and energy below 3 kWh

### Automated Graders
- **Task Completion Verification**: Automatic checking of optimization targets
- **Performance Metrics**: Efficiency scores and progress tracking
- **Reward Validation**: Ensures fair scoring based on actual improvements

### Reward Logic
- **Action Effectiveness**: Rewards based on actual resource reductions achieved
- **Task Completion Bonuses**: Significant rewards for meeting task objectives
- **Efficiency Incentives**: Bonuses for overall system optimization
- **Penalty System**: Penalties for aggressive actions that may cause system instability

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

### Running the Environment
```bash
# Start the OpenEnv server
uv run server

# The server will be available at http://localhost:8000
```

### Training an Agent
```python
from stable_baselines3 import PPO
from openenv.client import OpenEnvClient

# Connect to the environment
client = OpenEnvClient("http://localhost:8000")

# Create and train agent
model = PPO("MlpPolicy", client, verbose=1)
model.learn(total_timesteps=10000)

# Evaluate the trained agent
obs = client.reset()
total_reward = 0
while not obs.done:
    action, _ = model.predict(obs)
    obs = client.step(action)
    total_reward += obs.reward
    print(f"Step reward: {obs.reward:.2f}, Total: {total_reward:.2f}")
```

## Docker

```bash
# Build the container
docker build -t energy-optimization-rl .

# Run the environment
docker run --rm -p 8000:8000 energy-optimization-rl
```

## Environment Details

### State Space
- RAM usage percentage (0-100%)
- Energy consumption in kWh
- System load (0-1)
- Current task information
- Task completion progress
- Efficiency scores

### Action Space
- `reduce_ram`: Focus on RAM optimization with configurable intensity (0.0-1.0)
- `optimize_energy`: Focus on energy reduction with configurable intensity (0.0-1.0)
- `balance_resources`: Balanced approach to both resources
- `monitor_system`: Gather system information and slight load reduction

### Reward Structure
- Base rewards for resource reductions
- Task completion bonuses (difficulty × 10 points)
- Efficiency improvement bonuses
- Penalties for system instability from aggressive actions

## API Endpoints

- `POST /reset`: Reset the environment
- `POST /step`: Execute an optimization action
- `GET /state`: Get current environment state
- `GET /schema`: Get action/observation schemas
- `WS /ws`: WebSocket endpoint for persistent sessions

## Development

### Project Structure
```
he_demo/
├── models.py                 # Action and observation definitions
├── server/
│   ├── app.py               # FastAPI server application
│   └── he_demo_environment.py # Environment implementation
├── client.py                # Example client code
├── inference.py             # Training and inference scripts
├── Dockerfile               # Container configuration
├── pyproject.toml           # Project dependencies
└── README.md               # This file
```

### Adding New Tasks
Tasks are defined in the `_create_tasks()` method of `EnergyOptimizationEnvironment`. Each task includes:
- Name and description
- Difficulty level
- RAM and energy targets
- Maximum steps allowed

### Customizing Reward Logic
Modify the `_calculate_reward()` method to implement custom reward strategies based on your specific optimization goals.

## License

This project is licensed under the BSD-style license. See LICENSE file for details.
