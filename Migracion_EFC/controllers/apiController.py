import requests
import asyncio
import aiohttp
from typing import List, Dict, Any

from config.settings import API_URL, API_TOKEN

class APIController:
    """
    Middleware para manejar las peticiones a la API.
    """

    def __init__(self):
        self.base_url = API_URL # URL base de la API
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {API_TOKEN}'  # Token de autenticación
        }

        self.timeout = 30  # Timeout para las peticiones a la API

    def _make_request(self, method, endpoint, data=None):
        """
        Método para hacer peticiones a la API.
        """

        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()  # Lanza un error si la respuesta no es 200
            return response.json()  # Retorna el JSON de la respuesta
        except requests.RequestException as e:
            print(f"Error al hacer la petición a la API: {e}")
            return None
        
    def post_pedimento(self, pedimento):
        """
        Publica un pedimento en la API.
        """
        return self._make_request('POST', 'customs/pedimentos/', pedimento)
    
    def get_pedimentos(self):
        """
        Obtiene los pedimentos desde la API.
        """
        return self._make_request('GET', 'customs/pedimentos/')
    
    def get_existing_pedimentos_numbers(self) -> set:
        """
        Obtiene solo los números de pedimentos existentes para verificación rápida.
        """
        try:
            
            response = self.get_pedimentos()

            if response and isinstance(response, list):
                # Extraer solo los números de pedimento1
                return {pedimento.get('pedimento', '').strip() for pedimento in response if pedimento.get('pedimento')}
            elif response and isinstance(response, dict) and 'results' in response:
                # Si la API devuelve paginación
                return {pedimento.get('pedimento', '').strip() for pedimento in response['results'] if pedimento.get('pedimento')}
            return set()
        except Exception as e:
            print(f"Error al obtener pedimentos existentes: {e}")
            return set()
    
    def post_service(self, body):
        """
        Publica los servicios de un pedimento en la API.
        """
        return self._make_request('POST', 'customs/procesamientopedimentos/', body)
    
    def get_service_details(self, service_id):
        """
        Obtiene los detalles de un servicio específico.
        """
        return self._make_request('GET', f'customs/services/{service_id}/')
    
    # === MÉTODOS ASÍNCRONOS ===
    
    async def post_pedimentos_only_async(self, pedimentos: List[Dict[str, Any]], batch_size: int = 200) -> List[Dict[str, Any]]:
        """
        Publica SOLO pedimentos de manera asíncrona (sin servicios).
        
        Args:
            pedimentos: Lista de pedimentos a enviar
            batch_size: Número de pedimentos por lote (default: 200)
        """
        all_results = []
        total_pedimentos = len(pedimentos)
        
        print(f"📦 FASE 1: Enviando {total_pedimentos} pedimentos en lotes de {batch_size}...")
        
        # Procesar en lotes
        for i in range(0, total_pedimentos, batch_size):
            batch = pedimentos[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_pedimentos + batch_size - 1) // batch_size
            
            print(f"  Procesando lote {batch_num}/{total_batches} ({len(batch)} pedimentos)...")
            
            # Aumentar límite de conexiones para mejor rendimiento
            connector = aiohttp.TCPConnector(limit=200, limit_per_host=50)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Crear todos los pedimentos del lote
                pedimento_tasks = []
                for pedimento in batch:
                    task = self._post_pedimento_async(session, pedimento)
                    pedimento_tasks.append(task)
                
                pedimento_results = await asyncio.gather(*pedimento_tasks, return_exceptions=True)
                
                # Procesar resultados
                for j, result in enumerate(pedimento_results):
                    pedimento_num = batch[j].get('pedimento', f'pedimento_{i+j}')
                    
                    if isinstance(result, Exception):
                        print(f"    ❌ Error en pedimento {pedimento_num}: {result}")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'success': False,
                            'error': str(result),
                            'pedimento_id': None
                        })
                    elif result:
                        pedimento_id = result.get('id')
                        print(f"    ✅ Pedimento {pedimento_num} creado exitosamente")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'success': True,
                            'response': result,
                            'pedimento_id': pedimento_id
                        })
                    else:
                        print(f"    ❌ Error en pedimento {pedimento_num}: Respuesta vacía")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'success': False,
                            'error': 'Respuesta vacía',
                            'pedimento_id': None
                        })
            
            # Pausa más corta solo si hay más lotes
            if i + batch_size < total_pedimentos:
                print(f"    Pausa de 0.5 segundos antes del siguiente lote...")
                await asyncio.sleep(0.5)
        
        return all_results

    async def post_servicios_only_async(self, pedimentos_exitosos: List[Dict[str, Any]], batch_size: int = 200) -> List[Dict[str, Any]]:
        """
        Publica SOLO servicios de manera asíncrona para pedimentos ya creados.
        
        Args:
            pedimentos_exitosos: Lista de pedimentos exitosos con sus IDs
            batch_size: Número de servicios por lote (default: 200)
        """
        # Preparar todos los servicios
        all_services = []
        for pedimento_info in pedimentos_exitosos:
            pedimento_id = pedimento_info.get('pedimento_id')
            pedimento_num = pedimento_info.get('pedimento')
            
            if pedimento_id:
                for servicio_num in range(3, 4):  # Solo servicio 3 por pedimento
                    service_data = {
                        "estado": 1,
                        "tipo_procesamiento": 1,
                        "pedimento": pedimento_id,
                        "servicio": servicio_num
                    }
                    all_services.append({
                        'service_data': service_data,
                        'pedimento_num': pedimento_num,
                        'servicio_num': servicio_num,
                        'pedimento_id': pedimento_id
                    })
        
        total_services = len(all_services)
        print(f"🔧 FASE 2: Enviando {total_services} servicios en lotes de {batch_size}...")
        
        all_results = []
        
        # Procesar servicios en lotes
        for i in range(0, total_services, batch_size):
            batch = all_services[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_services + batch_size - 1) // batch_size
            
            print(f"  Procesando lote {batch_num}/{total_batches} ({len(batch)} servicios)...")
            
            # Aumentar límite de conexiones para mejor rendimiento
            connector = aiohttp.TCPConnector(limit=200, limit_per_host=50)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Crear todos los servicios del lote
                service_tasks = []
                for service_info in batch:
                    task = self._post_service_async(session, service_info['service_data'])
                    service_tasks.append(task)
                    
                
                service_results = await asyncio.gather(*service_tasks, return_exceptions=True)
                
                # Procesar resultados
                for j, result in enumerate(service_results):
                    service_info = batch[j]
                    pedimento_num = service_info['pedimento_num']
                    servicio_num = service_info['servicio_num']
                    
                    if isinstance(result, Exception):
                        print(f"    ❌ Error en servicio {servicio_num} del pedimento {pedimento_num}: {result}")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'servicio': servicio_num,
                            'success': False,
                            'error': str(result)
                        })
                    elif result:
                        print(f"    ✅ Servicio {servicio_num} creado para pedimento {pedimento_num}")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'servicio': servicio_num,
                            'success': True,
                            'response': result
                        })
                    else:
                        print(f"    ❌ Error en servicio {servicio_num} del pedimento {pedimento_num}: Respuesta vacía")
                        all_results.append({
                            'pedimento': pedimento_num,
                            'servicio': servicio_num,
                            'success': False,
                            'error': 'Respuesta vacía'
                        })
            
            # Pausa más corta solo si hay más lotes
            if i + batch_size < total_services:
                print(f"    Pausa de 0.5 segundos antes del siguiente lote...")
                await asyncio.sleep(0.5)
        

        
        return all_results

    async def post_pedimentos_async(self, pedimentos: List[Dict[str, Any]], batch_size: int = 200) -> List[Dict[str, Any]]:
        """
        Publica múltiples pedimentos de manera asíncrona en lotes para evitar timeouts.
        OPTIMIZADO: Servicios se crean de manera completamente asíncrona.
        
        Args:
            pedimentos: Lista de pedimentos a enviar
            batch_size: Número de pedimentos por lote (default: 200)
        """
        all_results = []
        total_pedimentos = len(pedimentos)
        
        print(f"Enviando {total_pedimentos} pedimentos en lotes de {batch_size}...")
        print(f"📋 Estrategia: Dos fases (1️⃣ Pedimentos → 2️⃣ Servicios)")
        
        # Procesar en lotes
        for i in range(0, total_pedimentos, batch_size):
            batch = pedimentos[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_pedimentos + batch_size - 1) // batch_size
            
            print(f"Procesando lote {batch_num}/{total_batches} ({len(batch)} pedimentos)...")
            
            batch_results = await self._process_batch_optimized(batch, i)
            all_results.extend(batch_results)
            
            # Pausa más corta solo si hay más lotes
            if i + batch_size < total_pedimentos:
                print(f"  Pausa de 0.5 segundos antes del siguiente lote...")
                await asyncio.sleep(0.5)  # Reducido de 2 a 0.5 segundos
        
        return all_results

    async def _process_batch_optimized(self, batch: List[Dict[str, Any]], offset: int) -> List[Dict[str, Any]]:
        """
        Procesa un lote de pedimentos de manera optimizada en dos fases:
        Fase 1: Crear todos los pedimentos
        Fase 2: Crear todos los servicios de los pedimentos exitosos
        """
        # Aumentar límite de conexiones para mejor rendimiento
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # === FASE 1: CREAR TODOS LOS PEDIMENTOS ===
            print(f"    📦 Fase 1: Creando {len(batch)} pedimentos...")
            pedimento_tasks = []
            for pedimento in batch:
                task = self._post_pedimento_async(session, pedimento)
                pedimento_tasks.append(task)
            
            pedimento_results = await asyncio.gather(*pedimento_tasks, return_exceptions=True)
            
            # === FASE 2: PREPARAR Y CREAR TODOS LOS SERVICIOS ===
            successful_pedimentos = []
            for j, result in enumerate(pedimento_results):
                pedimento_num = batch[j].get('pedimento', f'pedimento_{offset+j}')
                
                if not isinstance(result, Exception) and result:
                    pedimento_id = result.get('id')
                    if pedimento_id:
                        successful_pedimentos.append({
                            'index': j,
                            'pedimento_num': pedimento_num,
                            'pedimento_id': pedimento_id,
                            'result': result
                        })
                        print(f"      ✅ Pedimento {pedimento_num} creado exitosamente")
                    else:
                        print(f"      ❌ Pedimento {pedimento_num}: Sin ID en respuesta")
                else:
                    error_msg = str(result) if isinstance(result, Exception) else "Respuesta vacía"
                    print(f"      ❌ Pedimento {pedimento_num}: {error_msg}")
            
            # Crear servicios solo si hay pedimentos exitosos
            service_results = []
            service_to_pedimento_map = {}
            
            if successful_pedimentos:
                print(f"    🔧 Fase 2: Creando servicios para {len(successful_pedimentos)} pedimentos exitosos...")
                
                service_tasks = []
                for pedimento_info in successful_pedimentos:
                    # Crear solo servicio 3 para cada pedimento exitoso
                    for servicio_num in range(3, 4):
                        service_data = {
                            "estado": 1,
                            "tipo_procesamiento": 1,
                            "pedimento": pedimento_info['pedimento_id'],
                            "servicio": servicio_num
                        }
                        task = self._post_service_async(session, service_data)
                        service_tasks.append(task)
                        service_to_pedimento_map[len(service_tasks) - 1] = {
                            'pedimento_index': pedimento_info['index'],
                            'pedimento_num': pedimento_info['pedimento_num'],
                            'servicio_num': servicio_num
                        }
                
                print(f"      📡 Enviando {len(service_tasks)} servicios de manera asíncrona...")
                service_results = await asyncio.gather(*service_tasks, return_exceptions=True)
                print(f"      ✅ Servicios procesados completamente")
            else:
                print(f"    ⚠️  No hay pedimentos exitosos, saltando creación de servicios")
            
            # === PROCESAR RESULTADOS ===
            return self._process_batch_results_two_phase(batch, offset, pedimento_results, service_results, service_to_pedimento_map)

    def _process_batch_results_two_phase(self, batch, offset, pedimento_results, service_results, service_to_pedimento_map):
        """Procesa los resultados del lote usando el enfoque de dos fases."""
        all_results = []
        services_count = {}  # Contador de servicios exitosos por pedimento
        
        # Contar servicios exitosos por pedimento
        for service_index, service_result in enumerate(service_results):
            if service_index in service_to_pedimento_map:
                mapping = service_to_pedimento_map[service_index]
                pedimento_index = mapping['pedimento_index']
                servicio_num = mapping['servicio_num']
                pedimento_num = mapping['pedimento_num']
                
                if pedimento_index not in services_count:
                    services_count[pedimento_index] = 0
                
                if not isinstance(service_result, Exception) and service_result:
                    services_count[pedimento_index] += 1
                    print(f"        ✅ Servicio {servicio_num} creado para {pedimento_num}")
                else:
                    error_msg = str(service_result) if isinstance(service_result, Exception) else "Respuesta vacía"
                    print(f"        ❌ Error en servicio {servicio_num} para {pedimento_num}: {error_msg}")
        
        # Procesar resultados finales de pedimentos
        for j, result in enumerate(pedimento_results):
            pedimento_num = batch[j].get('pedimento', f'pedimento_{offset+j}')
            services_created = services_count.get(j, 0)
            
            if isinstance(result, Exception):
                all_results.append({
                    'pedimento': pedimento_num,
                    'success': False,
                    'error': str(result),
                    'services_created': 0
                })
            elif result:
                all_results.append({
                    'pedimento': pedimento_num,
                    'success': True,
                    'response': result,
                    'services_created': services_created
                })
            else:
                all_results.append({
                    'pedimento': pedimento_num,
                    'success': False,
                    'error': 'Respuesta vacía',
                    'services_created': 0
                })
        
        return all_results

    async def _post_pedimento_async(self, session: aiohttp.ClientSession, pedimento: Dict[str, Any]):
        """
        Publica un pedimento de manera asíncrona usando aiohttp con timeout más largo.
        """
        url = f"{self.base_url}/customs/pedimentos/"
        
        try:
            # Timeout más largo para evitar timeouts
            timeout = aiohttp.ClientTimeout(total=30)  # Aumentado a 30 segundos
            async with session.post(url, json=pedimento, headers=self.headers, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            raise Exception(f"Timeout (30s) al enviar pedimento")
        except aiohttp.ClientError as e:
            raise Exception(f"Error de cliente HTTP: {e}")
        except Exception as e:
            raise Exception(f"Error inesperado: {e}")

    async def post_services_async(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Publica múltiples servicios de manera asíncrona.
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for service in services:
                task = self._post_service_async(session, service)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados similar a post_pedimentos_async
            processed_results = []
            for i, result in enumerate(results):
                service_id = services[i].get('id', f'service_{i}')
                if isinstance(result, Exception):
                    processed_results.append({
                        'service_id': service_id,
                        'success': False,
                        'error': str(result)
                    })
                else:
                    processed_results.append({
                        'service_id': service_id,
                        'success': True,
                        'response': result
                    })
            
            return processed_results

    async def _post_service_async(self, session: aiohttp.ClientSession, service: Dict[str, Any]):
        """
        Publica un servicio de manera asíncrona usando aiohttp.
        """
        url = f"{self.base_url}/customs/procesamientopedimentos/"
        
        try:
            # Usar el mismo timeout que pedimentos para consistencia
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.post(url, json=service, headers=self.headers, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            raise Exception(f"Timeout (30s) al enviar servicio")
        except aiohttp.ClientError as e:
            raise Exception(f"Error de cliente HTTP en servicio: {e}")
        except Exception as e:
            raise Exception(f"Error inesperado en servicio: {e}")

    def run_async_post_pedimentos_only(self, pedimentos: List[Dict[str, Any]], batch_size: int = 200) -> List[Dict[str, Any]]:
        """
        Método sincrónico que ejecuta el envío asíncrono SOLO de pedimentos.
        """
        return asyncio.run(self.post_pedimentos_only_async(pedimentos, batch_size))

    def run_async_post_servicios_only(self, pedimentos_exitosos: List[Dict[str, Any]], batch_size: int = 200) -> List[Dict[str, Any]]:
        """
        Método sincrónico que ejecuta el envío asíncrono SOLO de servicios.
        """
        return asyncio.run(self.post_servicios_only_async(pedimentos_exitosos, batch_size))

    def run_async_post_pedimentos(self, pedimentos: List[Dict[str, Any]], batch_size: int = 200) -> List[Dict[str, Any]]:
        """
        Método sincrónico que ejecuta el envío asíncrono de pedimentos en lotes.
        Para usar desde código síncrono.
        
        Args:
            pedimentos: Lista de pedimentos a enviar
            batch_size: Número de pedimentos por lote (default: 200)
        """
        return asyncio.run(self.post_pedimentos_async(pedimentos, batch_size))

    def run_async_post_services(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Método sincrónico que ejecuta el envío asíncrono de servicios.
        Para usar desde código síncrono.
        """
        return asyncio.run(self.post_services_async(services))
    
    # === MÉTODOS SÍNCRONOS PARA MULTITHREADING ===
    
    def get_pedimento_sync(self, patente: str, pedimento: str, aduana: str):
        """
        Verifica si un pedimento ya existe en la API de manera síncrona.
        """
        try:
            # Construir query parameters para buscar el pedimento
            params = {
                'patente': patente,
                'pedimento': pedimento, 
                'aduana': aduana
            }
            
            url = f"{self.base_url}/customs/pedimentos/"
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            return response
        except requests.RequestException as e:
            print(f"Error verificando pedimento existente: {e}")
            return None
    
    def create_pedimento_sync(self, pedimento_data: dict):
        """
        Crea un pedimento de manera síncrona.
        """
        try:
            url = f"{self.base_url}/customs/pedimentos/"
            response = requests.post(url, json=pedimento_data, headers=self.headers, timeout=self.timeout)
            return response
        except requests.RequestException as e:
            print(f"Error creando pedimento: {e}")
            return None
    
    def create_servicio_sync(self, servicio_data: dict):
        """
        Crea un servicio de manera síncrona.
        """
        try:
            url = f"{self.base_url}/customs/procesamientopedimentos/"
            response = requests.post(url, json=servicio_data, headers=self.headers, timeout=self.timeout)
            return response
        except requests.RequestException as e:
            print(f"Error creando servicio: {e}")
            return None

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            # Aquí puedes agregar lógica para manejar las peticiones HTTP
            pass
        elif scope['type'] == 'websocket':
            # Aquí puedes agregar lógica para manejar las conexiones WebSocket
            pass

        await self.app(scope, receive, send)