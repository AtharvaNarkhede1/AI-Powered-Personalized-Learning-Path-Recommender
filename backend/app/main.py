"""
Career PathFinder API entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Docs available at http://localhost:8000/docs once running.

Routers (see app/api/*.py for full endpoint docs):
  /api/profile   - learner profiling engine
  /api/chat      - conversational interface
  /api/recommend - recommendation engine + explanations + assistant Q&A
  /api/path      - learning path generator
  /api/progress  - progress dashboard data

TODO:
- Add a health/readiness split (/healthz vs /readyz) before deploying behind
  a load balancer.
- Add request logging / rate limiting middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import profile, chat, recommend, path, progress

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(recommend.router)
app.include_router(path.router)
app.include_router(progress.router)


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "status": "ok"}


@app.get("/healthz")
def health():
    return {"status": "healthy"}
