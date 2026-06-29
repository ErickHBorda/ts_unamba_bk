from sqlalchemy import Column, Integer, String, Date, Text, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PeriodoServicio(Base):
    __tablename__ = "PERIODO_SERVICIO"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    docente_id       = Column(Integer, ForeignKey("DOCENTE.id", ondelete="CASCADE"), nullable=False)
    categoria_id     = Column(Integer, ForeignKey("CATEGORIA_DOCENTE.id", ondelete="RESTRICT"), nullable=False)
    condicion_id     = Column(Integer, ForeignKey("CONDICION_LABORAL.id", ondelete="RESTRICT"), nullable=False)
    resolucion_id    = Column(Integer, ForeignKey("RESOLUCION.id", ondelete="SET NULL"))
    tipo_registro    = Column(Enum("ACTIVO", "CON_FECHAS", "MANUAL"), nullable=False)
    etiqueta_periodo = Column(String(100))
    anio_periodo     = Column(Integer)
    fecha_inicio     = Column(Date)
    fecha_fin        = Column(Date)
    anios_brutos     = Column(Integer, default=0)
    meses_brutos     = Column(Integer, default=0)
    dias_brutos      = Column(Integer, default=0)
    activo           = Column(Boolean, default=True)
    observaciones    = Column(Text)
    created_at       = Column(DateTime, server_default=func.now())

    docente    = relationship("Docente", back_populates="periodos")
    categoria  = relationship("CategoriaDocente")
    condicion  = relationship("CondicionLaboral")
    resolucion = relationship("Resolucion")
    descuento  = relationship("DescuentoPeriodo", back_populates="periodo", uselist=False)
    detalles   = relationship("DetalleCalculo", back_populates="periodo")