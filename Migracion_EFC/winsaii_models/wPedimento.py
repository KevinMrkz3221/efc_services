from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class wPedimento(Base):
    """Modelo SQLAlchemy para la tabla SPedimentos"""
    
    __tablename__ = 'wPedimento'  # Nombre de la tabla en la base de datos
    
    # Definir las columnas basándose en el query SQL que ya tienes
    PEDIMENTO = Column(String(50), primary_key=True)  # Clave primaria
    ADUANA = Column(String(3))  # Código de aduana
    REGIMEN = Column(String(10))
    TIPOPEDIMENTO = Column(String(1))  # 'I' para importación, 'E' para exportación
    CLAVEPED = Column(String(20))
    FECHAINICIO = Column(DateTime)
    FECHAFINAL = Column(DateTime) 
    FECHAPAGO = Column(DateTime)
    
    # Puedes agregar más columnas según tu tabla real
    # ESTADO = Column(String(20))
    # IMPORTE = Column(Float)
    # RFC_IMPORTADOR = Column(String(13))
    # etc.
    
    def __repr__(self):
        return f"<SPedimento(pedimento='{self.PEDIMENTO}', regimen='{self.REGIMEN}', tipo='{self.TIPO}')>"
    
    
    
    def to_dict(self):
        """Convierte el objeto a diccionario para facilitar la serialización"""
        return {
            'PEDIMENTO': self.PEDIMENTO,
            'ADUANA': self.ADUANA,
            'REGIMEN': self.REGIMEN,
            'TIPO': self.TIPO,
            'CLAVEPED': self.CLAVEPED,
            'FECHAINICIO': self.FECHAINICIO if self.FECHAINICIO else None,
            'FECHAFINAL': self.FECHAFINAL if self.FECHAFINAL else None,
            'FECHAPAGO': self.FECHAPAGO if self.FECHAPAGO else None,
        }