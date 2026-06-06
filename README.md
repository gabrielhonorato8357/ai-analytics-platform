# AI Analytics Platform

[![CI](https://github.com/gabrielhonorato8357/ai-analytics-platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/gabrielhonorato8357/ai-analytics-platform/actions/workflows/ci.yml)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs&logoColor=white)](apps/web)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6?logo=typescript&logoColor=white)](apps/web/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white)](services/api)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](services/api/pyproject.toml)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-ready-2496ed?logo=docker&logoColor=white)](docker-compose.yml)
[![Last commit](https://img.shields.io/github/last-commit/gabrielhonorato8357/ai-analytics-platform)](https://github.com/gabrielhonorato8357/ai-analytics-platform/commits/main)
[![Issues](https://img.shields.io/github/issues/gabrielhonorato8357/ai-analytics-platform)](https://github.com/gabrielhonorato8357/ai-analytics-platform/issues)

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

Prerequisites:

- Docker and Docker Compose
- Node.js 22 for the web app
- Python 3.12 for the API service

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
make api-migrate
make api-bootstrap-admin
```

## Bootstrap Admin

Set these values in `.env` before bootstrapping the first administrator:

```bash
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=change-me-admin-password
FIRST_SUPERUSER_NAME=Platform Administrator
```

Then run:

```bash
make api-bootstrap-admin
```
