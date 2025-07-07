from dataclasses import dataclass
from config.settings import args
from config.db import get_db_session
from datetime import datetime, timedelta, date
import concurrent.futures
import threading
import time
import asyncio

from scaii_models.sPedimentoModel import SPedimento
from scaii_models.gEmpresaModel import GEmpresa
from winsaii_models.wPedimento import wPedimento

from controllers.apiController import APIController
from expediente_viejo.pedimentos import Pedimento

@dataclass
class Main:
    """Clase principal para manejar la lógica del monitor de pedimentos."""
    
    # Aquí puedes agregar más atributos si es necesario 
    def __post_init__(self):
        """Inicialización posterior a la creación de la instancia."""
        # Se obtienen los pedimentos a subir de la aplicacion SCAII o WINSAII
        self.pedimentos, self.contribuyente = self.get_db_pedimentos()
        print(self.contribuyente)

    def get_db_pedimentos(self):
        """Obtiene los pedimentos desde la base de datos."""
        with get_db_session(args) as session:
            if args.app == 1:
                return session.query(SPedimento).all(), session.query(GEmpresa).first()
            elif args.app == 2:
                return session.query(wPedimento).all(), None
            elif args.app == 3:
                # Para EXPEDIENTE_VIEJO - filtrar por licencia y contribuyente
                pedimentos = session.query(Pedimento).filter(
                    Pedimento.licencia == 71,
                    Pedimento.contribuyente == 'MTK861014317'
                ).limit(100).all()
                return pedimentos, None
            else:
                raise ValueError("Aplicación no reconocida. Usa 1 para SCAII o 2 para WINSAII.")

    def process_pedimentos(self, batch_size: int = 200):
        """
        Procesa pedimentos según el tipo de aplicación.
        
        Args:
            batch_size: Número de pedimentos por lote (default: 200)
        """
        print("🔍 Verificando pedimentos existentes en la API...")
        
        # Obtener pedimentos existentes para evitar duplicados
        api_controller = APIController()
        existing_pedimentos = api_controller.get_existing_pedimentos_numbers()
        
        print(f"📊 Pedimentos existentes en API: {len(existing_pedimentos)}")
        
        # Preparar todos los bodies primero
        bodies = []
        skipped_count = 0
        
        for pedimento in self.pedimentos:
            # Construir el body según el tipo de aplicación
            if args.app == 1:
                body = self._build_scaii_pedimento_body(pedimento)
            elif args.app == 2:
                body = self._build_winsaii_pedimento_body(pedimento)
            elif args.app == 3:  # Nueva opción para expediente_viejo
                body = self._build_expediente_viejo_pedimento_body(pedimento)
            else:
                raise ValueError("Aplicación no reconocida.")
            
            # Verificar si el pedimento ya existe
            pedimento_number = body['pedimento'].strip()
            if pedimento_number in existing_pedimentos:
                print(f"⏭️  Saltando pedimento {pedimento_number} (ya existe)")
                skipped_count += 1
                continue
            
            bodies.append(body)
        
        print(f"📈 Total pedimentos de la DB: {len(self.pedimentos)}")
        print(f"⏭️  Pedimentos saltados (duplicados): {skipped_count}")
        print(f"📤 Pedimentos nuevos a enviar: {len(bodies)}")
        
        if not bodies:
            print("✅ No hay pedimentos nuevos para enviar.")
            return
        
        # === FASE 1: ENVIAR TODOS LOS PEDIMENTOS ===
        print(f"🚀 Iniciando envío en lotes de {batch_size}...")
        pedimento_results = api_controller.run_async_post_pedimentos_only(bodies, batch_size)
        
        # Obtener pedimentos exitosos para la fase 2
        successful_pedimentos = [r for r in pedimento_results if r['success'] and r.get('pedimento_id')]
        failed_pedimentos = [r for r in pedimento_results if not r['success']]
        
        print(f"\n📊 RESULTADOS FASE 1 - PEDIMENTOS:")
        print(f"✅ Pedimentos exitosos: {len(successful_pedimentos)}")
        print(f"❌ Pedimentos fallidos: {len(failed_pedimentos)}")
        
        # === FASE 2: ENVIAR TODOS LOS SERVICIOS ===
        service_results = []
        total_services_created = 0
        
        if successful_pedimentos:
            print(f"\n� Iniciando creación de servicios...")
            service_results = api_controller.run_async_post_servicios_only(successful_pedimentos, batch_size)  # Más servicios por lote
            
            # Contar servicios exitosos por pedimento
            services_by_pedimento = {}
            for service_result in service_results:
                if service_result['success']:
                    pedimento = service_result['pedimento']
                    services_by_pedimento[pedimento] = services_by_pedimento.get(pedimento, 0) + 1
                    total_services_created += 1
            
            print(f"\n📊 RESULTADOS FASE 2 - SERVICIOS:")
            print(f"🔧 Total servicios creados: {total_services_created}")
            print(f"📈 Servicios esperados: {len(successful_pedimentos) * 7}")
            
            # Actualizar resultados de pedimentos con cuenta de servicios
            for pedimento_result in pedimento_results:
                if pedimento_result['success']:
                    pedimento_num = pedimento_result['pedimento']
                    pedimento_result['services_created'] = services_by_pedimento.get(pedimento_num, 0)
                else:
                    pedimento_result['services_created'] = 0
        else:
            print(f"\n⚠️  No hay pedimentos exitosos, saltando creación de servicios")
            # Asegurar que todos los pedimentos fallidos tengan services_created = 0
            for pedimento_result in pedimento_results:
                pedimento_result['services_created'] = 0
        
        # Usar pedimento_results como results para el resto del código
        results = pedimento_results
        
        # Mostrar resumen de resultados
        successful = len([r for r in results if r['success']])
        failed = len([r for r in results if not r['success']])
        total_services = sum([r.get('services_created', 0) for r in results])
        
        print(f"\n=== RESUMEN DE ENVÍO ===")
        print(f"📊 Total pedimentos procesados: {len(results)}")
        print(f"✅ Pedimentos exitosos: {successful}")
        print(f"❌ Pedimentos fallidos: {failed}")
        print(f"🔧 Total servicios creados: {total_services}")
        print(f"⏭️  Pedimentos saltados (duplicados): {skipped_count}")
        
        # Mostrar estadísticas de servicios
        if successful > 0:
            expected_services = successful * 7
            service_success_rate = (total_services / expected_services) * 100 if expected_services > 0 else 0
            print(f"📈 Servicios esperados: {expected_services}")
            print(f"📈 Tasa de éxito de servicios: {service_success_rate:.1f}%")
        
        # Mostrar detalles de los errores si hay
        if failed > 0:
            print(f"\n=== ERRORES DE PEDIMENTOS ({failed}) ===")
            error_count = 0
            for result in results:
                if not result['success']:
                    error_count += 1
                    print(f"❌ {error_count}. {result['pedimento']}: {result['error']}")
                    # Limitar la cantidad de errores mostrados
                    if error_count >= 10:
                        remaining_errors = failed - error_count
                        if remaining_errors > 0:
                            print(f"   ... y {remaining_errors} errores más")
                        break
        
        # Mostrar pedimentos con servicios incompletos
        incomplete_services = [r for r in results if r['success'] and r.get('services_created', 0) < 7]
        if incomplete_services:
            print(f"\n=== PEDIMENTOS CON SERVICIOS INCOMPLETOS ({len(incomplete_services)}) ===")
            for i, result in enumerate(incomplete_services[:10]):  # Limitar a 10
                services_created = result.get('services_created', 0)
                print(f"⚠️  {i+1}. {result['pedimento']}: {services_created}/7 servicios creados")
            
            if len(incomplete_services) > 10:
                print(f"   ... y {len(incomplete_services) - 10} más con servicios incompletos")

    def _transform_fecha(self, fecha_numerica):
        """Transforma fecha numérica a fecha normal usando la fórmula DATEADD(DAY, fecha - 4, '1801-01-01')"""
        if fecha_numerica:
            base_date = datetime(1801, 1, 1)
            fecha_transformada = base_date + timedelta(days=fecha_numerica - 4)
            # Convertir a string formato ISO para JSON serialization
            return fecha_transformada.date().isoformat()
        return None

    def _transform_hora(self, hora_numerica):
        """Transforma hora numérica a tiempo normal usando la fórmula DATEADD(MILLISECOND, (hora - 1) * 10, 0)"""
        if hora_numerica:
            milliseconds = (hora_numerica - 1) * 10
            # Convertir milliseconds a horas, minutos y segundos
            total_seconds = milliseconds // 1000
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            microseconds = (milliseconds % 1000) * 1000
            
            tiempo = datetime.min.replace(
                hour=hours % 24, 
                minute=minutes, 
                second=seconds, 
                microsecond=microseconds
            ).time()
            # Convertir a string formato HH:MM:SS para JSON serialization
            return tiempo.isoformat()
        return None
    
    def _build_scaii_pedimento_body(self, pedimento) -> dict:
        """Construye el cuerpo del pedimento para SCAII."""
        pedimento_parts = self._parse_pedimento_number(pedimento.PEDIMENTO)
        
        return {
            "pedimento": pedimento_parts['pedimento'],
            "patente": pedimento_parts['patente'],
            "aduana": pedimento.ADUANA_CRUCE.strip(),
            "regimen": pedimento.REGIMEN,
            "tipo_operacion": 1 if pedimento.TIPO == 'I' else 0,
            "clave_pedimento": pedimento.CLAVEPED,
            "fecha_inicio": self._transform_fecha(pedimento.FECHA_INICIO),
            "fecha_fin": self._transform_fecha(pedimento.FECHA_FIN),
            "fecha_pago": self._transform_fecha(pedimento.FECHA_PAGO),
            "alerta": True,
            "contribuyente": self.contribuyente.RFC.strip() if self.contribuyente and self.contribuyente.RFC else "",
            "agente_aduanal": "",
            "curp_apoderado": "",
            "importe_total": 0,
            "saldo_disponible": 0,
            "importe_pedimento": 0,
            "existe_expediente": True
        }

    def _build_winsaii_pedimento_body(self, pedimento) -> dict:
        """Construye el cuerpo del pedimento para WINSAII."""
        pedimento_parts = self._parse_pedimento_number(pedimento.PEDIMENTO, separator=' ')
        
        # Fecha por defecto si no existe
        fecha_default = date(2000, 1, 1).isoformat()
        
        return {
            "pedimento": pedimento.PEDIMENTO,
            "patente": pedimento_parts['patente'],
            "aduana": pedimento.ADUANA.strip(),
            "regimen": pedimento.REGIMEN,
            "tipo_operacion": pedimento.TIPOPEDIMENTO,
            "clave_pedimento": pedimento.CLAVEPED,
            "fecha_inicio": self._transform_fecha(pedimento.FECHAINICIO) if pedimento.FECHAINICIO else fecha_default,
            "fecha_fin": self._transform_fecha(pedimento.FECHAFINAL) if pedimento.FECHAFINAL else fecha_default,
            "fecha_pago": self._transform_fecha(pedimento.FECHAPAGO) if pedimento.FECHAPAGO else fecha_default,
            "alerta": True,
            "contribuyente": self.contribuyente.RFC if self.contribuyente and self.contribuyente.RFC else "",
            "agente_aduanal": "",
            "curp_apoderado": "",
            "importe_total": 0,
            "saldo_disponible": 0,
            "importe_pedimento": 0,
            "existe_expediente": True
        }
    
    def _parse_pedimento_number(self, pedimento_num: str, separator: str = '-') -> dict:
        """Extrae patente y aduana del número de pedimento."""
        if separator in pedimento_num:
            parts = pedimento_num.split(separator)
            return {
                'aduana': parts[0] if len(parts) > 0 else "",
                'patente': parts[1] if len(parts) > 1 else "",
                'pedimento': parts[2] if len(parts) > 1 else ""
            }
        return {'aduana': "", 'patente': "", 'pedimento': pedimento_num.strip()}

    def _send_pedimento(self, body: dict):
        """Envía el pedimento usando el middleware API."""
        api_controller = APIController()
        response = api_controller.post_pedimento(body)
        
        if response:
            print(f"Pedimento {body['pedimento']} enviado exitosamente")
        else:
            print(f"Error al enviar pedimento {body['pedimento']}")
                
    def _build_expediente_viejo_pedimento_body(self, pedimento) -> dict:
        """Construye el cuerpo del pedimento para EXPEDIENTE_VIEJO."""
        data=  {
            "pedimento": pedimento.pedimento if pedimento.pedimento else "",
            "patente": pedimento.patente if pedimento.patente else "",
            "aduana": pedimento.aduana if pedimento.aduana else "",
            "regimen": "",  # No hay régimen en la tabla pedimentos
            "tipo_operacion": 1 if pedimento.operacion == 1 else 0,
            "clave_pedimento": pedimento.clave if pedimento.clave else "",  
            "fecha_inicio": str(date.today()),
            "fecha_fin": str(date.today()), # No hay fecha_fin en la tabla
            "fecha_pago": pedimento.fechapago.isoformat() if pedimento.fechapago else None,
            "alerta": bool(pedimento.alerta) if pedimento.alerta else True,
            "contribuyente": pedimento.contribuyente if pedimento.contribuyente else "",
            "agente_aduanal": pedimento.agente if pedimento.agente else "",
            "curp_apoderado": pedimento.curpapoderado if pedimento.curpapoderado else "",
            "importe_total": float(pedimento.importeTotal) if pedimento.importeTotal else 0,
            "saldo_disponible": float(pedimento.saldoDisponible) if pedimento.saldoDisponible else 0,
            "importe_pedimento": float(pedimento.importePedimento) if pedimento.importePedimento else 0,
            "existe_expediente": bool(pedimento.ExisteExpediente) if pedimento.ExisteExpediente is not None else True
        }
        print(data)
        return data
    
    def run(self, batch_size: int = 200):
        """
        Método para ejecutar la migración de pedimentos de manera asíncrona.
        
        Args:
            batch_size: Número de pedimentos por lote (default: 200)
        """
        self.process_pedimentos(batch_size)
    
    def process_pedimentos_sync(self, batch_size: int = 200):
        """
        Procesa pedimentos de manera síncrona (secuencial) según el tipo de aplicación.
        
        Args:
            batch_size: Número de pedimentos por lote (default: 200)
        """
        print("🔍 Verificando pedimentos existentes en la API...")
        
        # Obtener pedimentos existentes para evitar duplicados
        api_controller = APIController()
        existing_pedimentos = api_controller.get_existing_pedimentos_numbers()
        
        print(f"📊 Pedimentos existentes en API: {len(existing_pedimentos)}")
        
        # Preparar todos los bodies primero
        bodies = []
        skipped_count = 0
        
        for pedimento in self.pedimentos:
            # Construir el body según el tipo de aplicación
            if args.app == 1:
                body = self._build_scaii_pedimento_body(pedimento)
            elif args.app == 2:
                body = self._build_winsaii_pedimento_body(pedimento)
            elif args.app == 3:  # Nueva opción para expediente_viejo
                body = self._build_expediente_viejo_pedimento_body(pedimento)
            else:
                raise ValueError("Aplicación no reconocida.")
            
            # Verificar si el pedimento ya existe
            pedimento_number = body['pedimento'].strip() if body['pedimento'] else ""

            if pedimento_number not in existing_pedimentos:
                bodies.append(body)
            else:
                print(f"⏭️  Saltando pedimento {pedimento_number} (ya existe)")
                skipped_count += 1
                continue

            
        
        print(f"📈 Total pedimentos de la DB: {len(self.pedimentos)}")
        print(f"⏭️  Pedimentos saltados (duplicados): {skipped_count}")
        print(f"📤 Pedimentos nuevos a enviar: {len(bodies)}")
        
        if not bodies:
            print("✅ No hay pedimentos nuevos para enviar.")
            return
        
        # === FASE 1: ENVIAR TODOS LOS PEDIMENTOS DE MANERA SÍNCRONA ===
        print(f"🚀 Iniciando envío síncrono en lotes de {batch_size}...")
        
        all_results = []
        total_pedimentos = len(bodies)
        
        # Procesar en lotes
        for i in range(0, total_pedimentos, batch_size):
            batch = bodies[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_pedimentos + batch_size - 1) // batch_size
            
            print(f"  📦 Procesando lote {batch_num}/{total_batches} ({len(batch)} pedimentos)...")
            
            # Procesar cada pedimento del lote de manera secuencial
            for j, pedimento_body in enumerate(batch):
                pedimento_num = pedimento_body.get('pedimento', f'pedimento_{i+j}')
                
                try:
                    # Enviar pedimento de manera síncrona
                    response = api_controller.post_pedimento(pedimento_body)
                    
                    if response and response.get('id'):
                        pedimento_id = response.get('id')
                        print(f"    ✅ Pedimento {pedimento_num} creado exitosamente (ID: {pedimento_id})")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'success': True,
                            'response': response,
                            'pedimento_id': pedimento_id
                        })
                    else:
                        print(f"    ❌ Error en pedimento {pedimento_num}: Respuesta sin ID")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'success': False,
                            'error': 'Respuesta sin ID válido',
                            'pedimento_id': None
                        })
                        
                except Exception as e:
                    print(f"    ❌ Error en pedimento {pedimento_num}: {e}")
                    all_results.append({
                        'pedimento': pedimento_num,
                        'success': False,
                        'error': str(e),
                        'pedimento_id': None
                    })
            
            # Pausa entre lotes para no saturar el servidor
            if i + batch_size < total_pedimentos:
                print(f"    ⏸️  Pausa de 1 segundo antes del siguiente lote...")
                time.sleep(1)
        
        # Obtener pedimentos exitosos para la fase 2
        successful_pedimentos = [r for r in all_results if r['success'] and r.get('pedimento_id')]
        failed_pedimentos = [r for r in all_results if not r['success']]
        
        print(f"\n📊 RESULTADOS FASE 1 - PEDIMENTOS:")
        print(f"✅ Pedimentos exitosos: {len(successful_pedimentos)}")
        print(f"❌ Pedimentos fallidos: {len(failed_pedimentos)}")
        
        # === FASE 2: ENVIAR TODOS LOS SERVICIOS DE MANERA SÍNCRONA ===
        service_results = []
        total_services_created = 0
        
        if successful_pedimentos:
            print(f"\n🔧 Iniciando creación síncrona de servicios...")
            
            # Crear servicios para cada pedimento exitoso
            services_by_pedimento = {}
            
            for pedimento_info in successful_pedimentos:
                pedimento_id = pedimento_info.get('pedimento_id')
                pedimento_num = pedimento_info.get('pedimento')
                
                if pedimento_id:
                    # Solo crear servicio 3 para cada pedimento
                    service_data = {
                        "estado": 1,
                        "tipo_procesamiento": 1,
                        "pedimento": pedimento_id,
                        "servicio": 3
                    }
                    
                    try:
                        service_response = api_controller.post_service(service_data)
                        
                        if service_response:
                            print(f"    ✅ Servicio 3 creado para pedimento {pedimento_num}")
                            services_by_pedimento[pedimento_num] = services_by_pedimento.get(pedimento_num, 0) + 1
                            total_services_created += 1
                            
                            service_results.append({
                                'pedimento': pedimento_num,
                                'servicio': 3,
                                'success': True,
                                'response': service_response
                            })
                        else:
                            print(f"    ❌ Error creando servicio 3 para pedimento {pedimento_num}: Respuesta vacía")
                            service_results.append({
                                'pedimento': pedimento_num,
                                'servicio': 3,
                                'success': False,
                                'error': 'Respuesta vacía'
                            })
                            
                    except Exception as e:
                        print(f"    ❌ Error creando servicio 3 para pedimento {pedimento_num}: {e}")
                        service_results.append({
                            'pedimento': pedimento_num,
                            'servicio': 3,
                            'success': False,
                            'error': str(e)
                        })
            
            print(f"\n📊 RESULTADOS FASE 2 - SERVICIOS:")
            print(f"🔧 Total servicios creados: {total_services_created}")
            print(f"📈 Servicios esperados: {len(successful_pedimentos)}")
            
            # Actualizar resultados de pedimentos con cuenta de servicios
            for pedimento_result in all_results:
                if pedimento_result['success']:
                    pedimento_num = pedimento_result['pedimento']
                    pedimento_result['services_created'] = services_by_pedimento.get(pedimento_num, 0)
                else:
                    pedimento_result['services_created'] = 0
        else:
            print(f"\n⚠️  No hay pedimentos exitosos, saltando creación de servicios")
            # Asegurar que todos los pedimentos fallidos tengan services_created = 0
            for pedimento_result in all_results:
                pedimento_result['services_created'] = 0
        
        # Usar all_results como results para el resto del código
        results = all_results
        
        # Mostrar resumen de resultados
        successful = len([r for r in results if r['success']])
        failed = len([r for r in results if not r['success']])
        total_services = sum([r.get('services_created', 0) for r in results])
        
        print(f"\n=== RESUMEN DE ENVÍO SÍNCRONO ===")
        print(f"📊 Total pedimentos procesados: {len(results)}")
        print(f"✅ Pedimentos exitosos: {successful}")
        print(f"❌ Pedimentos fallidos: {failed}")
        print(f"🔧 Total servicios creados: {total_services}")
        print(f"⏭️  Pedimentos saltados (duplicados): {skipped_count}")
        
        # Mostrar estadísticas de servicios (ajustado para 1 servicio por pedimento)
        if successful > 0:
            expected_services = successful  # Solo 1 servicio (servicio 3) por pedimento
            service_success_rate = (total_services / expected_services) * 100 if expected_services > 0 else 0
            print(f"📈 Servicios esperados: {expected_services}")
            print(f"📈 Tasa de éxito de servicios: {service_success_rate:.1f}%")
        
        # Mostrar detalles de los errores si hay
        if failed > 0:
            print(f"\n=== ERRORES DE PEDIMENTOS ({failed}) ===")
            error_count = 0
            for result in results:
                if not result['success']:
                    error_count += 1
                    print(f"❌ {error_count}. {result['pedimento']}: {result['error']}")
                    # Limitar la cantidad de errores mostrados
                    if error_count >= 10:
                        remaining_errors = failed - error_count
                        if remaining_errors > 0:
                            print(f"   ... y {remaining_errors} errores más")
                        break
        
        # Mostrar pedimentos con servicios incompletos (ajustado para 1 servicio)
        incomplete_services = [r for r in results if r['success'] and r.get('services_created', 0) < 1]
        if incomplete_services:
            print(f"\n=== PEDIMENTOS CON SERVICIOS INCOMPLETOS ({len(incomplete_services)}) ===")
            for i, result in enumerate(incomplete_services[:10]):  # Limitar a 10
                services_created = result.get('services_created', 0)
                print(f"⚠️  {i+1}. {result['pedimento']}: {services_created}/1 servicios creados")
            
            if len(incomplete_services) > 10:
                print(f"   ... y {len(incomplete_services) - 10} más con servicios incompletos")
    
    def process_pedimentos_multithreaded(self, max_workers=5):
        """
        Procesa pedimentos usando multithreading con número configurable de hilos
        """
        print(f"\n{'='*60}")
        print(f"PROCESAMIENTO MULTITHREADED - {max_workers} hilos")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Verificar pedimentos existentes para evitar duplicados
        print("🔍 Verificando pedimentos existentes en la API...")
        api_controller = APIController()
        existing_pedimentos = api_controller.get_existing_pedimentos_numbers()
        print(f"📊 Pedimentos existentes en API: {len(existing_pedimentos)}")
        
        # Preparar todos los bodies primero usando la misma lógica que el método síncrono
        bodies = []
        skipped_count = 0
        
        for pedimento in self.pedimentos:
            # Construir el body según el tipo de aplicación
            print(pedimento)
            if args.app == 1:
                body = self._build_scaii_pedimento_body(pedimento)
            elif args.app == 2:
                body = self._build_winsaii_pedimento_body(pedimento)
            elif args.app == 3:
                body = self._build_expediente_viejo_pedimento_body(pedimento)
            else:
                raise ValueError("Aplicación no reconocida.")
            
            # Verificar si el pedimento ya existe
            pedimento_number = body['pedimento'].strip() if body['pedimento'] else ""
            if pedimento_number in existing_pedimentos:
                print(f"⏭️  Saltando pedimento {pedimento_number} (ya existe)")
                skipped_count += 1
                continue
            
            bodies.append(body)
        
        print(f"📈 Total pedimentos de la DB: {len(self.pedimentos)}")
        print(f"⏭️  Pedimentos saltados (duplicados): {skipped_count}")
        print(f"📤 Pedimentos nuevos a enviar: {len(bodies)}")
        
        if not bodies:
            print("✅ No hay pedimentos nuevos para enviar.")
            return
        
        print(f"Se procesarán {len(bodies)} pedimentos usando {max_workers} hilos")
        
        # Estadísticas globales protegidas por locks
        stats_lock = threading.Lock()
        stats = {
            'pedimentos_creados': 0,
            'pedimentos_existentes': 0,
            'pedimentos_error': 0,
            'servicios_creados': 0,
            'servicios_error': 0
        }
        
        def process_single_pedimento(pedimento_body):
            """Procesa un solo pedimento y sus servicios"""
            local_stats = {
                'pedimentos_creados': 0,
                'pedimentos_existentes': 0,
                'pedimentos_error': 0,
                'servicios_creados': 0,
                'servicios_error': 0
            }
            
            # Crear una nueva instancia del API controller para cada hilo
            thread_api_controller = APIController()
            pedimento_num = pedimento_body.get('pedimento', 'unknown')
            
            try:
                # Crear el pedimento
                response = thread_api_controller.post_pedimento(pedimento_body)
                
                if response and response.get('id'):
                    pedimento_id = response.get('id')
                    print(f"[HILO-{threading.current_thread().ident}] ✅ Pedimento {pedimento_num} creado exitosamente (ID: {pedimento_id})")
                    local_stats['pedimentos_creados'] += 1
                    
                    # Crear servicio 3 para este pedimento
                    service_data = {
                        "estado": 1,
                        "tipo_procesamiento": 1,
                        "pedimento": pedimento_id,
                        "servicio": 3
                    }
                    
                    service_response = thread_api_controller.post_service(service_data)
                    
                    if service_response:
                        print(f"[HILO-{threading.current_thread().ident}] ✅ Servicio 3 creado para pedimento {pedimento_num}")
                        local_stats['servicios_creados'] += 1
                    else:
                        print(f"[HILO-{threading.current_thread().ident}] ❌ Error al crear servicio 3 para pedimento {pedimento_num}")
                        local_stats['servicios_error'] += 1
                        
                else:
                    print(f"[HILO-{threading.current_thread().ident}] ❌ Error al crear pedimento {pedimento_num}: Respuesta sin ID")
                    local_stats['pedimentos_error'] += 1
                    
            except Exception as e:
                print(f"[HILO-{threading.current_thread().ident}] ❌ Error procesando pedimento {pedimento_num}: {str(e)}")
                local_stats['pedimentos_error'] += 1
            
            return local_stats
        
        # Procesar pedimentos usando ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las tareas
            futures = {executor.submit(process_single_pedimento, body): body 
                      for body in bodies}
            
            # Recopilar resultados conforme van completándose
            for future in concurrent.futures.as_completed(futures):
                pedimento_body = futures[future]
                try:
                    local_stats = future.result()
                    
                    # Actualizar estadísticas globales de forma thread-safe
                    with stats_lock:
                        for key in stats:
                            stats[key] += local_stats[key]
                        
                except Exception as e:
                    pedimento_num = pedimento_body.get('pedimento', 'unknown')
                    print(f"Error procesando pedimento {pedimento_num}: {str(e)}")
                    with stats_lock:
                        stats['pedimentos_error'] += 1
        
        # Reporte final
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n{'='*60}")
        print(f"REPORTE FINAL - PROCESAMIENTO MULTITHREADED")
        print(f"{'='*60}")
        print(f"Tiempo total: {total_time:.2f} segundos")
        print(f"Hilos utilizados: {max_workers}")
        print(f"Pedimentos procesados: {len(bodies)}")
        print(f"Pedimentos creados: {stats['pedimentos_creados']}")
        print(f"Pedimentos ya existentes: {stats['pedimentos_existentes']}")
        print(f"Pedimentos con error: {stats['pedimentos_error']}")
        print(f"Servicios creados: {stats['servicios_creados']}")
        print(f"Servicios con error: {stats['servicios_error']}")
        print(f"Pedimentos saltados (duplicados): {skipped_count}")
        
        # Calcular estadísticas de éxito
        if len(bodies) > 0:
            success_rate = (stats['pedimentos_creados'] / len(bodies)) * 100
            service_success_rate = (stats['servicios_creados'] / stats['pedimentos_creados']) * 100 if stats['pedimentos_creados'] > 0 else 0
            print(f"Tasa de éxito pedimentos: {success_rate:.1f}%")
            print(f"Tasa de éxito servicios: {service_success_rate:.1f}%")
            print(f"Velocidad promedio: {len(bodies)/total_time:.2f} pedimentos/segundo")
        
        print(f"{'='*60}")
    
    def run_sync(self, batch_size: int = 200):
        """
        Método para ejecutar la lógica principal de manera síncrona.
        
        Args:
            batch_size: Número de pedimentos por lote (default: 200)
        """
        self.process_pedimentos_sync(batch_size)

