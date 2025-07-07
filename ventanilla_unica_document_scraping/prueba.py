import xml.etree.ElementTree as ET

"""
    Rutas:
    - Numero de operacion .//ns2:numeroOperacion
    - Encabezado
        - Pedimento .//ns2:pedimento/ns2:pedimento
        - CURP Apoderado Mandatario .//ns2:curpApoderadomandatario
        - RFC Agente Aduanal .//ns2:rfcAgenteAduanalSocFactura
        - Valor Aduanal Total .//ns2:valorAduanalTotal
        - Valor Comercial Total .//ns2:valorComercialTotal
    - Tasas
    - Partidas
        - Partidas .//ns2:partidas/ns2:partida (Func para obtener el valor mas alto)
    - 
"""
tree = ET.parse('archivo.xml')
root = tree.getroot()


# Definir los namespaces usados en el XML
namespaces = {
    'S': 'http://schemas.xmlsoap.org/soap/envelope/',
    'ns2': 'http://www.ventanillaunica.gob.mx/pedimentos/ws/oxml/consultarpedimentocompleto',
    'ns3': 'http://www.ventanillaunica.gob.mx/common/ws/oxml/respuesta',
    # agrega otros si los necesitas
}

# Acceder al elemento Body
no_operacion            = root.find('.//ns2:numeroOperacion', namespaces)
pedimento               = root.find('.//ns2:pedimento/ns2:pedimento', namespaces)
curp_apoderado          = root.find('.//ns2:curpApoderadomandatario', namespaces)
RFC_Agente_Aduanal      = root.find('.//ns2:rfcAgenteAduanalSocFactura', namespaces)
valor_aduanal_total     = root.find('.//ns2:valorAduanalTotal', namespaces)
valor_comercial_total   = root.find('.//ns2:valorComercialTotal', namespaces)

print(f'Numero de operacion: {no_operacion.text if no_operacion is not None else "No encontrado"}')
print(f'Pedimento: {pedimento.text if pedimento is not None else "No encontrado"}')
print(f'CURP Apoderado Mandatario: {curp_apoderado.text if curp_apoderado is not None else "No encontrado"}')
print(f'RFC Agente Aduanal: {RFC_Agente_Aduanal.text if RFC_Agente_Aduanal is not None else "No encontrado"}')
print(f'Valor Aduanal Total: {valor_aduanal_total.text if valor_aduanal_total is not None else "No encontrado"}')
print(f'Valor Comercial Total: {valor_comercial_total.text if valor_comercial_total is not None else "No encontrado"}')
