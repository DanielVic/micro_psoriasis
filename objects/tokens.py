#!/usr/bin/python
# -*- coding: utf-8 -*- 

#Cliente obtención tokens
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#23/01/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '30/01/2018'
__version__ = '1.0'

import ssl
import socket
import json
#import os
import configparser
import urllib
import time
import base64
from objects import class_token_DB as DB


configfile = "config.cfg"  #Archivo de configuración para el script
    

class server_token():

    def __init__(self):
        self.config = {}

        # Client Configuration from file config.cfg
        cfg = configparser.ConfigParser()  
        if not cfg.read(configfile): #if not cfg.read(["config.cfg"]):  
            print ("File does not exist")
        if cfg.has_option("net_oauth", "url_oauth"): #url_oauth
            self.config['URL_OAUTH'] = cfg.get("net_oauth", "url_oauth")
        else:
            print ("Config file need to have url_oauth field")
        if cfg.has_option("net_oauth", "file_cert_oauth"): #file_cert_oauth
            self.config['RUTA_CERT'] = cfg.get("net_oauth", "file_cert_oauth")
        else:
            print ("Config file need to have file_cert_oauth field")
        if cfg.has_option("net_oauth", "client_id"): #client_id
            self.config['CLIENT_ID'] = cfg.get("net_oauth", "client_id")
        else:
            print ("Config file need to have client_id field")
        if cfg.has_option("net_oauth", "secret"): #secret
            self.config['SECRET'] = cfg.get("net_oauth", "secret")
        else:
            print ("Config file need to have secret field")
        #if cfg.has_option("net_oauth", "save_token"): #save_token
        #    self.config['RUTA_SAVE'] = cfg.get("net_oauth", "save_token")
        #else:
        #    print ("Config file need to have save_token field")

        #Obtención del Host y el Port
        url = urllib.parse.urlparse(self.config['URL_OAUTH'])
        self.config['HOSTNAME'] = url.hostname
        self.config['PORT'] = url.port
    
        #Path para la comunicación
        if not url.path == '':
            self.config['PATH'] = url.path
        else:
            self.config['PATH'] = '/'
        if not url.params == '':
            self.config['PATH'] = self.config['PATH']+';'+url.params
        if not url.query == '':
            self.config['PATH'] = self.config['PATH']+'?'+url.query
        if not url.fragment == '':
            self.config['PATH'] = self.config['PATH']+'#'+url.fragment
        self.config['PATH'] = self.config['PATH']+'&client_id='+self.config['CLIENT_ID']+'&client_secret='+self.config['SECRET']
        
    
    def get_token(self):
        try:
            #Conexión y petición de token
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.config['HOSTNAME'], self.config['PORT']))
            s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1)
            s.sendall(bytes("GET "+self.config['PATH']+" HTTP/1.1\r\nHost: "+self.config['HOSTNAME']+"\r\nConnection: close\r\n\r\n", 'utf-8'))
    
            headers = {}
            data = {}
            almacenar = {}
            aux = 1
            while True:
                message = s.recv(4096)
                if aux == 1:   #Status code
                    print(str(message,'utf-8').replace("\r\n","") + "  NEW TOKEN")
            
                if aux == 2 or aux == 3 or aux == 4: #Headers (Server, Date, Content-type)
                    mensaje = str(message,'utf-8').replace("\r\n","").replace(" ","")
                    mensaje = mensaje.split(":")
                    headers[mensaje[0]] = mensaje[1]

                if aux == 5: #(Marca inicio respuesta)
                    pass
        
                if aux == 6: #Response
                    mensaje = str(message,'utf-8').replace("'","").replace("\r\n","").replace(" ","").replace("{","").replace("}","")
                    raw = mensaje
                    #Conversión string a diccionario para faciltar el uso
                    mensaje = mensaje.split(",")
                    for d in range(len(mensaje)):
                        data_aux = mensaje[d]
                        data_aux = data_aux.split(":")
                        data[data_aux[0]] = data_aux[1]
               
                if not message: #End response
                    s.close()
                    break
                aux=aux+1
        except:
            print('Error in GET token')

        try:
            #Almacenado de token
            #almacenar['Headers'] = headers
            #almacenar['Data'] = data
            
            DB.token.headers = headers
            DB.token.data = data
            
            #almacen = json.dumps(almacenar)
            #file = open(self.config['RUTA_SAVE'], 'w')
            #file.write(almacen)  #Datos almacenados en json
            #file.close()
            print('New token received')
        except:
            print('Save token Error')


    def exp_token(self):
        #Cargar token guardado
        try:
            #aux = {}
            #file = open(self.config['RUTA_SAVE'], 'r')
            #aux = file.read()
            #aux = json.loads(aux)
            #token_id = aux['Data']['id_token'].split('.')
            #file.close
            token_id = DB.token.data['id_token'].split('.')
        except:
            print('Error in token loading')

        #Decodificación time exp en token
        try:
            payload = base64.b64decode(token_id[1]+ '==')
            payload = json.loads(payload)
        except:
            print('Error in token decoding')

        #Comprobación tiempo de expiración
        if int(time.time()) < payload['exp']:
            print('CHECK TOKEN: Time exp '+str(payload['exp'])+' --> Not expired')
            pass
        else:
            #Si está caducado lo actualiza automáticamente
            print('CHECK TOKEN: Time exp '+str(payload['exp'])+' --> Expired')
            self.get_token()


    def get_tokenDB(self):
        #Cargar token guardado
        #try:
            token = {}
            #file = open(self.config['RUTA_SAVE'], 'r')
            #token = file.read()
            #token = json.loads(token)
            #file.close
            token['Headers'] = DB.token.headers
            token['Data'] = DB.token.data
            return token #Permite extraer el token para la autenftificación en la cominicación
        
        #except:
            #print('Error in token loading')


#if __name__ == "__main__":

#    a = server_token()
#    a.get_token()
#    print(DB.token.data)
#    print(DB.token.headers)
    #a.exp_token()
    #print(server_token("config.cfg").token)
    #a.get_token()
    #print(a.token['Data']['id_token'])
