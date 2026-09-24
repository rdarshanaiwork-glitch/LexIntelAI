from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.documents import router as docs_router
from app.api.research import router as research_router
from app.api.reports import router as reports_router
from app.api.health import router as health_router
from app.api.evaluation import router as evaluation_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(cases_router)
api_router.include_router(docs_router)
api_router.include_router(research_router)
api_router.include_router(reports_router)
api_router.include_router(evaluation_router)

__all__ = ["api_router"]
