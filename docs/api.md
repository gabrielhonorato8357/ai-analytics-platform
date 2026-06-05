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
- Natural language query submission
- SQL generation and validation
- Query execution
- Saved reports
- User management
- Audit logs
