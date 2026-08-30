"""
Main FastAPI Application Entrypoint.
Registers middleware, MongoDB + ML-engine startup, and API routers.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.api import (
    auth, onboarding, careers, skills, recommendations,
    paths, assessments, assistant, analytics, system
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered Career & Personalized Learning Path Operating System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(careers.router)
app.include_router(skills.router)
app.include_router(recommendations.router)
app.include_router(paths.router)
app.include_router(assessments.router)
app.include_router(assistant.router)
app.include_router(analytics.router)
app.include_router(system.router)


@app.exception_handler(PyMongoError)
def _mongo_unavailable(request: Request, exc: PyMongoError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is currently unavailable. Please try again shortly."},
    )


@app.on_event("startup")
def _startup():
    from app.db import mongo
    try:
        mongo.ping()
        mongo.ensure_indexes()
        print(f"[mongo] connected to '{settings.MONGODB_DB}'")
    except Exception as e:
        print(f"[mongo] connection failed: {e}")
    try:
        from app.ml.engine import engine
        engine.warm()
    except Exception as e:
        print(f"[startup] ML engine warm failed: {e}")


@app.get("/")
def root_status():
    return {"status": "online", "app": settings.APP_NAME, "version": settings.VERSION, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
