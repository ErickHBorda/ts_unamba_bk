from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.session import get_db
from app.models.categoria_docente import CategoriaDocente
from app.models.condicion_laboral import CondicionLaboral
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.response import success_response

router = APIRouter()


@router.get("/categorias", response_model=None)
def listar_categorias(
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_current_user)] = None,
):
    categorias = db.query(CategoriaDocente).order_by(CategoriaDocente.codigo).all()
    return success_response(
        data=[
            {
                "id": c.id,
                "codigo": c.codigo,
                "nombre": c.nombre,
                "modalidad": c.modalidad,
            }
            for c in categorias
        ]
    )


@router.get("/condiciones", response_model=None)
def listar_condiciones(
    db: Session = Depends(get_db),
    _: Annotated[Usuario, Depends(get_current_user)] = None,
):
    condiciones = db.query(CondicionLaboral).order_by(CondicionLaboral.nombre).all()
    return success_response(
        data=[{"id": c.id, "codigo": c.codigo, "nombre": c.nombre} for c in condiciones]
    )
