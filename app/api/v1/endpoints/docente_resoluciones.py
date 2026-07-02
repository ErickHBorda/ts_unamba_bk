from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.docente_resolucion import DocenteResolucion
from app.models.docente import Docente
from app.models.resolucion import Resolucion
from app.schemas.docente_resolucion import (
    DocenteResolucionCreate,
    DocenteResolucionResponse,
)

router = APIRouter()


@router.get(
    "/{docente_id}/resoluciones",
    response_model=list[DocenteResolucionResponse],
)
def listar_resoluciones_de_docente(
    docente_id: int,
    db:         Session = Depends(get_db),
):
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con id {docente_id} no encontrado.",
        )

    return db.query(DocenteResolucion).filter(
        DocenteResolucion.docente_id == docente_id
    ).all()


@router.get(
    "/{resolucion_id}/docentes",
    response_model=list[DocenteResolucionResponse],
)
def listar_docentes_de_resolucion(
    resolucion_id: int,
    db:            Session = Depends(get_db),
):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )

    return db.query(DocenteResolucion).filter(
        DocenteResolucion.resolucion_id == resolucion_id
    ).all()


@router.post(
    "/",
    response_model=DocenteResolucionResponse,
    status_code=status.HTTP_201_CREATED,
)
def asignar_resolucion_a_docente(
    payload: DocenteResolucionCreate,
    db:      Session = Depends(get_db),
):
    if not db.query(Docente).filter(Docente.id == payload.docente_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con id {payload.docente_id} no encontrado.",
        )
    if not db.query(Resolucion).filter(Resolucion.id == payload.resolucion_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {payload.resolucion_id} no encontrada.",
        )

    existente = db.query(DocenteResolucion).filter(
        DocenteResolucion.docente_id    == payload.docente_id,
        DocenteResolucion.resolucion_id == payload.resolucion_id,
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta resolución ya está asignada a este docente.",
        )

    relacion = DocenteResolucion(
        docente_id=payload.docente_id,
        resolucion_id=payload.resolucion_id,
    )
    db.add(relacion)
    db.commit()
    db.refresh(relacion)
    return relacion


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def desasignar_resolucion_de_docente(
    payload: DocenteResolucionCreate,
    db:      Session = Depends(get_db),
):
    relacion = db.query(DocenteResolucion).filter(
        DocenteResolucion.docente_id    == payload.docente_id,
        DocenteResolucion.resolucion_id == payload.resolucion_id,
    ).first()
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe una asignación entre este docente y esta resolución.",
        )

    db.delete(relacion)
    db.commit()