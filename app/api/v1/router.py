from fastapi import APIRouter
from app.api.v1.endpoints import (
    docentes, 
    resoluciones, 
    archivos, 
    periodos, 
    descuentos, 
    docente_resoluciones
)
router = APIRouter(prefix="/api/v1")
router.include_router(docentes.router, prefix="/docentes", tags=["Docentes"])
router.include_router(resoluciones.router, prefix="/resoluciones", tags=["Resoluciones"])
router.include_router(archivos.router,    prefix="/resoluciones",  tags=["Archivos PDF"])
router.include_router(periodos.router,    prefix="/periodos",     tags=["Periodos de Servicio"])
router.include_router(descuentos.router,  prefix="/periodos",     tags=["Descuentos de Periodo"])
router.include_router(docente_resoluciones.router, prefix="/docente-resoluciones", tags=["Docente Resoluciones"])