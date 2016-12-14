# coding=utf-8
import json
import sys
import requests
import itertools
from subprocess import call
import threading
import yaml
import numpy

def stopService(name_stack):
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])

sys.stdout.write("ENTRÓ EN EL LANZADOR DE STACKS\n")
#project_name = 'Model'
cont = 0
parametros=[]
parametrosNombre=[]
threads = []
time_out = 30.0

#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
sys.stdout.write("url de las entradas:"+url_entradas+"\n")
access_key = str(sys.argv[2])
sys.stdout.write("access key:"+access_key+"\n")
secret_key = str(sys.argv[3])
sys.stdout.write("secret key:"+secret_key+"\n")
url = str(sys.argv[4])
sys.stdout.write("url del rancher:"+url+"\n")
url_catalog = str(sys.argv[5])
sys.stdout.write("url del stack a lanzar:"+url_catalog+"\n")


#Peticion a la API para obtener el dockercompose
auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
r = requests.get(url=url_catalog, auth=auth)
content_all = r.json()
sys.stdout.write("Obtenido el objeto JSON de la API\n")
content_dockercompose = str(content_all["files"]["docker-compose.yml"])
docker_compose = open('docker-compose.yml', 'w')
docker_compose.write(content_dockercompose)
docker_compose.close()


#https://dl.dropboxusercontent.com/u/92981874/entradas.yml
entradas = requests.get(url=url_entradas)
entradas = yaml.load(entradas.text)
sys.stdout.write("Obtenido el fichero de configuracion\n")

#Lectura de los parametros de entrada -> FUNCIONA BIEN PERO NO SON EL TIPO DE PARAMETROS QUE SE VAN A RECIBIR
#for parametro in entradas:
#    parametrosNombre.append(parametro)
#    parametros.append(entradas[parametro])
#parametrosNombre = parametrosNombre[::-1]
#parametros = parametros[::-1]
#Lo mismo que lo de arriba pero teniendo en cuenta diferentes formas de configuración
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
    elif(opcion==2):
        #opcionesParametro
        pass
    elif(opcion=="absolute"):
        parametros.append(entradas[parametro]["param"])
parametrosNombre = parametrosNombre[::-1]
parametros = parametros[::-1]
sys.stdout.write("Obtenidos los parametros\n")

# entradas = open('./entradas.txt', 'r')
# for line in entradas:
#     parametrosNombre.append(line[0:line.index(">")])
#     parametros.append(line.split('>')[1].split(', '))
# entradas.close()

#iteracion para lanzar las combinaciones entre los parametros de entrada
for param in itertools.product(*parametros):
    #Escritura del fichero de respuestas
    answers = open('answers.txt', 'w')
    for j in range(len(parametrosNombre)):
        answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')
    answers.close()
    project_name = 'Model{num}'.format(num=cont)
    sys.stdout.write("Preparado para lanzar stack\n")
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



# # Set the url that Rancher is on
# export RANCHER_URL=http://185.24.5.232:8080/
# # Set the access key, i.e. username
# export RANCHER_ACCESS_KEY=377EC393AE145A755881
# # Set the secret key, i.e. password
# export RANCHER_SECRET_KEY=chk1Le5mmAJAMfB1ddNLbyL5yEC4sDPKmCV28bEL
