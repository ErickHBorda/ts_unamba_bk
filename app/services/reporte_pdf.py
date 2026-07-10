from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import date
import io

from app.core.config import settings

# ── Colores institucionales UNAMBA (exactos del HTML) ───────────────────
AZUL_PRIMARIO      = colors.HexColor("#0C447C")
AZUL_SECUNDARIO    = colors.HexColor("#378ADD")
AZUL_CLARO         = colors.HexColor("#B5D4F4")
AZUL_MUY_CLARO     = colors.HexColor("#E6F1FB")
ROJO_DESCUENTO     = colors.HexColor("#A32D2D")
BLANCO             = colors.white
GRIS_CLARO         = colors.HexColor("#f8fafc")
GRIS_TEXTO         = colors.HexColor("#64748b")
GRIS_BORDE         = colors.HexColor("#d1d9e6")
NEGRO_PRIMARIO     = colors.HexColor("#0f172a")
NEGRO_SECUNDARIO   = colors.HexColor("#475569")


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


def _dias_a_amd(dias_totales: int) -> tuple[int, int, int]:
    a = dias_totales // 360
    r = dias_totales % 360
    m = r // 30
    d = r % 30
    return a, m, d


def _meses_en_espanol(fecha_str: str) -> str:
    """Convierte fecha a formato español"""
    meses = {
        "January": "enero", "February": "febrero", "March": "marzo",
        "April": "abril", "May": "mayo", "June": "junio",
        "July": "julio", "August": "agosto", "September": "septiembre",
        "October": "octubre", "November": "noviembre", "December": "diciembre"
    }
    for eng, esp in meses.items():
        fecha_str = fecha_str.replace(eng, esp)
    return fecha_str


