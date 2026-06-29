from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class DocenteResolucion(Base):
    __tablename__ = "DOCENTE_RESOLUCION"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    docente_id    = Column(Integer, ForeignKey("DOCENTE.id", ondelete="CASCADE"), nullable=False)
    resolucion_id = Column(Integer, ForeignKey("RESOLUCION.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("docente_id", "resolucion_id", name="uq_docente_resolucion"),
    )

    docente    = relationship("Docente", back_populates="resoluciones")
    resolucion = relationship("Resolucion")