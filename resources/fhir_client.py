#!/usr/bin/python
# -*- coding: utf-8 -*-


#Server microservicio
#Programado empleando python 3.6.3
#Daniel Vicente Moya
#23/03/2017


__author__ = 'Daniel Vicente Moya'
__date__ = '26/03/2018'
__version__ = '1.0'


import http.client
import configparser
import urllib
import ssl
import json
import base64
import time
from objects import tokens


#Cabecera comunicación http
headers = {'Authorization': 'Bearer ',
           'Accept-Charset': 'utf-8',
           'Accept': ' application/fhir+xml;q=1.0, application/fhir+json;q=1.0, application/xml+fhir;q=0.9, application/json+fhir;q=0.9',
           'User-Agent': ' HAPI-FHIR/3.1.0-SNAPSHOT (FHIR Client; FHIR 3.0.1/DSTU3; apache)',
           'Accept-Encoding': 'json'}


configfile = "config.cfg"  #Archivo de configuración para el script
config = {}


# Client Configuration fom file config.cfg
cfg = configparser.ConfigParser()
if not cfg.read(configfile): #if not cfg.read(["config.cfg"]):  
    print ("File does not exist")
if cfg.has_option("net_fhir", "url_fhir"): #url_fhir
    config['URL_FHIR'] = cfg.get("net_fhir", "url_fhir")
else:
    print ("Config file need to have url_fhir field")

#Obtención del Host y el Port
url = urllib.parse.urlparse(config['URL_FHIR'])
config['HOSTNAME'] = url.hostname
config['PORT'] = url.port

    
# Función para la toma de imagén de la base de datos
def get_image(location, user): #localización base de datos, nombre de usuario como identificador
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']
    
    #Petición get a la base de datos
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('GET', config['URL_FHIR']+location, headers=headers)
    r = conn.getresponse()
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation GET image')
    data = json.loads(data)
    #print(data)
    
    conn.close()
    
    #La imagen está codificada en base64
    imagen = base64.b64decode(data['content']['data'])
    
    #La imagen se almacena para su tratamiento
    file = open('imagenes/' + user + '/reciv.jpg','wb')
    #file = open('imagenes/'+user+'.jpg','wb')#para pruebas
    file.write(imagen)
    file.close()
    return data


# Función para actualizar los datos de la imagen
def update_image(location, data): #localización base de datos
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']

    #Mensaje a enviar
    data['basedOn'] = [{"identifier" : {"use": "temp",
                                        "value": "Procedure_Monitorizacion_Psoriasis",
                                        "assigner": "UNIZAR"
                                        }}]
    data['device'] = {"identifier": { "use": "temp",
                                      "value": "Procesado_imagen",
                                      "assigner": "UNIZAR"
                                      }}
    payload = json.dumps(data)

    #Petición put a la base de datos para actualizar el recurso
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('PUT', config['URL_FHIR']+location, payload, headers)
    r = conn.getresponse()
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation Update image')
    data = json.loads(data)
    print(data)

    conn.close()


