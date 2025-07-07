#!/usr/bin/env python3
"""
Script para probar el main.py en modo debug específicamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno para debug
os.environ["DEBUG_MODE"] = "true"
os.environ["DEBUG_SINGLE_THREAD"] = "true"
os.environ["DEBUG_VERBOSE"] = "true"
os.environ["DEBUG_SAVE_RESPONSES"] = "true"

from main import MainProcess
from config.settings import SETTINGS

def test_main_debug():
    """Prueba el main.py en modo debug"""
    print("=== TESTING MAIN.PY EN MODO DEBUG ===")
    
    print(f"Configuración actual:")
    print(f"  - DEBUG_MODE: {SETTINGS.DEBUG_MODE}")
    print(f"  - DEBUG_SINGLE_THREAD: {SETTINGS.DEBUG_SINGLE_THREAD}")
    print(f"  - DEFAULT_START_PAGE: {SETTINGS.DEFAULT_START_PAGE}")
    print(f"  - DEFAULT_SERVICE_TYPE: {SETTINGS.DEFAULT_SERVICE_TYPE}")
    
    try:
        # Crear instancia del proceso principal
        main_process = MainProcess()
        print("✅ MainProcess inicializado correctamente")
        
        # Ejecutar en modo debug
        print("\n--- Ejecutando run() con debug_mode=True ---")
        results = main_process.run(
            start_page=1,
            end_page=1,  # Solo una página para debug
            service_type=3,
            max_workers=1,
            debug_mode=True
        )
        
        print(f"\n=== RESULTADOS ===")
        if results:
            print(f"✅ Resultados obtenidos:")
            for key, value in results.items():
                if key != 'debug_info':  # No mostrar debug_info completo
                    print(f"  - {key}: {value}")
            
            if 'debug_info' in results:
                print(f"  - debug_info: {len(results['debug_info'])} elementos")
        else:
            print("❌ No se obtuvieron resultados")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_direct_debug_method():
    """Prueba directamente el método debug_single_process"""
    print("\n=== TESTING debug_single_process DIRECTAMENTE ===")
    
    try:
        main_process = MainProcess()
        
        print("Ejecutando debug_single_process...")
        results = main_process.debug_single_process(
            page=1,
            service_type=3,
            limit_services=2  # Solo 2 servicios para test
        )
        
        print(f"\n=== RESULTADOS DIRECTOS ===")
        if results:
            print(f"✅ Resultados:")
            for key, value in results.items():
                if key != 'debug_info':
                    print(f"  - {key}: {value}")
        else:
            print("❌ No se obtuvieron resultados")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_api_controller_directly():
    """Prueba el API controller directamente"""
    print("\n=== TESTING APIController DIRECTAMENTE ===")
    
    try:
        main_process = MainProcess()
        api_controller = main_process.api_controller
        
        print("Obteniendo servicios directamente...")
        services = api_controller.get_pedimento_services(page=1, service_type=3)
        
        if services:
            print(f"✅ Servicios obtenidos:")
            print(f"  - Tipo: {type(services)}")
            print(f"  - Claves: {list(services.keys()) if isinstance(services, dict) else 'No es dict'}")
            
            if isinstance(services, dict) and 'results' in services:
                results_list = services['results']
                print(f"  - Cantidad de servicios: {len(results_list)}")
                
                if len(results_list) > 0:
                    print(f"  - Primer servicio: {results_list[0].get('id', 'Sin ID')}")
            else:
                print(f"  - Contenido completo: {services}")
        else:
            print("❌ No se obtuvieron servicios")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Iniciando testing completo del main.py...")
    
    # 1. Probar API controller directamente
    test_api_controller_directly()
    
    # 2. Probar método debug directamente
    test_direct_debug_method()
    
    # 3. Probar main completo
    test_main_debug()
    
    print("\n=== FIN DEL TESTING ===")
