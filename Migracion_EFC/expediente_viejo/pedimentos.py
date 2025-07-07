from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy.types import Numeric  # Cambiar Decimal por Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date

Base = declarative_base()

class Pedimento(Base):
    """Modelo SQLAlchemy para la tabla pedimentos"""
    
    __tablename__ = 'pedimentos'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Campos de texto
    patente = Column(String(50), nullable=True)
    pedimento = Column(String(50), nullable=True)
    aduana = Column(String(50), nullable=True)
    operacion = Column(String(1), nullable=True)
    clave = Column(String(50), nullable=True)
    contribuyente = Column(String(50), nullable=True)
    agente = Column(String(50), nullable=True)
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    seccion = Column(String(50), nullable=True)
    curpapoderado = Column(String(20), nullable=True)
    
    # Campos de fecha
    fechapago = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # Campos decimales - Cambiar Decimal por Numeric
    porcentaje = Column(Numeric(18, 0), nullable=True, default=0)
    vu = Column(Numeric(18, 0), nullable=True, default=0)
    importeTotal = Column(Numeric(16, 2), nullable=True)
    saldoDisponible = Column(Numeric(16, 2), nullable=True)
    importePedimento = Column(Numeric(16, 2), nullable=True)
    
    # Campos enteros
    alerta = Column(Integer, nullable=True, default=1)
    licencia = Column(Integer, nullable=True)
    contingencia = Column(Integer, nullable=False, default=0)
    filesize = Column(Integer, nullable=True)
    actualizado = Column(Integer, nullable=True)
    procesando = Column(Integer, nullable=True, default=0)
    
    # Campos de texto con valores por defecto
    af = Column(String(1), nullable=False, default='N')
    
    # Campo booleano
    ExisteExpediente = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"<Pedimento(id={self.id}, pedimento='{self.pedimento}', patente='{self.patente}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario para facilitar la serialización"""
        return {
            'id': self.id,
            'patente': self.patente,
            'pedimento': self.pedimento,
            'aduana': self.aduana,
            'operacion': self.operacion,
            'clave': self.clave,
            'fechapago': self.fechapago.isoformat() if self.fechapago else None,
            'contribuyente': self.contribuyente,
            'agente': self.agente,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'porcentaje': float(self.porcentaje) if self.porcentaje else None,
            'created_by': self.created_by,
            'alerta': self.alerta,
            'licencia': self.licencia,
            'contingencia': self.contingencia,
            'vu': float(self.vu) if self.vu else None,
            'filesize': self.filesize,
            'updated_by': self.updated_by,
            'seccion': self.seccion,
            'af': self.af,
            'actualizado': self.actualizado,
            'procesando': self.procesando,
            'curpapoderado': self.curpapoderado,
            'importeTotal': float(self.importeTotal) if self.importeTotal else None,
            'saldoDisponible': float(self.saldoDisponible) if self.saldoDisponible else None,
            'importePedimento': float(self.importePedimento) if self.importePedimento else None,
            'ExisteExpediente': self.ExisteExpediente
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia del modelo desde un diccionario"""
        # Convertir fechas string a objetos date/datetime si es necesario
        if 'fechapago' in data and isinstance(data['fechapago'], str):
            data['fechapago'] = datetime.strptime(data['fechapago'], '%Y-%m-%d').date()
        
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)