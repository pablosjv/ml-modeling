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


# Borra el stack TODO: Reformat el nombre->kill stack o algo asi y sin camelcase
def rm_stack(name_stack, url, access_key, secret_key):

    getLogsContainer(name_stack=name_stack)
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])
    stacksRunning -= 1

def create_stack(name_stack, url, access_key, secret_key):
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'create'])

def start_stack(name_stack, url, access_key, secret_key):
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'start'])

# TODO: hacer una clase bien definida con las operaciones para stack
class stack_manager(threading.Thread):
    def __init__(self, name_stack, timeout):
        threading.Thread.__init__(self)
        self.name_stack = name_stack
        self.timeout = timeout

    def run(self):
        # self.p = sub.Popen(self.cmd)
        # self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()      #use self.p.kill() if process needs a kill -9
            self.join()

# TODO: Set up del logger en condiciones. Ahora todo esta a critical. Puede que
# interese que escriba en algun lado
# logger = logging.getLogger('services_launcher')


# TODO: Configurar el limite para los experimentos. La técnica es la siguiente:
# Mediante la CLI de Rancher, se puede acceder a los serviceIds que son los
# containers dentro de un stack. Si hacemos rancher inspect con la CLI en esos
# containers podemos ver su estado.
# El json que nos devuelve tiene un apartado que es "state" que puede ser active
# o inactive. Con esto podemos ver si han acabado o no los stacks. Despues de
# eso obtener los logs y parar el servicio


def get_logs_container(name_stack, url, access_key, secret_key):

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



logging.critical('ENTRÓ EN EL LANZADOR DE STACKS')

# TODO: Dar nombre bien a los esperimentos lanzados.
#project_name = 'Model'
parametrosNombre=[]
parametros = []
threads = []
time_out = 10
# TODO: Hacer configurable el parametro time_out y stack_limit
sincronizacion = threading.Semaphore(value=stack_limit)
stack_limit = 100000

# TODO: Add argparse
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
logging.critical(content_all)

# TODO: Context manager -> with statement
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
cont = 0
#parametros = entradas["PARAMS"]
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
logging.critical("Nombre parametros:")
logging.critical(parametrosNombre)
logging.critical("Parametros:")
logging.critical(parametros)


#Iteracion para lanzar las combinaciones entre los parametros de entrada
for param in itertools.product(*parametros):
    #Escritura del fichero de respuestas
    # TODO: Context manager -> with statement
    answers = open('answers.txt', 'w')
    for j in range(len(parametrosNombre)):
        answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')
        logging.critical(parametrosNombre[j]+'='+str(param[j])+'\n')
    answers.close()
    project_name = 'Model{num}'.format(num=cont)
    logging.critical('Preparado para lanzar stacks')

    #Llamadas a rancher-compose
    create_stack(
        name_stack=project_name,
        url=url,
        access_key=access_key,
        secret_key=secret_key)
    start_stack(
        name_stack=project_name,
        url=url,
        access_key=access_key,
        secret_key=secret_key))

    threads.append(threading.Timer(time_out, rm_stack, args=[project_name, url, access_key, secret_key]))
    threads[cont].start()

    cont = cont + 1
