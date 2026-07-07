from datetime import date


def normalizar_dia(dia: int) -> int:
    """
    Bajo la regla de 30 días/mes, el día 31 se trata como día 30.
    """
    return 30 if dia > 30 else dia


def calcular_diferencia_30_360(fecha_inicio: date, fecha_fin: date) -> tuple[int, int, int]:
    """
    Calcula la diferencia entre dos fechas bajo la regla de 30 días por mes
    (método 30/360, usado en cálculo de tiempo de servicio del sector público).

    Retorna una tupla (anios, meses, dias).

    Regla de negocio crítica: 1 mes = 30 días exactos, sin importar
    el mes calendario real. Cuando hay préstamo de mes (día_fin < día_inicio),
    el día de inicio se cuenta como día trabajado (conteo inclusivo), por lo
    que se suman 31 días en vez de 30 al hacer el préstamo.
    """
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha_fin no puede ser anterior a fecha_inicio.")

    di, mi, ai = normalizar_dia(fecha_inicio.day), fecha_inicio.month, fecha_inicio.year
    df, mf, af = normalizar_dia(fecha_fin.day), fecha_fin.month, fecha_fin.year

    dias  = df - di
    meses = mf - mi
    anios = af - ai

    if dias < 0:
        dias += 31   # Préstamo inclusivo: se cuenta el día de inicio como trabajado
        meses -= 1

    if meses < 0:
        meses += 12
        anios -= 1

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