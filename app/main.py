from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router

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

app.include_router(router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "sistema": "UNAMBA Escalafón API v1.0"}