# Sistema de Credenciales Dinámicas SOAP

## Resumen de Mejoras

Se han implementado las siguientes mejoras al sistema de manejo de datos SOAP:

### 1. **Separación de Templates XML**
- Los templates XML ahora están en archivos separados en `payload_structure/templates/`
- Cada operación SOAP tiene su propio archivo XML template
- Los templates usan placeholders `{variable}` para datos dinámicos

### 2. **Modelos de Datos Estructurados**
- `CredencialesSOAP`: Para autenticación SOAP básica
- `CredencialesVUCEM`: Para credenciales obtenidas desde la API
- `ConsultaEstadoPedimento`, `ConsultaPedimentoCompleto`, etc.: Para parámetros de consulta

### 3. **Gestor de Credenciales Dinámicas**
- `CredentialsManager`: Obtiene credenciales desde el endpoint `get_vucem_credentials`
- Cache de credenciales para mejorar rendimiento
- Validación de permisos (acusecove, acuseedocument)

### 4. **Gestor de Templates**
- `SOAPTemplateManager`: Renderiza templates XML con datos dinámicos
- Métodos específicos para cada tipo de consulta
- Manejo de errores en carga de templates

## Estructura de Archivos

```
payload_structure/
├── __init__.py
├── soap_models.py              # Modelos de datos
├── credentials_manager.py      # Gestor de credenciales
├── template_manager.py         # Gestor de templates
└── templates/
    ├── consultar_estado_pedimento.xml
    ├── consultar_pedimento_completo.xml
    ├── consultar_partida.xml
    ├── consultar_acuses.xml
    └── consultar_remesas.xml
```

## Uso del Sistema

### Ejemplo Básico

```python
# Inicializar el proceso principal
main_process = MainProcess()

# Consultar estado de pedimento con credenciales dinámicas
result = main_process.consultar_estado_pedimento(
    importador="MABL620809BY7",
    numero_operacion="6739066752",
    aduana="070", 
    patente="3842",
    pedimento="5007760"
)
```

### Obtener Credenciales

```python
# El sistema obtiene automáticamente las credenciales desde la API
credentials_manager = CredentialsManager(api_controller)
soap_creds = credentials_manager.get_soap_credentials("MABL620809BY7")
```

### Flujo de Credenciales

1. **Solicitud**: Se solicita una operación SOAP con un importador
2. **API Call**: Se llama a `get_vucem_credentials(importador)`
3. **Validación**: Se valida que las credenciales estén activas
4. **Cache**: Se guarda en cache para futuras consultas
5. **Uso**: Se usan las credenciales para generar el XML SOAP

## Respuesta del Endpoint VUCEM

```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "usuario": "string",
  "password": "string", 
  "patente": "string",
  "is_importador": true,
  "acusecove": true,
  "acuseedocument": true,
  "is_active": true,
  "created_at": "2019-08-24T14:15:22Z",
  "updated_at": "2019-08-24T14:15:22Z",
  "created_by": "ee824cad-d7a6-4f48-87dc-e8461a9201c4",
  "updated_by": "deea00dc-b6b6-4412-a483-26ac61e1f6fe",
  "organizacion": "45ebc164-cfee-426a-b821-7146771602f2"
}
```

## Ventajas del Nuevo Sistema

1. **Mantenibilidad**: Templates separados facilitan modificaciones
2. **Reutilización**: Credenciales dinámicas permiten múltiples usuarios
3. **Seguridad**: No hay credenciales hardcodeadas
4. **Escalabilidad**: Fácil agregar nuevos tipos de consulta
5. **Flexibilidad**: Sistema de cache y validación de permisos
6. **Trazabilidad**: Mejor logging y manejo de errores

## Métodos Principales

- `consultar_estado_pedimento()`: Consulta estado con credenciales dinámicas
- `get_pedimento_completo()`: Obtiene pedimento completo
- `consultar_partidas()`: Consulta partidas específicas
- `get_acuses()`: Obtiene acuses (valida permisos)
- `consultar_remesas()`: Consulta remesas

## Configuración

Las credenciales se obtienen dinámicamente desde la API, pero puedes configurar fallbacks en `.env`:

```bash
# Fallback credentials (opcional)
DEFAULT_USERNAME=MABL620809BY7
DEFAULT_PASSWORD=password_here
```

## Próximos Pasos

1. Implementar validación de XML schemas
2. Agregar logging estructurado
3. Implementar retry logic para fallos de red
4. Agregar métricas de rendimiento
5. Implementar rate limiting
