# multi-agent-devops

A multi-agent DevOps assistant where a coordinator routes questions to specialist agents — a docs agent that searches internal runbooks and a system agent that runs live shell commands — then synthesizes their outputs into a single answer.

## How it works

```
Question → coordinator
              ├── docs_agent   → searches runbooks (if answer might be in docs)
              ├── system_agent → runs shell command (if live data needed)
              └── synthesizes both outputs → final answer
```

**Example routing:**
- *"What is the process to get Jenkins access?"* → docs only
- *"How much memory is my machine using?"* → system only
- *"Is my disk space healthy based on our guidelines?"* → both agents

## Endpoints

| Endpoint | Description |
|---|---|
| `POST /ask` | Routes question through coordinator, returns synthesized answer |
| `GET /health` | Health check for K8s probes |

## Run locally

**Prerequisites:** [Ollama](https://ollama.com) running with `llama3.2` pulled.

```bash
pip install -r requirements.txt

# As a service (recommended)
uvicorn server:app --reload --port 8000

# As a script (runs 3 test questions and exits)
python3 multi_agent.py
```

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is my disk space healthy based on our runbook guidelines?"}'
```

## Run with Docker

```bash
docker build -t multi-agent-devops .
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  multi-agent-devops
```

## Adding runbooks

Drop `.txt` files into `docs/`. They are loaded once at startup. Restart the service to pick up new docs.

## Deploy to Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Or via Helm
helm upgrade --install multi-agent-devops \
  ../devops-ai-assistant/helm \
  -f helm-values/multi-agent-devops.yaml \
  -n ai-platform --create-namespace \
  --set image.tag=<git-sha>
```

## K8s architecture

```
Ingress (/agents)
  └── Service (ClusterIP :80)
        └── Deployment (stateless — no PVC needed)
              └── Container: uvicorn server:app
```

Stateless service — no persistent storage. All state is in the LLM context per request.

## CI/CD

GitHub Actions: `test → build-push (GHCR) → deploy → helm test`

Image tagged with git SHA. Set `KUBECONFIG` as a base64-encoded repository secret to enable deploy.
