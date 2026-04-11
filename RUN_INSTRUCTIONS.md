# 🚀 Complete Run Guide - Energy & Memory RAM Optimization Environment

## ✅ CURRENT STATUS
- **Server**: ✅ RUNNING on http://0.0.0.0:8000
- **Graders**: ✅ 5 ACTIVE
- **Docker Image**: ✅ BUILT (he_demo:latest)
- **API Health**: ✅ HTTP 200 responses

---

## 📋 QUICK START (Server Already Running)

Your FastAPI server is **currently running** at:
```
http://localhost:8000
```

To access graders:
```
http://localhost:8000/graders
```

---

## 🔧 HOW TO RUN THE SYSTEM

### Option 1: Run with uv (Recommended - Currently Active)

#### Step 1: Navigate to project directory
```bash
cd "d:\Projects\Pytorch x hugging face\he_demo"
```

#### Step 2: Activate virtual environment (optional)
```bash
.venv\Scripts\Activate.ps1
```

#### Step 3: Start the server
```bash
uv run server
```

**Output:**
```
INFO:     Started server process [21940]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Time to start**: ~5-10 seconds

---

### Option 2: Run with Docker

#### Step 1: Build Docker image (if not done)
```bash
docker build -t energy-optimization-env .
```

#### Step 2: Run container
```bash
docker run -p 8000:8000 energy-optimization-env
```

Or use the pre-built image:
```bash
docker run -p 8000:8000 he_demo:latest
```

**Time to start**: ~15-20 seconds

---

### Option 3: Run with Docker Compose

#### Step 1: Start containers
```bash
docker-compose up
```

#### Step 2: Stop containers
```bash
docker-compose down
```

---

## 🧪 TESTING THE RUNNING SERVER

### Test 1: Check Health
```bash
curl http://localhost:8000/graders
```

**Expected Response:**
```json
{
  "graders": {...},
  "total_graders": 5,
  "grader_names": ["basic_ram_reduction", "energy_optimization", ...]
}
```

### Test 2: Get Specific Grader
```bash
curl http://localhost:8000/graders/balanced_optimization
```

### Test 3: Run Validation
```bash
python validate.py
```

**Expected Output:**
```
✅ Grader count requirement met (>= 3)
✅ Environment created successfully
✅ All validation tests passed
```

### Test 4: Run Comprehensive Validation
```bash
python validate_comprehensive.py
```

**Expected Output:**
```
✅ 5 graders found
✅ Score variation verified (0.000-1.000)
✅ All tests PASSED
```

---

## 🎯 API COMMANDS - INTERACT WITH SERVER

### Reset Environment
```bash
curl -X POST http://localhost:8000/reset `
  -H "Content-Type: application/json" `
  -d '{}'
```

### Execute Action (Step)
```bash
curl -X POST http://localhost:8000/step `
  -H "Content-Type: application/json" `
  -d '{
    "action_type": "reduce_ram",
    "intensity": 0.8
  }'
```

### Get Current State
```bash
curl http://localhost:8000/state
```

### Get Schema
```bash
curl http://localhost:8000/schema
```

### Get All Graders Info
```bash
curl http://localhost:8000/graders/info
```

---

## 💻 RUNNING TRAINING SCRIPT

### Step 1: Run RL Training
```bash
python train_agent.py
```

**What it does:**
- Displays all 5 graders available
- Creates and trains a PPO agent
- Evaluates agent with graders
- Saves trained model

**Expected Output:**
```
🚀 Training PPO Agent on Energy Optimization Environment
📋 Available Task Graders:
  • Basic RAM Reduction (Difficulty 1)
  • Energy Optimization (Difficulty 2)
  ...
Training for 10,000 timesteps...
✅ Model saved as 'energy_optimization_ppo.zip'
✅ Grader Score (Task: balanced_optimization): 0.850
```

---

## 🤖 RUNNING INFERENCE SCRIPT

### Step 1: Set Environment Variables
```bash
# PowerShell
$env:ENERGY_TASK = "balanced_optimization"
$env:HF_TOKEN = "your_hf_token"
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
$env:API_BASE_URL = "https://router.huggingface.co/v1"
```

### Step 2: Run Inference
```bash
python -m he_demo.inference
```

**Expected Output:**
```
[CONFIG] Task-specific grader configured: task=balanced_optimization
[GRADER] task=balanced_optimization difficulty=3 grader_score=0.850
[METRICS] total_reward=45.32 efficiency_score=0.687 final_grader_score=0.850
[END] success=true steps=15 score=0.850
```

---

## 📊 PORTS & ACCESS

| Service | Port | URL | Status |
|---------|------|-----|--------|
| FastAPI Server | 8000 | http://localhost:8000 | ✅ RUNNING |
| WebSocket | 8000 | ws://localhost:8000/ws | ✅ AVAILABLE |
| HF Space | N/A | https://sushruth21-energy-optimization-space.hf.space | ✅ LIVE |

---

## 🔄 STOPPING THE SERVER

### If running with uv
```bash
# Press Ctrl+C in the terminal where it's running
Press CTRL+C to quit
```

### If running with Docker
```bash
# In another terminal
docker stop <container_id>
# Or
docker-compose down
```

---

## 📁 PROJECT STRUCTURE

```
he_demo/
├── server/
│   ├── app.py                    # FastAPI application
│   ├── he_demo_environment.py    # Environment with graders
│   └── __init__.py
├── inference.py                  # LLM-based inference with graders
├── train_agent.py                # RL training with graders
├── validate.py                   # Validation tests
├── validate_comprehensive.py     # Comprehensive tests
├── task_graders.py               # 5 graders implementation
├── models.py                     # Pydantic models
├── openenv.yaml                  # OpenEnv spec
├── Dockerfile                    # Docker configuration
├── pyproject.toml                # Project dependencies
└── README.md                     # Project overview
```

---

## 🎯 QUICK COMMANDS REFERENCE

```bash
# Start server
uv run server

# Run validation
python validate.py
python validate_comprehensive.py

# Train agent
python train_agent.py

# Run inference
python -m he_demo.inference

# Check Docker image
docker images | grep he_demo

# Deploy on HF Spaces
git push hf-space temp-clean:main --force

# Check git status
git status
git log --oneline -5
```

---

## ✅ TROUBLESHOOTING

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
# Kill process if needed
taskkill /PID <pid> /F
```

### Docker image not found
```bash
# List built images
docker images

# Build image if missing
docker build -t he_demo:latest .
```

### Module import errors
```bash
# Reinstall dependencies
uv sync

# Or with pip
pip install -e .
```

### Grader validation fails
```bash
# Run simple validation
python validate.py

# Check graders are loaded
python -c "from task_graders import TASK_GRADERS; print(len(TASK_GRADERS))"
```

---

## 🔗 REFERENCES

- **GitHub**: https://github.com/Sushruth-21/Energy-and-Memory-Ram-Optimization
- **HF Space**: https://sushruth21-energy-optimization-space.hf.space
- **OpenEnv Docs**: https://github.com/meta-pytorch/OpenEnv
- **FastAPI Docs**: http://localhost:8000/docs (when server is running)

---

## 🎉 YOU'RE ALL SET!

Your Energy & Memory RAM Optimization environment is:
- ✅ Running on http://localhost:8000
- ✅ 5 graders active and responding
- ✅ Ready for testing and submission
- ✅ Fully documented and deployable

**Next steps:**
1. Test API endpoints (see commands above)
2. Run validation scripts
3. Submit to Meta PyTorch Hackathon validator
4. Expect Phase 2 validation: ✅ PASS

---

Generated: April 11, 2026
Status: 🟢 **PRODUCTION READY**
