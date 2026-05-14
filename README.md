# AgentOS Docker Template

An agent platform you build, improve, and run using coding agents.

The platform runs locally with Docker Compose, behind your auth, with all your data stored in your database. Because trace data, agent code, system logs, and the iteration tool all live in one place, coding agents like Claude Code can read, update, and improve the platform end-to-end.

## Built for coding agents

This codebase is designed primarily for coding agents. It comes with five prompts that cover the full agent development lifecycle:

1. **Create.** Claude asks a few questions, scaffolds the agent file, registers it in `app/main.py`, adds quick prompts to `app/config.yaml`, restarts the container, and smoke-tests via cURL. Usually 5-10 minutes for a simple agent.
2. **Improve.** Hardens and fine-tunes your agent based on its existing spec. Claude derives probes from the agent's `INSTRUCTIONS`, runs them against the live container, judges the responses, and edits until they pass. No input from you.
3. **Extend.** Add a new feature to an agent. You direct, Claude executes. Add tools, refine prompts, fix bugs. The Agno docs MCP is loaded so toolkit research is grounded in the real API.
4. **Hill Climb.** Claude runs the eval suite, diagnoses failures, and fixes what's in scope. Stops when all cases pass.
5. **Review.** Claude sweeps the repo for drift between docs, code, and config. Auto-fixes mechanical drift like stale paths and missing env vars; flags anything bigger.

3 of 5 run autonomously with no input needed from you.

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| WebSearch | Direct tools | Search the web using Parallel SDK or keyless MCP. |
| CodeSearch | Context provider | Answer questions about this codebase. |

## Get Started

### Step 1: Run locally

> **Prerequisite:** [Docker](https://www.docker.com/get-started/) installed and running.

```sh
# Clone the repo
git clone https://github.com/agno-agi/agentos-docker-template.git agentos
cd agentos

# Add OPENAI_API_KEY
cp example.env .env
# Edit .env and add your key

# Start the application
docker compose up -d --build
```

Confirm AgentOS is running at [http://localhost:8000/docs](http://localhost:8000/docs).

### Step 2: Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com) and login
2. Add OS → Local → `http://localhost:8000`
3. Click "Connect"

### Step 3: Stop the application

```sh
docker compose down
```

## Extending the Platform

### Multi-agent teams and workflows

For most things one agent is enough. When it isn't:

- **[Multi-agent teams](https://docs.agno.com/teams/overview).** Coordinate (a leader plans and synthesizes), route (a router picks the right specialist), or broadcast (run everyone in parallel). Use when the right specialist isn't known up front.
- **[Agentic workflows](https://docs.agno.com/workflows/overview).** Deterministic step-by-step pipelines. Use when a process needs to run the same way every time.

Rule of thumb: agents for open questions, teams for routing, workflows for processes.

### Scheduled tasks

`scheduler=True` is on in [`app/main.py`](app/main.py). Schedule any agent or workflow on a cron:

- **Maintenance.** Purge sessions older than 90 days. Vacuum tables.
- **Proactive runs.** Every weekday morning, summarize overnight news for your portfolio and send to Slack.
- **Periodic re-evaluation.** Wrap the eval suite as a scheduled workflow to catch behavior drift before users do.

See [Agno scheduler docs](https://docs.agno.com/agent-os/scheduler) for the cron API.

### Interfaces

Agents should live where your users are. Slack, Discord, Telegram, custom UIs in your product.

**Slack** is pre-wired. Set `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` in your `.env` and the interface lights up automatically. See [`app/main.py`](app/main.py):

```python
interfaces: list = []
if SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET:
    from agno.os.interfaces.slack import Slack

    interfaces.append(
        Slack(
            agent=code_search,
            streaming=True,
            token=SLACK_BOT_TOKEN,
            signing_secret=SLACK_SIGNING_SECRET,
            resolve_user_identity=True,
        )
    )
```

Swap the `agent=` arg to route Slack to a different agent. For the Slack-side app setup, see the [Agno Slack interface docs](https://docs.agno.com/agent-os/interfaces/overview).

For Discord, Telegram, WhatsApp, or a custom UI, mirror the same conditional with the relevant interface from Agno. See the [Agno interfaces guide](https://docs.agno.com/agent-os/interfaces/overview).

### Tools and MCP servers

The WebSearch agent in [`agents/web_search.py`](agents/web_search.py) shows the MCPTools pattern (URL plus transport). Copy it to wire any MCP server.

For built-in toolkits, Agno ships 100+. A typical wire-up is three lines:

```python
from agno.tools.linear import LinearTools

linear_agent = Agent(
    id="linear",
    model=default_model(),
    tools=[LinearTools()],
    instructions="You triage issues in Linear.",
    db=get_postgres_db(),
)
```

See [Agno tools](https://docs.agno.com/tools/toolkits) for the full catalog.

## Common Tasks

### Add your own agent

1. **Hand it to Claude Code** — paste `Run docs/create-new-agent.md` into a Claude Code session. Claude asks what the agent should do, generates the file, registers it, smoke-tests it.

2. **Do it manually** — create `agents/my_agent.py`:

```python
from agno.agent import Agent

from app.settings import default_model
from db import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=default_model(),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

Register in `app/main.py` and restart: `docker compose restart agentos-api`

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

```sh
# 1. Edit pyproject.toml
# 2. Regenerate requirements
./scripts/generate_requirements.sh upgrade
# 3. Rebuild
docker compose up -d --build
```

### Use a different model provider

1. Add your API key to `.env` (e.g., `ANTHROPIC_API_KEY`)
2. Update `app/settings.py`:

```python
from agno.models.anthropic import Claude

def default_model():
    return Claude(id="claude-sonnet-4-5")
```

3. Add dependency to `pyproject.toml`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `RUNTIME_ENV` | No | `prd` | `dev` enables hot-reload and disables JWT |
| `JWT_VERIFICATION_KEY` | Prd | - | Public key from os.agno.com |
| `AGENTOS_URL` | No | `http://127.0.0.1:8000` | Scheduler base URL |
| `PARALLEL_API_KEY` | No | - | Parallel SDK key (optional for WebSearch) |
| `SLACK_BOT_TOKEN` | No | - | Enable Slack interface |
| `SLACK_SIGNING_SECRET` | No | - | Enable Slack interface |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Agno Discord](https://agno.com/discord)