# Función para almacenar datos del análisis (almacena imagen de contornos, archivo con datos del análisis y el area total suelta)
def post_data(data, user, patient_id):
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']

    #Mensaje a enviar
    file = open('imagenes/' + user + '/contour.jpg','rb')
    image = file.read()    
    size_image = len(image)
    image = base64.b64encode(image) #paso archivo imagen a base 64
    image = str(image, 'utf-8')
    file.close()

    file = open('imagenes/' + user + '/datosDB.dat','rb')
    data_file = file.read()    
    size_data_file = len(data_file)
    data_file = base64.b64encode(data_file) #paso archivo imagen a base 64
    data_file = str(data_file, 'utf-8')
    file.close()
    
    payload = {"resourceType": "Observation",
               "basedOn": [{"identifier" : {"use": "temp",
                                            "value": "Monitorizacion_Psoriasis",
                                            "assigner": "UNIZAR"
                                            }},
                           {"identifier" : {"use": "temp",
                                            "value": "Procedure_Monitorizacion_Psoriasis",
                                            "assigner": "UNIZAR"
                                            }}
                           ],
               "status": "registered", #"preliminary"
               "code": {"coding": [{"system": "http://loinc.org",
                                    "code": "10206-1",
                                    "display": "Physical findings of Skin Narrative"
                                    },
                                   {"system": "http://unitsofmeasure.org",
                                     "code": "cm2",
                                     "display": "square centimeter"
                                     }],
                        "text": "Hallazgos fisicos sobre la piel"
                        },
               "subject": {"reference": "Patient/"+patient_id},
               "valueString": data,
               "device": {"identifier": { "use": "temp",
                                          "value": "Procesado_imagen",
                                          "assigner": "UNIZAR"
                                          }},
               "component": [{"code": {"coding": [{"system": "http://loinc.org",
                                                   "code": "10206-1",
                                                   "display": "Physical findings of Skin Narrative"
                                                   },
                                                  {"system": "http://hl7.org/fhir/digital-media-type",
                                                   "code": "photo",
                                                   "display": "Photo"
                                                   }],
                                       "text": "Hallazgos fisicos sobre la piel"
                                       },
                              "valueAttachment": {"contentType": "image/jpeg",
                                                  "data": image,
                                                  "size": size_image,
                                                  "creation": time.strftime("%Y-%m-%d"+"T"+"%I:%M:%S"+"+02:00")
                                                  },
                              },
                             {"code": {"coding": [{"system": "http://loinc.org",
                                                   "code": "10206-1",
                                                   "display": "Physical findings of Skin Narrative"
                                                   },
                                                  {"system": "http://unitsofmeasure.org",
                                                   "code": "cm2",
                                                   "display": "square centimeter"
                                                   }],
                                       "text": "Hallazgos fisicos sobre la piel"
                                       },
                              "valueAttachment": {"contentType": "application/octet-stream'",
                                                  "data": data_file,
                                                  "size": size_data_file,
                                                  "creation": time.strftime("%Y-%m-%d"+"T"+"%I:%M:%S"+"+02:00")
                                                  }
                              }]
               }
    payload = json.dumps(payload)

    #Petición post a la base de datos
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('POST', config['URL_FHIR']+"Observation", payload, headers)
    r = conn.getresponse()
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation Save Data')
    data = json.loads(data)
    print(data)
    
    conn.close()


# Función para crear el device de procesado (No es necesario si existe el recurso en la base de datos)
def DB_device_creation():
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']

    #Se comprueba si esta creado
    ##Device
    #Petición get a la base de datos
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('GET', config['URL_FHIR']+"Device?identifier:value=Procesado_imagen", headers=headers)
    r = conn.getresponse()                  #776
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation GET Device')
    data = json.loads(data)
    print(data)
    
    conn.close()

    if int(data['total']) != 0:
        pass           #Si ya está creado no lo vuelve a crear.
    else:
        #Mensajes a enviar
        ##Device
        payload = {"resourceType": "Device",
                   #"id": "776", #Se establece id fija (cambiar si está ocupada en el DB)
                   "identifier": [{ "use": "temp",
                                    "value": "Procesado_imagen",
                                    "assigner": "UNIZAR"
                                    }],
                   "status": "inactive",# active | inactive | entered-in-error | unknown
                   "type" : { "coding": [{"system": "http://snomed.info/sct",
                                          "code": "701654001",
                                          "display": "Self-care monitoring web-based application software"
                                          }],
                              "text": "Aplicación móvil de monitoirzación"
                              },
                   "version": "1.0",
                   "contact": [{ "system": "email",
                                 "value": "626838@unizar.es",
                                 }],
                   "url": "https://procesado.ehealthz.es",
                   "note": [{"authorString" : "Daniel Vicente Moya",
                             "time" : "2018-04-25T13:52:07+02:00",
                             "text": "Device en estado de desarrollo y pruebas"
                             }]
                   }
        payload = json.dumps(payload)

        #Petición post a la base de datos para crear recursos
        ##Device
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
        conn.request('POST', config['URL_FHIR']+"Device", payload, headers)
        r = conn.getresponse()
        header = r.getheaders()
        data = r.read()
        print(r.status, r.reason, 'DB_FHIR Creation Device')
        data = json.loads(data)
        print(data)

        conn.close()

    #Se comprueba si esta creado
    ##DeviceMetric
    #Petición get a la base de datos
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('GET', config['URL_FHIR']+"DeviceMetric?identifier:value=Procesado_imagen_Metric", headers=headers)
    r = conn.getresponse()              #777
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation GET DeviceMetric')
    data = json.loads(data)
    print(data)
    
    conn.close()

    if int(data['total']) != 0:
        pass           #Si ya está creado no lo vuelve a crear.
    else:
        ##DeviceMetric
        payload2 = {"resourceType" : "DeviceMetric",
                    #"id": "777", #Se establece id fija (cambiar si está ocupada en el DB)
                    "identifier" : {"use": "temp",
                                    "value": "Procesado_imagen_Metric",
                                    "assigner": "UNIZAR"
                                    },
                    "type" : {"coding":[{"system": "urn:iso:std:iso:11073:10101",
                                         "code": "_BSA",
                                         "display": "Body Surface Area"
                                         }],
                              "text": "Área superficie del cuerpo"
                              },
                    "unit" : {"coding":[{"system": "http://unitsofmeasure.org",
                                         "code": "cm2",
                                         "display": "square centimeter"
                                         }],
                              "text": "centímetros cuadrados"
                              },
                    "source" : {"identifier": { "use": "temp",
                                                "value": "Procesado_imagen",
                                                "assigner": "UNIZAR"
                                                }},
                    #"parent" : {"reference": "Procesado_imagen_Component"},
                    "operationalStatus" : "off", # on | off | standby | entered-in-error
                    "color" : "red",
                    "category" : "measurement"
                    }
        payload2 = json.dumps(payload2)

        #Petición post a la base de datos para crear recursos
        ##DeviceMetric
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
        conn.request('POST', config['URL_FHIR']+"DeviceMetric", payload2, headers)
        r = conn.getresponse()
        header = r.getheaders()
        data = r.read()
        print(r.status, r.reason, 'DB_FHIR Creation DeviceMetric')
        data = json.loads(data)
        print(data)
    
        conn.close()


