from pydantic import BaseModel, model_validator
from typing import Optional


class DescuentoPeriodoBase(BaseModel):
    faltas_injustificadas: int = 0
    permisos_sin_goce:     int = 0
    licencias_sin_goce:    int = 0
    observaciones:         Optional[str] = None

    @model_validator(mode="after")
    def validar_negativos(self) -> "DescuentoPeriodoBase":
        for campo in [self.faltas_injustificadas, self.permisos_sin_goce, self.licencias_sin_goce]:
            if campo < 0:
                raise ValueError("Los días de descuento no pueden ser negativos.")
        return self


class DescuentoPeriodoCreate(DescuentoPeriodoBase):
    pass


class DescuentoPeriodoUpdate(BaseModel):
    faltas_injustificadas: Optional[int] = None
    permisos_sin_goce:     Optional[int] = None
    licencias_sin_goce:    Optional[int] = None
    observaciones:         Optional[str] = None

    @model_validator(mode="after")
    def validar_negativos(self) -> "DescuentoPeriodoUpdate":
        for campo in [self.faltas_injustificadas, self.permisos_sin_goce, self.licencias_sin_goce]:
            if campo is not None and campo < 0:
                raise ValueError("Los días de descuento no pueden ser negativos.")
        return self


class DescuentoPeriodoResponse(BaseModel):
    id:                    int
    periodo_id:            int
    faltas_injustificadas: int
    permisos_sin_goce:     int
    licencias_sin_goce:    int
    total_dias_descuento:  int
    observaciones:         Optional[str] = None

    model_config = {"from_attributes": True}