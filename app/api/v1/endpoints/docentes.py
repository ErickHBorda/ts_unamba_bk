from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.db.session import get_db
from app.models.docente import Docente
from app.schemas.docente import DocenteCreate, DocenteUpdate, DocenteResponse, DocenteListResponse

router = APIRouter()


@router.get("/", response_model=list[DocenteListResponse])
def listar_docentes(
    buscar:      Optional[str]  = Query(None, description="Buscar por nombre, apellido o DNI"),
    activo:      Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    skip:        int            = Query(0, ge=0),
    limit:       int            = Query(20, ge=1, le=100),
    db:          Session        = Depends(get_db),
):
    query = db.query(Docente)

    if buscar:
        termino = f"%{buscar}%"
        query = query.filter(
            or_(
                Docente.nombres.ilike(termino),
                Docente.apellidos.ilike(termino),
                Docente.dni.ilike(termino),
            )
        )

    if activo is not None:
        query = query.filter(Docente.activo == activo)

    query = query.order_by(Docente.apellidos.asc(), Docente.nombres.asc())

    return query.offset(skip).limit(limit).all()


@router.get("/conteo", response_model=dict)
def conteo_docentes(db: Session = Depends(get_db)):
    total      = db.query(Docente).count()
    activos    = db.query(Docente).filter(Docente.activo == True).count()
    inactivos  = db.query(Docente).filter(Docente.activo == False).count()

    return {
        "total":     total,
        "activos":   activos,
        "inactivos": inactivos,
    }


@router.get("/{docente_id}", response_model=DocenteResponse)
def obtener_docente(docente_id: int, db: Session = Depends(get_db)):
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con id {docente_id} no encontrado.",
        )
    return docente


@router.post("/", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
def crear_docente(payload: DocenteCreate, db: Session = Depends(get_db)):
    existente = db.query(Docente).filter(Docente.dni == payload.dni).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un docente registrado con DNI {payload.dni}.",
        )

    docente = Docente(**payload.model_dump())
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


@router.patch("/{docente_id}", response_model=DocenteResponse)
def actualizar_docente(
    docente_id: int,
    payload:    DocenteUpdate,
    db:         Session = Depends(get_db),
):
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con id {docente_id} no encontrado.",
        )

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(docente, campo, valor)

    db.commit()
    db.refresh(docente)
    return docente


@router.delete("/{docente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_docente(docente_id: int, db: Session = Depends(get_db)):
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con id {docente_id} no encontrado.",
        )

    db.delete(docente)
    db.commit()