#!/usr/bin/python
# -*- coding: utf-8 -*-

#Cliente registro en el dispatcher
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


class registration():

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
        if cfg.has_option("net_dispatcher", "boolean_menu"): #boolean_menu
            self.config['MENU'] = cfg.get("net_dispatcher", "boolean_menu")
        else:
            print ("Config file need to have boolean_menu field")
        if cfg.has_option("net_dispatcher", "addrr"): #addrr
            self.config['ADDRR'] = cfg.get("net_dispatcher", "addrr")
        else:
            print ("Config file need to have addrr field")
        if cfg.has_option("net_dispatcher", "canUse"): #canUse
            self.config['CANUSE'] = cfg.get("net_dispatcher", "canUse")
        else:
            print ("Config file need to have canUse field")
        if cfg.has_option("net_dispatcher", "client_id"): #client_id
            self.config['CLIENT_ID'] = cfg.get("net_dispatcher", "client_id")
        else:
            print ("Config file need to have client_id field")
        if cfg.has_option("net_dispatcher", "message"): #message
            self.config['MESSAGE'] = cfg.get("net_dispatcher", "message")
        else:
            print ("Config file need to have message field")
        if cfg.has_option("net_dispatcher", "new_functionality"): #new_functionality
            self.config['NEW_FUNCTIONALITY'] = cfg.get("net_dispatcher", "new_functionality")
        else:
            print ("Config file need to have new_functionality field")

        # Obtención del Host y el Port
        url = urllib.parse.urlparse(self.config['NEW_FUNCTIONALITY'])
        self.config['HOSTNAME'] = url.hostname
        self.config['PORT'] = url.port
        self.config['PATH'] = url.path


    def register(self):
        # Comprobar expiración del token
        tokens.server_token().exp_token()

        # Mensaje post a enviar
        payload = "{\"message\":\"" + self.config['MESSAGE'] +"\",\"menu\":" + self.config['MENU'] + ",\"client_id\":\"" + self.config['CLIENT_ID'] + "\",\"address\":\"" + self.config['ADDRR'] + "\",\"canUse\":[" + self.config['CANUSE'] +"]}";

        # Disposición de Headers
        token = tokens.server_token().get_tokenDB()

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + token['Data']['id_token'],
                   'Content-length': str(len(payload))}

        # Conexión con el dispatcher
        data = client.peticion("POST", self.config['HOSTNAME'], self.config['PORT'], self.config['NEW_FUNCTIONALITY'], payload, headers, self.config['RUTA_CERT'])
        print(data)


#if __name__ == "__main__":
#    tokens.server_token().get_token()
#    a = registration()
#    a.register()
