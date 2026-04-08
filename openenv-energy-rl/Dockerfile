FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install torch transformers trl gym numpy pandas stable-baselines3
CMD ["python", "inference.py"]
