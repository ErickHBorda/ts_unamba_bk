from pydantic import BaseModel


class DocenteResolucionCreate(BaseModel):
    docente_id:    int
    resolucion_id: int


class DocenteResolucionResponse(BaseModel):
    id:            int
    docente_id:    int
    resolucion_id: int

    model_config = {"from_attributes": True}