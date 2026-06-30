from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.db.session import get_db
from app.models.resolucion import Resolucion
from app.schemas.resolucion import (
    ResolucionCreate,
    ResolucionUpdate,
    ResolucionResponse,
    ResolucionListResponse,
)

router = APIRouter()


@router.get("/", response_model=list[ResolucionListResponse])
def listar_resoluciones(
    buscar: Optional[str] = Query(None, description="Buscar por número o emisor"),
    skip:   int           = Query(0, ge=0),
    limit:  int           = Query(20, ge=1, le=100),
    db:     Session       = Depends(get_db),
):
    query = db.query(Resolucion)

    if buscar:
        termino = f"%{buscar}%"
        query = query.filter(
            or_(
                Resolucion.numero_resolucion.ilike(termino),
                Resolucion.emitida_por.ilike(termino),
                Resolucion.tipo.ilike(termino),
            )
        )

    query = query.order_by(Resolucion.fecha_emision.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/{resolucion_id}", response_model=ResolucionResponse)
def obtener_resolucion(resolucion_id: int, db: Session = Depends(get_db)):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )
    return resolucion


@router.post("/", response_model=ResolucionResponse, status_code=status.HTTP_201_CREATED)
def crear_resolucion(payload: ResolucionCreate, db: Session = Depends(get_db)):
    existente = db.query(Resolucion).filter(
        Resolucion.numero_resolucion == payload.numero_resolucion
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una resolución con el número {payload.numero_resolucion}.",
        )

    resolucion = Resolucion(**payload.model_dump())
    db.add(resolucion)
    db.commit()
    db.refresh(resolucion)
    return resolucion


@router.patch("/{resolucion_id}", response_model=ResolucionResponse)
def actualizar_resolucion(
    resolucion_id: int,
    payload:       ResolucionUpdate,
    db:            Session = Depends(get_db),
):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )

    if payload.numero_resolucion:
        duplicado = db.query(Resolucion).filter(
            Resolucion.numero_resolucion == payload.numero_resolucion,
            Resolucion.id != resolucion_id,
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra resolución con el número {payload.numero_resolucion}.",
            )

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(resolucion, campo, valor)

    db.commit()
    db.refresh(resolucion)
    return resolucion


@router.delete("/{resolucion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_resolucion(resolucion_id: int, db: Session = Depends(get_db)):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolución con id {resolucion_id} no encontrada.",
        )

    db.delete(resolucion)
    db.commit()