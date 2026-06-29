from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class CalculoTiempoServicio(Base):
    __tablename__ = "CALCULO_TIEMPO_SERVICIO"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    docente_id           = Column(Integer, ForeignKey("DOCENTE.id", ondelete="CASCADE"), nullable=False)
    fecha_calculo        = Column(DateTime, server_default=func.now())
    total_anios          = Column(Integer, default=0)
    total_meses          = Column(Integer, default=0)
    total_dias           = Column(Integer, default=0)
    total_dias_brutos    = Column(Integer, default=0)
    total_dias_descuento = Column(Integer, default=0)
    total_dias_efectivos = Column(Integer, default=0)
    generado_por         = Column(String(100))
    estado               = Column(Enum("VIGENTE", "HISTORICO"), default="VIGENTE")

    docente  = relationship("Docente", back_populates="calculos")
    detalles = relationship("DetalleCalculo", back_populates="calculo")