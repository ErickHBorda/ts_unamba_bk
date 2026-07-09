from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.docente import Docente
from app.models.periodo_servicio import PeriodoServicio
from app.models.descuento_periodo import DescuentoPeriodo
from app.models.calculo_tiempo_servicio import CalculoTiempoServicio
from app.models.detalle_calculo import DetalleCalculo
from app.schemas.response import success_response, error_response
from app.schemas.calculo import CalculoResponse
from app.services.calculo_tiempo import (
    calcular_dias_brutos_periodo,
    calcular_tiempo_efectivo_periodo,
    sumar_tiempos_efectivos,
)
from typing import Annotated
from app.core.dependencies import get_current_user, get_admin_user
from app.models.usuario import Usuario

router = APIRouter()


@router.post("/{docente_id}/calcular", response_model=None)
def calcular_tiempo_servicio(docente_id: int, db: Session = Depends(get_db), _: Annotated[Usuario, Depends(get_current_user)] = None):

    # ── 1. Verificar docente ────────────────────────────────────────────
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Docente con id {docente_id} no encontrado.",
            ),
        )

    # ── 2. Obtener periodos activos ─────────────────────────────────────
    periodos = (
        db.query(PeriodoServicio)
        .filter(
            PeriodoServicio.docente_id == docente_id,
            PeriodoServicio.activo == True,
        )
        .order_by(PeriodoServicio.fecha_inicio.asc())
        .all()
    )

    if not periodos:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="SIN_PERIODOS",
                message=f"El docente con id {docente_id} no tiene periodos de servicio registrados.",
            ),
        )

    # ── 3. Calcular cada periodo ────────────────────────────────────────
    resultados_periodos = []
    detalles_para_suma  = []

    for periodo in periodos:

        # 3a. Tiempo bruto según tipo de registro
        anios_b, meses_b, dias_b = calcular_dias_brutos_periodo(
            tipo_registro=periodo.tipo_registro,
            fecha_inicio=periodo.fecha_inicio,
            fecha_fin=periodo.fecha_fin,
            anios_brutos=periodo.anios_brutos,
            meses_brutos=periodo.meses_brutos,
            dias_brutos=periodo.dias_brutos,
        )

        # 3b. Obtener descuentos del periodo
        descuento = (
            db.query(DescuentoPeriodo)
            .filter(DescuentoPeriodo.periodo_id == periodo.id)
            .first()
        )
        total_descuento = descuento.total_dias_descuento if descuento else 0

        # 3c. Calcular tiempo efectivo
        (
            dias_brutos_total,
            dias_descuento,
            dias_efectivos_total,
            anios_ef,
            meses_ef,
            dias_ef,
        ) = calcular_tiempo_efectivo_periodo(
            anios_brutos=anios_b,
            meses_brutos=meses_b,
            dias_brutos=dias_b,
            total_dias_descuento=total_descuento,
        )

        resultados_periodos.append({
            "periodo":              periodo,
            "dias_brutos_total":    dias_brutos_total,
            "dias_descuento":       dias_descuento,
            "dias_efectivos_total": dias_efectivos_total,
            "anios_ef":             anios_ef,
            "meses_ef":             meses_ef,
            "dias_ef":              dias_ef,
        })

        detalles_para_suma.append({
            "dias_brutos_total":    dias_brutos_total,
            "dias_descuento":       dias_descuento,
            "dias_efectivos_total": dias_efectivos_total,
        })

    # ── 4. Sumar todos los periodos ─────────────────────────────────────
    (
        total_anios,
        total_meses,
        total_dias,
        total_dias_brutos,
        total_dias_descuento,
        total_dias_efectivos,
    ) = sumar_tiempos_efectivos(detalles_para_suma)

    # ── 5. Marcar cálculo anterior como HISTORICO ───────────────────────
    db.query(CalculoTiempoServicio).filter(
        CalculoTiempoServicio.docente_id == docente_id,
        CalculoTiempoServicio.estado == "VIGENTE",
    ).update({"estado": "HISTORICO"})

    # ── 6. Guardar nuevo cálculo ────────────────────────────────────────
    nuevo_calculo = CalculoTiempoServicio(
        docente_id=docente_id,
        total_anios=total_anios,
        total_meses=total_meses,
        total_dias=total_dias,
        total_dias_brutos=total_dias_brutos,
        total_dias_descuento=total_dias_descuento,
        total_dias_efectivos=total_dias_efectivos,
        generado_por="sistema",
        estado="VIGENTE",
    )
    db.add(nuevo_calculo)
    db.flush()  # Obtener el ID sin hacer commit aún

    # ── 7. Guardar detalles por periodo ────────────────────────────────
    detalles_response = []

    for r in resultados_periodos:
        periodo  = r["periodo"]
        detalle  = DetalleCalculo(
            calculo_id=nuevo_calculo.id,
            periodo_id=periodo.id,
            dias_brutos_periodo=r["dias_brutos_total"],
            dias_descuento_periodo=r["dias_descuento"],
            dias_efectivos_periodo=r["dias_efectivos_total"],
            anios_efectivos=r["anios_ef"],
            meses_efectivos=r["meses_ef"],
            dias_efectivos=r["dias_ef"],
        )
        db.add(detalle)

        detalles_response.append({
            "periodo_id":             periodo.id,
            "tipo_registro":          periodo.tipo_registro,
            "etiqueta_periodo":       periodo.etiqueta_periodo,
            "categoria":              periodo.categoria.nombre,
            "condicion":              periodo.condicion.nombre,
            "fecha_inicio":           periodo.fecha_inicio.isoformat() if periodo.fecha_inicio else None,
            "fecha_fin":              periodo.fecha_fin.isoformat() if periodo.fecha_fin else None,
            "dias_brutos_periodo":    r["dias_brutos_total"],
            "dias_descuento_periodo": r["dias_descuento"],
            "dias_efectivos_periodo": r["dias_efectivos_total"],
            "anios_efectivos":        r["anios_ef"],
            "meses_efectivos":        r["meses_ef"],
            "dias_efectivos":         r["dias_ef"],
        })

    db.commit()

    # ── 8. Retornar resultado completo ──────────────────────────────────
    return success_response(data={
        "calculo_id":           nuevo_calculo.id,
        "docente_id":           docente_id,
        "fecha_calculo":        nuevo_calculo.fecha_calculo.isoformat(),
        "total_anios":          total_anios,
        "total_meses":          total_meses,
        "total_dias":           total_dias,
        "total_dias_brutos":    total_dias_brutos,
        "total_dias_descuento": total_dias_descuento,
        "total_dias_efectivos": total_dias_efectivos,
        "estado":               "VIGENTE",
        "detalles":             detalles_response,
    })


@router.get("/{docente_id}/calculos", response_model=None)
def listar_calculos_docente(docente_id: int, db: Session = Depends(get_db), _: Annotated[Usuario, Depends(get_current_user)] = None):
    docente = db.query(Docente).filter(Docente.id == docente_id).first()
    if not docente:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="NOT_FOUND",
                message=f"Docente con id {docente_id} no encontrado.",
            ),
        )

    calculos = (
        db.query(CalculoTiempoServicio)
        .filter(CalculoTiempoServicio.docente_id == docente_id)
        .order_by(CalculoTiempoServicio.fecha_calculo.desc())
        .all()
    )

    return success_response(data=[
        {
            "calculo_id":           c.id,
            "fecha_calculo":        c.fecha_calculo.isoformat(),
            "total_anios":          c.total_anios,
            "total_meses":          c.total_meses,
            "total_dias":           c.total_dias,
            "total_dias_brutos":    c.total_dias_brutos,
            "total_dias_descuento": c.total_dias_descuento,
            "total_dias_efectivos": c.total_dias_efectivos,
            "estado":               c.estado,
        }
        for c in calculos
    ])