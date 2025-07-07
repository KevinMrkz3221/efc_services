# Uso de Modelos SQLAlchemy para SPedimentos

Este proyecto ahora incluye soporte para SQLAlchemy ORM además del método original con SQL crudo.

## Archivos Importantes

- `config/models.py` - Definición de modelos SQLAlchemy
- `config/db.py` - Funciones de conexión para ORM y SQL crudo
- `main_con_orm.py` - Ejemplo completo usando ambos métodos
- `ejemplo_orm.py` - Ejemplos específicos de SQLAlchemy

## Modelos Definidos

### SPedimento
Representa la tabla `SPedimentos` con los siguientes campos:
- `PEDIMENTO` (String, Primary Key)
- `REGIMEN` (String)
- `TIPO` (String) - 'I' para importación, 'E' para exportación
- `CLAVEPED` (String)
- `FECHA_INICIO` (DateTime)
- `FECHA_FIN` (DateTime)
- `FECHA_PAGO` (DateTime)

### SContribuyente
Representa la tabla `SContribuyente` con:
- `RFC` (String, Primary Key)
- `RAZON_SOCIAL` (String)

## Cómo usar

### 1. Método ORM
```bash
python main_con_orm.py --db-name tu_db --db-url tu_servidor --db-password tu_password --app 1 

```

## Ventajas del ORM

1. **Tipo de datos seguro** - Los modelos definen tipos específicos
2. **Validación automática** - SQLAlchemy valida los datos
3. **Consultas más expresivas** - Sintaxis más legible
4. **Manejo de relaciones** - Fácil manejo de FK
5. **Migraciones** - Control de versiones de esquema

## Ejemplos de Consultas ORM

```python
# Obtener todos los pedimentos
pedimentos = session.query(SPedimento).all()

# Filtrar por tipo
importaciones = session.query(SPedimento).filter(SPedimento.TIPO == 'I').all()

# Contar por régimen
from sqlalchemy import func
conteo = session.query(SPedimento.REGIMEN, func.count(SPedimento.PEDIMENTO)).group_by(SPedimento.REGIMEN).all()

# Pedimentos con fecha de pago
con_pago = session.query(SPedimento).filter(SPedimento.FECHA_PAGO.isnot(None)).all()
```

## Migración desde SQL crudo

Si ya tienes código funcionando con SQL crudo, puedes migrar gradualmente:

1. Mantén el código SQL existente
2. Agrega las consultas ORM equivalentes
3. Compara resultados
4. Reemplaza gradualmente el SQL crudo

El archivo `main_con_orm.py` muestra ambos métodos funcionando lado a lado.
