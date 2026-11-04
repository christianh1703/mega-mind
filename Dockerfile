FROM python:3.11-slim

WORKDIR /app

# Install system deps + Tor
RUN apt-get update && apt-get install -y --no-install-recommends \
    tor \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the 7 agent repos
COPY ag2 /app/ag2
COPY multi-agent-framework /app/multi-agent-framework
COPY oasis /app/oasis
COPY dgm /app/dgm
COPY self_improving_coding_agent /app/self_improving_coding_agent
COPY yoyo-evolve /app/yoyo-evolve
COPY darwin-agents /app/darwin-agents

# Copy our orchestration code
COPY main.py .
COPY agent_orchestrator.py .
COPY dark_web.py .
COPY menu.html .

EXPOSE 7860

CMD ["python", "main.py"]