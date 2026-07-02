from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.periodo_servicio import PeriodoServicio
from app.models.docente import Docente
from app.models.categoria_docente import CategoriaDocente
from app.models.condicion_laboral import CondicionLaboral
from app.models.resolucion import Resolucion
from app.schemas.periodo_servicio import (
    PeriodoServicioCreate,
    PeriodoServicioUpdate,
    PeriodoServicioResponse,
    PeriodoServicioListResponse,
)
from app.schemas.response import success_response, error_response

router = APIRouter()


def verificar_dependencias(payload, db: Session) -> Optional[JSONResponse]:
    if not db.query(Docente).filter(Docente.id == payload.docente_id).first():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Docente con id {payload.docente_id} no encontrado.",
            ),
        )
    if not db.query(CategoriaDocente).filter(CategoriaDocente.id == payload.categoria_id).first():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Categoría con id {payload.categoria_id} no encontrada.",
            ),
        )
    if not db.query(CondicionLaboral).filter(CondicionLaboral.id == payload.condicion_id).first():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Condición laboral con id {payload.condicion_id} no encontrada.",
            ),
        )
    if payload.resolucion_id:
        if not db.query(Resolucion).filter(Resolucion.id == payload.resolucion_id).first():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response(
                    code="NOT_FOUND",
                    message=f"Resolución con id {payload.resolucion_id} no encontrada.",
                ),
            )
    return None


@router.get("/", response_model=None)
def listar_periodos(
    docente_id:    Optional[int]  = Query(None, description="Filtrar por docente"),
    tipo_registro: Optional[str]  = Query(None, description="ACTIVO | CON_FECHAS | MANUAL"),
    activo:        Optional[bool] = Query(None, description="Filtrar por estado"),
    skip:          int            = Query(0, ge=0),
    limit:         int            = Query(20, ge=1, le=100),
    db:            Session        = Depends(get_db),
):
    query = db.query(PeriodoServicio)

    if docente_id is not None:
        query = query.filter(PeriodoServicio.docente_id == docente_id)
    if tipo_registro:
        query = query.filter(PeriodoServicio.tipo_registro == tipo_registro.upper())
    if activo is not None:
        query = query.filter(PeriodoServicio.activo == activo)

    query = query.order_by(PeriodoServicio.fecha_inicio.asc())
    periodos = query.offset(skip).limit(limit).all()

    return success_response(
        data=[PeriodoServicioListResponse.model_validate(p).model_dump(mode="json") for p in periodos]
    )


@router.get("/{periodo_id}", response_model=None)
def obtener_periodo(periodo_id: int, db: Session = Depends(get_db)):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Periodo con id {periodo_id} no encontrado.",
            ),
        )

    return success_response(
        data=PeriodoServicioResponse.model_validate(periodo).model_dump(mode="json")
    )


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def crear_periodo(payload: PeriodoServicioCreate, db: Session = Depends(get_db)):
    error = verificar_dependencias(payload, db)
    if error:
        return error

    periodo = PeriodoServicio(**payload.model_dump())
    db.add(periodo)
    db.commit()
    db.refresh(periodo)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success_response(
            data=PeriodoServicioResponse.model_validate(periodo).model_dump(mode="json")
        ),
    )


@router.patch("/{periodo_id}", response_model=None)
def actualizar_periodo(
    periodo_id: int,
    payload:    PeriodoServicioUpdate,
    db:         Session = Depends(get_db),
):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Periodo con id {periodo_id} no encontrado.",
            ),
        )

    datos = payload.model_dump(exclude_unset=True)

    if "categoria_id" in datos:
        if not db.query(CategoriaDocente).filter(CategoriaDocente.id == datos["categoria_id"]).first():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response(
                    code="NOT_FOUND",
                    message=f"Categoría con id {datos['categoria_id']} no encontrada.",
                ),
            )
    if "condicion_id" in datos:
        if not db.query(CondicionLaboral).filter(CondicionLaboral.id == datos["condicion_id"]).first():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response(
                    code="NOT_FOUND",
                    message=f"Condición laboral con id {datos['condicion_id']} no encontrada.",
                ),
            )
    if "resolucion_id" in datos and datos["resolucion_id"] is not None:
        if not db.query(Resolucion).filter(Resolucion.id == datos["resolucion_id"]).first():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response(
                    code="NOT_FOUND",
                    message=f"Resolución con id {datos['resolucion_id']} no encontrada.",
                ),
            )

    for campo, valor in datos.items():
        setattr(periodo, campo, valor)

    db.commit()
    db.refresh(periodo)

    return success_response(
        data=PeriodoServicioResponse.model_validate(periodo).model_dump(mode="json")
    )


@router.delete("/{periodo_id}", response_model=None)
def eliminar_periodo(periodo_id: int, db: Session = Depends(get_db)):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Periodo con id {periodo_id} no encontrado.",
            ),
        )

    db.delete(periodo)
    db.commit()

    return success_response(data={"mensaje": "Periodo eliminado correctamente."})