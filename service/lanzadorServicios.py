# coding=utf-8
import json
import sys
import requests
import itertools
from subprocess import call, Popen, PIPE
import threading
import yaml
import numpy
import logging

# TODO: Add an argeparser
# import argparse or click


# TODO: Tecnica para recoger los logs usando la cli
# El problema principal reside en identificar los containers dentro de los stacks pero se puede hacer
# comando rancher logs [ID-container] da los logs de ese container
# Comando rancher inspect [NOMBRE_DEL_STACK] da un json con info del stack. Tiene un apartado que es serviceIds,
# que da una lista con los ids de los containers del stack.
# Combinando estos dos comandos podemos obtener los logs usando el mismo nombre que le damos al stack (Model+numero)
# NOTA: Hay que mirar donde echa esos logs. Creo que los saca por salida estandar
# PROBLEMA: Si hay diferentes containers en el stack habrá que mirar todos los logs y puede ser un jaleo. Pero se puede hacer porque se pueden recorrer en forma de lista.

# TODO: Configurar el limite para los experimentos. La técnica es la siguiente:
# Mediante la CLI de Rancher, se puede acceder como esta explicado anteriormente a los serviceIds que son los containers dentro de un stack.
# Si hacemos rancher inspect con la CLI en esos containers podemos ver su estado. El json que nos devuelve tiene un apartado que es
# "state" que puede ser active o inactive. Con esto podemos ver si han acabado o no los stacks. Despues de eso obtener los logs y parar el servicio


def getLogsContainer(name_stack):

    logging.critical('Obteniendo logs para'+name_stack)
    llamadaInspect = Popen(
        ['./exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'inspect',name_stack],
        stdout=PIPE)
    logging.critical('Obteniendo serviceIds')
    (out, err) = llamadaInspect.communicate()
    if err:
        logging.critical('ERROR EN LA LLAMADA A RANCHER INSPECT')
        raise SyntaxError('Parametros en el yml de entradas incorectos')
    else:
        logging.critical('Llamada a rancher inspect correcta')

    info_stack = json.loads(out.decode('utf-8'))

    for service in info_stack['serviceIds']:
        logging.critical('Logs del servicio'+service)
        llamadaLogs = Popen(
            ['./exec/rancher',
            '--url', url,
            '--access-key', access_key,
            '--secret-key', secret_key,
            'logs',service],
            stdout=PIPE)
        logging.critical('Obteniendo serviceIds')
        (out, err) = llamadaLogs.communicate()
        if err:
            logging.critical('ERROR EN LA LLAMADA A RANCHER LOGS')
            raise SyntaxError('Parametros en el yml de entradas incorectos')
        else:
            logging.critical('Llamada a rancher logs correcta')
        service_logs = out.decode('utf-8')
        # TODO: Decidir que hacer con los logs
        print(service_logs)

# Borra el stack
def stopService(name_stack):

    getLogsContainer(name_stack=name_stack)
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])

# TODO: Set up del logger en condiciones. Ahora todo esta a critical. Puede que interese que escriba en algun lado
# logger = logging.getLogger('services_launcher')

logging.critical('ENTRÓ EN EL LANZADOR DE STACKS')

# TODO: Dar nombre bien a los esperimentos lanzados.
#project_name = 'Model'
cont = 0
parametros=[]
parametrosNombre=[]
threads = []
# TODO: Hacer configurable el parametro time_out
time_out = 60.0

#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
logging.critical('url de las entradas:'+url_entradas)
access_key = str(sys.argv[2])
logging.critical('access key:'+access_key)
secret_key = str(sys.argv[3])
logging.critical('secret key:'+secret_key)
url = str(sys.argv[4])
logging.critical('url del rancher:'+url)
url_catalog = str(sys.argv[5])
logging.critical('url del stack a lanzar:'+url_catalog)


#Peticion a la API para obtener el dockercompose
auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
r = requests.get(url=url_catalog, auth=auth)
content_all = r.json()
logging.critical('Obtenido el objeto JSON de la API')

content_dockercompose = str(content_all['files']['docker-compose.yml'])
docker_compose = open('docker-compose.yml', 'w')
docker_compose.write(content_dockercompose)
docker_compose.close()

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logging.critical('Obtenido el fichero de configuracion para los parametros')

#Las distintas formas que se consideran son: parametroNombre->n
#1. [valorInicial:valorFinal:Salto] -> Lineal
#2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
#3. [un String]
for parametro in entradas:
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
