from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class DetalleCalculo(Base):
    __tablename__ = "DETALLE_CALCULO"

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    calculo_id             = Column(Integer, ForeignKey("CALCULO_TIEMPO_SERVICIO.id", ondelete="CASCADE"), nullable=False)
    periodo_id             = Column(Integer, ForeignKey("PERIODO_SERVICIO.id", ondelete="CASCADE"), nullable=False)
    dias_brutos_periodo    = Column(Integer, default=0)
    dias_descuento_periodo = Column(Integer, default=0)
    dias_efectivos_periodo = Column(Integer, default=0)
    anios_efectivos        = Column(Integer, default=0)
    meses_efectivos        = Column(Integer, default=0)
    dias_efectivos         = Column(Integer, default=0)

    calculo = relationship("CalculoTiempoServicio", back_populates="detalles")
    periodo = relationship("PeriodoServicio", back_populates="detalles")