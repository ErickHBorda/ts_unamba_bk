from sqlalchemy import Column, Integer, String, Date, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Resolucion(Base):
    __tablename__ = "RESOLUCION"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    numero_resolucion = Column(String(100), nullable=False)
    fecha_emision     = Column(Date, nullable=False)
    tipo              = Column(String(100))
    descripcion       = Column(Text)
    emitida_por       = Column(String(150))
    archivo_pdf       = Column(String(255))
    created_at        = Column(DateTime, server_default=func.now())