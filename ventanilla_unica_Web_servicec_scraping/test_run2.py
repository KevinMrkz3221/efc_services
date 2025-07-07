#!/usr/bin/env python3
"""
Script simple para probar el método run2 de debugging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import MainProcess

def test_run2():
    """Prueba el método run2 para debugging"""
    print("=== TESTING MÉTODO run2 ===")
    
    try:
        # Crear instancia del proceso principal
        main_process = MainProcess()
        print("✅ MainProcess inicializado correctamente")
        
        # Ejecutar run2
        print("\n--- Ejecutando run2() ---")
        results = main_process.run2()
        
        print(f"\n=== RESULTADOS ===")
        if results:
            print(f"✅ Resultados obtenidos:")
            for key, value in results.items():
                print(f"  - {key}: {value}")
        else:
            print("❌ No se obtuvieron resultados")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_run2()
