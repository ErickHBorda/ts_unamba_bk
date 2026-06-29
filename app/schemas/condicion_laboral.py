from pydantic import BaseModel

class CondicionLaboralResponse(BaseModel):
    id:          int
    codigo:      str
    nombre:      str
    descripcion: str | None = None

    model_config = {"from_attributes": True}