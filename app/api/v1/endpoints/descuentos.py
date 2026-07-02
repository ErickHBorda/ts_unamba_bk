from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.descuento_periodo import DescuentoPeriodo
from app.models.periodo_servicio import PeriodoServicio
from app.schemas.descuento_periodo import (
    DescuentoPeriodoCreate,
    DescuentoPeriodoUpdate,
    DescuentoPeriodoResponse,
)

router = APIRouter()


def calcular_total(faltas: int, permisos: int, licencias: int) -> int:
    return faltas + permisos + licencias


@router.get("/{periodo_id}/descuento", response_model=DescuentoPeriodoResponse)
def obtener_descuento(periodo_id: int, db: Session = Depends(get_db)):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodo con id {periodo_id} no encontrado.",
        )

    descuento = db.query(DescuentoPeriodo).filter(
        DescuentoPeriodo.periodo_id == periodo_id
    ).first()
    if not descuento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El periodo {periodo_id} no tiene descuentos registrados.",
        )
    return descuento


@router.post(
    "/{periodo_id}/descuento",
    response_model=DescuentoPeriodoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_descuento(
    periodo_id: int,
    payload:    DescuentoPeriodoCreate,
    db:         Session = Depends(get_db),
):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodo con id {periodo_id} no encontrado.",
        )

    existente = db.query(DescuentoPeriodo).filter(
        DescuentoPeriodo.periodo_id == periodo_id
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El periodo {periodo_id} ya tiene descuentos registrados. Usa PATCH para actualizar.",
        )

    total = calcular_total(
        payload.faltas_injustificadas,
        payload.permisos_sin_goce,
        payload.licencias_sin_goce,
    )

    descuento = DescuentoPeriodo(
        periodo_id=periodo_id,
        faltas_injustificadas=payload.faltas_injustificadas,
        permisos_sin_goce=payload.permisos_sin_goce,
        licencias_sin_goce=payload.licencias_sin_goce,
        total_dias_descuento=total,
        observaciones=payload.observaciones,
    )
    db.add(descuento)
    db.commit()
    db.refresh(descuento)
    return descuento


@router.patch("/{periodo_id}/descuento", response_model=DescuentoPeriodoResponse)
def actualizar_descuento(
    periodo_id: int,
    payload:    DescuentoPeriodoUpdate,
    db:         Session = Depends(get_db),
):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodo con id {periodo_id} no encontrado.",
        )

    descuento = db.query(DescuentoPeriodo).filter(
        DescuentoPeriodo.periodo_id == periodo_id
    ).first()
    if not descuento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El periodo {periodo_id} no tiene descuentos registrados. Usa POST para crear.",
        )

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(descuento, campo, valor)

    # Recalcular total con los valores actuales tras el update
    descuento.total_dias_descuento = calcular_total(
        descuento.faltas_injustificadas,
        descuento.permisos_sin_goce,
        descuento.licencias_sin_goce,
    )

    db.commit()
    db.refresh(descuento)
    return descuento


@router.delete("/{periodo_id}/descuento", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_descuento(periodo_id: int, db: Session = Depends(get_db)):
    periodo = db.query(PeriodoServicio).filter(PeriodoServicio.id == periodo_id).first()
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodo con id {periodo_id} no encontrado.",
        )

    descuento = db.query(DescuentoPeriodo).filter(
        DescuentoPeriodo.periodo_id == periodo_id
    ).first()
    if not descuento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El periodo {periodo_id} no tiene descuentos registrados.",
        )

    db.delete(descuento)
    db.commit()