# Función para actualizar el estado del device
def device_update_DB(estado): #active, inactive
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']

    #Mensajes a enviar
    ##Device
    payload = {"resourceType": "Device",
               #"id": "776", #sujeto a cambios en el DB
               "identifier": [{ "use": "temp",
                                "value": "Procesado_imagen",
                                "assigner": "UNIZAR"
                                }],
               "status": estado,# active | inactive | entered-in-error | unknown
               "type" : { "coding": [{"system": "http://snomed.info/sct",
                                      "code": "701654001",
                                      "display": "Self-care monitoring web-based application software"
                                      }],
                          "text": "Aplicación móvil de monitoirzación"
                          },
               "version": "1.0",
               "contact": [{ "system": "email",
                             "value": "626838@unizar.es"
                             }],
               "url": "https://procesado.ehealthz.es",
               "note": [{"authorString" : "Daniel Vicente Moya",
                         "time" : "2018-04-25T13:52:07+02:00",
                         "text": "Device en estado de desarrollo y pruebas"
                         }]
               }
    payload = json.dumps(payload)
    
    ##DeviceMetric
    if estado == "active":
        status = "on"
    elif estado == "inactive":
        status = "off"
    else:
        status = "entered-in-error"
    
    payload2 = {"resourceType" : "DeviceMetric",
                #"id": "777", #sujeto a cambios en el DB
                "identifier" : {"use": "temp",
                                "value": "Procesado_imagen_Metric",
                                "assigner": "UNIZAR"
                                },
                "type" : {"coding":[{"system": "urn:iso:std:iso:11073:10101",
                                     "code": "_BSA",
                                     "display": "Body Surface Area"
                                     }],
                          "text": "Área superficie del cuerpo"
                          },
                "unit" : {"coding":[{"system": "http://unitsofmeasure.org",
                                     "code": "cm2",
                                     "display": "square centimeter"
                                     }],
                          "text": "centímetros cuadrados"
                          },
                "source" : {"identifier": { "use": "temp",
                                            "value": "Procesado_imagen",
                                            "assigner": "UNIZAR"
                                            }},
                #"parent" : {"reference": "Procesado_imagen_Component"},
                "operationalStatus" : status, # on | off | standby | entered-in-error
                "color" : "red",
                "category" : "measurement"
                }
    payload2 = json.dumps(payload2)

    #Petición put a la base de datos para actualizar recursos
    ##Device
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('PUT', config['URL_FHIR']+"Device?identifier:value=Procesado_imagen", payload, headers)#La id del Device puede estar sujeta a cambios (se recomienda comporbaren el DB)
    r = conn.getresponse()
    header = r.getheaders()
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Update Device')
    data = json.loads(data)
    print(data)

    ##DeviceMetric
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('PUT', config['URL_FHIR']+"DeviceMetric?identifier:value=Procesado_imagen_Metric", payload2, headers) #La id del DeviceMetric puede estar sujeta a cambios (se recomienda comporbaren el DB)
    r = conn.getresponse()
    header = r.getheaders()
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Update DeviceMetric')
    data = json.loads(data)
    print(data)
    
    conn.close()


