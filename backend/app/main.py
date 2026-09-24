import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.session import init_db
from app.rag.knowledge_service import knowledge_service
from app.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lexintel.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing LexIntel AI database tables...")
    init_db()
    logger.info("Bootstrapping sample legal knowledge base into vector store...")
    knowledge_service.bootstrap_sample_knowledge()
    logger.info("LexIntel AI backend ready.")
    yield
    logger.info("Shutting down LexIntel AI backend.")

app = FastAPI(
    title="LexIntel AI",
    description="Multi-Agent Agentic Legal Intelligence System for Strategic Legal Decision-Making",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development on any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred in LexIntel AI.", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)