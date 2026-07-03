from datetime import date
from app.services.calculo_tiempo import calcular_diferencia_30_360

print(calcular_diferencia_30_360(date(2012, 8, 20), date(2012, 12, 31)))  # (0, 2, 24)
print(calcular_diferencia_30_360(date(2012, 4, 16), date(2012, 7, 31)))   # (0, 4, 23)
print(calcular_diferencia_30_360(date(2013, 4, 21), date(2013, 8, 9)))   # (0, 4, 9)
print(calcular_diferencia_30_360(date(2020, 11, 14), date(2021, 4, 6)))    # (0, 4, 1)