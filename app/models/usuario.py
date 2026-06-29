from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "USUARIO"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(100), nullable=False, unique=True)
    email          = Column(String(150), nullable=False, unique=True)
    password_hash  = Column(String(255), nullable=False)
    rol            = Column(Enum("ADMINISTRADOR", "CONSULTOR"), nullable=False, default="CONSULTOR")
    
    # Al usar Boolean, SQLAlchemy entenderá perfectamente tu TINYINT(1) de MySQL
    activo         = Column(Boolean, default=True) 
    
    ultimo_acceso  = Column(DateTime)
    created_at     = Column(DateTime, server_default=func.now())