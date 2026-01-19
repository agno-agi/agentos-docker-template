# Agent OS Template

Welcome to Agent OS Docker Template: a robust, production-ready application for serving Agentic Applications as an API. It includes:

- An **AgentOS instance**: An API-based interface for production-ready Agentic Applications.
- A **PostgreSQL database** for storing Agent sessions, knowledge, and memories.

## Quickstart

Follow these steps to get your Agent OS up and running:

> [Get Docker Desktop](https://www.docker.com/products/docker-desktop) should be installed and running.
> [Get OpenAI API key](https://platform.openai.com/api-keys)

### Clone the repo

```sh
git clone https://github.com/agno-agi/agentos-docker-template.git
cd agentos-docker-template
```

### Configure API keys

We use GPT 5 Mini as the default model, please export the `OPENAI_API_KEY` environment variable to get started.

```sh
export OPENAI_API_KEY="YOUR_API_KEY_HERE"
```

> **Note**: You can use any model provider, just update the agents in the `/agents` folder and add the required library in the `pyproject.toml` and `requirements.txt` file.

### Start the application

```sh
docker compose up -d --build
```

This command starts:

- The **AgentOS instance**, which is a FastAPI server, running on [http://localhost:8080](http://localhost:8080).
- The **PostgreSQL database**, accessible on `localhost:5432`.

Once started, you can:

- Test the API at [http://localhost:8080/docs](http://localhost:8080/docs).

### Connect to AgentOS UI

- Open the [Agno AgentOS UI](https://os.agno.com).
- Connect your OS with `http://localhost:8080` as the endpoint. You can name it `AgentOS` (or any name you prefer).
- Explore all the features of AgentOS or go straight to the Chat page to interact with your Agents.

### How to load the knowledge base locally

To load the knowledge base, you can use the following command:

```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

### Stop the application

When you're done, stop the application using:

```sh
docker compose down
```

## Development Setup

To setup your local virtual environment:

### Install `uv`

We use `uv` for python environment and package management. Install it by following the the [`uv` documentation](https://docs.astral.sh/uv/#getting-started) or use the command below for unix-like systems:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Create Virtual Environment & Install Dependencies

Run the `dev_setup.sh` script. This will create a virtual environment and install project dependencies:

```sh
./scripts/dev_setup.sh
```

### Activate Virtual Environment

Activate the created virtual environment:

```sh
source .venv/bin/activate
```

(On Windows, the command might differ, e.g., `.venv\Scripts\activate`)

## Managing Python Dependencies

If you need to add or update python dependencies:

### Modify pyproject.toml

Add or update your desired Python package dependencies in the `[dependencies]` section of the `pyproject.toml` file.

### Generate requirements.txt

The `requirements.txt` file is used to build the application image. After modifying `pyproject.toml`, regenerate `requirements.txt` using:

```sh
./scripts/generate_requirements.sh
```

To upgrade all existing dependencies to their latest compatible versions, run:

```sh
./scripts/generate_requirements.sh upgrade
```

### Rebuild Docker Images

Rebuild your Docker images to include the updated dependencies:

```sh
docker compose up -d --build
```
