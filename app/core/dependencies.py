from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.session import get_db
from app.models.usuario import Usuario
from app.core.security import decodificar_token
from app.schemas.response import error_response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db:    Session = Depends(get_db),
) -> Usuario:
    """
    Dependencia base: valida el token JWT y retorna el usuario autenticado.
    Lanza 401 si el token es inválido o expirado.
    """
    payload = decodificar_token(token)
    if not payload:
        raise _unauthorized("Token inválido o expirado.")

    nombre_usuario = payload.get("sub")
    if not nombre_usuario:
        raise _unauthorized("Token inválido: falta el campo 'sub'.")

    usuario = db.query(Usuario).filter(
        Usuario.nombre_usuario == nombre_usuario
    ).first()

    if not usuario:
        raise _unauthorized("El usuario del token no existe.")

    if not usuario.activo:
        raise _forbidden("Tu cuenta está desactivada. Contacta al administrador.")

    return usuario


def get_admin_user(
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    """
    Dependencia de rol: solo permite acceso a usuarios ADMINISTRADOR.
    Lanza 403 si el usuario es CONSULTOR.
    """
    if current_user.rol != "ADMINISTRADOR":
        raise _forbidden("No tienes permisos para realizar esta acción.")
    return current_user


# ── Helpers privados ────────────────────────────────────────────────────

from fastapi import HTTPException

def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_response(
            code="NO_AUTENTICADO",
            message=message,
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=error_response(
            code="SIN_PERMISOS",
            message=message,
        ),
    )