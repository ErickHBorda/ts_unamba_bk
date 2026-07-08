#from datetime import date
#from app.services.calculo_tiempo import calcular_diferencia_30_360
from datetime import date
from app.services.calculo_tiempo import calcular_diferencia_30_360

print(calcular_diferencia_30_360(date(2019, 4, 29), date(2019, 8, 30)))  # Esperado: (0, 4, 1)
print(calcular_diferencia_30_360(date(2020, 7, 15), date(2020, 11, 13))) # Esperado: (0, 3, 29)
print(calcular_diferencia_30_360(date(2020, 11, 14), date(2021, 4, 6)))  # Esperado: (0, 4, 23)
print(calcular_diferencia_30_360(date(2021, 6, 9),  date(2021, 10, 18))) # Esperado: (0, 4, 9)
print(calcular_diferencia_30_360(date(2021, 10, 20), date(2022, 3, 9)))  # Esperado: (0, 4, 17)
print(calcular_diferencia_30_360(date(2020, 1, 1),  date(2022, 12, 31))) # Esperado: (3, 0, 0)
#from datetime import date
#from app.services.calculo_tiempo import calcular_dias_brutos_periodo

# Modo ACTIVO — resultado varía según la fecha actual del servidor
#r1 = calcular_dias_brutos_periodo(
#    tipo_registro="ACTIVO",
#    fecha_inicio=date(2024, 3, 1),
#    fecha_fin=None,
#    anios_brutos=0, meses_brutos=0, dias_brutos=0
#)
#print("ACTIVO:", r1)

# Modo CON_FECHAS
#r2 = calcular_dias_brutos_periodo(
#    tipo_registro="CON_FECHAS",
#    fecha_inicio=date(2020, 1, 1),
#    fecha_fin=date(2022, 12, 31),
#    anios_brutos=0, meses_brutos=0, dias_brutos=0
#)
#print("CON_FECHAS:", r2)  # Esperado: (2, 11, 30)

# Modo MANUAL
#r3 = calcular_dias_brutos_periodo(
#    tipo_registro="MANUAL",
#    fecha_inicio=None,
#    fecha_fin=None,
#    anios_brutos=1, meses_brutos=6, dias_brutos=15
#)
#print("MANUAL:", r3)  # Esperado: (1, 6, 15)

from app.services.calculo_tiempo import (
    calcular_tiempo_efectivo_periodo,
    sumar_tiempos_efectivos,
)

# Periodo con descuentos
r1 = calcular_tiempo_efectivo_periodo(
    anios_brutos=0,
    meses_brutos=4,
    dias_brutos=23,
    total_dias_descuento=10,
)
print("Periodo con descuento:", r1)
# Esperado: (143, 10, 133, 4, 13, 3)
# 4m 23d = 143 días brutos — 10 descuento = 133 días efectivos = 4m 13d 3d

# Periodo sin descuentos
r2 = calcular_tiempo_efectivo_periodo(
    anios_brutos=2,
    meses_brutos=11,
    dias_brutos=0,
    total_dias_descuento=0,
)
print("Periodo sin descuento:", r2)
# Esperado: (1050, 0, 1050, 2, 11, 0)

# Suma de ambos periodos
periodos = [
    {"dias_brutos_total": r1[0], "dias_descuento": r1[1], "dias_efectivos_total": r1[2]},
    {"dias_brutos_total": r2[0], "dias_descuento": r2[1], "dias_efectivos_total": r2[2]},
]
total = sumar_tiempos_efectivos(periodos)
print("Total:", total)
# Esperado: (3, 3, 13, 1193, 10, 1183)