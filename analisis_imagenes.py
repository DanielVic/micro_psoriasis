#Funciones para el análisis de la imagen
#Daniel Vicente Moya
#24/11/2017


import cv2
import numpy as np
import math

__author__ = 'Daniel Vicente Moya'
__date__ = '18/01/2018'
__version__ = '1.0'


MARCADOR = 28 #cm2 de area aproximada de marcador (radio = 3cm)


###Función para el cargado de la imagen
def cargar_imagen(image):
        #Cargado imagen
    try:
        img = cv2.imread(image)
        return img
        
    except:
        print("Problema con el cargado de la imágen")
        return


###Función para el guardado de la imagen    
def guardar_imagen(location, image):
    #Guardado de la imagen
    try:
        cv2.imwrite(location,image)

    except:
        print("Problema con el guardado de la imágen")
        return

 
###Función para el recorte de la zona delimitada por los marcadores
def recorte(image, save_location): #RGB, Gray
    img = cargar_imagen(image)
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ##Detección de circulos de los marcadores
    circles = cv2.HoughCircles(imgray, cv2.HOUGH_GRADIENT, 2, 100, minRadius=100, maxRadius=300);

    circles = np.uint16(np.around(circles))
    centros = []
    radios = []
    for i in circles[0,:]:
        #Extraer centros
        centros.append([i[0],i[1]])
        radios.append(i[2])

    #Se calcula el área del marcador para calculos posteriores de área
    r_media = np.sum(radios)/int(len(radios))
    area_marcador = math.pi * r_media**2
    area_marcador = int(np.around(area_marcador)) #redondeo
    
        

    #Se dibujan los circulos sobre los marcadores
    for marca in range(0,4):
        img = cv2.circle(img,tuple(centros[marca]),radios[marca] + 20,(0,0,0),-1)
        #imgray = cv2.circle(imgray,tuple(centros[marca]),radios[marca] + 10,(0,0,0),-1)

    ##Recorte del area contenida en los keypoints
    try:    
        centros = np.array(centros, dtype = np.int32)#transforma tipo list a array de enteros
        x,y,w,h = cv2.boundingRect(centros) #rectangulo del area de recorte
    
        recorte = img[y:y+h,x:x+w]   #región de interes recortada en la imagen
        recorte2 = imgray[y:y+h,x:x+w]     #región en la imagen a color

        #Guardado imagen recorte
        guardar_imagen(save_location, recorte)

        return area_marcador

    except:
        print("No se detectan los  marcadores correctamente")
        return    
    

###Función para detecctar áreas blancas
def blancos(image): #Imagen en escala RGB
    try:
        #cambio escala de colores
        hsvb = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
        kernelb = np.ones((7,7),np.uint8)  #10,10
        kernelb2 = np.ones((3,3),np.uint8)   #3,3
        kernelb3 = np.ones((5,5),np.uint8)   #5,5

        #Blancos (escamaciones)
        blancos_bajos = np.array([15, 0, 180], dtype=np.uint8)    #[15,0,180]
        blancos_altos = np.array([175, 60, 255], dtype=np.uint8)  #[175,60,255]

        #Máscara blanco
        mascara_blancos = cv2.inRange(hsvb, blancos_bajos, blancos_altos)
    
        #Dilatación erosión máscara blancos
        mascara_blancos = cv2.morphologyEx(mascara_blancos, cv2.MORPH_CLOSE, kernelb)
        mascara_blancos = cv2.erode(mascara_blancos,kernelb,iterations = 1) #1
        mascara_blancos = cv2.morphologyEx(mascara_blancos, cv2.MORPH_CLOSE, kernelb2)
        return mascara_blancos
    
    except:
        print("Problema en la detección de blancos")
        return



###Función para detecctar áreas rojas
def rojos(image): #Imagen en escala RGB
    try:
        #cambio escala de colores
        hsvr = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #Rojos
        rojo_bajos1 = np.array([0, 65, 0], dtype=np.uint8) #[0,65,75]
        rojo_altos1 = np.array([8, 255, 255], dtype=np.uint8) #[12, 255, 255] 8,,
        rojo_bajos2 = np.array([160, 65, 0], dtype=np.uint8) #[240,65,75] 160,,
        rojo_altos2 = np.array([180, 255, 255], dtype=np.uint8) #[255, 255, 255] 180,,

        #Máscara rojo
        mascara_rojo1 = cv2.inRange(hsvr, rojo_bajos1, rojo_altos1)
        mascara_rojo2 = cv2.inRange(hsvr, rojo_bajos2, rojo_altos2)
        mascara_rojos = cv2.add(mascara_rojo1, mascara_rojo2)

        #Dilatación erosión máscara rojos
        kernelr = np.ones((7,7),np.uint8)  #10,10
        kernelr2 = np.ones((3,3),np.uint8)   #3,3
        kernelr3 = np.ones((5,5),np.uint8)   #5,5
    
        mascara_rojos = cv2.morphologyEx(mascara_rojos, cv2.MORPH_CLOSE, kernelr)
        mascara_rojos = cv2.erode(mascara_rojos,kernelr,iterations = 1)  #2
        mascara_rojos = cv2.morphologyEx(mascara_rojos, cv2.MORPH_CLOSE, kernelr3)
        return mascara_rojos
    
    except:
        print("Problema en la detección de rojos")
        return


