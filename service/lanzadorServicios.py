import json
import sys
import requests
import itertools
from subprocess import call
import threading
import yaml

def stopService(name_stack):
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])


project_name = 'Model'
cont = 0
parametros=[]
parametrosNombre=[]
threads = []
time_out = 30.0

#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
access_key = str(sys.argv[2])
secret_key = str(sys.argv[3])
url = str(sys.argv[4])
url_catalog = str(sys.argv[5])

#Peticion a la API para obtener el dockercompose
auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
r = requests.get(url=url_catalog, auth=auth)
content_all = r.json()
content_dockercompose = str(content_all["files"]["docker-compose.yml"])

#https://dl.dropboxusercontent.com/u/92981874/entradas.yml
entradas = requests.get(url=url_entradas)
entradas = yaml.load(entradas.text)
#Lectura de los parametros de entrada
for parametro in entradas:
    parametrosNombre.append(parametro)
    parametros.append(entradas[parametro])

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
