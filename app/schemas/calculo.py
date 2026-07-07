from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DetalleCalculoResponse(BaseModel):
    periodo_id:             int
    tipo_registro:          str
    etiqueta_periodo:       Optional[str] = None
    categoria:              str
    condicion:              str
    fecha_inicio:           Optional[str] = None
    fecha_fin:              Optional[str] = None
    dias_brutos_periodo:    int
    dias_descuento_periodo: int
    dias_efectivos_periodo: int
    anios_efectivos:        int
    meses_efectivos:        int
    dias_efectivos:         int

    model_config = {"from_attributes": True}


class CalculoResponse(BaseModel):
    calculo_id:           int
    docente_id:           int
    fecha_calculo:        datetime
    total_anios:          int
    total_meses:          int
    total_dias:           int
    total_dias_brutos:    int
    total_dias_descuento: int
    total_dias_efectivos: int
    estado:               str
    detalles:             list[DetalleCalculoResponse]

    model_config = {"from_attributes": True}