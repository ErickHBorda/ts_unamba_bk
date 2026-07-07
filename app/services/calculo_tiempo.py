from datetime import date


def normalizar_dia(dia: int) -> int:
    """
    Bajo la regla de 30 días/mes, el día 31 se trata como día 30.
    """
    return 30 if dia > 30 else dia


def calcular_diferencia_30_360(fecha_inicio: date, fecha_fin: date) -> tuple[int, int, int]:
    """
    Calcula la diferencia entre dos fechas bajo la regla de 30 días por mes
    (método 30/360, compatible con SIFECHA de Excel).

    Reglas aplicadas:
    - Día 31 en fecha_inicio se trata como día 30.
    - Día 31 en fecha_fin se trata como día 30 SOLO para normalización final.
    - Cuando hay préstamo de mes (dias < 0), se suman 31 días (conteo inclusivo).
    - Si dias == 30 tras el cálculo, se normaliza como 1 mes adicional.
    """
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha_fin no puede ser anterior a fecha_inicio.")

    di = normalizar_dia(fecha_inicio.day)
    mi, ai = fecha_inicio.month, fecha_inicio.year

    # fecha_fin: NO normalizar antes de restar, usar el día real
    df = fecha_fin.day
    mf, af = fecha_fin.month, fecha_fin.year

    dias  = df - di
    meses = mf - mi
    anios = af - ai

    if dias < 0:
        dias += 31
        meses -= 1

    if meses < 0:
        meses += 12
        anios -= 1

    # Normalizar día 31 en fecha_fin DESPUÉS de restar
    if dias >= 30:
        dias = 0
        meses += 1

    if meses == 12:
        meses = 0
        anios += 1

    return anios, meses, dias


def convertir_a_dias_totales(anios: int, meses: int, dias: int) -> int:
    """
    Convierte una duración en (años, meses, días) a su equivalente
    en días totales, bajo la regla de 30 días/mes y 360 días/año.
    """
    return (anios * 360) + (meses * 30) + dias


def convertir_dias_a_anios_meses_dias(dias_totales: int) -> tuple[int, int, int]:
    """
    Operación inversa: convierte un número de días totales de vuelta
    a su representación en (años, meses, días), bajo la misma regla.
    """
    anios = dias_totales // 360
    resto = dias_totales % 360
    meses = resto // 30
    dias  = resto % 30
    return anios, meses, dias


def calcular_dias_periodo_activo(fecha_inicio: date) -> tuple[int, int, int]:
    """
    Para periodos en Modo ACTIVO (sin fecha_fin), calcula el tiempo
    transcurrido desde fecha_inicio hasta hoy usando la misma regla 30/360.
    
    La fecha actual del servidor se usa como fecha_fin temporal.
    Este valor NO se persiste en la BD — se recalcula en cada ejecución.
    """
    hoy = date.today()

    if fecha_inicio > hoy:
        raise ValueError("La fecha_inicio no puede ser posterior a la fecha actual.")

    return calcular_diferencia_30_360(fecha_inicio, hoy)


def calcular_dias_brutos_periodo(
    tipo_registro: str,
    fecha_inicio: date | None,
    fecha_fin: date | None,
    anios_brutos: int,
    meses_brutos: int,
    dias_brutos: int,
) -> tuple[int, int, int]:
    """
    Punto de entrada unificado para calcular el tiempo bruto de cualquier
    tipo de periodo (ACTIVO, CON_FECHAS, MANUAL).

    Retorna siempre una tupla (anios, meses, dias) bajo la misma regla.
    """
    if tipo_registro == "ACTIVO":
        if not fecha_inicio:
            raise ValueError("Periodo ACTIVO requiere fecha_inicio.")
        return calcular_dias_periodo_activo(fecha_inicio)

    elif tipo_registro == "CON_FECHAS":
        if not fecha_inicio or not fecha_fin:
            raise ValueError("Periodo CON_FECHAS requiere fecha_inicio y fecha_fin.")
        return calcular_diferencia_30_360(fecha_inicio, fecha_fin)

    elif tipo_registro == "MANUAL":
        # Los datos ya están ingresados manualmente, se usan directamente
        return anios_brutos, meses_brutos, dias_brutos

    else:
        raise ValueError(f"Tipo de registro desconocido: {tipo_registro}")
    
# Algoritmo de resta de fechas basado en la regla de 30 días por mes y 360 días por año.

def calcular_tiempo_efectivo_periodo(
    anios_brutos:        int,
    meses_brutos:        int,
    dias_brutos:         int,
    total_dias_descuento: int,
) -> tuple[int, int, int, int, int]:
    """
    Calcula el tiempo efectivo de un periodo restando los días de descuento
    al tiempo bruto.

    Flujo:
    1. Convierte tiempo bruto (años, meses, días) a días totales.
    2. Resta el total de días de descuento.
    3. Convierte el resultado de vuelta a (años, meses, días).

    Retorna una tupla:
    (dias_brutos_total, dias_descuento, dias_efectivos_total, anios_ef, meses_ef, dias_ef)
    """
    if total_dias_descuento < 0:
        raise ValueError("El total de días de descuento no puede ser negativo.")

    dias_brutos_total = convertir_a_dias_totales(anios_brutos, meses_brutos, dias_brutos)

    # Protección: el descuento no puede superar el tiempo bruto
    if total_dias_descuento > dias_brutos_total:
        raise ValueError(
            f"El descuento ({total_dias_descuento} días) supera el tiempo "
            f"bruto del periodo ({dias_brutos_total} días)."
        )

    dias_efectivos_total = dias_brutos_total - total_dias_descuento
    anios_ef, meses_ef, dias_ef = convertir_dias_a_anios_meses_dias(dias_efectivos_total)

    return (
        dias_brutos_total,
        total_dias_descuento,
        dias_efectivos_total,
        anios_ef,
        meses_ef,
        dias_ef,
    )


def sumar_tiempos_efectivos(periodos: list[dict]) -> tuple[int, int, int, int, int, int]:
    """
    Suma los tiempos efectivos de todos los periodos de un docente.

    Cada elemento de `periodos` debe tener la clave `dias_efectivos_total`.

    Flujo:
    1. Suma todos los días efectivos de cada periodo.
    2. Suma todos los días brutos de cada periodo.
    3. Suma todos los días de descuento de cada periodo.
    4. Convierte el total efectivo a (años, meses, días).

    Retorna:
    (total_anios, total_meses, total_dias, total_dias_brutos,
     total_dias_descuento, total_dias_efectivos)
    """
    total_dias_brutos    = sum(p["dias_brutos_total"]    for p in periodos)
    total_dias_descuento = sum(p["dias_descuento"]       for p in periodos)
    total_dias_efectivos = sum(p["dias_efectivos_total"] for p in periodos)

    total_anios, total_meses, total_dias = convertir_dias_a_anios_meses_dias(
        total_dias_efectivos
    )

    return (
        total_anios,
        total_meses,
        total_dias,
        total_dias_brutos,
        total_dias_descuento,
        total_dias_efectivos,
    )