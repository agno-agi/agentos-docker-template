# Src Architecture Guide

This folder contains the runtime composition, teams, agents, prompts, and tools used by AgentOS.

## Teams

- `src/teams/neo_orchestrator.py` - Top-level coordinator team (`neo_team`) and autonomous heartbeat agent (`pulse_agent`).
- `src/teams/dev_team.py` - Development execution sub-team (`dev_implementer`, `dev_reviewer`).
- `src/teams/research_team.py` - Research and synthesis sub-team (`deep_researcher`, `research_analyst`).
- `src/teams/shared.py` - Shared skills, learning store, and local DuckDB path setup.

## Agents

- `src/agents/agno_assist.py` - Personal "second brain" assistant with learning, search, MCP tools, and DuckDB tools.
- `src/agents/knowledge_agent.py` - RAG-first knowledge agent backed by pgvector and optional default docs loader.

## Runtime and Config

- `src/runtime/bootstrap.py` - Composition root that builds `AgentOS`, wires teams/agents, and registers schedules.
- `settings.py` - Environment-driven runtime settings loader.
- `src/schedules/pulse_schedule.py` - Pulse heartbeat cron schedule registration.

## Tools and Prompts

- `src/tools/mcp_tools.py` - URL-driven MCP setup plus optional Plane stdio MCP from env vars.
- `src/prompts/*.md` - Role and behavior prompts for agents/teams.

