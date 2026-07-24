from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.db.session import get_db
from app.models.docente import Docente
from app.schemas.docente import (
    DocenteCreate,
    DocenteUpdate,
    DocenteResponse,
    DocenteListResponse,
)
from app.schemas.response import success_response, error_response
from typing import Annotated
from app.core.dependencies import get_current_user, get_admin_user
from app.models.usuario import Usuario
from app.models.periodo_servicio import PeriodoServicio
from app.models.categoria_docente import CategoriaDocente
from app.models.condicion_laboral import CondicionLaboral

router = APIRouter()


@router.get("/", response_model=None)
def listar_docentes(
    buscar: Optional[str] = Query(
        None, description="Buscar por nombre, apellido o DNI"
    ),
    activo: Optional[bool] = Query(
        None, description="Filtrar por estado activo/inactivo"
    ),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    condicion_id: Optional[int] = Query(
        None, description="Filtrar por condición laboral"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_current_user)] = None,
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

    # Filtro por categoría o condición via subquery en PERIODO_SERVICIO
    if categoria_id is not None or condicion_id is not None:
        subquery = db.query(PeriodoServicio.docente_id).filter(
            PeriodoServicio.activo == True
        )
        if categoria_id is not None:
            subquery = subquery.filter(PeriodoServicio.categoria_id == categoria_id)
        if condicion_id is not None:
            subquery = subquery.filter(PeriodoServicio.condicion_id == condicion_id)
        query = query.filter(Docente.id.in_(subquery))

    query = query.order_by(Docente.apellidos.asc(), Docente.nombres.asc())
    docentes = query.offset(skip).limit(limit).all()

    # Construir respuesta con categoría y condición del último periodo activo
    resultado = []
    for docente in docentes:
        ultimo_periodo = (
            db.query(PeriodoServicio)
            .filter(
                PeriodoServicio.docente_id == docente.id,
                PeriodoServicio.activo == True,
            )
            .order_by(PeriodoServicio.id.desc())
            .first()
        )
        resultado.append(
            {
                "id": docente.id,
                "nombres": docente.nombres,
                "apellidos": docente.apellidos,
                "dni": docente.dni,
                "email": docente.email,
                "activo": docente.activo,
                "categoria_codigo": (
                    ultimo_periodo.categoria.codigo if ultimo_periodo else None
                ),
                "categoria_nombre": (
                    ultimo_periodo.categoria.nombre if ultimo_periodo else None
                ),
                "condicion_nombre": (
                    ultimo_periodo.condicion.nombre if ultimo_periodo else None
                ),
            }
        )

    return success_response(data=resultado)


@router.get("/conteo", response_model=None)
def conteo_docentes(
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_current_user)] = None,
):
    total = db.query(Docente).count()
    activos = db.query(Docente).filter(Docente.activo == True).count()
    inactivos = db.query(Docente).filter(Docente.activo == False).count()

    return success_response(
        data={
            "total": total,
            "activos": activos,
            "inactivos": inactivos,
        }
    )


@router.get("/{docente_id}", response_model=None)
def obtener_docente(
    docente_id: int,
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_current_user)] = None,
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

    return success_response(
        data=DocenteResponse.model_validate(docente).model_dump(mode="json")
    )


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def crear_docente(
    payload: DocenteCreate,
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_admin_user)] = None,
):
    existente = db.query(Docente).filter(Docente.dni == payload.dni).first()
    if existente:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(
                code="DNI_DUPLICADO",
                message=f"Ya existe un docente registrado con DNI {payload.dni}.",
            ),
        )

    docente = Docente(**payload.model_dump())
    db.add(docente)
    db.commit()
    db.refresh(docente)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success_response(
            data=DocenteResponse.model_validate(docente).model_dump(mode="json")
        ),
    )


@router.patch("/{docente_id}", response_model=None)
def actualizar_docente(
    docente_id: int,
    payload: DocenteUpdate,
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_admin_user)] = None,
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

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(docente, campo, valor)

    db.commit()
    db.refresh(docente)

    return success_response(
        data=DocenteResponse.model_validate(docente).model_dump(mode="json")
    )


@router.delete("/{docente_id}", response_model=None)
def eliminar_docente(
    docente_id: int,
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_admin_user)] = None,
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

    db.delete(docente)
    db.commit()

    return success_response(data={"mensaje": "Docente eliminado correctamente."})
