"""API v1 router"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, patients, history, documents, summaries, abdm

router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(auth.router)
router.include_router(patients.router)
router.include_router(history.router)
router.include_router(documents.router)
router.include_router(summaries.router)
router.include_router(abdm.router)
