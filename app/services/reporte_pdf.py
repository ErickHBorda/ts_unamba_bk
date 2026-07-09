from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date
import io

from app.core.config import settings

# ── Colores institucionales UNAMBA ──────────────────────────────────────
AZUL_PRIMARIO   = colors.HexColor("#0C447C")
AZUL_SECUNDARIO = colors.HexColor("#378ADD")
AZUL_CLARO      = colors.HexColor("#B5D4F4")
ROJO_DESCUENTO  = colors.HexColor("#A32D2D")
BLANCO          = colors.white
GRIS_CLARO      = colors.HexColor("#F5F5F5")


def _formato_tiempo(anios: int, meses: int, dias: int) -> str:
    partes = []
    if anios > 0:
        partes.append(f"{anios} año{'s' if anios != 1 else ''}")
    if meses > 0:
        partes.append(f"{meses} mes{'es' if meses != 1 else ''}")
    if dias > 0:
        partes.append(f"{dias} día{'s' if dias != 1 else ''}")
    return ", ".join(partes) if partes else "0 días"


def _formato_tiempo_corto(anios: int, meses: int, dias: int) -> str:
    return f"{anios}a {meses}m {dias}d"


def generar_reporte_pdf(
    docente:   dict,
    calculo:   dict,
    detalles:  list[dict],
) -> bytes:
    """
    Genera el PDF del reporte de tiempo de servicios de un docente.
    Retorna los bytes del PDF generado.
    """
    buffer = io.BytesIO()
    ancho, alto = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    # Márgenes
    margen_izq  = 2 * cm
    margen_der  = ancho - 2 * cm
    margen_sup  = alto - 1.5 * cm
    y            = margen_sup

    # ── MEMBRETE ────────────────────────────────────────────────────────

    # Logo
    logo_path = settings.LOGO_UNAMBA
    if logo_path.exists():
        c.drawImage(
            str(logo_path),
            margen_izq, y - 2.8 * cm,
            width=2.5 * cm, height=2.5 * cm,
            preserveAspectRatio=True,
        )

    # Texto del membrete
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(5 * cm, y - 0.8 * cm, "UNIVERSIDAD NACIONAL MICAELA BASTIDAS DE APURÍMAC")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(5 * cm, y - 1.4 * cm, "Dirección de Recursos Humanos")
    c.drawString(5 * cm, y - 1.9 * cm, "Sub Unidad de Escalafón, Control y Asuntos Laborales")

    # Fecha y número de reporte
    fecha_hoy = date.today().strftime("%d/%m/%Y")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawRightString(margen_der, y - 0.8 * cm, f"Fecha de emisión: {fecha_hoy}")
    c.drawRightString(margen_der, y - 1.3 * cm, f"N° Reporte: {calculo['calculo_id']:04d}")

    y -= 3.2 * cm

    # Línea separadora
    c.setStrokeColor(AZUL_PRIMARIO)
    c.setLineWidth(2)
    c.line(margen_izq, y, margen_der, y)

    y -= 0.6 * cm

    # ── TÍTULO ──────────────────────────────────────────────────────────
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(ancho / 2, y, "REPORTE DE TIEMPO DE SERVICIOS")

    y -= 0.5 * cm
    c.setLineWidth(0.5)
    c.line(margen_izq, y, margen_der, y)
    y -= 0.7 * cm

    # ── SECCIÓN I — DATOS DEL DOCENTE ───────────────────────────────────
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margen_izq, y, "SECCIÓN I — DATOS DEL DOCENTE")
    y -= 0.5 * cm

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)

    campos_docente = [
        ("Apellidos y Nombres", f"{docente['apellidos']}, {docente['nombres']}"),
        ("DNI",                 docente['dni']),
        ("Email",               docente.get('email') or "—"),
    ]

    for etiqueta, valor in campos_docente:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margen_izq, y, f"{etiqueta}:")
        c.setFont("Helvetica", 9)
        c.drawString(6 * cm, y, valor)
        y -= 0.45 * cm

    y -= 0.3 * cm
    c.setStrokeColor(AZUL_CLARO)
    c.setLineWidth(0.5)
    c.line(margen_izq, y, margen_der, y)
    y -= 0.6 * cm

    # ── SECCIÓN II — DETALLE DE PERIODOS ────────────────────────────────
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margen_izq, y, "SECCIÓN II — DETALLE DE PERIODOS DE SERVICIO")
    y -= 0.6 * cm

    # Encabezados de tabla
    encabezados = [
        "Periodo",
        "Condición",
        "Categoría",
        "Bruto",
        "Descuento",
        "Efectivo",
    ]

    # Filas de datos
    filas = [encabezados]
    for d in detalles:
        filas.append([
            d.get("etiqueta_periodo") or "—",
            d.get("condicion")        or "—",
            d.get("categoria")        or "—",
            _formato_tiempo_corto(
                d.get("anios_efectivos", 0) + (d["dias_brutos_periodo"] // 360),
                (d["dias_brutos_periodo"] % 360) // 30,
                (d["dias_brutos_periodo"] % 360) % 30,
            ),
            str(d.get("dias_descuento_periodo", 0)) + "d",
            _formato_tiempo_corto(
                d.get("anios_efectivos", 0),
                d.get("meses_efectivos", 0),
                d.get("dias_efectivos", 0),
            ),
        ])

    # Fila de totales
    filas.append([
        "TOTAL",
        "",
        "",
        _formato_tiempo_corto(
            calculo["total_dias_brutos"] // 360,
            (calculo["total_dias_brutos"] % 360) // 30,
            (calculo["total_dias_brutos"] % 360) % 30,
        ),
        str(calculo["total_dias_descuento"]) + "d",
        _formato_tiempo_corto(
            calculo["total_anios"],
            calculo["total_meses"],
            calculo["total_dias"],
        ),
    ])

    # Anchos de columna
    col_widths = [3.5*cm, 3.5*cm, 4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm]

    tabla = Table(filas, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        # Encabezado
        ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_PRIMARIO),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),

        # Filas de datos
        ("FONTNAME",      (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -2), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [BLANCO, GRIS_CLARO]),
        ("ALIGN",         (3, 1), (-1, -2), "CENTER"),

        # Fila de totales
        ("BACKGROUND",    (0, -1), (-1, -1), AZUL_CLARO),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, -1), (-1, -1), 8),
        ("ALIGN",         (0, -1), (-1, -1), "CENTER"),

        # Bordes
        ("GRID",          (0, 0), (-1, -1), 0.5, AZUL_SECUNDARIO),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),

        # Padding
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))

    # Posicionar tabla
    tabla_ancho, tabla_alto = tabla.wrapOn(c, ancho - 4*cm, alto)
    tabla.drawOn(c, margen_izq, y - tabla_alto)
    y -= tabla_alto + 0.8 * cm

    # ── BANNER RESULTADO FINAL ───────────────────────────────────────────
    banner_alto = 2.2 * cm
    c.setFillColor(AZUL_PRIMARIO)
    c.roundRect(margen_izq, y - banner_alto, margen_der - margen_izq, banner_alto, 5, fill=1, stroke=0)

    c.setFillColor(BLANCO)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(ancho / 2, y - 0.8 * cm, "TIEMPO TOTAL DE SERVICIOS")

    tiempo_total = _formato_tiempo(
        calculo["total_anios"],
        calculo["total_meses"],
        calculo["total_dias"],
    )
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(ancho / 2, y - 1.6 * cm, tiempo_total.upper())

    y -= banner_alto + 1.2 * cm

    # ── FIRMAS ───────────────────────────────────────────────────────────
    firma_y = y - 1.5 * cm

    # Firma izquierda
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(margen_izq, firma_y, margen_izq + 6*cm, firma_y)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(margen_izq + 3*cm, firma_y - 0.4*cm, "Responsable de Escalafón")
    c.setFont("Helvetica", 7)
    c.drawCentredString(margen_izq + 3*cm, firma_y - 0.8*cm, "Sub Unidad de Escalafón")

    # Firma derecha
    c.line(margen_der - 6*cm, firma_y, margen_der, firma_y)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(margen_der - 3*cm, firma_y - 0.4*cm, "Jefe de Recursos Humanos")
    c.setFont("Helvetica", 7)
    c.drawCentredString(margen_der - 3*cm, firma_y - 0.8*cm, "Dirección de RR.HH. — UNAMBA")

    # ── PIE DE PÁGINA ────────────────────────────────────────────────────
    c.setStrokeColor(AZUL_CLARO)
    c.setLineWidth(0.5)
    c.line(margen_izq, 1.5*cm, margen_der, 1.5*cm)
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawString(margen_izq, 1.0*cm, "Sistema de Escalafón — UNAMBA")
    c.drawRightString(margen_der, 1.0*cm, f"Generado el {fecha_hoy}")

    c.save()
    buffer.seek(0)
    return buffer.read()