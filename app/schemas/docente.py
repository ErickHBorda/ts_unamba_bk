from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional

class DocenteBase(BaseModel):
    nombres:          str
    apellidos:        str
    dni:              str
    email:            Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None

    @field_validator("dni")
    @classmethod
    def dni_debe_ser_8_digitos(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 8:
            raise ValueError("El DNI debe contener exactamente 8 dígitos numéricos.")
        return v

    @field_validator("nombres", "apellidos")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return v.strip()


class DocenteCreate(DocenteBase):
    pass


class DocenteUpdate(BaseModel):
    nombres:          Optional[str] = None
    apellidos:        Optional[str] = None
    email:            Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None
    activo:           Optional[bool] = None

    @field_validator("nombres", "apellidos", mode="before")
    @classmethod
    def no_vacio(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return v.strip() if v else v


class DocenteResponse(DocenteBase):
    id:         int
    activo:     bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocenteListResponse(BaseModel):
    id:        int
    nombres:   str
    apellidos: str
    dni:       str
    email:     Optional[str] = None
    activo:    bool

    model_config = {"from_attributes": True}