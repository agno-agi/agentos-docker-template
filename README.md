# AgentOS Docker Template

Run agents, teams, and workflows as a production-ready API. Deploy anywhere Docker runs.

## Quickstart

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- [OpenAI API key](https://platform.openai.com/api-keys)

### Clone and configure

```sh
git clone https://github.com/agno-agi/agentos-docker-template.git agentos-docker
cd agentos-docker

cp example.env .env
# Add OPENAI_API_KEY to .env
```

> Agno works with any model provider. Update the agents in `/agents` and add dependencies to `pyproject.toml`.

### Start AgentOS

```sh
docker compose up -d --build
```

This starts:
- **AgentOS** (FastAPI server) on http://localhost:8000
- **PostgreSQL** with pgvector on localhost:5432

Open http://localhost:8000/docs to see the API.

### Connect to the control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" and select "Local"
3. Enter `http://localhost:8000`

### Stop AgentOS

```sh
docker compose down
```

## Project Structure

```
agentos-docker/
├── agents/              # Your agents
├── app/                 # AgentOS entry point
├── db/                  # Database connection
├── scripts/             # Helper scripts
├── compose.yaml         # Docker Compose configuration
├── Dockerfile           # Container build
├── example.env          # Example environment variables
└── pyproject.toml       # Python dependencies
```

## Common Tasks

### Load a knowledge base
```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

### View logs
```sh
docker compose logs -f
```

### Restart after code changes
```sh
docker compose restart
```

## Local Development

For development without Docker:

### Install uv
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup environment
```sh
./scripts/venv_setup.sh
source .venv/bin/activate
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements:
```sh
./scripts/generate_requirements.sh
```
3. Rebuild:
```sh
docker compose up -d --build
```

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os)
- [Discord Community](https://agno.link/discord)