# card-cascade

Custom multiplayer card game, built as a learning project

## Stack

- **Frontend**: React + TypeScript (Vite), TailwindCSS + daisyUI
- **Backend**: FastAPI (Python 3.12, managed with `uv`)
- **Database**: PostgreSQL
- **Dev environment**: Docker Compose, with hot reload

## Structure

```
card-cascade/
├── frontend/ React + TypeScript (Vite)
├── backend/ FastAPI + uv
├── database/ Postgres init scripts
└── docker-compose.dev.yml
```

## Getting started

⚠️ Requires Docker + Docker Compose. 

```bash
docker compose -f docker-compose.dev.yml up
```

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/health
- API docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432

## Notes

- `.env.dev`files are committed on purpose - dummy dev-only credentials
- For editor autocompletion (VS Code), also install dependencies on the host: `npm install` in `/frontend`, `uv sync` in `/backend`. These stay isolated from the containers' own copies via named Docker volumes.
