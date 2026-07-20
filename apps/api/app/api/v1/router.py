from fastapi import APIRouter

from app.api.v1 import ai, auth, downloads, files, generate, preview, projects

api_router = APIRouter()
api_router.include_router(ai.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(files.router)
api_router.include_router(downloads.router)
api_router.include_router(preview.router)
api_router.include_router(preview.live_router)
api_router.include_router(generate.router)
