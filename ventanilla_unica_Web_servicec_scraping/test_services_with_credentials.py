#!/usr/bin/env python3
"""
Script para verificar servicios disponibles filtrando por importadores con credenciales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.RESTController import APIController

def check_services_for_importador_with_credentials():
    """Verifica servicios para importadores que tienen credenciales"""
    print("=== VERIFICANDO SERVICIOS PARA IMPORTADORES CON CREDENCIALES ===")
    
    api_controller = APIController()
    
    # Lista de importadores que sabemos que tienen credenciales
    importadores_con_credenciales = ["MFN031210AT9"]
    
    print(f"\n--- Obteniendo servicios de la página 1 ---")
    services = api_controller.get_pedimento_services(page=1, service_type=3)
    
    if not services:
        print("❌ No se pudieron obtener servicios")
        return
    
    services_list = services.get('results', [])
    print(f"✅ {len(services_list)} servicios obtenidos")
    
    # Filtrar servicios por importadores con credenciales
    matching_services = []
    all_importadores = set()
    
    for service in services_list:
        importador = service.get('pedimento', {}).get('contribuyente')
        all_importadores.add(importador)
        
        if importador in importadores_con_credenciales:
            matching_services.append(service)
            print(f"✅ Servicio compatible encontrado:")
            print(f"   ID: {service.get('id')}")
            print(f"   Importador: {importador}")
            print(f"   Pedimento: {service.get('pedimento', {}).get('pedimento')}")
            print(f"   Aduana: {service.get('pedimento', {}).get('aduana')}")
            print(f"   Patente: {service.get('pedimento', {}).get('patente')}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Total servicios: {len(services_list)}")
    print(f"Servicios con credenciales disponibles: {len(matching_services)}")
    print(f"Importadores únicos encontrados: {len(all_importadores)}")
    print(f"Primeros 10 importadores: {list(all_importadores)[:10]}")
    
    return matching_services

def test_process_with_credentials():
    """Prueba procesar un servicio con credenciales disponibles"""
    matching_services = check_services_for_importador_with_credentials()
    
    if not matching_services:
        print("\n❌ No hay servicios con credenciales disponibles para procesar")
        return False
        
    print(f"\n=== PROBANDO PROCESAR UN SERVICIO CON CREDENCIALES ===")
    
    # Usar el primer servicio que tenga credenciales
    service = matching_services[0]
    print(f"Probando procesar servicio ID: {service.get('id')}")
    
    # Aquí podrías llamar al método del MainProcess para procesar este servicio específico
    # Para el ejemplo, solo mostramos que es posible
    print(f"✅ Servicio listo para procesamiento:")
    print(f"   - Importador: {service.get('pedimento', {}).get('contribuyente')}")
    print(f"   - Credenciales: Disponibles")
    
    return True

if __name__ == "__main__":
    test_process_with_credentials()
