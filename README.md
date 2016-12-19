<!-- TODO: Terminar correctamente la documentación -->
<!-- TODO: Añadir un readme para el catalogo  -->

# ml-modeling

Este proyecto servirá para las tareas de ml-modeling. El objetivo actual es lanzar varias instancias de un stack desde el catalogo de rancher con diferentes configuraciones que se darán mediante una lista. Este proyecto tiene dos partes diferenciadas. Una es la parte donde se aloja el script de python y su correspondiente dockerizacion. La segunda es la carpeta que añadirá este servicio como stack del catalogo de rancher para que se pueda lanzar desde ahi. Estas dos partes se describirán más en detalle a continuación.

## IMPORTANTE: Notas sobre la version actual

Para pruebas, ahora mismo esta configurado el script de python de tal forma que se borran los stacks lanzados pasado un tiempo determinado. De momento solo queremos comprobar que lanza los stacks correctamente desde rancher y docker.
Este parametr

## dockerizacion python script

En la carpeta service tenemos la dockerizacion del script en python con todo lo necesario para convertirlo en un container independiente que lance servicios.

## Getting Started

Para conseguir que funcione el programa se deben de añadir a la carpeta configuration los siguientes archivos

<!-- ### Rancher CLI y rancher-compose

Es necesario añadir a la carpeta configuration la version compatible con tu sistema operativo de la rancher CLI y rancher-compose. Puedes descargar estos archivos desde la pagina de tu rancher. En la esquina inferior derecha haz click en RancherCLI y selecciona tu sistema operativo para el rancherCLI y el rancher-compose

####ACTUALIZACION:
Esto ya no será necesario cuando dockericemos el funcionamiento. Habrá que quitar del gitignore el rancher y el rancher-compose -->

### Fichero url_acces.txt

Este fichero tiene que ser creado dentro de la carpeta configuration. El programa lo usará para obtener las claves de acceso para tu rancher, asi como la url donde este hubicado el rancher y el rancher catalog.
El formato para el archivo tiene que ser el siguiente

```
access_key=Tu access key aqui
secret_key=tu secret key aqui
url=http://url_de_ejemlo_donde_este_tu_rancher/
url_catalog=http://url_de_ejemlo_donde_este_tu_rancher/v1-catalog/templates/nombre_del_catalogo:nobre_del_servicio:0
```

### Fichero entradas.txt

<!-- Por defecto en la version actual esta añadido. -->

##Servicios "Dockerizados"

El programa esta preparado para funcionar en container de docker. Para hacer que esto funcione se deben ejecutar los siguientes comandos en el directorio donde se encuentre el proyecto:

```
docker build -t my-app-name .
docker run -it --rm --name my-running-app-name lanzador-python
```
##Comando para ejecutar lanzadorServicios

<!-- NOTA IMPORTANTE: Recuerda comprobar la ip donde se hubican los host del rancher, debe ser la privada -->

```
python lanzadorServicios.py http://ml-modeling.neocities.org/entradas.txt 377EC393AE145A755881 chk1Le5mmAJAMfB1ddNLbyL5yEC4sDPKmCV28bEL http://185.24.5.232:8080/ http://185.24.5.232:8080/v1-catalog/templates/myRancher-Catalog:TestCatalog:0
``
