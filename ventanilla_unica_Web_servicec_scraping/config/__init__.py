import os
import ssl
from dotenv import load_dotenv
import datetime
# Load environment variables from .env file
# Ensure the .env file is in the same directory as this script or provide the full path
load_dotenv()

# Load environment variables from .env file
class Config:
    SOAP_SERVICE_URL = "https://www.ventanillaunica.gob.mx"
    
    """Area de pruebas o produccion
        Indica si se utilizara la version de pruebas o la de produccion 
        Si Debug es True significa que estamos en prueba
        False estamos en produccion
    """
    DEBUG = os.getenv('DEBUG')
    ROOT = os.path.dirname(os.path.abspath(__file__))
    """# Configura el folder de produccion y el de pruebas"""
    if DEBUG:
        STATIC = ROOT + \
            f'/response/Testing/{datetime.date.today()}'
    else:
        STATIC = ROOT + \
            f'/response/Production/{datetime.date.today()}'
            
    """# Database configuration #
        Parametros de conexion a la bgase de datos
    """
    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DRIVER = os.getenv("DB_DRIVER")

    """# SOAP service configuration #
        Es necesario bajar la seguridad de nuestras peticiones SOAP
        esto es debido a que si hacemos las peticiones con la seguridad por
        defecto nos devolvera un server error.
    """
    context = ssl.create_default_context()
    context.set_ciphers('DEFAULT:@SECLEVEL=1')
    
    """# Script configuration #
        Nos indica el nivel de generacion de logs que estaremos utilizando
    """
    SCRIPT_LOG_LEVEL = os.getenv("SCRIPT_LOG_LEVEL", "DEBUG")
    SCRIPT_LOG_FILE = os.getenv("SCRIPT_LOG_FILE", "logs/soap_service.log")

# Project Settings
# This is where you can define your project settings and configurations
SETTINGS = Config()