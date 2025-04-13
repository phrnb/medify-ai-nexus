
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, patients, images, analyses, reports, notifications, analytics, knowledge_base, ai_feedback

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["knowledge_base"])
api_router.include_router(ai_feedback.router, prefix="/ai-feedback", tags=["ai_feedback"])
