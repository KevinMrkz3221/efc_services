# 🚀 Migración EFC - Sistema de Transferencia de Pedimentos

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4+-green.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-Internal-red.svg)]()

## 📋 Descripción

Sistema robusto de migración de datos para transferir pedimentos aduanales desde múltiples sistemas legacy (SCAII, WINSAII, EXPEDIENTE_VIEJO) hacia una API REST moderna. Ofrece múltiples estrategias de procesamiento optimizadas para diferentes escenarios de carga.

## ✨ Características

- 🔄 **Múltiples fuentes**: Soporte para SCAII, WINSAII y EXPEDIENTE_VIEJO
- ⚡ **Procesamiento optimizado**: Asíncrono, síncrono y multithreaded
- 🛡️ **Manejo robusto de errores**: Validación y reintentos automáticos
- 📊 **Monitoreo en tiempo real**: Métricas detalladas de rendimiento
- 🔍 **Detección de duplicados**: Evita envíos redundantes
- 🚀 **Escalable**: Procesamiento en lotes configurables

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar el proyecto
cd Migracion_EFC

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

Crear archivo `.env`:
```env
API_URL=http://localhost:8000/api/v1
API_TOKEN=tu_token_aqui
DB_USER=sa
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=1433
DB_NAME=tu_base_datos
```

### 3. Ejecución

```bash
python main.py --db-name TU_DB --db-url localhost --db-password "password" --app 1
```

**Opciones de aplicación:**
- `--app 1`: Sistema SCAII
- `--app 2`: Sistema WINSAII  
- `--app 3`: Sistema EXPEDIENTE_VIEJO

## 🎯 Estrategias de Procesamiento

| Estrategia | Rendimiento | Estabilidad | Uso Recomendado |
|------------|-------------|-------------|-----------------|
| 🚀 **Asíncrono** | 50-100 ped/s | Media | Alto volumen, red estable |
| 📝 **Síncrono** | 5-15 ped/s | Alta | Datos críticos, debugging |
| 🧵 **Multithreaded** | 20-40 ped/s | Alta | Balance rendimiento/estabilidad |

## 🏗️ Arquitectura

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   SCAII     │    │  WINSAII    │    │ EXPEDIENTE  │
│ (SQLServer) │    │ (SQLServer) │    │   VIEJO     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                ┌─────────▼─────────┐
                │  MIGRACIÓN EFC    │
                │  ┌─────────────┐  │
                │  │ Procesador  │  │
                │  │ (Async/Sync)│  │
                │  └─────────────┘  │
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │    API DESTINO    │
                │   (REST/Django)   │
                └───────────────────┘
```

## 📊 Ejemplo de Reporte

```
=== RESUMEN DE ENVÍO ===
📊 Total pedimentos procesados: 1000
✅ Pedimentos exitosos: 987
❌ Pedimentos fallidos: 13
🔧 Total servicios creados: 987
⏭️  Pedimentos saltados (duplicados): 156
📈 Tasa de éxito: 98.7%
⚡ Velocidad promedio: 67.3 ped/s
```

## 🛠️ Dependencias Principales

- **SQLAlchemy**: ORM para base de datos
- **aiohttp**: Cliente HTTP asíncrono
- **requests**: Cliente HTTP síncrono
- **pyodbc**: Conector SQL Server
- **python-dotenv**: Variables de entorno

## 📚 Documentación

- 📖 **[Documentación Completa](DOCUMENTACION_PROYECTO.md)**: Guía técnica detallada
- 📋 **[README ORM](README_ORM.md)**: Guía específica de SQLAlchemy
- 🔧 **[Configuración](.env.example)**: Archivo de ejemplo de configuración

## 🚨 Solución de Problemas

### Error de Conexión a BD
```bash
# Verificar credenciales
cat .env

# Test de conectividad
telnet localhost 1433
```

### Error de API Token
```bash
# Verificar token
curl -H "Authorization: Token TU_TOKEN" http://tu-api.com/api/v1/
```

### Optimizar Rendimiento
```python
# Ajustar parámetros según red
batch_size = 200  # Reducir si hay timeouts
max_workers = 5   # Para multithreading
```

## 📈 Métricas de Rendimiento

| Configuración | Pedimentos/seg | Memoria RAM | CPU |
|---------------|----------------|-------------|-----|
| Async (500 batch) | 50-100 | ~200MB | 30-50% |
| Sync (50 batch) | 5-15 | ~50MB | 10-20% |
| Threaded (5 hilos) | 20-40 | ~100MB | 20-40% |

## 🤝 Contribuir

1. Fork del proyecto
2. Crear branch (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Proyecto de uso interno. Todos los derechos reservados.

---

**Desarrollado por**: [Tu Nombre] | **Versión**: 1.0 | **Fecha**: Julio 2025
