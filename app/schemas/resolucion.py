from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class ResolucionBase(BaseModel):
    numero_resolucion: str
    fecha_emision:     date
    tipo:              Optional[str] = None
    descripcion:       Optional[str] = None
    emitida_por:       Optional[str] = None

    @field_validator("numero_resolucion")
    @classmethod
    def numero_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El número de resolución no puede estar vacío.")
        return v.strip()

    @field_validator("tipo", "emitida_por", mode="before")
    @classmethod
    def limpiar_texto(cls, v: str | None) -> str | None:
        return v.strip() if v else None


class ResolucionCreate(ResolucionBase):
    pass


class ResolucionUpdate(BaseModel):
    numero_resolucion: Optional[str] = None
    fecha_emision:     Optional[date] = None
    tipo:              Optional[str] = None
    descripcion:       Optional[str] = None
    emitida_por:       Optional[str] = None

    @field_validator("numero_resolucion", mode="before")
    @classmethod
    def numero_no_vacio(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("El número de resolución no puede estar vacío.")
        return v.strip() if v else None


class ResolucionResponse(ResolucionBase):
    id:          int
    archivo_pdf: Optional[str] = None
    created_at:  datetime

    model_config = {"from_attributes": True}


class ResolucionListResponse(BaseModel):
    id:                int
    numero_resolucion: str
    fecha_emision:     date
    tipo:              Optional[str] = None
    emitida_por:       Optional[str] = None
    archivo_pdf:       Optional[str] = None

    model_config = {"from_attributes": True}