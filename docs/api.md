# API Documentation

FastAPI generates interactive OpenAPI documentation at `/docs` and the raw OpenAPI schema at `/openapi.json`.

## Current Endpoints

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

