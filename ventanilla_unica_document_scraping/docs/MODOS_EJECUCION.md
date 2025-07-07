# Ejemplo de Uso - Modos de Ejecución

## Modo Interactivo (Por defecto)
```python
python main.py
```
Al ejecutar el script aparecerá un menú para elegir:
1. Procesamiento Multihilo (Asíncrono) - Más rápido
2. Procesamiento Secuencial (Síncrono) - Más seguro

## Uso Programático

### Modo Multihilo (Asíncrono)
```python
from main import Main

# Crear instancia con configuración personalizada
main = Main(max_workers=8)

# Ejecutar en modo multihilo
main.run()
```

### Modo Secuencial (Síncrono)
```python
from main import Main

# Crear instancia
main = Main()

# Ejecutar en modo secuencial
main.run_sync()
```

## Comparación de Modos

### Modo Multihilo (Asíncrono)
**Ventajas:**
- ✅ Procesamiento más rápido (3-5x)
- ✅ Mejor utilización de recursos
- ✅ Ideal para grandes volúmenes

**Desventajas:**
- ⚠️ Mayor consumo de memoria
- ⚠️ Puede sobrecargar la API
- ⚠️ Logs entremezclados

**Cuándo usar:**
- Muchos documentos (>20)
- API robusta que soporta concurrencia
- Red estable y rápida

### Modo Secuencial (Síncrono)
**Ventajas:**
- ✅ Más predecible y estable
- ✅ Logs ordenados y claros
- ✅ Menor carga en el servidor
- ✅ Más fácil para debugging

**Desventajas:**
- ⏳ Procesamiento más lento
- ⏳ Infrautilización de recursos

**Cuándo usar:**
- Pocos documentos (<20)
- API limitada o inestable
- Conexión lenta o inestable
- Debugging o desarrollo

## Configuración Recomendada por Escenario

### Desarrollo/Testing
```python
main = Main(max_workers=2)  # Pocos hilos
main.run_sync()             # Modo secuencial para ver errores claramente
```

### Producción - Volumen Bajo
```python
main = Main(max_workers=3)
main.run()                  # Multihilo moderado
```

### Producción - Volumen Alto
```python
main = Main(max_workers=8)
main.run()                  # Máximo rendimiento
```

### Servidor Limitado
```python
main = Main()
main.run_sync()             # Sin concurrencia para no sobrecargar
```

## Monitoreo y Logs

### Modo Multihilo
```
🚀 Ejecutando en modo MULTIHILO con 5 hilos...
Se encontraron 15 servicios para procesar
Iniciando procesamiento del servicio 123 - Pedimento 1005032
Iniciando procesamiento del servicio 124 - Pedimento 1005033
✓ Servicio 123 - Pedimento 1005032 actualizado correctamente
✓ Servicio 124 - Pedimento 1005033 actualizado correctamente
```

### Modo Secuencial
```
🔄 Ejecutando en modo SECUENCIAL...
Se encontraron 15 servicios para procesar
Procesando servicio 1/15: 123
Iniciando procesamiento del servicio 123 - Pedimento 1005032
✓ Servicio 123 - Pedimento 1005032 actualizado correctamente
Procesando servicio 2/15: 124
```
