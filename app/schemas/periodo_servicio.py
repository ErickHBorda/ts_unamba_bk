from pydantic import BaseModel, field_validator, model_validator
from datetime import date, datetime
from typing import Optional, Literal


class PeriodoServicioBase(BaseModel):
    docente_id:       int
    categoria_id:     int
    condicion_id:     int
    resolucion_id:    Optional[int] = None
    tipo_registro:    Literal["ACTIVO", "CON_FECHAS", "MANUAL"]
    etiqueta_periodo: Optional[str] = None
    anio_periodo:     Optional[int] = None
    fecha_inicio:     Optional[date] = None
    fecha_fin:        Optional[date] = None
    anios_brutos:     int = 0
    meses_brutos:     int = 0
    dias_brutos:      int = 0
    observaciones:    Optional[str] = None

    @model_validator(mode="after")
    def validar_segun_tipo(self) -> "PeriodoServicioBase":
        if self.tipo_registro == "ACTIVO":
            if not self.fecha_inicio:
                raise ValueError("ACTIVO requiere fecha_inicio.")
            if self.fecha_fin:
                raise ValueError("ACTIVO no debe tener fecha_fin.")

        elif self.tipo_registro == "CON_FECHAS":
            if not self.fecha_inicio or not self.fecha_fin:
                raise ValueError("CON_FECHAS requiere fecha_inicio y fecha_fin.")
            if self.fecha_fin <= self.fecha_inicio:
                raise ValueError("fecha_fin debe ser posterior a fecha_inicio.")

        elif self.tipo_registro == "MANUAL":
            if any(v < 0 for v in [self.anios_brutos, self.meses_brutos, self.dias_brutos]):
                raise ValueError("Los valores de tiempo bruto no pueden ser negativos.")
            if self.anios_brutos == 0 and self.meses_brutos == 0 and self.dias_brutos == 0:
                raise ValueError("MANUAL requiere al menos un valor de tiempo bruto mayor a cero.")

        return self


class PeriodoServicioCreate(PeriodoServicioBase):
    pass


class PeriodoServicioUpdate(BaseModel):
    categoria_id:     Optional[int] = None
    condicion_id:     Optional[int] = None
    resolucion_id:    Optional[int] = None
    etiqueta_periodo: Optional[str] = None
    anio_periodo:     Optional[int] = None
    fecha_inicio:     Optional[date] = None
    fecha_fin:        Optional[date] = None
    anios_brutos:     Optional[int] = None
    meses_brutos:     Optional[int] = None
    dias_brutos:      Optional[int] = None
    activo:           Optional[bool] = None
    observaciones:    Optional[str] = None


class PeriodoServicioResponse(PeriodoServicioBase):
    id:         int
    activo:     bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PeriodoServicioListResponse(BaseModel):
    id:               int
    docente_id:       int
    categoria_id:     int
    condicion_id:     int
    tipo_registro:    str
    etiqueta_periodo: Optional[str] = None
    fecha_inicio:     Optional[date] = None
    fecha_fin:        Optional[date] = None
    anios_brutos:     int
    meses_brutos:     int
    dias_brutos:      int
    activo:           bool

    model_config = {"from_attributes": True}