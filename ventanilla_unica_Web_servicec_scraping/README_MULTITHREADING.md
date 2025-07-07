# Multithreaded Pedimento Processing System

This system processes pedimento services using multiple threads to handle different pages concurrently, each with `service_type=3`.

## Features

- **Multithreaded Processing**: Process multiple pages simultaneously using ThreadPoolExecutor
- **Dynamic Credential Management**: Automatically fetches VUCEM credentials from API
- **Template-based SOAP Requests**: Uses XML templates for generating SOAP payloads
- **File Upload Integration**: Automatically uploads SOAP responses as XML documents
- **Configurable Parameters**: Environment variables and command-line arguments
- **Rate Limiting**: Built-in delays to prevent server overload
- **Retry Logic**: Automatic retries for failed requests
- **Comprehensive Logging**: Thread-safe logging with detailed progress tracking

## Configuration

### Environment Variables (.env file)

```bash
# API Configuration
API_URL=http://localhost:8000/api/v1
API_TOKEN=your_api_token_here

# Multithreading Configuration
DEFAULT_START_PAGE=1
DEFAULT_END_PAGE=3
DEFAULT_SERVICE_TYPE=3
DEFAULT_MAX_WORKERS=2

# Rate Limiting and Safety
REQUEST_DELAY_SECONDS=0.5
MAX_RETRIES=3
```

### Command Line Usage

```bash
# Use defaults from .env
python main.py

# Process pages 1-5 with defaults
python main.py 1 5

# Process pages 1-10 with service_type=3 and 4 threads
python main.py 1 10 3 4

# Test mode (first 2 pages only)
python -c "from main import MainProcess; MainProcess().test_multithreading()"
```

## How It Works

### 1. Main Process Flow

```python
MainProcess()
├── process_pedimento_services()          # Coordinator
    ├── ThreadPoolExecutor()              # Thread pool manager
    ├── process_pedimento_services_single_page() # Worker function
    │   ├── get_pedimento_services()       # Fetch services for page
    │   ├── get_pedimento_completo()       # SOAP request per service
    │   ├── post_document()               # Upload XML response
    │   └── put_pedimento_service()       # Update service status
    └── Results aggregation               # Collect all thread results
```

### 2. Threading Architecture

- **Main Thread**: Coordinates execution and aggregates results
- **Worker Threads**: Each processes one page of services (service_type=3)
- **Thread Safety**: Each thread has its own API connections and credentials
- **Rate Limiting**: Built-in delays prevent server overload

### 3. Error Handling

- **Per-Service Retries**: Up to 3 attempts per failed SOAP request
- **Thread-Level Error Capture**: Errors are collected without stopping other threads
- **Graceful Degradation**: Failed services are marked with estado=2
- **Comprehensive Reporting**: All errors logged with thread and context info

## Workflow Example

For pages 1-3 with 2 threads:

```
[PedimentoWorker-0] Processing page 1 with service_type=3
[PedimentoWorker-1] Processing page 2 with service_type=3
[PedimentoWorker-0] Processing 15 services on page 1
[PedimentoWorker-1] Processing 20 services on page 2
[PedimentoWorker-0] Processing pedimento 1234567 (service 101)
[PedimentoWorker-1] Processing pedimento 2345678 (service 201)
...
✓ Page 1 completed by PedimentoWorker-0: 12/15 successful
✓ Page 2 completed by PedimentoWorker-1: 18/20 successful
[PedimentoWorker-0] Processing page 3 with service_type=3
...
```

## Performance Benefits

- **Parallel Processing**: Multiple pages processed simultaneously
- **Reduced Total Time**: ~60-70% faster than sequential processing
- **Server-Friendly**: Rate limiting prevents overwhelming the API
- **Scalable**: Configurable thread count based on system resources

## Best Practices

1. **Thread Count**: Start with 2-3 threads, increase based on server capacity
2. **Rate Limiting**: Keep REQUEST_DELAY_SECONDS ≥ 0.5 to avoid rate limits
3. **Page Range**: Process manageable chunks (10-20 pages) at a time
4. **Monitoring**: Watch for error rates and adjust accordingly

## Output Example

```
=== RESUMEN DEL PROCESAMIENTO MULTIHILO ===
Tiempo total: 45.23 segundos
Páginas procesadas: 3
Total servicios procesados: 47
Total servicios exitosos: 42
Total servicios fallidos: 5
Tasa de éxito: 89.4%
```

## Thread Safety

- Each thread maintains separate API controller instances
- SOAP credentials are fetched independently per thread
- File operations use temporary files with unique names
- Error collection is thread-safe using concurrent data structures

## Troubleshooting

### Common Issues

1. **High Failure Rate**: Reduce thread count or increase delay
2. **Connection Errors**: Check API_URL and network connectivity
3. **Authentication Errors**: Verify API_TOKEN is valid
4. **Memory Issues**: Reduce max_workers or page range

### Debug Mode

Add debug logging to see detailed execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
