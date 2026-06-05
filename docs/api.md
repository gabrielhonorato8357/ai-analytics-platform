# API Documentation

FastAPI generates interactive OpenAPI documentation at `/docs` and the raw OpenAPI schema at `/openapi.json`.

## Current Endpoints

### `POST /api/v1/auth/register`

Creates a user account and returns a bearer token.

Request body:

```json
{
  "email": "analyst@example.com",
  "full_name": "Ada Analyst",
  "password": "correct-horse-battery"
}
```

### `POST /api/v1/auth/login`

Authenticates a user and returns a bearer token.

Request body:

```json
{
  "email": "analyst@example.com",
  "password": "correct-horse-battery"
}
```

### `GET /api/v1/auth/me`

Returns the authenticated user for the supplied `Authorization: Bearer <token>` header.

### `POST /api/v1/queries/generate`

Accepts a natural language analytics question and returns generated SQL when an AI SQL provider is configured.

Configuration:

- `AI_SQL_PROVIDER=disabled`: returns `503 Service Unavailable`
- `AI_SQL_PROVIDER=local`: uses a deterministic local development generator
- `AI_SQL_PROVIDER=openai`: calls the OpenAI Responses API with Structured Outputs

OpenAI configuration requires `OPENAI_API_KEY`; `OPENAI_MODEL` defaults to `gpt-5.4-mini`.

### `POST /api/v1/queries/execute`

Executes one read-only PostgreSQL `SELECT` query after parser validation and applies a server-side row limit.

Request body:

```json
{
  "sql": "select segment, revenue from revenue_by_segment",
  "limit": 100
}
```

### `GET /api/v1/reports`

Lists saved reports owned by the authenticated user.

### `POST /api/v1/reports`

Creates a saved report for the authenticated user.

Request body:

```json
{
  "title": "Revenue by segment",
  "description": "Quarterly revenue report",
  "sql": "select segment, revenue from revenue_by_segment",
  "visualization_type": "bar",
  "chart_config": {
    "xKey": "segment",
    "yKey": "revenue"
  }
}
```

### `GET /api/v1/reports/{report_id}`

Returns one saved report owned by the authenticated user.

### `DELETE /api/v1/reports/{report_id}`

Deletes one saved report owned by the authenticated user.

### `GET /api/v1/users`

Lists platform users. Requires a superuser bearer token.

### `PATCH /api/v1/users/{user_id}`

Updates managed user fields. Requires a superuser bearer token and writes an audit log entry.

Request body:

```json
{
  "full_name": "Grace Analyst",
  "is_active": true,
  "is_superuser": false
}
```

### `GET /api/v1/audit-logs`

Lists recent platform audit events. Requires a superuser bearer token.

### `GET /api/v1/health`

Returns application liveness metadata.

Example response:

```json
{
  "status": "ok",
  "service": "ai-analytics-api",
  "environment": "development"
}
```

## Planned Endpoint Groups

- Authentication and session management
