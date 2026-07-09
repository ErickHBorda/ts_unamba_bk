from pydantic import BaseModel
from typing import Literal


class LoginRequest(BaseModel):
    nombre_usuario: str
    password:       str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    rol:          Literal["ADMINISTRADOR", "CONSULTOR"]
    nombre_usuario: str