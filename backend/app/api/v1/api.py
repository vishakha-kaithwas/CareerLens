from fastapi import APIRouter
from app.api.v1.routes import health, resume, job, matching, analysis, roadmap, improvement

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(resume.router)
api_router.include_router(job.router)
api_router.include_router(matching.router)
api_router.include_router(analysis.router)
api_router.include_router(roadmap.router)
api_router.include_router(improvement.router)
