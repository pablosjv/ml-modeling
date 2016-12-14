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

def stopService(name_stack):
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])

#Set up del logger
# logger = logging.getLogger('services_launcher')

logging.critical('ENTRÓ EN EL LANZADOR DE STACKS')
#sys.stdout.write("ENTRÓ EN EL LANZADOR DE STACKS\n")
#project_name = 'Model'
cont = 0
parametros=[]
parametrosNombre=[]
threads = []
time_out = 30.0

#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
logging.critical('url de las entradas:'+url_entradas)
# sys.stdout.write("url de las entradas:"+url_entradas+"\n")
access_key = str(sys.argv[2])
logging.critical('access key:'+access_key)
# sys.stdout.write("access key:"+access_key+"\n")
secret_key = str(sys.argv[3])
logging.critical('secret key:'+secret_key)
# sys.stdout.write("secret key:"+secret_key+"\n")
url = str(sys.argv[4])
logging.critical('url del rancher:'+url)
# sys.stdout.write("url del rancher:"+url+"\n")
url_catalog = str(sys.argv[5])
logging.critical('url del stack a lanzar:'+url_catalog)
# sys.stdout.write("url del stack a lanzar:"+url_catalog+"\n")


#Peticion a la API para obtener el dockercompose
auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
r = requests.get(url=url_catalog, auth=auth)
content_all = r.json()
logging.critical('Obtenido el objeto JSON de la API')
# sys.stdout.write("Obtenido el objeto JSON de la API\n")
content_dockercompose = str(content_all["files"]["docker-compose.yml"])
docker_compose = open('docker-compose.yml', 'w')
docker_compose.write(content_dockercompose)
docker_compose.close()

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logging.critical('Obtenido el fichero de configuracion')
# sys.stdout.write("Obtenido el fichero de configuracion\n")

#Las distintas formas que se consideran son: parametroNombre->n
#1. [valorInicial:valorFinal:Salto] -> Lineal
#2. [valorInicial:valorFinal:Función] -> Otro tipo de funcion
#3. [un String]
for parametro in entradas:
    parametrosNombre.append(parametro)
    opcion = entradas[parametro]["type"] #parametro[parametro.index("{"):parametro.index("}")]
    if(opcion=="lineal"):
        valorInicial = entradas[parametro]["initial-value"]
        valorFinal = entradas[parametro]["final-value"]
        valorSalto = entradas[parametro]["interval"]
        opcionesParametro = numpy.arange(valorInicial, valorFinal, valorSalto)
        parametros.append(opcionesParametro.tolist())
    # elif(opcion==2):
    #     #opcionesParametro
    #     pass
    elif(opcion=="absolute"):
        parametros.append(entradas[parametro]["param"])
parametrosNombre = parametrosNombre[::-1]
parametros = parametros[::-1]
logging.critical('Obtenida la lista de posibles parametros')
# sys.stdout.write("Obtenidos los parametros\n")


#iteracion para lanzar las combinaciones entre los parametros de entrada
for param in itertools.product(*parametros):
    #Escritura del fichero de respuestas
    answers = open('answers.txt', 'w')
    for j in range(len(parametrosNombre)):
        answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')
    answers.close()
    project_name = 'Model{num}'.format(num=cont)
    logging.critical('Preparado para lanzar stacks')

    # sys.stdout.write("Preparado para lanzar stack\n")
    #Llamadas a rancher-compose
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', project_name,
        'create'])
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', project_name,
        'start'])

    threads.append(threading.Timer(time_out, stopService, args=[project_name]))
    threads[cont].start()

    cont = cont + 1
