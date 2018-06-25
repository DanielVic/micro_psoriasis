#!/usr/bin/python
# -*- coding: utf-8 -*-

#Script para respuestas del bot
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#17/04/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '17/04/2018'
__version__ = '1.0'


import configparser
import urllib
import base64
import time
import json
from objects import tokens
from resources import cliente_servidor as client


config = {}
configfile = "config.cfg"


# Client Configuration from file config.cfg
cfg = configparser.ConfigParser()  
if not cfg.read(configfile): #if not cfg.read(["config.cfg"]):  
    print ("File does not exist")
if cfg.has_option("net_dispatcher", "url_message"): #url_message
    config['URL_MESSAGE'] = cfg.get("net_dispatcher", "url_message")
else:
    print ("Config file need to have url_message field")
if cfg.has_option("net_dispatcher", "url_attachment"): #url_attachment
    config['URL_ATTACHMENT'] = cfg.get("net_dispatcher", "url_attachment")
else:
    print ("Config file need to have url_attachment field")
if cfg.has_option("net_dispatcher", "file_cert_dispatcher"): #file_cert_dispatcher
    config['RUTA_CERT'] = cfg.get("net_dispatcher", "file_cert_dispatcher")
else:
    print ("Config file need to have file_cert_dispatcher field")


# Obtención del Host y el Port
url = urllib.parse.urlparse(config['URL_MESSAGE'])
config['HOSTNAME'] = url.hostname
config['PORT'] = url.port
config['PATH'] = url.path


def enviar(data, attach, body):
    if attach != None:
        #Codificado de la imagen en base 64
        file = open(attach, 'rb')
        data_file = file.read()
        length_image = int(len(data_file))
        data_file = base64.b64encode(data_file)
        data_file = str(data_file, 'utf-8')
        file.close()

        attachment = {}
        attachment['contentType'] = "image/jpeg"
        attachment['data'] = data_file
        attachment['size'] = length_image

        # Mensaje a enviar
        payload = {}
        payload['message'] = {}
        payload['user'] = data['user']
        payload['platform'] = data['platform']
        payload['message']['timestamp'] = int(time.time())
        payload['message']['body'] = body
        payload['message']['attachments'] = attachment
        payload = json.dumps(payload)

        payload = bytes(payload, 'utf-8')
    
        # Disposición de Headers
        token = tokens.server_token().get_tokenDB()
        headers = {'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token['Data']['id_token'],
        'Content-length': str(len(payload))}
    
        resp = client.peticion('POST',config['HOSTNAME'],config['PORT'],config['URL_ATTACHMENT'],payload,headers,config['RUTA_CERT'])
        print(resp)

    else:
        attachment = None
            
        # Mensaje a enviar
        payload = {}
        payload['message'] = {}
        payload['user'] = data['user']
        payload['platform'] = data['platform']
        payload['message']['timestamp'] = int(time.time())
        payload['message']['body'] = body
        payload['message']['attachments'] = attachment
        payload = json.dumps(payload)
        payload = bytes(payload, 'utf-8')
    
        # Disposición de Headers
        token = tokens.server_token().get_tokenDB()
        headers = {'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token['Data']['id_token'],
        'Content-length': str(len(payload))}
    
        resp = client.peticion('POST',config['HOSTNAME'],config['PORT'],config['URL_MESSAGE'],payload,headers,config['RUTA_CERT'])
        print(resp)
