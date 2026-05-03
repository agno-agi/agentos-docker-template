## Learned User Preferences

- Keep each agent in its own file under `agents/`; import agents into orchestrators rather than defining them inline.
- Store agent prompts in `agents/prompts/*.md` loaded via `agents/prompts/__init__.py load_prompt()` — never inline instructions in Python.
- Always use `python3 -m pip` or `uv` for package management; `pip` is not on PATH in this project's venv.
- Use factory pattern (`OpenRouter.create(...)`) for model instantiation; export from `models/__init__.py`.
- App must start gracefully without optional tokens (SLACK_TOKEN, etc.) — use try/except guards in `app/main.py`.
- `slack-sdk` stays in dependencies even when Slack integration code is removed, for future rebuilds.
- Write plans to `.cursor/plans/*.plan.md` before touching code for multi-step tasks.
- Use `uv export --frozen --no-hashes --no-editable` to regenerate `requirements.txt` — never include `-e .` or `.` lines.
- Logger convention: `log = logging.getLogger(__name__)` placed after all imports; use `log.warning(...)` not `print`.
- Prefer graceful multi-MCP over single-server wiring; agents accept multiple MCP server URLs from env vars.
- Compose port mapping pattern: `${PORT:-8080}:8000` (fixed internal `8000`, configurable external); Coolify container port is always `8000`.
- Neo orchestrator runs a 3-5 question onboarding intake for new users before routing work.

## Learned Workspace Facts

- Project is AgentOS (`feat/fresh-start` branch), based on `agno-agi/agentos-docker-template`; GitHub remote is `https://github.com/TheAiBuildr/AgentOS.git`.
- Flat layout at repo root: `agents/`, `models/`, `app/`, `db/`, `knowledge/`, `scripts/` — no `src/` prefix on the current branch.
- Custom OpenRouter wrapper: `models/openrouter.py` with `OpenRouter.create(model_id=None, **kwargs)`; default model from `OPENROUTER_MODEL` env var; optional `OPENROUTER_APP_URL` and `OPENROUTER_APP_NAME` headers.
- agno `SlackTools` requires `SLACK_TOKEN` in env; `compose.yaml` passes `SLACK_BOT_TOKEN`, so startup code mirrors it: `os.environ["SLACK_TOKEN"] = settings.slack_bot_token`.
- `pypdf` is required for PDF knowledge ingestion; knowledge files are loaded via `knowledge_dir.rglob("*")` glob pattern.
- Plane workspace slug is `agent-ws` (lowercase) — `Agent-ws` returns 403 Forbidden.
- `agno[scheduler]` extra is in requirements; `croniter` is also pinned explicitly to avoid deploy failures.
- Composio integration uses Hosted MCP path with a dedicated `composio_agent` in the root team.
- Healthcheck in `compose.yaml`: interval `300s`, retries `5`; scheduler poll interval in settings: `30` seconds.
- Multi-MCP servers (Plane, Composio, etc.) are configured via environment variables and passed to agents at construction.
- `OPENROUTER_API_KEY` is the primary LLM credential; OpenAI embeddings are used for knowledge search (`OpenAIEmbedder`).
- Agents in `agents/` use the Agno `Agent` class with `instructions`, `role`, `model`, and `tools` params; sub-teams use `Team` with a `leader` agent and `members` list.
