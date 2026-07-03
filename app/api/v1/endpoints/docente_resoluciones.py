from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.docente_resolucion import DocenteResolucion
from app.models.docente import Docente
from app.models.resolucion import Resolucion
from app.schemas.docente_resolucion import (
    DocenteResolucionCreate,
    DocenteResolucionResponse,
)
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/{docente_id}/resoluciones", response_model=None)
def listar_resoluciones_de_docente(
    docente_id: int,
    db:         Session = Depends(get_db),
):
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Docente con id {docente_id} no encontrado.",
            ),
        )

    relaciones = db.query(DocenteResolucion).filter(
        DocenteResolucion.docente_id == docente_id
    ).all()

    return success_response(
        data=[DocenteResolucionResponse.model_validate(r).model_dump(mode="json") for r in relaciones]
    )


@router.get("/{resolucion_id}/docentes", response_model=None)
def listar_docentes_de_resolucion(
    resolucion_id: int,
    db:            Session = Depends(get_db),
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

    relaciones = db.query(DocenteResolucion).filter(
        DocenteResolucion.resolucion_id == resolucion_id
    ).all()

    return success_response(
        data=[DocenteResolucionResponse.model_validate(r).model_dump(mode="json") for r in relaciones]
    )


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def asignar_resolucion_a_docente(
    payload: DocenteResolucionCreate,
    db:      Session = Depends(get_db),
):
    if not db.query(Docente).filter(Docente.id == payload.docente_id).first():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Docente con id {payload.docente_id} no encontrado.",
            ),
        )

    if not db.query(Resolucion).filter(Resolucion.id == payload.resolucion_id).first():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Resolución con id {payload.resolucion_id} no encontrada.",
            ),
        )

    existente = db.query(DocenteResolucion).filter(
        DocenteResolucion.docente_id    == payload.docente_id,
        DocenteResolucion.resolucion_id == payload.resolucion_id,
    ).first()
    if existente:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(
                code="ASIGNACION_DUPLICADA",
                message="Esta resolución ya está asignada a este docente.",
            ),
        )

    relacion = DocenteResolucion(
        docente_id=payload.docente_id,
        resolucion_id=payload.resolucion_id,
    )
    db.add(relacion)
    db.commit()
    db.refresh(relacion)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success_response(
            data=DocenteResolucionResponse.model_validate(relacion).model_dump(mode="json")
        ),
    )


@router.delete("/", response_model=None)
def desasignar_resolucion_de_docente(
    payload: DocenteResolucionCreate,
    db:      Session = Depends(get_db),
):
    relacion = db.query(DocenteResolucion).filter(
        DocenteResolucion.docente_id    == payload.docente_id,
        DocenteResolucion.resolucion_id == payload.resolucion_id,
    ).first()
    if not relacion:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message="No existe una asignación entre este docente y esta resolución.",
            ),
        )

    db.delete(relacion)
    db.commit()

    return success_response(data={"mensaje": "Asignación eliminada correctamente."})