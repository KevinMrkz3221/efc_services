from dataclasses import dataclass
from dotenv import load_dotenv
import os
import argparse

# Load environment variables from .env file FIRST
load_dotenv()

# Configuration settings - Load immediately after dotenv
API_URL     = os.getenv('API_URL')
API_TOKEN   = os.getenv('API_TOKEN')

# Database settings
DB_USER     = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = os.getenv('DB_PORT', '5432')
DB_NAME     = os.getenv('DB_NAME', 'migracion_efc')

@dataclass
class Settings:
    """Clase para manejar la configuración del monitor de pedimentos."""
    
    # Configuración de la API
    api_url: str = API_URL
    api_token: str = API_TOKEN

    # Configuración de la base de datos
    db_user: str = DB_USER
    db_password: str = DB_PASSWORD
    db_host: str = DB_HOST
    db_port: str = DB_PORT
    db_name: str = DB_NAME

    connection_string: str = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

settings = Settings()

# Configuration settings
API_URL     = os.getenv('API_URL')
API_TOKEN   = os.getenv('API_TOKEN')

# Database settings
DB_USER     = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = os.getenv('DB_PORT', '5432')
DB_NAME     = os.getenv('DB_NAME', 'migracion_efc')


# Argument parser for command line arguments
parser = argparse.ArgumentParser(description='Monitor de pedimentos')
parser.add_argument('--db-name', '-dn', required=True, help='Nombre de la base de datos')
parser.add_argument('--db-url', '-du', required=True, help='URL de conexión a la base de datos')
parser.add_argument('--db-password', '-dp', required=True, help='Contraseña de la base de datos')
parser.add_argument('--app', '-a', type=int, choices=[1, 2, 3], required=True, help='Aplicación: 1=SCAII, 2=WINSAII')    
args = parser.parse_args()    
