from fastapi import APIRouter
from app.api.v1.endpoints import docentes

router = APIRouter(prefix="/api/v1")
router.include_router(docentes.router, prefix="/docentes", tags=["Docentes"])