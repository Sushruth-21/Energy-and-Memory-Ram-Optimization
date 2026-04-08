# OpenEnv Energy RL

A lightweight RL example environment for energy and memory optimization.

## Files

- `environment.py`: custom `gym.Env` implementation for RAM and electricity reduction.
- `inference.py`: trains a PPO agent and runs one episode.
- `Dockerfile`: containerizes the example.
- `requirements.txt`: dependency list for the example.

## Quick start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python inference.py
```

## Docker

```bash
docker build -t openenv-energy-rl .
docker run --rm openenv-energy-rl
```
