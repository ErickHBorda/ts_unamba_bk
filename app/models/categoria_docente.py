from sqlalchemy import Column, Integer, String, Enum
from app.db.base import Base

class CategoriaDocente(Base):
    __tablename__ = "CATEGORIA_DOCENTE"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    codigo    = Column(String(20), nullable=False, unique=True)
    nombre    = Column(String(100), nullable=False)
    modalidad = Column(Enum("TIEMPO_COMPLETO", "TIEMPO_PARCIAL"), nullable=False)