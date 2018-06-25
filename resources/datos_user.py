#!/usr/bin/python
# -*- coding: utf-8 -*-

#Server microservicio
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#21/02/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '15/03/2018'
__version__ = '1.0'


import configparser
import urllib
from objects import tokens
from resources import cliente_servidor as client
import json


configfile = "config.cfg"  #Archivo de configuración para el script


class userDB():

    def __init__(self):
        self.config = {}

        # Client Configuration from file config.cfg
        cfg = configparser.ConfigParser()  
        if not cfg.read(configfile): #if not cfg.read(["config.cfg"]):  
            print ("File does not exist")
        if cfg.has_option("net_dispatcher", "file_cert_dispatcher"): #file_cert_dispatcher
            self.config['RUTA_CERT'] = cfg.get("net_dispatcher", "file_cert_dispatcher")
        else:
            print ("Config file need to have file_cert_dispatcher field")
        if cfg.has_option("net_dispatcher", "db_request"): #db_request
            self.config['DB_REQUEST'] = cfg.get("net_dispatcher", "db_request")
        else:
            print ("Config file need to have db_request field")

        # Obtención del Host y el Port
        url = urllib.parse.urlparse(self.config['DB_REQUEST'])
        self.config['HOSTNAME'] = url.hostname
        self.config['PORT'] = url.port
        self.config['PATH'] = url.path


    def get_user_data(self, user_number):
        # Comprobar expiración del token
        tokens.server_token().exp_token()

        # Mensaje post a enviar
        payload = "{\"url\":\"users/_find?criteria={\\\"id_signal\\\":\\\""+user_number+"\\\"}\",\"data\":null}"

        # Disposición de Headers
        token = tokens.server_token().get_tokenDB()

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + token['Data']['id_token'],
                   'Content-length': str(len(payload))}
        
        # Conexión con el dispatcher
        data_DB = client.peticion("POST", self.config['HOSTNAME'], self.config['PORT'], self.config['DB_REQUEST'], payload, headers, self.config['RUTA_CERT'])
        
        # Descompresión json (ok, results, data)
        #print(data_DB)
        data_DB = json.loads(data_DB)
        #print(data_DB)

        # Devuelve el diccionario con los datos del paciente
        return data_DB['results'][0] #Interesan los datos del usuario almacenados en results


    def change_user_data(self, user_number, data_user):
        # Comprobar expiración del token
        tokens.server_token().exp_token()

        # Mensaje post a enviar
        data_user = json.dumps(data_user)
        data_user = data_user.replace('"','\\\"')#Al crear el json se pierden comillas contenidas dentro
        payload = "{\"url\": \"users/_update\", \"data\": \"criteria={\\\"id_signal\\\": \\\""+user_number+"\\\"}&newobj="+data_user+"\"}"
        
        # Disposición de Headers
        token = tokens.server_token().get_tokenDB()

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + token['Data']['id_token'],
                   'Content-length': str(len(payload))}
        
        # Conexión con el dispatcher
        resp = client.peticion("POST", self.config['HOSTNAME'], self.config['PORT'], self.config['DB_REQUEST'], payload, headers, self.config['RUTA_CERT'])
        print(resp)

#if __name__ == "__main__":
    #tokens.server_token().get_token()
    #a = userDB()
    #data = a.get_user_data('+34699706335')
    #data['runningFunctionality'] = 'Procesado_imagen'
    #data['runningFunctionality'] = None
    #data['context'] = ", recuerda las opciones que tienes disponibles \\ud83d\\ude42"
    #data='{"runningFunctionality": "Procesado_imagen", "id_signal": "+34699706335", "surname": "", "name": "Daniel Vicente", "admin": false, "registered": true, "discarded": false, "context": ", recuerda las opciones que tienes disponibles \\ud83d\\ude42", "patient": null, "listFunctionalities": ["Ayuda", "Gestionar opciones", "Modificar datos personales"], "type": "Paciente", "id": "416"}'
    #a.change_user_data('+34699706335', data)
    #user_data = a.get_user_data('+34699706335')
    #print(user_data)
    
    
