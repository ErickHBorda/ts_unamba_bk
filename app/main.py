from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.exception_handlers import (
    validation_exception_handler,
    integrity_error_handler,
    generic_exception_handler,
)

app = FastAPI(
    title="UNAMBA Escalafón API",
    version="1.0.0",
    description="Sistema de cálculo de tiempo de servicios docentes — UNAMBA",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "sistema": "UNAMBA Escalafón API v1.0"}