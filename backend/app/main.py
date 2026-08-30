from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import settings
from app.db.database import engine, Base
from app.api import auth, onboarding, careers, skills, recommendations, paths, assessments, assistant, analytics, system
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, description='Industry-Ready AI-Powered Gen-Z Career & Personalized Learning Path Operating System')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
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

@app.on_event('startup')
def _warm_ml_engine():
    try:
        from app.ml.engine import engine
        engine.warm()
    except Exception as e:
        print(f'[startup] ML engine warm failed: {e}')

@app.get('/')
def root_status():
    return {'status': 'online', 'app': settings.APP_NAME, 'version': settings.VERSION, 'docs': '/docs'}
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=True)
