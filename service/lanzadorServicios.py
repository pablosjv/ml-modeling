# coding=utf-8
import json
import sys
import requests
import itertools
from subprocess import call
import threading
import yaml
import numpy
import logging

# TODO: Add an argeparser
# import argparse or click

def stopService(name_stack):
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])
    stacksRunning -= 1

def createService(name_stack):
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'create'])

def startService(name_stack):
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'start'])

# TODO: Set up del logger en condiciones. Ahora todo esta a critical. Puede que interese que escriba en algun lado
# logger = logging.getLogger('services_launcher')

logging.critical('ENTRÓ EN EL LANZADOR DE STACKS')

# TODO: Dar nombre bien a los esperimentos lanzados.
#project_name = 'Model'
parametrosNombre=[]
threads = []
catalogs = []
catalogName = ''

#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
logging.critical('url de las entradas:'+url_entradas)
"""
access_key = str(sys.argv[2])
logging.critical('access key:'+access_key)
secret_key = str(sys.argv[3])
logging.critical('secret key:'+secret_key)
url = str(sys.argv[4])
logging.critical('url del rancher:'+url)
url_catalog = str(sys.argv[5])
logging.critical('url del stack a lanzar:'+url_catalog)
"""

#Peticion a la API para obtener el dockercompose
#auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
#r = requests.get(url=url_catalog, auth=auth)
#content_all = r.json()
#logging.critical('Obtenido el objeto JSON de la API')

#content_dockercompose = str(content_all['files']['docker-compose.yml'])
#docker_compose = open('docker-compose.yml', 'w')
#docker_compose.write(content_dockercompose)
#docker_compose.close()

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logging.critical('Obtenido el fichero de configuracion para los parametros')

time_stop = entradas["time_stop"]
limitStacks = entradas["limit_stacks"]
stacksRunning = 0
for catalog in entradas["stacks_catalog"]:
    catalogName = catalog
    cont = 0
    getConfiguration(catalog)

def getConfiguration(catalog):
    url_catalog = catalog["URL_API"]
    access_key = catalog["ACCESS_KEY"]
    secret_key = catalog["SECRET_KEY"]
    url = catalog["URL_RANCHER"]
    #Peticion a la API para obtener el dockercompose
    auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
    r = requests.get(url=url_catalog, auth=auth)
    content_all = r.json()
    logging.critical('Obtenido el objeto JSON de la API')
    content_dockercompose = str(content_all['files']['docker-compose.yml'])
    docker_compose = open('docker-compose.yml', 'w')
    docker_compose.write(content_dockercompose)
    docker_compose.close()
    parametros = catalog["PARAMS"]
    getParams(parametros)

def getParams(parametrosYml):
    parametros=[]
    #Las distintas formas que se consideran son: parametroNombre->n
    #1. [valorInicial:valorFinal:Salto] -> Lineal
    #2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
    #3. [un String]
    for parametro in parametrosYml:
        parametrosNombre.append(parametro)
        opcion = entradas[parametro]['type'] #parametro[parametro.index("{"):parametro.index("}")]
        if(opcion=='lineal'):
            valorInicial = entradas[parametro]['initial-value']
            valorFinal = entradas[parametro]["final-value"]
            valorSalto = entradas[parametro]["interval"]
            opcionesParametro = numpy.arange(valorInicial, valorFinal, valorSalto)
            parametros.append(opcionesParametro.tolist())
        elif(opcion==2):
            #opcionesParametro
            pass
        elif(opcion=="absolute"):
            parametros.append(entradas[parametro]["param"])
        else:
            logging.critical('ERROR: FORMATO DE PARAMETROS INCORRECTO')
            raise SyntaxError('Parametros en el yml de entradas incorectos')

    parametrosNombre = parametrosNombre[::-1]
    parametros = parametros[::-1]
    logging.critical('Obtenida la lista de posibles parametros')

    for param in itertools.product(*parametros):
        #Escritura del fichero de respuestas
        answers = open('answers.txt', 'w')
        for j in range(len(parametrosNombre)):
            answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')
        answers.close()
        project_name = ''.join([catalogName,'Model{num}'.format(num=cont)])
        logging.critical('Preparado para lanzar stacks')

        #Llamadas a rancher-compose
        createService(project_name)
        startService(project_name)

        while(stacksRunning>=limitStacks):
            pass

        threads.append(threading.Timer(time_stop, stopService, args=[project_name]))
        threads[cont].start()
        stacksRunning += 1
        cont = cont + 1

#Las distintas formas que se consideran son: parametroNombre->n
#1. [valorInicial:valorFinal:Salto] -> Lineal
#2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
#3. [un String]
"""
parametros = entradas["PARAMS"]
for parametro in parametros:
    parametrosNombre.append(parametro)
    opcion = entradas[parametro]['type'] #parametro[parametro.index("{"):parametro.index("}")]
    if(opcion=='lineal'):
        valorInicial = entradas[parametro]['initial-value']
        valorFinal = entradas[parametro]["final-value"]
        valorSalto = entradas[parametro]["interval"]
        opcionesParametro = numpy.arange(valorInicial, valorFinal, valorSalto)
        parametros.append(opcionesParametro.tolist())
    elif(opcion==2):
        #opcionesParametro
        pass
    elif(opcion=="absolute"):
        parametros.append(entradas[parametro]["param"])
    else:
        logging.critical('ERROR: FORMATO DE PARAMETROS INCORRECTO')
        raise SyntaxError('Parametros en el yml de entradas incorectos')
parametrosNombre = parametrosNombre[::-1]
parametros = parametros[::-1]
logging.critical('Obtenida la lista de posibles parametros')


#iteracion para lanzar las combinaciones entre los parametros de entrada
for param in itertools.product(*parametros):
    #Escritura del fichero de respuestas
    answers = open('answers.txt', 'w')
    for j in range(len(parametrosNombre)):
        answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')
    answers.close()
    project_name = 'Model{num}'.format(num=cont)
    logging.critical('Preparado para lanzar stacks')

    #Llamadas a rancher-compose
    createService(project_name)
    startService(project_name)

    threads.append(threading.Timer(time_stop, stopService, args=[project_name]))
    threads[cont].start()

    cont = cont + 1
"""