#!/usr/bin/python
# -*- coding: utf-8 -*-


#Script de almacenado y lectura de datos de procesado
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#30/11/2017

__author__ = 'Daniel Vicente Moya'
__date__ = '13/12/2017'
__version__ = '1.0'


import csv
import json


#Campos que se empléan
fieldnames = ['area_t', 'tarea_pelo', 'area_marcador']

fields = ['area', 'puntos', 'valor_pixeles'] #píxeles en hsv


# Función para lectura de datos almacenados sobre operaciones a realizar
def cargar_datos(user):
    with open('imagenes/'+user+'/datos.dat', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            area = row['area_t']
            pelo = row['tarea_pelo']
            a_marcador = row['area_marcador']
    return area, pelo, a_marcador

         
    
# Función para el guardado de datos en un archivo csv
def guardar_datos(user, area, pelo, area_marcador): #datos en str
    #Comprueba si hay algo guardado antes
    try: #Se realiza en caso de que haya datos previos
        [aux_area, aux_pelo, aux_area_marcador] = cargar_datos(user)
        if area == None:
            area = aux_area
        if pelo == None:
            pelo = aux_pelo
        if area_marcador == None:
            area_marcador = aux_area_marcador
    except:
        pass
    
    csvfile = open('imagenes/'+user+'/datos.dat','w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'area_t': area, 'tarea_pelo': pelo, 'area_marcador': area_marcador})


# Función para lectura de datos almacenados obtenidos
def cargar_datosDB(user):
    with open('imagenes/'+user+'/datosDB.dat', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            area = row['area']
            punto = row['puntos']
            pixel = row['valor_pixeles']
    return area, punto, pixel


# Función para el guardado de datos obtenidos para almacenar en el DB
def guardar_datosDB(user, area, punto, pixel): #datos en str
    #Comprueba si hay algo guardado antes
    try: #Se realiza en caso de que haya datos previos
        [aux_area, aux_punto, aux_pixel] = cargar_datosDB(user)
        if area == None:
            area = aux_area
        if punto == None:
            punto = aux_punto
        if pixel == None:
            pixel = aux_pixel
    except:
        pass
    #Creación de json
    csvfile = open('imagenes/'+user+'/datosDB.dat','w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerow({'area': area, 'puntos': punto, 'valor_pixeles': pixel})

    


##if __name__ == "__main__":
##    area = [333,43213,5343]
##    #print(type(area))
##    punto = [[456,44],[444,888],[112,990]]
##    pixel =[[333, 333, 333],[432, 88, 0],[3, 77, 903]]
##    guardar_datos('+34619173338', '3', None, None)
##    [area, pelo, area_marcador] = cargar_datos('+34619173338')
##    #print(area)
##    #print(pelo)
##    guardar_datosDB('+34619173338', area, punto, pixel)
##    datos = cargar_datosDB('+34619173338')
##    #print(datos)
##    #dat = json.loads(datos[0]) #descomprimir con json para obtener otra vez la lista de datos
##    #print(type(dat))
