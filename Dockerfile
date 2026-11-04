FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tor curl git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY agent_orchestrator.py .
COPY dark_web.py .
COPY menu.html .

EXPOSE 7860

CMD ["python", "main.py"]