def generar_reporte_pdf(
    docente:  dict,
    calculo:  dict,
    detalles: list[dict],
) -> bytes:
    buffer = io.BytesIO()
    ancho, alto = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    # Márgenes
    margen_izq = 2.0 * cm
    margen_der = ancho - 2.0 * cm
    ancho_util = margen_der - margen_izq
    y = alto - 1.5 * cm

    # ─ HEADER INSTITUCIONAL ────────────────────────────────────────────
    
    # Logo UNAMBA (solo imagen, sin fondo azul)
    logo_box_x = margen_izq
    logo_box_y = y - 2.4 * cm
    logo_box_w = 2.2 * cm
    logo_box_h = 2.2 * cm
    
    logo_path = settings.LOGO_UNAMBA
    if logo_path.exists():
        c.drawImage(
            str(logo_path),
            logo_box_x,
            logo_box_y,
            width=logo_box_w,
            height=logo_box_h,
            preserveAspectRatio=True,
            mask="auto",
        )
    
    # Texto institucional (centro-izquierda)
    texto_x = margen_izq + 2.6 * cm
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(texto_x, y - 0.7 * cm, "UNIVERSIDAD NACIONAL MICAELA BASTIDAS DE APURÍMAC")
    
    c.setFont("Helvetica", 8.5)
    c.setFillColor(NEGRO_SECUNDARIO)
    c.drawString(texto_x, y - 1.2 * cm, "Dirección General de Recursos Humanos")
    c.drawString(texto_x, y - 1.6 * cm, "Sub Unidad de Escalafón, Control y Asuntos Laborales")
    
    # Fecha y N° reporte (derecha)
    fecha_hoy = date.today().strftime("%d de %B de %Y")
    fecha_hoy = _meses_en_espanol(fecha_hoy)
    
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRIS_TEXTO)
    c.drawRightString(margen_der, y - 0.5 * cm, "FECHA DE EMISIÓN")
    
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(NEGRO_PRIMARIO)
    c.drawRightString(margen_der, y - 0.9 * cm, fecha_hoy)
    
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRIS_TEXTO)
    c.drawRightString(margen_der, y - 1.35 * cm, "N° REPORTE")
    
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(NEGRO_PRIMARIO)
    c.drawRightString(margen_der, y - 1.75 * cm, f"RPT-{date.today().year}-{calculo['calculo_id']:05d}")
    
    y -= 2.8 * cm
    
    # Línea separadora gruesa azul
    c.setStrokeColor(AZUL_PRIMARIO)
    c.setLineWidth(2.5)
    c.line(margen_izq, y, margen_der, y)
    
    y -= 0.8 * cm
    
    # ── TÍTULO DEL DOCUMENTO ────────────────────────────────────────────
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(ancho / 2, y, "CONSTANCIA DE TIEMPO DE SERVICIOS")
    
    y -= 0.5 * cm
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(NEGRO_SECUNDARIO)
    c.drawCentredString(ancho / 2, y, "Personal Docente — Universidad Nacional Micaela Bastidas de Apurímac")
    
    y -= 1.0 * cm
    
    # ─ SECCIÓN I: DATOS DEL DOCENTE ───────────────────────────────────
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margen_izq, y, "I. DATOS DEL DOCENTE")
    
    y -= 0.5 * cm
    
    # Caja con fondo azul muy claro
    box_h = 2.2 * cm
    c.setFillColor(AZUL_MUY_CLARO)
    c.setStrokeColor(colors.HexColor("#c8ddf0"))
    c.setLineWidth(0.75)
    c.roundRect(margen_izq, y - box_h, ancho_util, box_h, 6, fill=1, stroke=1)
    
    # Datos en grid 2x2
    col1_x = margen_izq + 0.5 * cm
    col2_x = margen_izq + ancho_util * 0.52
    
    # Fila 1
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(GRIS_TEXTO)
    c.drawString(col1_x, y - 0.5 * cm, "APELLIDOS Y NOMBRES:")
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NEGRO_PRIMARIO)
    nombre_completo = f"{docente['apellidos']}, {docente['nombres']}"
    c.drawString(col1_x, y - 0.9 * cm, nombre_completo)
    
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(GRIS_TEXTO)
    c.drawString(col2_x, y - 0.5 * cm, "DNI:")
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NEGRO_PRIMARIO)
    c.drawString(col2_x, y - 0.9 * cm, docente['dni'])
    
    # Fila 2
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(GRIS_TEXTO)
    c.drawString(col1_x, y - 1.4 * cm, "CATEGORÍA ACTUAL:")
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(AZUL_PRIMARIO)
    c.drawString(col1_x, y - 1.8 * cm, docente.get("categoria_actual", "—"))
    
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(GRIS_TEXTO)
    c.drawString(col2_x, y - 1.4 * cm, "CONDICIÓN LABORAL:")
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NEGRO_PRIMARIO)
    c.drawString(col2_x, y - 1.8 * cm, docente.get("condicion_actual", "—"))
    
    y -= box_h + 0.8 * cm
    
    #  SECCIÓN II: TABLA DE PERIODOS ──────────────────────────────────
    c.setFillColor(AZUL_PRIMARIO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margen_izq, y, "II. DETALLE DE PERIODOS DE SERVICIO")
    
    y -= 0.6 * cm
    
    # Preparar datos de la tabla
    encabezados = ["PERIODO", "CONDICIÓN", "CATEGORÍA", "TIEMPO BRUTO", "DESCUENTOS", "TIEMPO EFECTIVO", "RESOLUCIÓN"]
    
    filas = [encabezados]
    for d in detalles:
        a_b, m_b, d_b = _dias_a_amd(d["dias_brutos_periodo"])
        descuento_texto = f"{d['dias_descuento_periodo']}d"
        
        fila = [
            d.get("etiqueta_periodo") or "—",
            d.get("condicion") or "—",
            d.get("categoria_codigo") or "—",
            _formato_tiempo_corto(a_b, m_b, d_b),
            descuento_texto,
            _formato_tiempo_corto(
                d.get("anios_efectivos", 0),
                d.get("meses_efectivos", 0),
                d.get("dias_efectivos", 0),
            ),
            d.get("numero_resolucion") or "—",
        ]
        filas.append(fila)
    
    # Fila TOTAL
    a_bt, m_bt, d_bt = _dias_a_amd(calculo["total_dias_brutos"])
    filas.append([
        "TOTAL", "", "",
        _formato_tiempo_corto(a_bt, m_bt, d_bt),
        f"–{calculo['total_dias_descuento']}d",
        _formato_tiempo_corto(
            calculo["total_anios"],
            calculo["total_meses"],
            calculo["total_dias"],
        ),
        "",
    ])
    
    # Anchos de columna - AJUSTADOS PARA OCUPAR TODO EL ANCHO_UTIL
    factor = 17 / 15  # 1.1333
    col_widths = [
        2.0*factor*cm,   # PERIODO
        2.0*factor*cm,   # CONDICIÓN
        2.2*factor*cm,   # CATEGORÍA
        2.2*factor*cm,   # TIEMPO BRUTO
        1.8*factor*cm,   # DESCUENTOS
        2.8*factor*cm,   # TIEMPO EFECTIVO
        2.0*factor*cm,   # RESOLUCIÓN
    ]
    # Total: 15.0cm (ajustar según ancho_util)
    
    # Estilos de tabla
    estilo = [
        # Encabezado
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL_PRIMARIO),
        ("TEXTCOLOR",     (0, 0), (-1, 0), BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 7.5),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0), "MIDDLE"),
        
        # Filas de datos
        ("FONTNAME",      (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -2), 8),
        ("ALIGN",         (0, 1), (-1, -2), "CENTER"),
        ("VALIGN",        (0, 1), (-1, -2), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [BLANCO, GRIS_CLARO]),
        
        # Fila TOTAL
        ("BACKGROUND",    (0, -1), (-1, -1), AZUL_PRIMARIO),
        ("TEXTCOLOR",     (0, -1), (-1, -1), BLANCO),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, -1), (-1, -1), 8),
        ("ALIGN",         (0, -1), (-1, -1), "CENTER"),
        ("VALIGN",        (0, -1), (-1, -1), "MIDDLE"),
        
        # Bordes
        ("BOX",           (0, 0), (-1, -1), 0, AZUL_PRIMARIO),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, AZUL_CLARO),
        ("LINEBELOW",     (0, 0), (-1, 0), 1, AZUL_SECUNDARIO),
        
        # Padding
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]
    
    # Descuentos en rojo
    for i, d in enumerate(detalles, start=1):
        if d.get("dias_descuento_periodo", 0) > 0:
            estilo.append(("TEXTCOLOR", (4, i), (4, i), ROJO_DESCUENTO))
            estilo.append(("FONTNAME", (4, i), (4, i), "Helvetica-Bold"))
    
    # Resoluciones en azul secundario
    for i in range(1, len(filas) - 1):
        estilo.append(("TEXTCOLOR", (6, i), (6, i), AZUL_SECUNDARIO))
        estilo.append(("FONTNAME", (6, i), (6, i), "Helvetica"))
        estilo.append(("FONTSIZE", (6, i), (6, i), 7.5))
    
    # Alinear izquierda condición y categoría
    estilo.append(("ALIGN", (1, 1), (2, -2), "LEFT"))
    
    tabla = Table(filas, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle(estilo))
    
    tabla_ancho, tabla_alto = tabla.wrapOn(c, ancho_util, alto)
    tabla.drawOn(c, margen_izq, y - tabla_alto)
    y -= tabla_alto + 1.0 * cm
    
    # ── TARJETA DE RESUMEN (fondo azul oscuro) ──────────────────────────
    banner_h = 2.6 * cm
    c.setFillColor(AZUL_PRIMARIO)
    c.roundRect(margen_izq, y - banner_h, ancho_util, banner_h, 8, fill=1, stroke=0)
    
    # Lado izquierdo
    c.setFillColor(BLANCO)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(margen_izq + 0.6*cm, y - 0.8*cm, "TIEMPO DE SERVICIOS EFECTIVO TOTAL")
    
    tiempo_total = _formato_tiempo(
        calculo["total_anios"],
        calculo["total_meses"],
        calculo["total_dias"],
    )
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margen_izq + 0.6*cm, y - 1.8*cm, tiempo_total)
    
    # Lado derecho
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(margen_der - 0.6*cm, y - 0.8*cm, "EQUIVALENTE EN DÍAS")
    
    c.setFont("Helvetica-Bold", 14)
    dias_texto = f"{calculo['total_dias_efectivos']:,}".replace(",", ",")
    c.drawRightString(margen_der - 0.6*cm, y - 1.8*cm, f"{dias_texto} días efectivos")
    
    y -= banner_h + 3.0 * cm  # Más espacio antes de las firmas
    
    # ── FIRMAS ──────────────────────────────────────────────────────────
    firma_ancho = 6.5 * cm
    firma_izq_x = margen_izq + 1.0 * cm
    firma_der_x = margen_der - firma_ancho - 1.0 * cm
    
    # Líneas de firma
    c.setStrokeColor(NEGRO_PRIMARIO)
    c.setLineWidth(1.2)
    c.line(firma_izq_x, y, firma_izq_x + firma_ancho, y)
    c.line(firma_der_x, y, firma_der_x + firma_ancho, y)
    
    # Cargo
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NEGRO_PRIMARIO)
    c.drawCentredString(firma_izq_x + firma_ancho/2, y - 0.5*cm, "Responsable de Escalafón")
    c.drawCentredString(firma_der_x + firma_ancho/2, y - 0.5*cm, "Jefe de Recursos Humanos")
    
    # Dependencia
    c.setFont("Helvetica", 8)
    c.setFillColor(GRIS_TEXTO)
    c.drawCentredString(firma_izq_x + firma_ancho/2, y - 0.9*cm, "Sub Unidad de Escalafón, Control")
    c.drawCentredString(firma_izq_x + firma_ancho/2, y - 1.2*cm, "y Asuntos Laborales")
    
    c.drawCentredString(firma_der_x + firma_ancho/2, y - 0.9*cm, "Dirección General de")
    c.drawCentredString(firma_der_x + firma_ancho/2, y - 1.2*cm, "Recursos Humanos — UNAMBA")
    
    y -= 3.5 * cm  # Más espacio antes del footer
    
    # ── FOOTER ──────────────────────────────────────────────────────────
    c.setStrokeColor(GRIS_BORDE)
    c.setLineWidth(0.75)
    c.line(margen_izq, y, margen_der, y)
    
    y -= 0.6 * cm
    
    c.setFont("Helvetica", 8)
    c.setFillColor(GRIS_TEXTO)
    c.drawString(margen_izq, y, "Documento generado por el Sistema de Tiempo de Servicios — UNAMBA")
    c.drawRightString(margen_der, y, "Página 1 de 1")
    
    c.save()
    buffer.seek(0)
    return buffer.read()