from pydantic import BaseModel
from typing import Literal

class CategoriaDocenteResponse(BaseModel):
    id:        int
    codigo:    str
    nombre:    str
    modalidad: Literal["TIEMPO_COMPLETO", "TIEMPO_PARCIAL"]

    model_config = {"from_attributes": True}