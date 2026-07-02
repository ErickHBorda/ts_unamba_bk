from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detalles = [
        {
            "campo":   " → ".join(str(loc) for loc in err["loc"]),
            "mensaje": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data":    None,
            "error": {
                "code":    "VALIDATION_ERROR",
                "message": "Los datos enviados no son válidos.",
                "details": detalles,
            },
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "data":    None,
            "error": {
                "code":    "INTEGRITY_ERROR",
                "message": "Conflicto de integridad en la base de datos.",
                "details": str(exc.orig),
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data":    None,
            "error": {
                "code":    "INTERNAL_SERVER_ERROR",
                "message": "Ocurrió un error inesperado en el servidor.",
                "details": None,
            },
        },
    )