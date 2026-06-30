from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import uuid

from app.db.session import get_db
from app.models.resolucion import Resolucion
from app.core.config import settings

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post(
    "/{resolucion_id}/pdf",
    status_code=status.HTTP_200_OK,
    summary="Subir o reemplazar PDF de una resolución",
)
async def subir_pdf_resolucion(
    resolucion_id: int,
    archivo:       UploadFile = File(...),
    db:            Session    = Depends(get_db),
):
    # Verificar que la resolución existe
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )

    # Validar tipo de archivo
    if archivo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se permiten archivos en formato PDF.",
        )

    # Leer contenido y validar tamaño
    contenido = await archivo.read()
    if len(contenido) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite permitido de {MAX_FILE_SIZE_MB} MB.",
        )

    # Eliminar PDF anterior si existe
    if resolucion.archivo_pdf:
        archivo_anterior = Path(resolucion.archivo_pdf)
        if archivo_anterior.exists():
            archivo_anterior.unlink()

    # Generar nombre único para evitar colisiones
    extension  = Path(archivo.filename).suffix.lower()
    nombre_archivo = f"resolucion_{resolucion_id}_{uuid.uuid4().hex}{extension}"
    ruta_destino   = settings.RESOLUCIONES_DIR / nombre_archivo

    # Guardar archivo en disco
    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    # Guardar ruta relativa en BD
    resolucion.archivo_pdf = str(ruta_destino)
    db.commit()
    db.refresh(resolucion)

    return {
        "mensaje":      "PDF subido correctamente.",
        "resolucion_id": resolucion_id,
        "archivo_pdf":  nombre_archivo,
    }


@router.get(
    "/{resolucion_id}/pdf",
    summary="Descargar o visualizar PDF de una resolución",
)
def descargar_pdf_resolucion(
    resolucion_id: int,
    db:            Session = Depends(get_db),
):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )

    if not resolucion.archivo_pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta resolución no tiene un PDF adjunto.",
        )

    ruta_archivo = Path(resolucion.archivo_pdf)
    if not ruta_archivo.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo PDF no fue encontrado en el servidor.",
        )

    return FileResponse(
        path=ruta_archivo,
        media_type="application/pdf",
        filename=ruta_archivo.name,
    )


@router.delete(
    "/{resolucion_id}/pdf",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar PDF de una resolución",
)
def eliminar_pdf_resolucion(
    resolucion_id: int,
    db:            Session = Depends(get_db),
):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )

    if not resolucion.archivo_pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta resolución no tiene un PDF adjunto.",
        )

    ruta_archivo = Path(resolucion.archivo_pdf)
    if ruta_archivo.exists():
        ruta_archivo.unlink()

    resolucion.archivo_pdf = None
    db.commit()