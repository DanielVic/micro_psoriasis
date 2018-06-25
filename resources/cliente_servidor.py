#!/usr/bin/python
# -*- coding: utf-8 -*-

#Cliente genérico para la comunicación del servidor
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#15/02/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '15/02/2018'
__version__ = '1.0'

import http.client
import ssl

# Función que realiza la petición como cliente
def peticion(verbo, host_name, port, ruta, data, headers, ruta_cert):
        # Conexión con el dispatcher
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.load_verify_locations(ruta_cert)
        conn = http.client.HTTPSConnection(host_name, port, context=context) 

        # Petición
        conn.request(verbo, ruta, data, headers)

        # Respuesta recivida
        response = conn.getresponse()
        data = response.read()
        print(response.status, response.reason)
        #print(data)
        
        conn.close()

        return data
