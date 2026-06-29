from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Docente(Base):
    __tablename__ = "DOCENTE"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    nombres          = Column(String(150), nullable=False)
    apellidos        = Column(String(150), nullable=False)
    dni              = Column(String(8), nullable=False, unique=True)
    email            = Column(String(150))
    fecha_nacimiento = Column(Date)
    activo           = Column(Boolean, default=True)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())

    periodos    = relationship("PeriodoServicio", back_populates="docente")
    calculos    = relationship("CalculoTiempoServicio", back_populates="docente")
    resoluciones = relationship("DocenteResolucion", back_populates="docente")