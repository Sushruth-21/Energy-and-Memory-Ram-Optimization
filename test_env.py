#!/usr/bin/env python
"""Test environment variables loading"""
from dotenv import load_dotenv
import os

load_dotenv()

print(f"HF_TOKEN set: {'Yes' if os.getenv('HF_TOKEN') else 'No'}")
print(f"MODEL_NAME: {os.getenv('MODEL_NAME')}")
print(f"API_BASE_URL: {os.getenv('API_BASE_URL')}")
print("\nNow running inference.py...")

# Run inference.py
import subprocess
result = subprocess.run([os.sys.executable, "inference.py"], capture_output=False)
exit(result.returncode)
