#!/usr/bin/python
# -*- coding: utf-8 -*-

#Cliente obtención tokens
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#02/02/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '08/02/2018'
__version__ = '1.0'


import configparser
import urllib
from objects import tokens
from resources import cliente_servidor as client


configfile = "config.cfg"  #Archivo de configuración para el script


class deregistration():

    def __init__(self):
        self.config = {}

        # Client Configuration from file config.cfg
        cfg = configparser.ConfigParser()  
        if not cfg.read(configfile): #if not cfg.read(["config.cfg"]):  
            print ("File does not exist")
        if cfg.has_option("net_dispatcher", "client_id"): #client_id
            self.config['CLIENT_ID'] = cfg.get("net_dispatcher", "client_id")
        else:
            print ("Config file need to have client_id field")
        if cfg.has_option("net_dispatcher", "file_cert_dispatcher"): #file_cert_dispatcher
            self.config['RUTA_CERT'] = cfg.get("net_dispatcher", "file_cert_dispatcher")
        else:
            print ("Config file need to have file_cert_dispatcher field")
        if cfg.has_option("net_dispatcher", "delete_functionality"): #delete_functionality
            self.config['DELETE_FUNCTIONALITY'] = (cfg.get("net_dispatcher", "delete_functionality"))
        else:
            print ("Config file need to have delete_functionality field")
        
        # Obtención del Host y el Port
        url = urllib.parse.urlparse(self.config['DELETE_FUNCTIONALITY'])
        self.config['HOSTNAME'] = url.hostname
        self.config['PORT'] = url.port
        self.config['PATH'] = url.path


    def deregister(self):
        # Comprobar expiración del token
        tokens.server_token().exp_token()

        # Mensaje post a enviar
        payload = "{\"client_id\":\"" + self.config['CLIENT_ID'] + "\"}"

        # Disposición de Headers
        token = tokens.server_token().get_tokenDB()

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + token['Data']['id_token'],
                   'Content-length': str(len(payload))}

        # Conexión con el dispatcher
        data = client.peticion("DELETE", self.config['HOSTNAME'], self.config['PORT'], self.config['DELETE_FUNCTIONALITY'], payload, headers, self.config['RUTA_CERT'])
        print(data)

        
#if __name__ == "__main__":
#    tokens.server_token().get_token()
#    a = deregistration()
#    a.deregister()
