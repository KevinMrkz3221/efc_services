from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class GEmpresa(Base):
    """Modelo SQLAlchemy para la tabla GEmpresa"""
    
    __tablename__ = 'GEmpresa'
    
    # Ajusta las columnas según tu tabla real
    RFC = Column(String(13), primary_key=True)
    NOMBRE = Column(String(255))
    # Agrega más columnas según necesites
    
    def __repr__(self):
        return f"<GEmpresa(rfc='{self.RFC}', NOMBRE='{self.NOMBRE}')>"
    
    def to_dict(self):
        return {
            'RFC': self.RFC,
            'NOMBRE': self.NOMBRE,
        }