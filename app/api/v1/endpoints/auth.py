from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest
from app.schemas.response import success_response, error_response
from app.core.security import verify_password, crear_access_token
from datetime import datetime

router = APIRouter()


@router.post("/login", response_model=None)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    # ── 1. Buscar usuario por nombre_usuario ────────────────────────────
    usuario = db.query(Usuario).filter(
        Usuario.nombre_usuario == payload.nombre_usuario
    ).first()

    if not usuario:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                code="CREDENCIALES_INVALIDAS",
                message="Usuario o contraseña incorrectos.",
            ),
        )

    # ── 2. Verificar contraseña ─────────────────────────────────────────
    if not verify_password(payload.password, usuario.password_hash):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                code="CREDENCIALES_INVALIDAS",
                message="Usuario o contraseña incorrectos.",
            ),
        )

    # ── 3. Verificar que el usuario esté activo ─────────────────────────
    if not usuario.activo:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response(
                code="USUARIO_INACTIVO",
                message="Tu cuenta está desactivada. Contacta al administrador.",
            ),
        )

    # ── 4. Generar token JWT ────────────────────────────────────────────
    token = crear_access_token(data={
        "sub": usuario.nombre_usuario,
        "rol": usuario.rol,
        "id":  usuario.id,
    })

    # ── 5. Registrar último acceso ──────────────────────────────────────
    usuario.ultimo_acceso = datetime.utcnow()
    db.commit()

    return success_response(data={
        "access_token":  token,
        "token_type":    "bearer",
        "rol":           usuario.rol,
        "nombre_usuario": usuario.nombre_usuario,
    })