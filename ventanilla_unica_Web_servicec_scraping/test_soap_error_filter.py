#!/usr/bin/env python3
"""
Script de prueba para verificar el filtro de errores SOAP
"""

from main import MainProcess

def test_soap_error_filter():
    """
    Prueba la funcionalidad de filtrado de errores SOAP
    """
    print("Iniciando prueba del filtro de errores SOAP...")
    
    # Crear instancia del proceso principal
    main_process = MainProcess()
    
    # Ejecutar prueba de detección de errores
    result = main_process.test_soap_error_detection()
    
    if result:
        print("\n✅ El filtro de errores SOAP está funcionando correctamente")
        print("Las respuestas con <ns3:tieneError>true</ns3:tieneError> serán descartadas automáticamente")
    else:
        print("\n❌ Hay un problema con el filtro de errores SOAP")
    
    return result

if __name__ == "__main__":
    test_soap_error_filter()
