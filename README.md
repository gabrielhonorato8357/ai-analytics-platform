# AI Analytics Platform

Production-oriented analytics platform for natural language data exploration.

## Stack

- Frontend: Next.js 15, TypeScript, TailwindCSS, shadcn/ui-style components
- Backend: FastAPI, PostgreSQL, Redis
- Operations: Docker Compose, GitHub Actions CI

## Repository Layout

```text
apps/
  web/          Next.js web application
services/
  api/          FastAPI service
docs/
  api.md        API documentation notes
```

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Phase Roadmap

1. Platform foundation: monorepo layout, service skeletons, Docker, CI, smoke tests
2. Authentication: JWT login, password hashing, user persistence, protected routes
3. Query workflow: natural language query intake, SQL generation contracts, execution service
4. Reporting: visualizations, saved reports, dashboard composition
5. Administration: user management, audit logs, operational hardening

## Development Commands

```bash
make api-test
make web-typecheck
```

