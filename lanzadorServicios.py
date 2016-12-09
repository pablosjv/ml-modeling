import json
import sys
import requests
import itertools
from subprocess import call
import threading


def stopService(nameService):
    call([
        './rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'stop', nameService])

access_key = '377EC393AE145A755881'
secret_key = 'chk1Le5mmAJAMfB1ddNLbyL5yEC4sDPKmCV28bEL'
url = 'http://185.24.5.232:8080/'
url_catalog = 'http://185.24.5.232:8080/v1-catalog/templates/myRancher-Catalog:TestCatalog:0'
project_name = 'Mensajes'
cont = 0
parametros=[]
threads = []

time_out = '3000'

#Peticion a la API para obtener el dockercompose
auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
r = requests.get(url=url_catalog, auth=auth)
content_all = r.json()
content_dockercompose = str(content_all["files"]["docker-compose.yml"])

#Lectura de los parametros de entrada
entradas = open('entradas.txt', 'r')
for line in entradas:
    parametros.append(line.split('=')[1].split(', '))
entradas.close

#iteracion para lanzar las combinaciones entre los parametros de entrada
for param in itertools.product(*parametros):
    #Escritura del fichero de respuestas
    answers = open('answers.txt', 'w')
    answers.write('PARAM1=' + param[0] + '\nPARAM2=' + param[1])
    answers.close()
    #Cambio de nombre de servicio en el dockercompose
    dockercompose = open('docker-compose.yml', 'w')
    dockercompose.write(content_dockercompose.replace(
        'mensajes1',
        'mensajes{num}'.format(num=cont)))
    dockercompose.close()
    nameService = 'mensajes{num}'.format(num=cont)
    #Llamadas a rancher-compose
    call([
        './rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', project_name,
        'create'])
    call([
        './rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', project_name,
        'start'])

    threads.append(threading.Timer(20.0, stopService, args=[nameService]))
    threads[cont].start()


    cont = cont + 1



# # Set the url that Rancher is on
# export RANCHER_URL=http://185.24.5.232:8080/
# # Set the access key, i.e. username
# export RANCHER_ACCESS_KEY=377EC393AE145A755881
# # Set the secret key, i.e. password
# export RANCHER_SECRET_KEY=chk1Le5mmAJAMfB1ddNLbyL5yEC4sDPKmCV28bEL
