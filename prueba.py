#from datetime import date
#from app.services.calculo_tiempo import calcular_diferencia_30_360
from datetime import date
from app.services.calculo_tiempo import calcular_diferencia_30_360

print(calcular_diferencia_30_360(date(2020, 1, 1),  date(2022, 12, 31))) # Esperado: (3, 0, 0)
print(calcular_diferencia_30_360(date(2020, 8, 20), date(2020, 11, 13))) # Esperado: (0, 2, 24)
print(calcular_diferencia_30_360(date(2020, 11, 14), date(2021, 4, 6)))  # Esperado: (0, 4, 23)
print(calcular_diferencia_30_360(date(2021, 6, 9),  date(2021, 10, 18))) # Esperado: (0, 4, 9)
print(calcular_diferencia_30_360(date(2021, 11, 8), date(2022, 3, 9)))   # Esperado: (0, 4, 1)

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