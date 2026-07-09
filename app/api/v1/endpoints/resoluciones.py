from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
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
from app.schemas.response import success_response, error_response

from typing import Annotated
from app.core.dependencies import get_current_user, get_admin_user
from app.models.usuario import Usuario

router = APIRouter()


@router.get("/", response_model=None)
def listar_resoluciones(
    buscar: Optional[str] = Query(None, description="Buscar por número o emisor"),
    skip:   int           = Query(0, ge=0),
    limit:  int           = Query(20, ge=1, le=100),
    db:     Session       = Depends(get_db),
    _:      Annotated[Usuario, Depends(get_current_user)] = None,
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
    resoluciones = query.offset(skip).limit(limit).all()

    return success_response(
        data=[ResolucionListResponse.model_validate(r).model_dump(mode="json") for r in resoluciones]
    )


@router.get("/{resolucion_id}", response_model=None)
def obtener_resolucion(resolucion_id: int, db: Session = Depends(get_db), _: Annotated[Usuario, Depends(get_current_user)] = None):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Resolución con id {resolucion_id} no encontrada.",
            ),
        )

    return success_response(
        data=ResolucionResponse.model_validate(resolucion).model_dump(mode="json")
    )


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def crear_resolucion(payload: ResolucionCreate, db: Session = Depends(get_db), _: Annotated[Usuario, Depends(get_admin_user)] = None):
    existente = db.query(Resolucion).filter(
        Resolucion.numero_resolucion == payload.numero_resolucion
    ).first()
    if existente:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(
                code="NUMERO_DUPLICADO",
                message=f"Ya existe una resolución con el número {payload.numero_resolucion}.",
            ),
        )

    resolucion = Resolucion(**payload.model_dump())
    db.add(resolucion)
    db.commit()
    db.refresh(resolucion)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success_response(
            data=ResolucionResponse.model_validate(resolucion).model_dump(mode="json")
        ),
    )


@router.patch("/{resolucion_id}", response_model=None)
def actualizar_resolucion(
    resolucion_id: int,
    payload:       ResolucionUpdate,
    db:            Session = Depends(get_db),
    _:             Annotated[Usuario, Depends(get_admin_user)] = None,  
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

    if payload.numero_resolucion:
        duplicado = db.query(Resolucion).filter(
            Resolucion.numero_resolucion == payload.numero_resolucion,
            Resolucion.id != resolucion_id,
        ).first()
        if duplicado:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=error_response(
                    code="NUMERO_DUPLICADO",
                    message=f"Ya existe otra resolución con el número {payload.numero_resolucion}.",
                ),
            )

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(resolucion, campo, valor)

    db.commit()
    db.refresh(resolucion)

    return success_response(
        data=ResolucionResponse.model_validate(resolucion).model_dump(mode="json")
    )


@router.delete("/{resolucion_id}", response_model=None)
def eliminar_resolucion(resolucion_id: int, db: Session = Depends(get_db), _: Annotated[Usuario, Depends(get_admin_user)] = None):
    resolucion = db.query(Resolucion).filter(Resolucion.id == resolucion_id).first()
    if not resolucion:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Resolución con id {resolucion_id} no encontrada.",
            ),
        )

    db.delete(resolucion)
    db.commit()

    return success_response(data={"mensaje": "Resolución eliminada correctamente."})