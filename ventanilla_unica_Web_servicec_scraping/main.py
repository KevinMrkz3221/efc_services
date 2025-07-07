from dataclasses import dataclass
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from controllers.RESTController import APIController
from controllers.SOAPService import SOAPController
from payload_structure.template_manager import SOAPTemplateManager
from payload_structure.credentials_manager import CredentialsManager
from config.settings import SETTINGS  # Import SETTINGS

from payload_structure.soap_models import (
    CredencialesSOAP, 
    CredencialesVUCEM,
    ConsultaEstadoPedimento,
    ConsultaPedimentoCompleto,
    ConsultaPartida,
    ConsultaAcuses,
    ConsultaRemesas
)

@dataclass
class MainProcess:
    """
    Clase principal que inicia el proceso de scraping.
    """
    api_controller: APIController = APIController()
    soap_controller: SOAPController = SOAPController()
    template_manager: SOAPTemplateManager = SOAPTemplateManager()
    credentials_manager: CredentialsManager = None
    
    def __post_init__(self):
        """
        Método que se ejecuta después de la inicialización de la clase.
        Aquí puedes agregar cualquier configuración adicional necesaria.
        """
        print("Inicializando el proceso de scraping...")
        
        # Inicializar el gestor de credenciales
        self.credentials_manager = CredentialsManager(self.api_controller)

        #self.pedimentos = APIController.get_pedimentos()
    
    def consultar_estado_pedimento(self, importador: str, numero_operacion: str, 
                                   aduana: str, patente: str, pedimento: str):
        """
        Consulta el estado de un pedimento específico
        
        Args:
            importador: Usuario del importador para obtener credenciales
            numero_operacion: Número de operación del pedimento
            aduana: Código de aduana
            patente: Número de patente
            pedimento: Número de pedimento
        """
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.ventanillaunica.gob.mx/pedimentos/ws/oxml/consultarpedimentocompleto/consultarPedimentoCompleto'
        }
        
        # Obtener credenciales dinámicamente
        credenciales = self.credentials_manager.get_soap_credentials(importador)
        if not credenciales:
            print(f"No se pudieron obtener credenciales para el importador: {importador}")
            return None
        
        # Crear objeto de consulta
        consulta = ConsultaEstadoPedimento(
            numero_operacion=numero_operacion,
            aduana=aduana,
            patente=patente, 
            pedimento=pedimento
        )
        
        # Generar XML usando el template manager
        _data = self.template_manager.generar_consulta_estado_pedimento(
            credenciales=credenciales,
            consulta=consulta
        )
        
        pedimento_result = self.soap_controller.make_request(
            "ventanilla-ws-pedimentos/ConsultarEstadoPedimentosService?wsdl",
            data=_data,
            headers=headers
        )

        if pedimento_result:
            # Verificar si la respuesta contiene error
            if self._has_soap_error(pedimento_result):
                print(f"Respuesta SOAP contiene error para estado de pedimento {pedimento}, descartando...")
                return None
            print(f"Estado del pedimento obtenido: {pedimento_result.content}")
            return pedimento_result
        else:
            print("Error al consultar estado del pedimento")
            return None
    # Funcion deprecada, se recomienda usar get_pedimento_completo
    def listar_pedimentos(self):
        """Lista pedimentos disponibles (implementación pendiente)"""
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.ventanillaunica.gob.mx/pedimentos/ws/oxml/consultarpedimentocompleto/consultarPedimentoCompleto'
        }
        
        # Nota: Este método requiere implementación específica del XML
        # según la documentación del servicio
        # Nota: Ya no funciona endpoint 'ventanilla-ws-pedimentos/ListarPedimentosService?wsdl'

        _data = """"""
        
        pedimentos = self.soap_controller.make_request(
            endpoint='ventanilla-ws-pedimentos/ListarPedimentosService?wsdl',
            data=_data,
            headers=headers
        )
        
        if pedimentos:
            print(f"Pedimentos listados: {pedimentos.content}")
        else:
            print("Error al listar pedimentos")
    
    def get_pedimento_completo(self, importador: str, aduana: str, patente: str, pedimento: str):
        """
        Obtiene la información completa de un pedimento
        
        Args:
            importador: Usuario del importador para obtener credenciales
            aduana: Código de aduana
            patente: Número de patente
            pedimento: Número de pedimento
        """
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
        }
        
        # Obtener credenciales dinámicamente
        credenciales = self.credentials_manager.get_soap_credentials(importador)
        if not credenciales:
            print(f"No se pudieron obtener credenciales para el importador: {importador}")
            return None
        
        # Crear objeto de consulta
        consulta = ConsultaPedimentoCompleto(
            aduana=aduana,
            patente=patente,
            pedimento=pedimento
        )
        
        # Generar XML usando el template manager
        _data = self.template_manager.generar_consulta_pedimento_completo(
            credenciales=credenciales,
            consulta=consulta
        )

        
        pedimento_response = self.soap_controller.make_request(
            endpoint='ventanilla-ws-pedimentos/ConsultarPedimentoCompletoService?wsdl',
            data=_data,
            headers=headers
        )

        
        if pedimento_response:
            # Verificar si la respuesta contiene error
            if self._has_soap_error(pedimento_response):
                print(f"Respuesta SOAP contiene error para pedimento {pedimento}, descartando...")
                return None
            return pedimento_response
        else:
            return None
    
    def consultar_partidas(self, importador: str, aduana: str, patente: str, 
                          pedimento: str, numero_operacion: str, numero_partida: str):
        """
        Consulta partidas específicas de un pedimento
        
        Args:
            importador: Usuario del importador para obtener credenciales
            aduana: Código de aduana
            patente: Número de patente
            pedimento: Número de pedimento
            numero_operacion: Número de operación
            numero_partida: Número de partida
        """
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
        }
        
        # Obtener credenciales dinámicamente
        credenciales = self.credentials_manager.get_soap_credentials(importador)
        if not credenciales:
            print(f"No se pudieron obtener credenciales para el importador: {importador}")
            return None
        
        # Crear objeto de consulta
        consulta = ConsultaPartida(
            aduana=aduana,
            patente=patente,
            pedimento=pedimento,
            numero_operacion=numero_operacion,
            numero_partida=numero_partida
        )
        
        # Generar XML usando el template manager
        _data = self.template_manager.generar_consulta_partida(
            credenciales=credenciales,
            consulta=consulta
        )

        response = self.soap_controller.make_request(
            endpoint='/ventanilla-ws-pedimentos/ConsultarPartidaService?wsdl',
            data=_data,
            headers=headers
        )

        if response:
            # Verificar si la respuesta contiene error
            if self._has_soap_error(response):
                print(f"Respuesta SOAP contiene error para partidas del pedimento {pedimento}, descartando...")
                return None
            print(f"Partidas obtenidas: {response.content}")
            return response
        else:
            print("Error al consultar partidas")
            return None
    
    def consultar_remesas(self, importador: str, aduana: str, patente: str, pedimento: str):
        """
        Consulta remesas de un pedimento
        
        Args:
            importador: Usuario del importador para obtener credenciales
            aduana: Código de aduana
            patente: Número de patente
            pedimento: Número de pedimento
        """
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
        }
        
        # Obtener credenciales dinámicamente
        credenciales = self.credentials_manager.get_soap_credentials(importador)
        if not credenciales:
            print(f"No se pudieron obtener credenciales para el importador: {importador}")
            return None
        
        # Crear objeto de consulta
        consulta = ConsultaRemesas(
            aduana=aduana,
            patente=patente, 
            pedimento=pedimento
        )
        
        # Generar XML usando el template manager
        _data = self.template_manager.generar_consulta_remesas(
            credenciales=credenciales,
            consulta=consulta
        )
        
        remesas = self.soap_controller.make_request(
            endpoint='ventanilla-ws-pedimentos/ConsultarRemesasService?wsdl',
            data=_data,
            headers=headers
        )
        
        if remesas:
            # Verificar si la respuesta contiene error
            if self._has_soap_error(remesas):
                print(f"Respuesta SOAP contiene error para remesas del pedimento {pedimento}, descartando...")
                return None
            print(f"Remesas obtenidas: {remesas.content}")
            return remesas
        else:
            print("Error al consultar remesas")
            return None
    
    def get_acuses(self, importador: str, id_edocument: str):
        """
        Obtiene acuses de documentos electrónicos
        
        Args:
            importador: Usuario del importador para obtener credenciales
            id_edocument: ID del documento electrónico
        """
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.ventanillaunica.gob.mx/ventanilla/ConsultaAcusesService/consultarAcuseCove',
            'Accept-Encoding': 'gzip, deflate'
        }

        # Obtener credenciales dinámicamente
        credenciales = self.credentials_manager.get_soap_credentials(importador)
        if not credenciales:
            print(f"No se pudieron obtener credenciales para el importador: {importador}")
            return None
        
        # Verificar si el usuario tiene permisos para acuses
        vucem_creds = self.credentials_manager.get_credentials_by_user(importador)
        if vucem_creds and not vucem_creds.acusecove:
            print(f"El usuario {importador} no tiene permisos para consultar acuses COVE")
            return None

        # Crear objeto de consulta
        consulta = ConsultaAcuses(
            id_edocument=id_edocument
        )
        
        # Generar XML usando el template manager
        _data = self.template_manager.generar_consulta_acuses(
            credenciales=credenciales,
            consulta=consulta
        )

        response = self.soap_controller.make_request(
            endpoint='ventanilla-acuses-HA/ConsultaAcusesServiceWS?wsdl',
            data=_data,
            headers=headers
        )

        if response:
            # Verificar si la respuesta contiene error
            if self._has_soap_error(response):
                print(f"Respuesta SOAP contiene error para acuses del documento {id_edocument}, descartando...")
                return None
            print(f"Acuse obtenido: {response.content}")
            return response
        else:
            print("Error al obtener acuses")
            return None
    
    def run_services(self):
        """
        Método para iniciar los servicios necesarios.
        Aquí puedes agregar la lógica para iniciar los servicios que necesites.
        """
        print("Iniciando servicios...")
        # Ejemplo: iniciar el servicio SOAP
    
    def process_pedimento_services_single_page(self, page=1, service_type=3):
        """
        Procesa servicios de pedimentos de una página específica
        
        Args:
            page: Número de página a procesar
            service_type: Tipo de servicio (default 3)
        
        Returns:
            Dict con resultados del procesamiento de la página
        """
        thread_id = threading.current_thread().name
        print(f"[{thread_id}] Procesando página {page} con service_type={service_type}")
        
        results = {
            'page': page,
            'thread_id': thread_id,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Pequeña pausa para evitar sobrecarga del servidor
            time.sleep(SETTINGS.REQUEST_DELAY_SECONDS)
            
            # Obtener servicios de pedimentos desde la API para esta página
            services = self.api_controller.get_pedimento_services(page=page, service_type=service_type)
            services_list = services.get('results', []) if services else []

            if not services:
                print(f"[{thread_id}] No se pudieron obtener servicios para página {page}")
                results['errors'].append(f"No se pudieron obtener servicios para página {page}")
                return results
            
            if not services_list:
                print(f"[{thread_id}] No hay servicios en página {page}")
                return results
            
            print(f"[{thread_id}] Procesando {len(services_list)} servicios en página {page}")
            
            # Procesar cada servicio de esta página
            for service in services_list:
                results['processed'] += 1
                
                try:
                    importador = service.get('pedimento', {}).get('contribuyente')
                    aduana = service.get('pedimento', {}).get('aduana')
                    patente = service.get('pedimento', {}).get('patente')
                    pedimento = service.get('pedimento', {}).get('pedimento')
                    service_id = service.get('id')
                    
                    if not all([importador, aduana, patente, pedimento, service_id]):
                        error_msg = f"Datos incompletos en servicio {service_id}: importador={importador}, aduana={aduana}, patente={patente}, pedimento={pedimento}"
                        print(f"[{thread_id}] {error_msg}")
                        results['errors'].append(error_msg)
                        results['failed'] += 1
                        continue
                    
                    print(f"[{thread_id}] Procesando pedimento {pedimento} (servicio {service_id})")
                    
                    # Intentar obtener el pedimento completo con reintentos
                    soap_result = None
                    for attempt in range(SETTINGS.MAX_RETRIES):
                        try:
                            # Pequeña pausa entre intentos
                            if attempt > 0:
                                time.sleep(SETTINGS.REQUEST_DELAY_SECONDS * (attempt + 1))
                                print(f"[{thread_id}] Reintento {attempt + 1}/{SETTINGS.MAX_RETRIES} para pedimento {pedimento}")
                            
                            soap_result = self.get_pedimento_completo(
                                importador=importador,
                                aduana=aduana,
                                patente=patente,
                                pedimento=pedimento
                            )
                            
                            if soap_result:
                                break  # Éxito, salir del loop de reintentos
                                
                        except IndexError as e:
                            error_msg = f"Error de índice de lista en intento {attempt + 1} para pedimento {pedimento}: {str(e)}"
                            print(f"[{thread_id}] {error_msg}")
                            # Para IndexError, no reintentar ya que es un problema de datos
                            results['errors'].append(f"Error de credenciales para pedimento {pedimento}: {str(e)}")
                            break
                        except Exception as e:
                            print(f"[{thread_id}] Error en intento {attempt + 1} para pedimento {pedimento}: {str(e)}")
                            if attempt == SETTINGS.MAX_RETRIES - 1:  # Último intento
                                results['errors'].append(f"Error después de {SETTINGS.MAX_RETRIES} intentos para pedimento {pedimento}: {str(e)}")
                    
                    if soap_result:
                        # Enviar respuesta SOAP como documento
                        doc_result = self.api_controller.post_document(
                            soap_response=soap_result, 
                            organizacion=services.get('organizacion', ''), 
                            pedimento=service.get('pedimento', {}).get('id'), 
                            file_name=f"pedimento_completo_{pedimento}.xml"
                        )
                        
                        if doc_result:
                            print(f"[{thread_id}] Pedimento completo XML {pedimento} enviado exitosamente")
                            
                            # Actualizar estado a exitoso (3)
                            update_result = self.api_controller.put_pedimento_service(
                                service_id=service_id,
                                data={
                                    "estado": 3,
                                    "pedimento": service.get('pedimento', {}).get('id'),
                                    "tipo_procesamiento": 2,
                                    "servicio": 8
                                }
                            )
                            self.api_controller.post_pedimento_service(
                                data={
                                    "estado": 1,
                                    "pedimento": service.get('pedimento', {}).get('id'),
                                    "tipo_procesamiento": 2,
                                    "servicio": 8
                                }
                            )
                                
                            
                            
                            if update_result:
                                results['successful'] += 1
                                print(f"[{thread_id}] Estado actualizado a exitoso para servicio {service_id}")
                            else:
                                results['errors'].append(f"Error actualizando estado exitoso para servicio {service_id}")
                        else:
                            results['errors'].append(f"Error enviando documento para pedimento {pedimento}")
                            results['failed'] += 1
                    else:
                        print(f"[{thread_id}] Error obteniendo pedimento completo {pedimento} después de {SETTINGS.MAX_RETRIES} intentos")
                        
                        # Actualizar estado a fallido (2)
                        self.api_controller.put_pedimento_service(
                            service_id=service_id,
                            data={
                                "estado": 2,
                                "pedimento": service.get('pedimento', {}).get('id')
                            }
                        )
                        results['failed'] += 1
                        
                    # Pausa entre servicios para no sobrecargar
                    time.sleep(SETTINGS.REQUEST_DELAY_SECONDS)
                        
                except Exception as e:
                    error_msg = f"Error procesando servicio {service.get('id', 'unknown')}: {str(e)}"
                    print(f"[{thread_id}] {error_msg}")
                    results['errors'].append(error_msg)
                    results['failed'] += 1
                    continue
            
            print(f"[{thread_id}] Página {page} completada: {results['successful']} exitosos, {results['failed']} fallidos")
            return results
            
        except Exception as e:
            error_msg = f"Error general en página {page}: {str(e)}"
            print(f"[{thread_id}] {error_msg}")
            results['errors'].append(error_msg)
            return results

    def process_pedimento_services(self, start_page=1, end_page=5, service_type=3, max_workers=3):
        """
        Procesa servicios de pedimentos usando múltiples hilos para diferentes páginas
        
        Args:
            start_page: Página inicial (default 1)
            end_page: Página final (default 5)
            service_type: Tipo de servicio (default 3)
            max_workers: Número máximo de hilos concurrentes (default 3)
        """
        print("=== Iniciando procesamiento multihilo de servicios de pedimentos ===")
        print(f"Páginas: {start_page} a {end_page}, Tipo de servicio: {service_type}, Hilos: {max_workers}")
        
        start_time = time.time()
        all_results = []
        total_processed = 0
        total_successful = 0
        total_failed = 0
        all_errors = []
        
        # Crear pool de hilos
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="PedimentoWorker") as executor:
            # Enviar tareas para cada página
            future_to_page = {
                executor.submit(self.process_pedimento_services_single_page, page, service_type): page 
                for page in range(start_page, end_page + 1)
            }
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    # Agregar estadísticas
                    total_processed += result['processed']
                    total_successful += result['successful']
                    total_failed += result['failed']
                    all_errors.extend(result['errors'])
                    
                    print(f"✓ Página {page} completada por {result['thread_id']}: "
                          f"{result['successful']}/{result['processed']} exitosos")
                    
                except Exception as e:
                    error_msg = f"Error en hilo procesando página {page}: {str(e)}"
                    print(f"✗ {error_msg}")
                    all_errors.append(error_msg)
        
        # Mostrar resumen final
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("RESUMEN DEL PROCESAMIENTO MULTIHILO")
        print("="*60)
        print(f"Tiempo total: {duration:.2f} segundos")
        print(f"Páginas procesadas: {len(all_results)}")
        print(f"Total servicios procesados: {total_processed}")
        print(f"Total servicios exitosos: {total_successful}")
        print(f"Total servicios fallidos: {total_failed}")
        print(f"Tasa de éxito: {(total_successful/total_processed*100):.1f}%" if total_processed > 0 else "N/A")
        
        if all_errors:
            print(f"\nErrores encontrados ({len(all_errors)}):")
            for i, error in enumerate(all_errors[:10], 1):  # Mostrar solo los primeros 10 errores
                print(f"  {i}. {error}")
            if len(all_errors) > 10:
                print(f"  ... y {len(all_errors) - 10} errores más")
        
        print("="*60)
        
        return {
            'duration': duration,
            'pages_processed': len(all_results),
            'total_processed': total_processed,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'success_rate': (total_successful/total_processed*100) if total_processed > 0 else 0,
            'errors': all_errors,
            'detailed_results': all_results
        }
        
    def test_multithreading(self, max_workers=2):
        """
        Método de prueba para verificar que el multithreading funciona correctamente
        Procesa solo las primeras 2 páginas como test
        """
        print("=== MODO PRUEBA: Verificando multithreading ===")
        return self.process_pedimento_services(
            start_page=1,
            end_page=2,
            service_type=3,
            max_workers=max_workers
        )

    def run_example_queries(self):
        # """
        # Ejecuta consultas de ejemplo usando credenciales dinámicas
        # """
        # print("=== Ejecutando consultas de ejemplo ===")
        
        # # # Ejemplo 1: Consultar estado de pedimento
        # print("\n1. Consultando estado de pedimento...")
        # self.consultar_estado_pedimento(
        #     importador="MABL620809BY7",
        #     numero_operacion="6739066752",
        #     aduana="070",
        #     patente="3842",
        #     pedimento="5007760"
        # )
        
        # # Ejemplo 2: Obtener pedimento completo
        # print("\n2. Obteniendo pedimento completo...")
        # self.get_pedimento_completo(
        #     importador="MFN031210AT9",
        #     aduana="07",
        #     patente="1800",
        #     pedimento="1005033"
        # )
        
        # # Ejemplo 3: Consultar partidas
        # print("\n3. Consultando partidas...")
        # self.consultar_partidas(
        #     importador="MFN031210AT9",
        #     aduana="240",
        #     patente="3452",
        #     pedimento="4007188",
        #     numero_operacion="20181397545",
        #     numero_partida="16"
        # )
        
        # # # Ejemplo 4: Consultar acuses
        # print("\n4. Consultando acuses...")
        # self.get_acuses(
        #     importador="MFN031210AT9",
        #     id_edocument="COVE2474LMA64"
        # )
        pass
        
    def run(self, start_page=None, end_page=None, service_type=None, max_workers=None):
        """
        Método para iniciar el proceso de scraping con credenciales dinámicas y multithreading.
        
        Args:
            start_page: Página inicial a procesar (default desde configuración)
            end_page: Página final a procesar (default desde configuración)
            service_type: Tipo de servicio a procesar (default desde configuración)
            max_workers: Número máximo de hilos concurrentes (default desde configuración)
        """
        # Usar valores de configuración si no se especifican
        start_page = start_page or SETTINGS.DEFAULT_START_PAGE
        end_page = end_page or SETTINGS.DEFAULT_END_PAGE
        service_type = service_type or SETTINGS.DEFAULT_SERVICE_TYPE
        max_workers = max_workers or SETTINGS.DEFAULT_MAX_WORKERS
        
        print("Iniciando el proceso de scraping multihilo con credenciales dinámicas...")
        print(f"Configuración: Páginas {start_page}-{end_page}, Tipo servicio: {service_type}, Hilos: {max_workers}")
        print(f"Rate limiting: {SETTINGS.REQUEST_DELAY_SECONDS}s entre requests, {SETTINGS.MAX_RETRIES} reintentos máximo")
        
        # Procesar servicios de pedimentos con multithreading
        results = self.process_pedimento_services(
            start_page=start_page,
            end_page=end_page, 
            service_type=service_type,
            max_workers=max_workers
        )
        
        print("\nProceso de scraping completado.")
        return results
    
    def run2(self):
        thread_id = 1
        page = 2  # Cambiar a página 2 que SÍ tiene servicios con credenciales
        service_type = 3  # Definir service_type para debugging
        
        print(f"[{thread_id}] Procesando página {page} con service_type={service_type}")
        print(f"[{thread_id}] NOTA: Usando página 2 porque tiene servicios con credenciales disponibles")
        
        results = {
            'page': page,
            'thread_id': thread_id,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Pequeña pausa para evitar sobrecarga del servidor
            time.sleep(SETTINGS.REQUEST_DELAY_SECONDS)
            
            # Obtener servicios de pedimentos desde la API para esta página
            services = self.api_controller.get_pedimento_services(page=page, service_type=service_type)
            services_list = services.get('results', []) if services else []

            if not services:
                print(f"[{thread_id}] No se pudieron obtener servicios para página {page}")
                results['errors'].append(f"No se pudieron obtener servicios para página {page}")
                return results
            
            if not services_list:
                print(f"[{thread_id}] No hay servicios en página {page}")
                return results
            
            print(f"[{thread_id}] Procesando {len(services_list)} servicios en página {page}")
            
            # Procesar cada servicio de esta página
            for service in services_list:
                results['processed'] += 1
                
                try:
                    importador = service.get('pedimento', {}).get('contribuyente')
                    aduana = service.get('pedimento', {}).get('aduana')
                    patente = service.get('pedimento', {}).get('patente')
                    pedimento = service.get('pedimento', {}).get('pedimento')
                    service_id = service.get('id')
                    
                    if not all([importador, aduana, patente, pedimento, service_id]):
                        error_msg = f"Datos incompletos en servicio {service_id}: importador={importador}, aduana={aduana}, patente={patente}, pedimento={pedimento}"
                        print(f"[{thread_id}] {error_msg}")
                        results['errors'].append(error_msg)
                        results['failed'] += 1
                        continue
                    
                    print(f"[{thread_id}] Procesando pedimento {pedimento} (servicio {service_id})")
                    
                    # Intentar obtener el pedimento completo con reintentos
                    soap_result = None
                    for attempt in range(SETTINGS.MAX_RETRIES):
                        try:
                            # Pequeña pausa entre intentos
                            if attempt > 0:
                                time.sleep(SETTINGS.REQUEST_DELAY_SECONDS * (attempt + 1))
                                print(f"[{thread_id}] Reintento {attempt + 1}/{SETTINGS.MAX_RETRIES} para pedimento {pedimento}")
                            
                            soap_result = self.get_pedimento_completo(
                                importador=importador,
                                aduana=aduana,
                                patente=patente,
                                pedimento=pedimento
                            )
                            
                            if soap_result:
                                break  # Éxito, salir del loop de reintentos
                                
                        except IndexError as e:
                            error_msg = f"Error de índice de lista en intento {attempt + 1} para pedimento {pedimento}: {str(e)}"
                            print(f"[{thread_id}] {error_msg}")
                            # Para IndexError, no reintentar ya que es un problema de datos
                            results['errors'].append(f"Error de credenciales para pedimento {pedimento}: {str(e)}")
                            break
                        except Exception as e:
                            print(f"[{thread_id}] Error en intento {attempt + 1} para pedimento {pedimento}: {str(e)}")
                            if attempt == SETTINGS.MAX_RETRIES - 1:  # Último intento
                                results['errors'].append(f"Error después de {SETTINGS.MAX_RETRIES} intentos para pedimento {pedimento}: {str(e)}")
                    
                    if soap_result:
                        # Enviar respuesta SOAP como documento
                        doc_result = self.api_controller.post_document(
                            soap_response=soap_result, 
                            organizacion=services.get('organizacion', ''), 
                            pedimento=service.get('pedimento', {}).get('id'), 
                            file_name=f"pedimento_completo_{pedimento}.xml"
                        )
                        
                        if doc_result:
                            print(f"[{thread_id}] Pedimento completo XML {pedimento} enviado exitosamente")
                            
                            # Actualizar estado a exitoso (3)
                            update_result = self.api_controller.put_pedimento_service(
                                service_id=service_id,
                                data={
                                    "estado": 3,
                                    "pedimento": service.get('pedimento', {}).get('id'),
                                    "tipo_procesamiento": 2,
                                    "servicio": 8
                                }
                            )
                                
                            
                            
                            if update_result:
                                results['successful'] += 1
                                print(f"[{thread_id}] Estado actualizado a exitoso para servicio {service_id}")
                            else:
                                results['errors'].append(f"Error actualizando estado exitoso para servicio {service_id}")
                        else:
                            results['errors'].append(f"Error enviando documento para pedimento {pedimento}")
                            results['failed'] += 1
                    else:
                        print(f"[{thread_id}] Error obteniendo pedimento completo {pedimento} después de {SETTINGS.MAX_RETRIES} intentos")
                        
                        # Actualizar estado a fallido (2)
                        self.api_controller.put_pedimento_service(
                            service_id=service_id,
                            data={
                                "estado": 2,
                                "pedimento": service.get('pedimento', {}).get('id')
                            }
                        )
                        results['failed'] += 1
                        
                    # Pausa entre servicios para no sobrecargar
                    time.sleep(SETTINGS.REQUEST_DELAY_SECONDS)
                        
                except Exception as e:
                    error_msg = f"Error procesando servicio {service.get('id', 'unknown')}: {str(e)}"
                    print(f"[{thread_id}] {error_msg}")
                    results['errors'].append(error_msg)
                    results['failed'] += 1
                    continue
            
            print(f"[{thread_id}] Página {page} completada: {results['successful']} exitosos, {results['failed']} fallidos")
            return results
            
        except Exception as e:
            error_msg = f"Error general en página {page}: {str(e)}"
            print(f"[{thread_id}] {error_msg}")
            results['errors'].append(error_msg)
            return results

    def _has_soap_error(self, soap_response):
        """
        Verifica si la respuesta SOAP contiene un error
        
        Args:
            soap_response: Respuesta del servicio SOAP
            
        Returns:
            bool: True si contiene error, False en caso contrario
        """
        try:
            # Verificar si la respuesta tiene contenido
            if not soap_response or not hasattr(soap_response, 'content'):
                return False
                
            # Obtener el contenido XML como string
            xml_content = soap_response.content
            if isinstance(xml_content, bytes):
                xml_content = xml_content.decode('utf-8')
            
            # Buscar el patrón de error en el XML
            if '<ns3:tieneError>true</ns3:tieneError>' in xml_content:
                return True
                
            # También verificar otras posibles variaciones del namespace
            error_patterns = [
                '<tieneError>true</tieneError>',
                ':tieneError>true</',
                'tieneError="true"'
            ]
            
            for pattern in error_patterns:
                if pattern in xml_content:
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error verificando respuesta SOAP: {str(e)}")
            # En caso de error de parsing, asumir que no hay error para continuar
            return False
    
    def test_soap_error_detection(self):
        """
        Método de prueba para verificar la detección de errores SOAP
        """
        print("=== PRUEBA: Detección de errores SOAP ===")
        
        # Crear una respuesta mock con error
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        # Caso 1: Respuesta con error
        error_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <ns3:response xmlns:ns3="http://example.com">
                    <ns3:tieneError>true</ns3:tieneError>
                    <ns3:mensaje>Error en la consulta</ns3:mensaje>
                </ns3:response>
            </soap:Body>
        </soap:Envelope>"""
        
        mock_response_error = MockResponse(error_xml)
        
        # Caso 2: Respuesta exitosa
        success_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <ns3:response xmlns:ns3="http://example.com">
                    <ns3:tieneError>false</ns3:tieneError>
                    <ns3:datos>Información del pedimento</ns3:datos>
                </ns3:response>
            </soap:Body>
        </soap:Envelope>"""
        
        mock_response_success = MockResponse(success_xml)
        
        # Probar detección
        error_detected = self._has_soap_error(mock_response_error)
        success_detected = self._has_soap_error(mock_response_success)
        
        print(f"Respuesta con error detectado: {error_detected}")  # Debería ser True
        print(f"Respuesta exitosa detectada como error: {success_detected}")  # Debería ser False
        
        if error_detected and not success_detected:
            print("✓ Detección de errores SOAP funciona correctamente")
            return True
        else:
            print("✗ Error en la detección de errores SOAP")
            return False
# main
    


if __name__ == "__main__":
    import sys
    import argparse

    # Usar argparse para manejar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Procesador de servicios de pedimentos (scraping multihilo)")
    parser.add_argument("--start_page", '-sp',type=int, default=SETTINGS.DEFAULT_START_PAGE, help="Página inicial a procesar")
    parser.add_argument("--end_page", '-ep',type=int, default=SETTINGS.DEFAULT_END_PAGE, help="Página final a procesar")
    parser.add_argument("--service_type", '-st',type=int, default=SETTINGS.DEFAULT_SERVICE_TYPE, help="Tipo de servicio a procesar")
    parser.add_argument("--max_workers", '-mw',type=int, default=SETTINGS.DEFAULT_MAX_WORKERS, help="Número máximo de hilos concurrentes")
    parser.add_argument(
        "--list_service_types",
        action="store_true",
        help="Muestra los tipos de service_type disponibles y su descripción"
    )

    SERVICE_TYPE_DESCRIPTIONS = {
        1: "Consulta Estado Pedimento",
        2: "Consulta Partidas",
        3: "Consulta Pedimento Completo",
        4: "Consulta Remesas",
        5: "Consulta Acuses"
    }

    if "--list_service_types" in sys.argv:
        print("\nTipos de service_type disponibles:")
        for k, v in SERVICE_TYPE_DESCRIPTIONS.items():
            print(f"  {k}: {v}")
        sys.exit(0)
    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page
    service_type = args.service_type
    max_workers = args.max_workers

    print(f"Configuración por defecto: páginas {start_page}-{end_page}, service_type={service_type}, max_workers={max_workers}")

    # Validar argumentos de argparse
    if args.start_page < 1:
        print(f"Advertencia: start_page inválido ({args.start_page}), usando default: {SETTINGS.DEFAULT_START_PAGE}")
        start_page = SETTINGS.DEFAULT_START_PAGE
    if args.end_page < start_page:
        print(f"Advertencia: end_page ({args.end_page}) menor que start_page ({start_page}), usando default: {SETTINGS.DEFAULT_END_PAGE}")
        end_page = SETTINGS.DEFAULT_END_PAGE
    if args.service_type not in SERVICE_TYPE_DESCRIPTIONS:
        print(f"Advertencia: service_type inválido ({args.service_type}), usando default: {SETTINGS.DEFAULT_SERVICE_TYPE}")
        service_type = SETTINGS.DEFAULT_SERVICE_TYPE
    if args.max_workers < 1:
        print(f"Advertencia: max_workers inválido ({args.max_workers}), usando default: {SETTINGS.DEFAULT_MAX_WORKERS}")
        max_workers = SETTINGS.DEFAULT_MAX_WORKERS

    # Mostrar instrucciones de uso si no hay argumentos
    if len(sys.argv) == 1:
        print("\nUso:")
        print("  python main.py --start_page 1 --end_page 5 --service_type 3 --max_workers 3")
        print("  O usar variables de entorno: DEFAULT_START_PAGE, DEFAULT_END_PAGE, DEFAULT_SERVICE_TYPE, DEFAULT_MAX_WORKERS")
    
    main_process = MainProcess()
    final_results = main_process.run(
        start_page=start_page, 
        end_page=end_page, 
        service_type=service_type, 
        max_workers=max_workers
    )
