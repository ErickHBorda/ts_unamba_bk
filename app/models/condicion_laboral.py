from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class CondicionLaboral(Base):
    __tablename__ = "CONDICION_LABORAL"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    codigo      = Column(String(30), nullable=False, unique=True)
    nombre      = Column(String(100), nullable=False)
    descripcion = Column(Text)