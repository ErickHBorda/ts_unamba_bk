from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Annotated
import io

from app.db.session import get_db
from app.models.docente import Docente
from app.models.calculo_tiempo_servicio import CalculoTiempoServicio
from app.models.detalle_calculo import DetalleCalculo
from app.models.periodo_servicio import PeriodoServicio
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.response import error_response
from app.services.reporte_pdf import generar_reporte_pdf

router = APIRouter()


@router.get("/{docente_id}/reporte-pdf")
def generar_reporte(
    docente_id: int,
    db:         Session = Depends(get_db),
    _:          Annotated[Usuario, Depends(get_current_user)] = None,
):
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

    # ── 2. Obtener cálculo VIGENTE ──────────────────────────────────────
    calculo = (
        db.query(CalculoTiempoServicio)
        .filter(
            CalculoTiempoServicio.docente_id == docente_id,
            CalculoTiempoServicio.estado     == "VIGENTE",
        )
        .order_by(CalculoTiempoServicio.fecha_calculo.desc())
        .first()
    )

    if not calculo:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(
                code="SIN_CALCULO",
                message=f"El docente con id {docente_id} no tiene un cálculo vigente. "
                        "Ejecuta primero el cálculo de tiempo de servicios.",
            ),
        )

    # ── 3. Obtener detalles del cálculo ─────────────────────────────────
    detalles_orm = (
        db.query(DetalleCalculo)
        .filter(DetalleCalculo.calculo_id == calculo.id)
        .all()
    )

    # ── 4. Construir lista de detalles con datos del periodo ─────────────
    detalles = []
    for detalle in detalles_orm:
        periodo = db.query(PeriodoServicio).filter(
            PeriodoServicio.id == detalle.periodo_id
        ).first()

        detalles.append({
            "periodo_id":             detalle.periodo_id,
            "etiqueta_periodo":       periodo.etiqueta_periodo if periodo else "—",
            "condicion":              periodo.condicion.nombre if periodo else "—",
            "categoria":              periodo.categoria.nombre if periodo else "—",
            "categoria_codigo":       periodo.categoria.codigo if periodo else "—",
            "numero_resolucion":      periodo.resolucion.numero_resolucion if periodo and periodo.resolucion else "—",
            "fecha_inicio":           periodo.fecha_inicio.isoformat() if periodo and periodo.fecha_inicio else None,
            "fecha_fin":              periodo.fecha_fin.isoformat() if periodo and periodo.fecha_fin else None,
            "dias_brutos_periodo":    detalle.dias_brutos_periodo,
            "dias_descuento_periodo": detalle.dias_descuento_periodo,
            "dias_efectivos_periodo": detalle.dias_efectivos_periodo,
            "anios_efectivos":        detalle.anios_efectivos,
            "meses_efectivos":        detalle.meses_efectivos,
            "dias_efectivos":         detalle.dias_efectivos,
        })

    # Obtener último periodo activo para categoría y condición actual
    ultimo_periodo = (
        db.query(PeriodoServicio)
        .filter(
            PeriodoServicio.docente_id == docente_id,
            PeriodoServicio.activo     == True,
        )
        .order_by(PeriodoServicio.id.desc())
        .first()
    )
    # ── 5. Construir dict del docente ────────────────────────────────────
    docente_data = {
        "id":               docente.id,
        "nombres":          docente.nombres,
        "apellidos":        docente.apellidos,
        "dni":              docente.dni,
        "email":            docente.email,
        "categoria_actual": ultimo_periodo.categoria.nombre if ultimo_periodo else "—",
        "condicion_actual": ultimo_periodo.condicion.nombre if ultimo_periodo else "—",
    }

    # ── 6. Construir dict del cálculo ────────────────────────────────────
    calculo_data = {
        "calculo_id":           calculo.id,
        "fecha_calculo":        calculo.fecha_calculo,
        "total_anios":          calculo.total_anios,
        "total_meses":          calculo.total_meses,
        "total_dias":           calculo.total_dias,
        "total_dias_brutos":    calculo.total_dias_brutos,
        "total_dias_descuento": calculo.total_dias_descuento,
        "total_dias_efectivos": calculo.total_dias_efectivos,
    }

    # ── 7. Generar PDF ───────────────────────────────────────────────────
    pdf_bytes = generar_reporte_pdf(
        docente=docente_data,
        calculo=calculo_data,
        detalles=detalles,
    )

    # ── 8. Retornar PDF como respuesta binaria ───────────────────────────
    nombre_archivo = f"reporte_ts_{docente.dni}_{calculo.id:04d}.pdf"

    return StreamingResponse(
        content=io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={nombre_archivo}",
        },
    )