# Configuración para el procesamiento multihilo

# Configuración de hilos
DEFAULT_MAX_WORKERS = 5  # Número de hilos por defecto
MIN_WORKERS = 1          # Mínimo número de hilos
MAX_WORKERS = 10         # Máximo número de hilos recomendado

# Configuración de timeouts
REQUEST_TIMEOUT = 30     # Timeout para peticiones HTTP en segundos
RETRY_DELAY = 1          # Delay entre reintentos en segundos
MAX_RETRIES = 3          # Número máximo de reintentos

# Configuración de procesamiento
BATCH_SIZE = 50          # Tamaño de lote para procesar servicios
PAGE_SIZE = 50           # Tamaño de página para peticiones a la API

# Estados de servicio
SERVICE_STATE_PENDING = 1    # Estado pendiente
SERVICE_STATE_COMPLETED = 3  # Estado completado

# Tipos de documento
DOCUMENT_TYPE_PEDIMENTO_COMPLETO = 2

# Tipos de servicio
SERVICE_TYPE_DEFAULT = 8
