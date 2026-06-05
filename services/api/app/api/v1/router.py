from fastapi import APIRouter

from app.api.v1.routers.audit_logs import router as audit_logs_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.queries import router as queries_router
from app.api.v1.routers.reports import router as reports_router
from app.api.v1.routers.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(audit_logs_router)
api_router.include_router(health_router, tags=["health"])
api_router.include_router(queries_router)
api_router.include_router(reports_router)
api_router.include_router(users_router)