# Función crear request para el device
def DB_device_request_creation():
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']

    #Se comprueba si esta creado
    #Petición get a la base de datos
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('GET', config['URL_FHIR']+"DeviceRequest?identifier:value=Monitorizacion_Psoriasis", headers=headers)
    r = conn.getresponse()
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation GET DeviceRequest')
    data = json.loads(data)
    print(data)
    
    conn.close()

    if int(data['total']) != 0:
        pass           #Si ya está creado no lo vuelve a crear.
    else:
        #Mensaje a enviar
        payload = {"resourceType": "DeviceRequest",
                   #"id": "798", #sujeto a cambios en el DB
                   "identifier" : [{"use": "temp",
                                    "value": "Monitorizacion_Psoriasis",
                                    "assigner": "UNIZAR"
                                    }],
                   "intent" : {"coding": [{"system": "http://hl7.org/fhir/request-intent",
                                           "code": "proposal",
                                           "display": "Proposal"
                                           }]
                                         },
                   #"priority" : "routine",
                   "subject" : {"identifier": [{ "use": "temp",
                                                 "value": "Procesado_imagen",
                                                 "assigner": "UNIZAR"
                                                 }]},
                   "authoredOn" : time.strftime("%Y-%m-%d"+"T"+"%I:%M:%S"+"+02:00"),
                   "reasonCode" : [{"coding": [{"system": "http://snomed.info/sct",
                                                "code": "9014002",
                                                "display": "psoriasis"
                                                }]
                                    }]
                   }
        payload = json.dumps(payload)

        #Petición post a la base de datos para crear recurso
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
        conn.request('POST', config['URL_FHIR']+"DeviceRequest", payload, headers)
        r = conn.getresponse()
        header = r.getheaders()
        data = r.read()
        print(r.status, r.reason, 'DB_FHIR Create DeviceRequest')
        data = json.loads(data)
        print(data)

        conn.close()


# Función crear el procedure request
def DB_procedure_request_creation():
    #Disposición de Headers
    token = tokens.server_token().get_tokenDB()
    headers['Authorization'] = 'Bearer ' + token['Data']['id_token']

    #Se comprueba si esta creado
    #Petición get a la base de datos
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
    conn.request('GET', config['URL_FHIR']+"ProcedureRequest?identifier:value=Procedure_Monitorizacion_Psoriasis", headers=headers)
    r = conn.getresponse()
    header = r.getheaders()
    #print(header)
    data = r.read()
    print(r.status, r.reason, 'DB_FHIR Operation GET ProcedureRequest')
    data = json.loads(data)
    print(data)
    
    conn.close()

    if int(data['total']) != 0:
        pass           #Si ya está creado no lo vuelve a crear.
    else:
        #Mensaje a enviar
        payload = {"resourceType": "ProcedureRequest",
                   #"id": "800",
                   "identifier" : [{"use": "temp",
                                    "value": "Procedure_Monitorizacion_Psoriasis",
                                    "assigner": "UNIZAR"
                                    }],
                   "replaces" : [{"identifier" : {"use": "temp",
                                                  "value": "Monitorización_Psoriasis",
                                                  "assigner": "UNIZAR"
                                                  }}],
                   "status" : "active",
                   "intent" : "proposal",
                   #"priority" : "routine",
                   "code": {"coding": [{"system": "http://snomed.info/sct",
                                        "code": "701654001",
                                        "display": "Self-care monitoring web-based application software"
                                        }],
                            },
                   "subject" : {"identifier": { "use": "temp",
                                                "value": "Procesado_imagen",
                                                "assigner": "UNIZAR"
                                                }},
                   "authoredOn" : time.strftime("%Y-%m-%d"+"T"+"%I:%M:%S"+"+02:00"),
                   "reasonCode" : [{"coding": [{"system": "http://snomed.info/sct",
                                                "code": "9014002",
                                                "display": "psoriasis"
                                                }]
                                    }]
                   }
        payload = json.dumps(payload)

        #Petición post a la base de datos para crear recurso
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        conn = http.client.HTTPSConnection(config['HOSTNAME'], config['PORT'], context=context)
        conn.request('POST', config['URL_FHIR']+"ProcedureRequest", payload, headers)
        r = conn.getresponse()
        header = r.getheaders()
        data = r.read()
        print(r.status, r.reason, 'DB_FHIR Create ProcedureRequest')
        data = json.loads(data)
        print(data)

        conn.close()


#if __name__ == "__main__":
    #DB_device("active")
    #import cv2
    #tokens.server_token().get_token()
    #get_image('Media/457', 'usuario')
    #imagen = cv2.imread('imagenes/temp_imag.jpg')
    #cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    #cv2.resizeWindow('image',600,600)
    #cv2.imshow('image',imagen)
    
    #post_data(63633,"Patient/416")
    
    #device_update_DB("active")