if __name__ == "__main__":
    main_instance = Main()
    
    # Configuración optimizada para velocidad
    batch_size = 300    # Valor optimizado balanceado para sync/multithreaded
    
    # Mapeo de aplicaciones
    app_names = {1: "SCAII", 2: "WINSAII", 3: "EXPEDIENTE_VIEJO"}
    app_name = app_names.get(args.app, f"APP_{args.app}")
    
    print(f"🚀 Iniciando con configuración optimizada:")
    print(f"📱 Aplicación: {app_name}")
    print(f"📦 Lotes de: {batch_size} pedimentos")
    
    if args.app == 3:
        print(f"🔍 Filtros aplicados: licencia=71, contribuyente=MTK861014317, límite=100")
    
    # Preguntar al usuario qué tipo de procesamiento quiere
    print(f"\n¿Qué tipo de procesamiento deseas usar?")
    print(f"1.  Síncrono (Seguro - una petición a la vez)")
    print(f"2. 🧵 Multithreaded (Configurable - múltiples hilos)")
    
    try:
        choice = input("Selecciona una opción (1 o 2): ").strip()
        
        if choice == "1":
            print(f"📝 Procesamiento síncrono seleccionado")
            print(f"🔗 Conexiones: Secuenciales para mayor estabilidad")
            main_instance.run_sync(batch_size)
        elif choice == "2":
            # Solicitar número de hilos
            try:
                max_workers = int(input("Ingrese el número de hilos (1-20, recomendado 5-10): ").strip())
                if max_workers < 1 or max_workers > 20:
                    print("Número de hilos fuera de rango. Usando 5 hilos por defecto.")
                    max_workers = 5
            except ValueError:
                print("Valor inválido. Usando 5 hilos por defecto.")
                max_workers = 5
            
            print(f"🧵 Procesamiento multithreaded seleccionado con {max_workers} hilos")
            print(f"🔗 Conexiones: Controladas por pool de hilos")
            main_instance.process_pedimentos_multithreaded(max_workers)
        else:
            print(f"❌ Opción inválida. Usando procesamiento síncrono por defecto.")
            main_instance.run_sync(batch_size)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Proceso cancelado por el usuario.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"🔄 Usando procesamiento síncrono por defecto.")
        main_instance.run_sync(batch_size)