#!/usr/bin/python
# -*- coding: utf-8 -*-


#Server microservicio
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#24/06/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '13/12/2017'
__version__ = '1.0'

import http.server
import ssl
import json
import os
import shutil
import time
import configparser
import urllib
from bots import bot
import analisis_imagenes as an
from objects import tokens
import registration
import deregistration
from auth import interceptors as auth
from resources import cliente_message as client_m
from resources import datos_user
from resources import fhir_client
from resources import datos_proceso as dat_p
  

# HTTPRequestHandler class
class HTTPServer_RequestHandler(http.server.BaseHTTPRequestHandler):
    #Plantilla types (en principio sólo se emplean tipos de imagen y json)
    mimetypes = { "html" : "text/html",
                  "htm" : "text/html",
                  "plain" : "text/plain",
                  "gif" : "image/gif",
                  "jpg" : "image/jpeg",
                  "jpeg" : "image/jpeg",
                  "png" : "image/png",
                  "json" : "application/json",
                  "css" : "text/css",
                  "js" : "text/javascript",
                  "ico" : "image/vnd.microsoft.icon",
                  "icon" : "image/vnd.microsoft.icon"}
    
    
    #GET
    def do_GET(self):
        try:
            #Conprobación del token
            decodedtoken = auth.auth_jwt(self.headers['Authorization'])
            if decodedtoken == None:
                self.send_error(401,'Unauthorized')
                return
            
            # Extracción del path del archivo
            request_path = self.path
            #file_path = os.path.normpath(file_path)
            #file_path = file_path.split(os.sep)
            file_path = urllib.parse.urlparse(request_path)

            # Apertura archivo a enviar
            #file = open(file_path[-2] + '/' + file_path[-1],'rb')
            file = open(file_path.path, 'rb')
            message = file.read()
            file.close()
        
            # Send response status code
            self.send_response(200) #OK
 
            # Send headers
            try:
                #tipo = file_path[-1].split('.')
                tipo = file_path.split('.')
                self.send_header('Content-Type',self.mimetypes[tipo[-1]])
            except:
                self.send_error(406,'Not acceptable')
                return
                                
            self.send_header('Content-Length', str(len(message)))
            self.send_header('Last-Modified', self.date_time_string(time.time()))
            self.end_headers()
            
            # Send response
            self.wfile.write(message)
            return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
            return


    ##POST
    def do_POST(self):
        # Escuchar mensajes que llegan a /message
        if self.path == "/message":
            #Conprobación del token
            decodedtoken = auth.auth_jwt(self.headers['Authorization'])
            if decodedtoken == None:
                self.send_error(401,'Unauthorized')
                return
        
            #Extrae headers
            #print(self.headers)

            #Comprobación del tamaño del mensaje (evita bloqueos al recivir imágenes no deseadas)
            if int(self.headers['Content-Length']) > 500:
                self.send_error(431, 'Request Header Fields Too Large')
                return
        
            #Extracción del mensaje
            try:
                content_length = int(self.headers['Content-Length']) # Get data size
                post_data = self.rfile.read(int(content_length)) # Get data
                #print(post_data)
                
            except:
                self.send_error(411,'Length Required')
                return
            
            # Operaciones si el mensaje contiene un json
            if self.headers['Content-Type'] == self.mimetypes["json"]:
                #Descompresión del json
                data = json.loads(post_data)
                #print(data)
                
                #Respuesta del bot
                aux = data['message']['body']
                aux = aux.split('/')
                    
                [responsebot, microservice, tarea] = bot.response(aux[0])

                #Datos usuario para cambiar funcionalidad conectada
                user = datos_user.userDB()
                user_data = user.get_user_data(data['user'])
                #print(user_data)

                # Operación de eliminar vello
                if tarea == 'Pelo':
                    an.quitar_pelo('imagenes/'+data['user']+'/recort.jpg',
                                   'imagenes/'+data['user']+'/limpia.jpg')
                    
                    #Se guarda que se hizo este proceso
                    dat_p.guardar_datos(data['user'], None, 'Pelo', None)
                    
                elif tarea == 'No_Pelo':
                    #Se guarda que se hizo este proceso
                    dat_p.guardar_datos(data['user'], None, 'No_Pelo', None)
                    
                #Análisis según tipo
                elif tarea == 'Gota' or tarea == 'Placa':
                    #Se cargan los datos de las operaciones realizadas
                    [area_t, pelo, area_marcador] = dat_p.cargar_datos(data['user'])
                    
                    if pelo == 'Pelo':  #Si se realizó la operación de eliminar vello
                        [area_t, area, puntos, v_pixels] = an.analisis(tarea,
                                    'imagenes/'+data['user']+'/limpia.jpg',
                                    'imagenes/'+data['user']+'/recort.jpg',
                                    'imagenes/'+data['user']+'/keypoint.jpg',
                                    'imagenes/'+data['user']+'/contour.jpg')
                        
                    elif pelo == 'No_Pelo': #Si no se realizó la operación de eliminar vello
                        [area_t, area, puntos, v_pixels] = an.analisis(tarea,
                                    'imagenes/'+data['user']+'/recort.jpg',
                                    'imagenes/'+data['user']+'/recort.jpg',
                                    'imagenes/'+data['user']+'/keypoint.jpg',
                                    'imagenes/'+data['user']+'/contour.jpg')

                    #Se guardan los datos obtenidos
                    dat_p.guardar_datosDB(data['user'], area, puntos, v_pixels)
                    dat_p.guardar_datos(data['user'], str(area_t), None, None)

                    #Se cargan los datos de las operaciones realizadas
                    [area_t, pelo, area_marcador] = dat_p.cargar_datos(data['user'])
                    
                    #Se calcula el area se psoriasis
                    #area_marcador=17000 #Para pruebas
                    area_detec = an.calc_area(area_t, area_marcador, tarea)

                    #Envio de imagenes al cliente
                    #client_m.enviar(data,'imagenes/'+data['user']+'/keypoint.jpg',None)
                    client_m.enviar(data,'imagenes/'+data['user']+'/contour.jpg',
                                    #'El área total detectada es:'+str(area_t))
                                    'El área total detectada es:'+str(area_detec)+'cm2')

                 #Almacenado de datos
                elif tarea == 'Guardar':
                    #Se cargan los datos de las operaciones realizadas
                    [area_t, pelo, area_marcador] = dat_p.cargar_datos(data['user'])

                    #Se calcula el area se psoriasis
                    #area_marcador=17000 #Para pruebas
                    area_detec = an.calc_area(area_t, area_marcador, tarea)
                    
                    #Envío de datos a la base de datos
                    fhir_client.post_data(area_detec, data['user'], user_data['id'])
                
                # Operaciones entrada microservicio
                if microservice == 'Procesado_imagen':
                    #Envío de cambios en el perfil de usuario
                    user_data['runningFunctionality'] = 'Procesado_imagen'
                    user.change_user_data(data['user'], user_data)

                    #Creación de directorio para manejo de las imágenes de procesado del usuario
                    try:
                        os.mkdir('imagenes/'+data['user'])
                    except FileExistsError: #Si ya existe no lo crea de nuevo y salta el mensaje de error
                        pass

                    #Obtención de la imagen a analizar
                    dt_im = fhir_client.get_image(data['message']['body'], data['user'])
                    fhir_client.update_image(data['message']['body'], dt_im)
                    
                    #Recorte área marcadores
                    try:
                        area_marcador = an.recorte('imagenes/'+data['user']+'/reciv.jpg',
                                                   'imagenes/'+data['user']+'/recort.jpg')
                        dat_p.guardar_datos(data['user'], None, None, str(area_marcador))
                        #print(area_marcador)
                        client_m.enviar(data,'imagenes/'+data['user']+'/recort.jpg',
                                    'Si el recorte no salió bien, puede salir y repetir.')
                    except:
                        client_m.enviar(data, None, 'No se detectaron bien los marcadores. Salir y repetir la foto.')
                        pass
                        
                # Operación de salida del microservicio
                elif microservice == 'Salir':
                    #Envío de cambios en el perfil de usuario
                    user_data['runningFunctionality'] = None
                    user.change_user_data(data['user'], user_data)

                    #Eliminación del directorio de imágenes del usuario
                    shutil.rmtree('imagenes/'+data['user'])

                
                # Mensaje a enviar
                payload = {}
                payload['message'] = {}
                payload['user'] = data['user']
                payload['platform'] = data['platform']
                payload['message']['timestamp'] = int(time.time())
                #payload['message']['body'] = "Hola"
                payload['message']['body'] = responsebot
                payload['message']['attachments'] = None
                payload = json.dumps(payload)
                payload = bytes(payload, 'utf-8')

                # Send response status code
                self.send_response(200) #OK

                # Send headers
                token = tokens.server_token().get_tokenDB()
                self.send_header('Authorization', 'Bearer ' + token['Data']['id_token'])
                self.send_header('Content-Type', self.mimetypes["json"])
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('Last-Modified', self.date_time_string(time.time()))
                self.end_headers()
                  
                # Send response
                self.wfile.write(payload)
                
                  
            else:
                self.send_error(415,'Unsupported Media Type')
                return

        else:
            # Send response status code
            self.send_response(204) #No content
            return


