from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SPedimento(Base):
    """Modelo SQLAlchemy para la tabla SPedimentos"""
    
    __tablename__ = 'SPedimentos'  # Nombre de la tabla en la base de datos
    
    # Definir las columnas basándose en el query SQL que ya tienes
    PEDIMENTO = Column(String(50), primary_key=True)  # Clave primaria
    REGIMEN = Column(String(10))
    ADUANA_CRUCE = Column(String(3))  # Código de aduana
    TIPO = Column(String(1))  # 'I' para importación, 'E' para exportación
    CLAVEPED = Column(String(20))
    FECHA_INICIO = Column(DateTime)
    FECHA_FIN = Column(DateTime) 
    FECHA_PAGO = Column(DateTime)
    
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
            'REGIMEN': self.REGIMEN,
            'ADUAN_ACRUCE': self.ADUANA_CRUCE,
            'TIPO': self.TIPO,
            'CLAVEPED': self.CLAVEPED,
            'FECHA_INICIO': self.FECHA_INICIO if self.FECHA_INICIO else None,
            'FECHA_FIN': self.FECHA_FIN if self.FECHA_FIN else None,
            'FECHA_PAGO': self.FECHA_PAGO if self.FECHA_PAGO else None,
        }