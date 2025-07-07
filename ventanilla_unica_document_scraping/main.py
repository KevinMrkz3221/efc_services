from typing import List, Dict, Any
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import concurrent.futures
import threading
from time import sleep

import requests
load_dotenv()
import os

API_URL = os.getenv('API_URL')
API_TOKEN = os.getenv('API_TOKEN')

class APIController:
    """
    Controlador para manejar las peticiones a la API.
    """

    def __init__(self):
        self.base_url = API_URL # URL base de la API
        self.headers = {
            'Authorization': f'Token {API_TOKEN}'  # Token de autenticación
        }

        self.timeout = 10  # Timeout para las peticiones a la API

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

    def get_documents(self, document_type, pedimento) -> List[Dict[str, Any]]:
        """

        Método para obtener la lista de servicios desde la API.
        """
        url = f"{self.base_url}/record/documents/?pedimento={pedimento}&document_type={document_type}"
        return self._make_request('GET', f'record/documents/?pedimento={pedimento}&document_type={document_type}')
    
    def download_document(self, document_id: int) -> Dict[str, Any]:
        """
        Método para descargar un documento específico desde la API.
        
        Args:
            document_id: ID del documento a descargar.
        
        Returns:
            Diccionario con el contenido del documento.
        """
        payload = {}
        headers = {
            "Authorization": f"Token {API_TOKEN}",
        }
        url = f"{API_URL}/record/documents/descargar/{document_id}/"

        response = requests.request("GET", url, headers=headers, data=payload)
        return response
    
    def get_pedimento_services(self, page, service_type=8) -> List[Dict[str, Any]]:
        """
        Método para obtener la lista de servicios desde la API.
        """
        return self._make_request('GET', f'customs/procesamientopedimentos/?page={page}&page_size=50&estado=1&servicio={service_type}')
    
    def put_pedimento_service(self, service_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método para actualizar un servicio de pedimento en la API.
        """
        return self._make_request('PUT', f'customs/procesamientopedimentos/{service_id}/', data=data)

    def put_pedimento(self, pedimento_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método para actualizar un pedimento en la API.
        """
        return self._make_request('PUT', f'customs/pedimentos/{pedimento_id}/', data=data)


class Main:
    """
    Clase principal para ejecutar el script.
    """

    def __init__(self, max_workers=5):
        self.api_controller = APIController()
        self.max_workers = max_workers
        self.lock = threading.Lock()  # Para evitar conflictos en las salidas de print

    def extract_xml_data(self, xml_content: str) -> Dict[str, Any]:
        """
        Método para extraer datos específicos del XML.
        
        Args:
            xml_content: Contenido del XML como string.
        
        Returns:
            Diccionario con los datos extraídos.
        """
        try:
            root = ET.fromstring(xml_content)
            namespaces = {
                'ns2': 'http://www.ventanillaunica.gob.mx/pedimentos/ws/oxml/consultarpedimentocompleto',
            }
            
            # Extraer datos con manejo de errores individual
            data = {}
            
            # Número de operación
            numero_operacion = root.find('.//ns2:numeroOperacion', namespaces)
            data['numero_operacion'] = numero_operacion.text if numero_operacion is not None else None
            
            # Pedimento
            pedimento = root.find('.//ns2:pedimento/ns2:pedimento', namespaces)
            data['pedimento'] = pedimento.text if pedimento is not None else None
            
            # CURP Apoderado
            curp_apoderado = root.find('.//ns2:curpApoderadomandatario', namespaces)
            data['curp_apoderado'] = curp_apoderado.text if curp_apoderado is not None else None
            
            # RFC Agente Aduanal
            agente_aduanal = root.find('.//ns2:rfcAgenteAduanalSocFactura', namespaces)
            data['agente_aduanal'] = agente_aduanal.text if agente_aduanal is not None else None
            
            # Verificar que se extrajeron los datos esenciales
            if not any([data['numero_operacion'], data['pedimento'], data['curp_apoderado'], data['agente_aduanal']]):
                return {}
            
            return data
            
        except ET.ParseError as e:
            print(f"Error al parsear el XML: {e}")
            return {}
        except Exception as e:
            print(f"Error inesperado al extraer datos del XML: {e}")
            return {}

    def process_service(self, service: Dict[str, Any], sync_mode: bool = False) -> Dict[str, Any]:
        """
        Procesa un servicio individual.
        
        Args:
            service: Diccionario con información del servicio.
            sync_mode: Si es True, no usa threading.Lock para los prints.
            
        Returns:
            Diccionario con el resultado del procesamiento.
        """
        try:
            service_id = service['id']
            pedimento_id = service['pedimento']['id']
            pedimento_number = service['pedimento']['pedimento']
            
            # En modo síncrono no necesitamos lock
            if sync_mode:
                print(f"Iniciando procesamiento del servicio {service_id} - Pedimento {pedimento_number}")
            else:
                with self.lock:
                    print(f"Iniciando procesamiento del servicio {service_id} - Pedimento {pedimento_number}")
            
            # Obtener documentos
            # '6085d811-403b-404b-aabe-fe13a21f0dad'

            documents = self.api_controller.get_documents(document_type=2, pedimento=pedimento_id)
            if not documents or not documents.get('results'):
                message = f"No se encontraron documentos para el pedimento {pedimento_number}"
                if sync_mode:
                    print(message)
                else:
                    with self.lock:
                        print(message)
                return {
                    'service_id': service_id,
                    'status': 'error',
                    'message': 'No se encontraron documentos'
                }
            
            document_results = documents.get('results', [])[0]
            
            # Descargar documento
            pedimento_completo = self.api_controller.download_document(document_results['id'])
            print(pedimento_completo.content.decode('utf-8'))
            if not pedimento_completo:
                message = f"Error al descargar documento para el pedimento {pedimento_number}"
                if sync_mode:
                    print(message)
                else:
                    with self.lock:
                        print(message)
                return {
                    'service_id': service_id,
                    'status': 'error',
                    'message': 'Error al descargar documento'
                }
            
            # Extraer datos del XML
            data = self.extract_xml_data(pedimento_completo.content.decode('utf-8'))
            print(data)
            if not data:
                message = f"Error al extraer datos del XML para el pedimento {pedimento_number}"
                if sync_mode:
                    print(message)
                else:
                    with self.lock:
                        print(message)
                return {
                    'service_id': service_id,
                    'status': 'error',
                    'message': 'Error al extraer datos del XML'
                }
            
            # Preparar datos para actualización
            service_complete = {
                "estado": 3,
                "pedimento": pedimento_id
            }
            data['pedimento'] = pedimento_number
            
            # Actualizar pedimento y servicio
            print(data['numero_operacion'])
            response_put_pedimento = self.api_controller.put_pedimento(pedimento_id, data)
            response_put_pedimento_service = self.api_controller.put_pedimento_service(service_id, service_complete)
            
            if response_put_pedimento and response_put_pedimento_service:
                message = f"✓ Servicio {service_id} - Pedimento {pedimento_number} actualizado correctamente"
                if sync_mode:
                    print(message)
                else:
                    with self.lock:
                        print(message)
                return {
                    'service_id': service_id,
                    'status': 'success',
                    'message': 'Actualizado correctamente'
                }
            else:
                message = f"✗ Error al actualizar servicio {service_id} - Pedimento {pedimento_number}"
                if sync_mode:
                    print(message)
                else:
                    with self.lock:
                        print(message)
                return {
                    'service_id': service_id,
                    'status': 'error',
                    'message': 'Error al actualizar en la API'
                }
                
        except Exception as e:
            message = f"✗ Error procesando servicio {service.get('id', 'Unknown')}: {str(e)}"
            if sync_mode:
                print(message)
            else:
                with self.lock:
                    print(message)
            return {
                'service_id': service.get('id', 'Unknown'),
                'status': 'error',
                'message': f'Excepción: {str(e)}'
            }

    def run(self):
        """
        Método principal para ejecutar el script con procesamiento multihilo.
        """
        print(f"Iniciando procesamiento con {self.max_workers} hilos...")
        
        # Obtener servicios
        services = self.api_controller.get_pedimento_services(page=1, service_type=8)
        
        if not services:
            print("Error al obtener servicios de la API")
            return
            
        services_result = services.get('results', [])
        
        if not services_result:
            print("No se encontraron servicios para procesar")
            return
            
        print(f"Se encontraron {len(services_result)} servicios para procesar")
        
        # Procesamiento multihilo
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todos los trabajos al pool de hilos
            future_to_service = {
                executor.submit(self.process_service, service): service 
                for service in services_result
            }
            
            # Recoger resultados conforme se completan
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    with self.lock:
                        print(f'Servicio {service.get("id", "Unknown")} generó una excepción: {exc}')
                    results.append({
                        'service_id': service.get('id', 'Unknown'),
                        'status': 'error',
                        'message': f'Excepción en hilo: {str(exc)}'
                    })
        
        # Mostrar resumen final
        self.print_summary(results)
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """
        Imprime un resumen de los resultados del procesamiento.
        
        Args:
            results: Lista de resultados del procesamiento.
        """
        successful = [r for r in results if r['status'] == 'success']
        errors = [r for r in results if r['status'] == 'error']
        
        print("\n" + "="*60)
        print("RESUMEN DE PROCESAMIENTO")
        print("="*60)
        print(f"Total de servicios procesados: {len(results)}")
        print(f"Exitosos: {len(successful)}")
        print(f"Con errores: {len(errors)}")
        
        if errors:
            print("\nErrores encontrados:")
            for error in errors:
                print(f"  - Servicio {error['service_id']}: {error['message']}")
        
        print("="*60)
    
    def run_sync(self):
        """
        Método para ejecutar el script de manera síncrona (secuencial).
        Procesa un servicio a la vez sin multihilos.
        """
        print("Iniciando procesamiento síncrono (secuencial)...")
        
        # Obtener servicios
        services = self.api_controller.get_pedimento_services(page=1, service_type=8)
        
        if not services:
            print("Error al obtener servicios de la API")
            return
            
        services_result = services.get('results', [])
        
        if not services_result:
            print("No se encontraron servicios para procesar")
            return
            
        print(f"Se encontraron {len(services_result)} servicios para procesar")
        
        # Procesamiento secuencial
        results = []
        for i, service in enumerate(services_result, 1):
            print(f"Procesando servicio {i}/{len(services_result)}: {service['id']}")
            result = self.process_service(service, sync_mode=True)
            results.append(result)
        
        # Mostrar resumen final
        self.print_summary(results)
    
    def choose_execution_mode(self):
        """
        Permite al usuario elegir entre procesamiento síncrono o asíncrono.
        """
        print("\n" + "="*50)
        print("SELECCIONAR MODO DE PROCESAMIENTO")
        print("="*50)
        print("1. Procesamiento Multihilo (Asíncrono) - Más rápido")
        print("2. Procesamiento Secuencial (Síncrono) - Más seguro")
        print("="*50)
        
        while True:
            try:
                choice = input("Seleccione una opción (1 o 2): ").strip()
                if choice == "1":
                    print(f"\n🚀 Ejecutando en modo MULTIHILO con {self.max_workers} hilos...")
                    self.run()
                    break
                elif choice == "2":
                    print("\n🔄 Ejecutando en modo SECUENCIAL...")
                    self.run_sync()
                    break
                else:
                    print("❌ Opción inválida. Por favor, seleccione 1 o 2.")
            except KeyboardInterrupt:
                print("\n\n❌ Operación cancelada por el usuario.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    # ...existing code...
if __name__ == "__main__":
    # Configurar el número de hilos (ajusta según tu servidor y capacidad)
    max_workers = 5  # Puedes ajustar este número según tus necesidades
    
    main = Main(max_workers=max_workers)
    
    # Permitir al usuario elegir el modo de ejecución
    main.choose_execution_mode()
    
    # Alternativamente, puedes ejecutar directamente sin menú:
    # main.run()        # Para procesamiento multihilo (más rápido)
    # main.run_sync()   # Para procesamiento secuencial (más seguro/predecible)