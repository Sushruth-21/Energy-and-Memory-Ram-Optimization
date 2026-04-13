# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **OpenEnv-based reinforcement learning environment** for training AI agents to optimize energy consumption and RAM usage in simulated computer systems. It deploys as a Docker-based Hugging Face Space using FastAPI.

## Commands

```bash
# Install dependencies (uv is the package manager)
uv sync

# Run the server locally
uv run server
# Or directly with uvicorn:
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

# Run with custom port
uv run server --port 8001

# Build Docker image
docker build -t energy-optimization-rl .

# Run Docker container
docker run --rm -p 8000:8000 energy-optimization-rl

# Verify graders are discoverable
python check_graders.py          # Basic verification
python check_graders.py verify   # Import & callable check
python check_graders.py json     # JSON manifest output
```

There are no tests in this project. The `pyproject.toml` lists `pytest` as a dev dependency but no test directory exists.

## Architecture

### Core Flow

1. **`openenv.yaml`** — Declarative config that defines 5 tasks with their grader references (`graders:grade_*`). This is what the OpenEnv validator reads first.
2. **`server/app.py`** — FastAPI app created via `openenv.core.env_server.http_server.create_app()`, which wires up `/reset`, `/step`, `/state`, `/schema`, and `/ws` endpoints. Additional `/graders`, `/tasks`, `/validate` endpoints are added for validator tool detection.
3. **`server/he_demo_environment.py`** — The `EnergyOptimizationEnvironment` class implementing `Environment` from openenv-core. Manages state transitions, reward calculation, and task progression.
4. **`models.py`** — Pydantic models: `EnergyOptimizationAction`, `EnergyOptimizationObservation`, `Task`, `TaskSummary`. Also contains legacy grader functions that duplicate logic from `graders.py`.

### Dual Grader System

There are **two separate grader implementations** that must be kept in sync:

- **`graders.py`** — Self-contained, no external dependencies (uses only `getattr` on observations). This is what `openenv.yaml` references (`graders:grade_basic_ram_reduction`, etc.). **Must remain dependency-free** because the OpenEnv validator imports it in a minimal environment.
- **`task_graders.py`** — Imports from `models.py`, has richer scoring with weighted formulas. Used by the server endpoints and `task_registry.py`.

When modifying grader logic or adding tasks, update **both** `graders.py` and `task_graders.py`, plus the `__all__` lists.

### Grader Discovery Modules

There are multiple redundant discovery/manifest modules that the server endpoints import:

- **`grader_manifest.py`** — Lightweight manifest dict for `/graders/manifest` endpoint
- **`graders_manifest.py`** — Detailed manifest with scoring methodology, performance examples, and validation checklist
- **`grader_discovery.py`** — Discovery manifest with import paths and openenv references
- **`task_registry.py`** — Registry mapping task names to grader functions and metadata

### Other Root Modules

- **`client.py`** — `EnergyOptimizationEnv` subclassing `EnvClient` from openenv-core. WebSocket-based client for connecting to the server.
- **`inference.py`** — LLM inference script with benchmarking (Random vs Heuristic vs LLM). Uses HF API. Configured via env vars (`API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`).
- **`evaluate_inference.py`** — Evaluation script for LLM performance across tasks.
- **`gym_wrapper.py`** — `EnergyOptimizationGymEnv` wrapping the environment in a Gymnasium interface for SB3 training.
- **`openenv-energy-rl/`** — Standalone sub-project with a simpler `EnergyEnv` (gym-based, not OpenEnv).

### Key Design Points

- The environment starts at RAM 80%, energy 8.0 kWh, system load 0.7. Actions reduce these deterministically (no randomness — system dynamics are disabled).
- Reward is `intensity * 0.1` clamped to [0, 1], with task completion bonuses of `difficulty * 0.5`.
- Episodes end at 100 steps or when all 5 tasks are completed.
- The Dockerfile is multi-stage (`ghcr.io/meta-pytorch/openenv-base:latest` base), installs via `uv sync`, and runs `uvicorn` from `/app/env`.
- `PYTHONPATH` in Docker includes both `/app/env` and `/app` for grader discovery.
- HF Space config: SDK docker, port 8000, base path `/web`.

### Task Definitions

All 5 tasks are defined in three places that must stay consistent:
1. `openenv.yaml` (task names, descriptions, grader references, max_steps)
2. `_create_tasks()` in `server/he_demo_environment.py` (Task objects with targets)
3. Grader functions in `graders.py` and `task_graders.py` (scoring thresholds)

Tasks: basic_ram_reduction → energy_optimization → balanced_optimization → advanced_efficiency → expert_optimization (difficulty 1–5).