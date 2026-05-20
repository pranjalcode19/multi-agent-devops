FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY multi_agent.py .
COPY docs/ ./docs/

CMD ["python3", "multi_agent.py"]
