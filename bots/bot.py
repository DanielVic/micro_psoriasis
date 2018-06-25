#!/usr/bin/python
# -*- coding: utf-8 -*-

#Script para respuestas del bot
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#12/02/2018


__author__ = 'Daniel Vicente Moya'
__date__ = '13/02/2018'
__version__ = '1.0'


import aiml
import configparser
import xml.etree.ElementTree as ET


configfile = "config.cfg"  #Archivo de configuración para el script
kernel = aiml.Kernel()     #Kernel bot
config = {}

    
def initialize():
    # Bot Configuration fom file config.cfg
    cfg = configparser.ConfigParser()
    if not cfg.read(configfile): #if not cfg.read(["config.cfg"]):  
        print ("File does not exist")
    if cfg.has_option("bot", "file_aiml"): #file_aiml
        config['RUTA_AIML'] = cfg.get("bot", "file_aiml")
    else:
        print ("Config file need to have file_aiml field")

    # Create the kernel and learn AIML files
    kernel.learn(config['RUTA_AIML'])

        
def response(string):
    # Read the AIML file to extract information
    tree = ET.parse(config['RUTA_AIML'])
    root = tree.getroot()
    
    # Bot response
    resp = kernel.respond(string)

    # Tag extraction
    microservice = None
    tarea = None
    for category in root:
        try:
            template = category.find('template').text
            if resp == template:
                #Extrae tag microservice
                try:
                    microservice = category.find('microservice').text
                except: #En caso de que no exista la subclase microservice en la ctaegoría
                    microservice = None
                try:
                    tarea = category.find('tarea').text
                except: #En caso de que no exista la subclase tarea
                    tarea = None

        except:
            print('Template error in aiml file. Tag not found') 
    return resp, microservice, tarea

#if __name__ == "__main__":
#    initialize()
#    resp = response("analizar")
#    print(resp)
