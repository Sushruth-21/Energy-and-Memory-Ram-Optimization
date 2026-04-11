# 🚀 QUICK START - 5 EASY STEPS

## ✅ SERVER IS ALREADY RUNNING!

Your FastAPI server is **currently active** at:
```
http://localhost:8000
```

---

## 📋 STEP-BY-STEP RUN GUIDE

### STEP 1: Open Terminal
```powershell
# Open PowerShell or Command Prompt
# Navigate to project directory
cd "d:\Projects\Pytorch x hugging face\he_demo"
```

### STEP 2: Start Virtual Environment (Optional)
```powershell
# Activate Python virtual environment
.venv\Scripts\Activate.ps1
```

### STEP 3: Run the Server
```powershell
# Start FastAPI server with uv
uv run server
```

**Expected Output:**
```
INFO:     Started server process [pid]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### STEP 4: Verify Server is Running (New Terminal)
```powershell
# In a new terminal, test the API
curl http://localhost:8000/graders

# Or with PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/graders" -UseBasicParsing
```

**Expected Response:**
```json
{
  "graders": {...},
  "total_graders": 5,
  "grader_names": [...]
}
```

### STEP 5: Run Validation Tests
```powershell
# Test environment and graders
python validate.py

# Or comprehensive tests
python validate_comprehensive.py
```

**Expected Output:**
```
✅ Grader count requirement met (>= 3)
✅ All validation tests passed
✅ 5 graders WORKING
```

---

## 🧪 TEST COMMANDS (While Server Running)

### Test 1: Check All Graders
```powershell
curl http://localhost:8000/graders
```

### Test 2: Get Specific Grader
```powershell
curl "http://localhost:8000/graders/balanced_optimization"
```

### Test 3: Get Grader Info
```powershell
curl http://localhost:8000/graders/info
```

### Test 4: Reset Environment
```powershell
curl -X POST http://localhost:8000/reset `
  -H "Content-Type: application/json" `
  -d '{}'
```

### Test 5: Execute Action
```powershell
curl -X POST http://localhost:8000/step `
  -H "Content-Type: application/json" `
  -d '{"action_type": "reduce_ram", "intensity": 0.8}'
```

---

## 🎓 TRAINING & INFERENCE

### Run Training Script
```powershell
python train_agent.py
```
- Trains RL agent on environment
- Evaluates with graders
- Saves model as `energy_optimization_ppo.zip`

### Run Inference Script
```powershell
# Set environment variables first
$env:ENERGY_TASK = "balanced_optimization"
$env:HF_TOKEN = "your_token"
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

# Then run
python -m he_demo.inference
```

---

## 🐳 RUN WITH DOCKER (Alternative)

### Build Docker Image
```powershell
docker build -t energy-optimization-env .
```

### Run Docker Container
```powershell
# Port 8000 on your machine maps to 8000 in container
docker run -p 8000:8000 he_demo:latest

# Or with interactive terminal
docker run -it -p 8000:8000 he_demo:latest
```

---

## ⏹️ STOP THE SERVER

```powershell
# In the terminal running the server:
Press CTRL+C

# Or if running Docker:
docker stop <container_id>
```

---

## 📊 VERIFY EVERYTHING WORKS

Run this quick verification:
```powershell
# 1. Check server status
curl http://localhost:8000/graders

# 2. Run validation
python validate.py

# 3. Check all graders
python validate_comprehensive.py
```

All three should ✅ PASS

---

## 🎯 WHAT'S RUNNING

| Component | Status | Port | Command |
|-----------|--------|------|---------|
| **FastAPI Server** | ✅ RUNNING | 8000 | `uv run server` |
| **5 Graders** | ✅ ACTIVE | 8000/graders | Built-in |
| **WebSocket** | ✅ READY | 8000/ws | Real-time updates |
| **Validation** | ✅ READY | N/A | `python validate.py` |

---

## 🔗 IMPORTANT LINKS

- **Local Server**: http://localhost:8000
- **GitHub Repo**: https://github.com/Sushruth-21/Energy-and-Memory-Ram-Optimization
- **HF Space**: https://sushruth21-energy-optimization-space.hf.space
- **Complete Guide**: See RUN_INSTRUCTIONS.md

---

## ✅ TROUBLESHOOTING

### Port 8000 already in use?
```powershell
# Find process using port
netstat -ano | findstr :8000
# Kill process
taskkill /PID <pid> /F
```

### Module not found error?
```powershell
# Reinstall dependencies
uv sync
```

### Docker image not building?
```powershell
# Use pre-built image
docker run -p 8000:8000 he_demo:latest
```

---

## 🎉 YOU'RE READY!

1. ✅ Server is running
2. ✅ 5 Graders are working
3. ✅ API is responding
4. ✅ Ready to submit to hackathon

**Next: Run validation tests and submit!**

---

**Current Server Status**: 🟢 **RUNNING ON http://localhost:8000**
