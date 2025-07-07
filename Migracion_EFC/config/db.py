from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import logging


@contextmanager
def get_db_connection(args):
    """Context manager para manejar la conexión a la base de datos usando SQLAlchemy"""
    # Codificar la contraseña para URL
    password_encoded = quote_plus(args.db_password)
    
    # Crear connection string para SQLAlchemy
    connection_string = (
        f"mssql+pyodbc://sa:{password_encoded}@{args.db_url}/"
        f"{args.db_name}?driver=ODBC+Driver+17+for+SQL+Server"
    )
    
    engine = None
    conn = None
    try:
        engine = create_engine(connection_string)
        conn = engine.connect()
        print("Conexión a SQL Server exitosa.")
        yield conn
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {e}")
        raise
    finally:
        if conn:
            conn.close()
        if engine:
            engine.dispose()
        print("Conexión cerrada.")

@contextmanager  
def get_db_session(args):
    """Context manager para manejar sesiones de SQLAlchemy ORM"""
    # Codificar la contraseña para URL
    password_encoded = quote_plus(args.db_password)
    
    # Crear connection string para SQLAlchemy
    connection_string = (
        f"mssql+pyodbc://sa:{password_encoded}@{args.db_url}/"
        f"{args.db_name}?driver=ODBC+Driver+17+for+SQL+Server"
    )
    
    engine = None
    session = None
    try:
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        print("Sesión SQLAlchemy creada exitosamente.")
        yield session
    except Exception as e:
        if session:
            session.rollback()
        logging.error(f"Error en la sesión de base de datos: {e}")
        raise
    finally:
        if session:
            session.close()
        if engine:
            engine.dispose()
        print("Sesión cerrada.")

def read_sql(filename):
    """Lee un archivo SQL y retorna su contenido"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()