#Arranque servidor
def run(server_class=http.server.HTTPServer, handler_class=HTTPServer_RequestHandler):
    print('Starting server...')

    # Server Configuration from file config.cfg
    config = {}
    cfg = configparser.ConfigParser()  
    if not cfg.read(["config.cfg"]):  
        print ("File does not exist")
    if cfg.has_option("net", "ip"): #ip
        config['ip'] = cfg.get("net", "ip")
    else:
        print ("Config file need to have ip field")
    #if cfg.has_option("net", "name"): #host_name
    #    config['host_name'] = cfg.get("net", "name")
    #else:
    #    print ("Config file need to have name field")
    if cfg.has_option("net", "port"): #port
        config['port'] = int(cfg.get("net", "port"))
    else:
        print ("Config file need to have port field")
    if cfg.has_option("net", "file_key"): #file_key
        config['file_key'] = cfg.get("net", "file_key")
    else:
        print ("Config file need to have file_key field")
    if cfg.has_option("net", "file_cert"): #file_key
        config['file_cert'] = cfg.get("net", "file_cert")
    else:
        print ("Config file need to have file_cert field")
    #if cfg.has_option("net", "max_conect"): #max_conect
    #    max_conexiones = int(cfg.get("net", "max_conect"))
    #else:
    #    print ("Config file need to have max_conect field")

    # Create the kernel and learn AIML files for bot response
    bot.initialize()

    # Server settings
    server_address = (config['ip'], config['port'])
    httpd = server_class(server_address, handler_class)
    #httpd.socket.listen(max_conexiones) #Límite de clientes conectados

    # Seguridad https
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   keyfile = config['file_key'], #keyfile = RUTA_KEY,
                                   certfile = config['file_cert'], #certfile = RUTA_CERT,
                                   server_side = True,
                                   )

    # Authentication token
    tokens.server_token().get_token()
    
    # Registro en el dispatcher
    reg = registration.registration()
    reg.register()

    # Creación de recursos en la base FHIR si no existen
    fhir_client.DB_device_creation()
    fhir_client.DB_device_request_creation()
    fhir_client.DB_procedure_request_creation()

    # Cambio estado Device
    fhir_client.device_update_DB("active")

    # Run and Stop server
    #while True:
    try:
        #Ejecución del servidor
        httpd.serve_forever()
        #httpd.handle_request() #handle one request (while loop needed)
        print('Running server...')
        print('Server port:', port)
        
    except KeyboardInterrupt:
        print('Keyboard interrupt received: EXITING')
        
    finally:
        #Desregistro en el dispatcher
        dereg = deregistration.deregistration()
        dereg.deregister()

        #Cambio estado Device
        fhir_client.device_update_DB("inactive")

        #Apagado del servidor
        httpd.shutdown()
        httpd.server_close()
        print('Server stopped')
        return
        #break


if __name__ == '__main__':
    run()
    