###Función para el umbralizado adaptativo
def bordes(image):  #Imagen en escala de grises
    ##Binarización
    try:
        #ret,th_g = cv2.threshold(imgray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #imagen,umbral,max,binarizado      
        th_g = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV,11,7) #11,7

        #Erosionado y dilatado
        kernel = np.ones((5,5),np.uint8)   #5,5
        kernel2 = np.ones((7,7),np.uint8)  #7,7
        kernel3 = np.ones((3,3),np.uint8)  #3,3
  
        closing = cv2.morphologyEx(th_g, cv2.MORPH_CLOSE, kernel)
        opening2 = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel2)
        dilation = cv2.dilate(opening2,kernel3,iterations = 1) #2
        return dilation
    
    except:
        print("Problema en la detección de bordes")
        return


###Función para detectar blobs de las máscaras
def deteccion(image,imagen_original):
    ##Extracción de blobs
    #Ajuste de parametros del detector
    params = cv2.SimpleBlobDetector_Params()

    # Filter by color
    params.blobColor= 255
    params.filterByColor = True
    # Min distance between blobs
    #params.minDistBetweenBlobs = 10
    # Change thresholds
    #params.minThreshold = 0;
    #params.maxThreshold = 255;
    # Filter by Area.
    params.filterByArea = False
    params.minArea = 10
    #params.maxArea = 100
    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0
    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0
    # Filter by Inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0
    # Create a detector with the parameters
    ver = (cv2.__version__).split('.')
    if int(ver[0]) < 3 :
        detector = cv2.SimpleBlobDetector(params)
    else : 
        detector = cv2.SimpleBlobDetector_create(params)
        
    #Detección de blobs
    keypoints = detector.detect(image)

    ##Mostrar por pantalla centro blobs
    try:
        #centros = []
        #for c in keypoints:
        #    centros.append(c.pt)
        #print(centros)    
 
        #Dibuja los blobs detectados
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        im_with_keypoints = cv2.drawKeypoints(imagen_original, keypoints, np.array([]),
                                             (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #Dibuja numero de blob
        aux = 1
        for c in keypoints:
            cv2.putText(im_with_keypoints, str(aux), (int(c.pt[0]), int(c.pt[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)
            aux = aux + 1
        
    except:
        print("Problema en la detección de blobs")
        return
    
    ##Detección del contorno
    try:
        [imagen, contours, hierarchy] = cv2.findContours(image,cv2.RETR_TREE,
                                                         cv2.CHAIN_APPROX_SIMPLE)
        
        #Dibujar contornos
        im_contours = cv2.drawContours(imagen_original, contours, -1, (0,0,255), 3)
    #Dibuja número de contorno (Por naturaleza de opencv es inestable)
    #try:
        puntos = []
        pix = []
        v_pixels = []
        aux = 1
        for c in contours:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            puntos.append([cX, cY])  #Guarda valor del punto
            #print(imagen_original.shape)
            pix = imagen_original[cY, cX]
            v_pixels.append([pix[0],pix[1],pix[2]])  #Guarda valor del pixel
            cv2.putText(im_contours, str(aux), (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)
            aux = aux + 1
    #except:
    #    pass

        #Extracción del área de cada contorno
        areas = []
        for c in contours:
            a = cv2.contourArea(c)
            areas.append(a)
        
    except:
        print("Problema en la detección de contornos")
        return

    return im_with_keypoints, im_contours, areas, puntos, v_pixels


###Función para eliminar el pelo sobre la zona de psoriasis
def eliminar_pelo(image):  
    ##Toma imagen en color y extrae canal rojo
    try:
        #image = cv2.imread(image)
        [x,y,c] = image.shape #extraemos tamaño imagen a operar
        imgR = image[:,:,2]  #extraemos rojos
        
    except:
        print("La imagen no dispone de tres canales de color para detectar pelo")
        return

    ##Equalizado de tonos rojos para resaltar contraste del pelo
    try:
        #Procesado detección de pelo por contraste
        #equ = cv2.equalizeHist(imgR)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(5,5))
        cl = clahe.apply(imgR)
        #Filtrado adaptativo
        #ret2,th_g = cv2.threshold(cl,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        th_g = cv2.adaptiveThreshold(cl,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV,11,7)

        #Recubre las zonas de pelo con color del los pixeles cercanos
        dst = cv2.inpaint(image,th_g,3,cv2.INPAINT_TELEA)
        return dst

    except:
        print('Problema en la detección del pelo a eliminar')
        return


###Función para extraer areas de piel
def zona_piel(image):
    ##Toma imagen en color RGB y la convierte a HSV
    try:
        [x,y,c] = image.shape #extraemos tamaño imagen a operar
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
    except:
        print("La imagen no dispone de tres canales de color para detectar piel")
        return

    ##Extrae máscara de piel y la 
    try:
        piel_bajos = np.array([0,0,0], dtype=np.uint8)
        piel_altos = np.array([50,255,255], dtype=np.uint8)
        #Máscara áreas de peil en la imagen
        mascara_piel = cv2.inRange(hsv, piel_bajos, piel_altos)

        #Extracción de la imagen
        for i1 in range(0,x):
            for i2 in range(0,y):
                if mascara_piel[i1,i2] == 0:
                    image[i1,i2,:] = 0
        return image

    except:
        print("problema en la detección de piel")



####Funciones de operación según tipología
def analisis(tarea,image,original,save_location_keypoint,save_location_contour):
    img = cargar_imagen(image)
    #img = cv2.GaussianBlur(img,(3,3),0) #Filtrado para eleiminar el posible ruido Gaussiano
    img_orig = cargar_imagen(original)
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #Máscaras
    if tarea == 'Gota':
        m_rojos = rojos(img)
        m_bordes = bordes (imgray)
        mask = cv2.add(m_rojos, m_bordes)
    elif tarea == 'Placa':
        m_blancos = blancos(img)
        m_rojos = rojos(img)
        m_bordes = bordes (imgray)
        mask = cv2.add(m_rojos, m_blancos)
        mask = cv2.add(mask, m_bordes)
    
    #Dilatación erosión de la máscara final
    kernel = np.ones((20,20),np.uint8)   #20,20  #7,7
    kernel2 = np.ones((10,10),np.uint8)  #10,10  #5,5
    kernel3 = np.ones((3,3),np.uint8)    #3,3
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel2)
    mask = cv2.dilate(mask,kernel3,iterations = 1)
    #mask = cv2.blur(mask,(3,3)) #smooth

    [im_keypoint, im_contour, area, puntos, v_pixels] = deteccion(mask, img_orig)
    #Guardado de imágenes obtenidas
    guardar_imagen(save_location_keypoint, im_keypoint)
    guardar_imagen(save_location_contour, im_contour)
    
    #Área total de psoriasis
    area_t = np.sum(area)
    area_t = int(np.around(area_t)) #redondeo
    
    return area_t, area, puntos, v_pixels


####Función de operación eliminar pelo
def quitar_pelo(image, save_location):
    img = cargar_imagen(image)
    img_elim = eliminar_pelo(img)
    guardar_imagen(save_location, img_elim)
    return


####Función para calcular el area en cm2
def calc_area(area, area_marcador):
    area = int(area)
    area_marcador = int(area_marcador)
    area_real_cm2 = (MARCADOR * area)/ area_marcador
    area_real_cm2 = int(np.around(area_real_cm2)) #redondeo
    return area_real_cm2
    


##if __name__ == "__main__":
##    im = cargar_imagen("imagenes/psoriasis01.jpg")
##    cv2.namedWindow('original',cv2.WINDOW_NORMAL)
##    cv2.resizeWindow('original',600,600)
##    cv2.imshow('original',im)
##    #im = cv2.GaussianBlur(im,(3,3),0)
##    #im = eliminar_pelo(im)
##    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
##    #imgray = im[:,:,2]
##    #im = zona_piel(im)
##    m_blancos = blancos(im)
##    m_rojos = rojos(im)
##    m_bordes = bordes (imgray)
##    mask = cv2.add(m_rojos, m_blancos)
##    #mask = m_rojos
##    #mask = m_blancos
##    #mask = m_bordes
##    mask = cv2.add(mask, m_bordes)
##    
##    #Dilatación erosión de la máscara final
##    kernel = np.ones((20,20),np.uint8)   #20,20  #7,7
##    kernel2 = np.ones((10,10),np.uint8)  #10,10  #5,5
##    kernel3 = np.ones((3,3),np.uint8)    #3,3
##    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
##    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel2)
##    mask = cv2.dilate(mask,kernel3,iterations = 1)
##    
##    imagen = deteccion(mask, im)
##    
##
##    cv2.namedWindow('image',cv2.WINDOW_NORMAL)
##    cv2.resizeWindow('image',600,600)
##    cv2.imshow('image',imagen[0])
##    cv2.namedWindow('image2',cv2.WINDOW_NORMAL)
##    cv2.resizeWindow('image2',600,600)
##    cv2.imshow('image2',imagen[1])
##    cv2.namedWindow('image3',cv2.WINDOW_NORMAL)
##    cv2.resizeWindow('image3',600,600)
##    cv2.imshow('image3',im)


##    im= cargar_imagen("imagenes/Maria2.jpg")
##    area = recorte("imagenes/Maria2.jpg","imagenes/Prueba.jpg")
##    print(area)
##
##
##    cv2.namedWindow('imagen inicial',cv2.WINDOW_NORMAL)
##    cv2.resizeWindow('imagen inicial',600,600)
##    cv2.imshow('imagen inicial',im)
##    cv2.namedWindow('imagen recorte',cv2.WINDOW_NORMAL)
##    cv2.resizeWindow('imagen recorte',600,600)
##    cv2.imshow('imagen recorte',m_rojos)
