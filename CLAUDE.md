# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenMOSS is a **Self-Organizing Multi-Agent System** built on OpenClaw. It's a middleware that orchestrates multiple AI agents (Planner, Executor, Reviewer, Patrol) to collaborate autonomously on tasks.

## Common Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode (auto-reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 6565 --reload

# Run in production
python -m uvicorn app.main:app --host 0.0.0.0 --port 6565
```

### Frontend (Vue 3)

```bash
cd webui

# Install dependencies
npm install

# Development server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Build and deploy to static/
npm run build:deploy
```

## Architecture

### Middleware Architecture

OpenMOSS sits between OpenClaw and AI agents, coordinating their collaboration through a REST API. Agents communicate asynchronously — they never talk to each other directly, only through the OpenMOSS API.

### Agent Roles

| Role | Responsibility |
|------|-----------------|
| **planner** | Break down requirements, create modules/sub-tasks, assign agents |
| **executor** | Claim tasks, produce deliverables |
| **reviewer** | Review quality, score, approve or reject for rework |
| **patrol** | Monitor system health, flag blocked tasks |

### Task Lifecycle

```
pending → assigned → in_progress → review → done
         review → rejected → rework → in_progress
```

### API Prefix

All API routes use `/api` prefix. Example: `/api/health`, `/api/tasks`, `/api/agents`

### Key Endpoints

- `GET /api/health` — Health check
- `GET /api/docs` — Swagger API documentation

## Code Structure

### Backend (`app/`)

```
app/
├── main.py              # FastAPI entry point, route registration, SPA static serving
├── config.py            # Config loader (reads config.yaml)
├── database.py          # SQLAlchemy database initialization
├── auth/
│   └── dependencies.py # API Key / Admin Token validation
├── middleware/
│   └── request_logger.py  # Request logging (drives activity feed)
├── models/              # SQLAlchemy ORM models (10 tables)
├── routers/             # API route handlers
├── services/            # Business logic layer
└── schemas/             # Pydantic serialization models
```

### Frontend (`webui/`)

```
webui/
├── src/
│   ├── views/           # Page components
│   ├── components/      # UI components (ui/feed/common)
│   ├── api/             # API client
│   ├── stores/           # Pinia state management
│   └── router/          # Vue Router
└── dist/                # Build output
```

### Configuration

- `config.yaml` — Main config file (auto-generated from `config.example.yaml` on first launch)
- `config.yaml` is watched at startup; changes require server restart
- Key settings: `admin.password`, `agent.registration_token`, `workspace.root`, `server.port`

## Database

- SQLite via SQLAlchemy
- Database path: `./data/tasks.db` (configurable in config.yaml)
- 10 tables: tasks, modules, sub_tasks, agents, reviews, scores, logs, etc.

## WebUI Routes

The backend serves the Vue SPA at all unmatched paths. Key pages:

| Path | Description |
|------|-------------|
| `/setup` | First-time initialization wizard |
| `/login` | Admin login |
| `/dashboard` | System overview |
| `/tasks` | Task management |
| `/agents` | Agent management |
| `/feed` | Activity feed |
| `/scores` | Score leaderboard |
| `/prompts` | Role prompt management |
| `/settings` | System configuration |
