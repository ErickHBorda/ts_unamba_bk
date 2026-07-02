from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import uuid

from app.db.session import get_db
from app.models.resolucion import Resolucion
from app.core.config import settings
from app.schemas.response import success_response, error_response

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_MB    = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

@router.post("/{resolucion_id}/pdf", response_model=None)
async def subir_pdf_resolucion(
    resolucion_id: int,
    archivo:       UploadFile = File(...),
    db:            Session    = Depends(get_db),
):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Resolución con id {resolucion_id} no encontrada.",
            ),
        )

    if archivo.content_type not in ALLOWED_CONTENT_TYPES:
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content=error_response(
                code="TIPO_INVALIDO",
                message="Solo se permiten archivos en formato PDF.",
            ),
        )

    contenido = await archivo.read()
    if len(contenido) > MAX_FILE_SIZE_BYTES:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content=error_response(
                code="ARCHIVO_MUY_GRANDE",
                message=f"El archivo supera el límite permitido de {MAX_FILE_SIZE_MB} MB.",
            ),
        )

    if resolucion.archivo_pdf:
        archivo_anterior = Path(resolucion.archivo_pdf)
        if archivo_anterior.exists():
            archivo_anterior.unlink()

    extension     = Path(archivo.filename).suffix.lower()
    nombre_archivo = f"resolucion_{resolucion_id}_{uuid.uuid4().hex}{extension}"
    ruta_destino   = settings.RESOLUCIONES_DIR / nombre_archivo

    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    resolucion.archivo_pdf = str(ruta_destino)
    db.commit()
    db.refresh(resolucion)

    return success_response(data={
        "mensaje":       "PDF subido correctamente.",
        "resolucion_id": resolucion_id,
        "archivo_pdf":   nombre_archivo,
    })


@router.get("/{resolucion_id}/pdf")
def descargar_pdf_resolucion(resolucion_id: int, db: Session = Depends(get_db)):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Resolución con id {resolucion_id} no encontrada.",
            ),
        )

    if not resolucion.archivo_pdf:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="SIN_PDF",
                message="Esta resolución no tiene un PDF adjunto.",
            ),
        )

    ruta_archivo = Path(resolucion.archivo_pdf)
    if not ruta_archivo.exists():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="ARCHIVO_NO_ENCONTRADO",
                message="El archivo PDF no fue encontrado en el servidor.",
            ),
        )

    return FileResponse(
        path=ruta_archivo,
        media_type="application/pdf",
        filename=ruta_archivo.name,
    )


@router.delete("/{resolucion_id}/pdf", response_model=None)
def eliminar_pdf_resolucion(resolucion_id: int, db: Session = Depends(get_db)):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Resolución con id {resolucion_id} no encontrada.",
            ),
        )

    if not resolucion.archivo_pdf:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="SIN_PDF",
                message="Esta resolución no tiene un PDF adjunto.",
            ),
        )

    ruta_archivo = Path(resolucion.archivo_pdf)
    if ruta_archivo.exists():
        ruta_archivo.unlink()

    resolucion.archivo_pdf = None
    db.commit()

    return success_response(data={"mensaje": "PDF eliminado correctamente."})