import json
import sys
import requests
import itertools
from subprocess import call
import threading


def stopService(name_stack):
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])


project_name = 'Mensajes'
cont = 0
parametros=[]
parametrosNombre=[]
threads = []
time_out = 30.0

#Lectura de parametros para las url y las keys
access_key = str(sys.argv[1])
print(access_key)
secret_key = str(sys.argv[2])
print(secret_key)
url = str(sys.argv[3])
print(url)
url_catalog = str(sys.argv[4])
print(url_catalog)

#Peticion a la API para obtener el dockercompose
auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
r = requests.get(url=url_catalog, auth=auth)
content_all = r.json()
content_dockercompose = str(content_all["files"]["docker-compose.yml"])

#Lectura de los parametros de entrada
entradas = open('./entradas.txt', 'r')
for line in entradas:
    parametrosNombre.append(line[0:line.index(">")])
    parametros.append(line.split('>')[1].split(', '))
entradas.close()

#iteracion para lanzar las combinaciones entre los parametros de entrada
for param in itertools.product(*parametros):
    #Escritura del fichero de respuestas
    answers = open('answers.txt', 'w')
    for j in range(len(parametrosNombre)):
        answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')
    answers.close()
    #Cambio de nombre de servicio en el dockercompose
    dockercompose = open('docker-compose.yml', 'w')
    dockercompose.write(content_dockercompose.replace(
        'mensajes1',
        'mensajes{num}'.format(num=cont)))
    dockercompose.close()
    project_name = 'mensajes{num}'.format(num=cont)
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
