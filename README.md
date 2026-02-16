# AgentOS Docker Template

Deploy a multi-agent system with Docker.

[What is AgentOS?](https://docs.agno.com/agent-os/introduction) · [Agno Docs](https://docs.agno.com) · [Discord](https://agno.com/discord)

---

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| Knowledge Agent | RAG | Answers questions from a knowledge base |
| MCP Agent | Tool Use | Connects to external services via MCP |

---

## Get Started

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone and configure

```sh
git clone https://github.com/agno-agi/agentos-docker-template.git agentos-docker
cd agentos-docker
cp example.env .env
# Add your OPENAI_API_KEY to .env
```

### 2. Start locally

```sh
docker compose up -d --build

# Load documents for the knowledge agent
docker exec -it agentos-api python -m agents.knowledge_agent
```

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### 3. Connect to control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" → "Local"
3. Enter `http://localhost:8000`

---

## The Agents

### Knowledge Agent

Answers questions using a vector knowledge base (RAG pattern).

**Try it:**
```
What is Agno?
How do I create my first agent?
What documents are in your knowledge base?
```

**Load documents:**
```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

### MCP Agent

Connects to external tools via the Model Context Protocol.

**Try it:**
```
What tools do you have access to?
Search the docs for how to use LearningMachine
Find examples of agents with memory
```

---

## Project Structure

```
├── agents/
│   ├── knowledge_agent.py   # RAG agent
│   └── mcp_agent.py         # MCP tools agent
├── app/
│   ├── main.py              # AgentOS entry point
│   └── config.yaml          # Quick prompts config
├── db/
│   ├── session.py           # Database session helpers
│   └── url.py               # Connection URL builder
├── scripts/                 # Helper scripts
├── compose.yaml             # Docker Compose config
├── Dockerfile
└── pyproject.toml           # Dependencies
```

---

## Common Tasks

### Add your own agent

1. Create `agents/my_agent.py`:
```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from db import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
)
```

2. Register in `app/main.py`:
```python
from agents.my_agent import my_agent

agent_os = AgentOS(
    name="AgentOS",
    agents=[knowledge_agent, mcp_agent, my_agent],
    ...
)
```

3. Restart: `docker compose restart`

### Add tools to an agent

Agno includes 100+ tool integrations. See the [full list](https://docs.agno.com/tools/toolkits).
```python
from agno.tools.slack import SlackTools
from agno.tools.google_calendar import GoogleCalendarTools

my_agent = Agent(
    ...
    tools=[
        SlackTools(),
        GoogleCalendarTools(),
    ],
)
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements: `./scripts/generate_requirements.sh`
3. Rebuild: `docker compose up -d --build`

### Use a different model provider

1. Add your API key to `.env` (e.g., `ANTHROPIC_API_KEY`)
2. Update agents to use the new provider:
```python
from agno.models.anthropic import Claude

model=Claude(id="claude-sonnet-4-5")
```
3. Add dependency: `anthropic` in `pyproject.toml`

---

## Local Development

For development without Docker:
```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Start PostgreSQL (required)
docker compose up -d agentos-db

# Run the app
python -m app.main
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |

---

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Tools & Integrations](https://docs.agno.com/tools/toolkits)
- [Discord Community](https://agno.com/discord)
