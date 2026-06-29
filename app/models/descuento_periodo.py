from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class DescuentoPeriodo(Base):
    __tablename__ = "DESCUENTO_PERIODO"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    periodo_id            = Column(Integer, ForeignKey("PERIODO_SERVICIO.id", ondelete="CASCADE"), nullable=False, unique=True)
    faltas_injustificadas = Column(Integer, default=0)
    permisos_sin_goce     = Column(Integer, default=0)
    licencias_sin_goce    = Column(Integer, default=0)
    total_dias_descuento  = Column(Integer, default=0)
    observaciones         = Column(Text)

    periodo = relationship("PeriodoServicio", back_populates="descuento")