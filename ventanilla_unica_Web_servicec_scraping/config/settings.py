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
    API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
    API_TOKEN = os.getenv("API_TOKEN")
    

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
    
    # Multithreading configuration
    DEFAULT_START_PAGE = int(os.getenv("DEFAULT_START_PAGE", "1"))
    DEFAULT_END_PAGE = int(os.getenv("DEFAULT_END_PAGE", "3"))
    DEFAULT_SERVICE_TYPE = int(os.getenv("DEFAULT_SERVICE_TYPE", "3"))
    DEFAULT_MAX_WORKERS = int(os.getenv("DEFAULT_MAX_WORKERS", "2"))
    
    # Thread safety and rate limiting
    REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))  # Delay between requests in same thread
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))  # Max retries per failed request


# Project Settings
# This is where you can define your project settings and configurations
SETTINGS = Config()