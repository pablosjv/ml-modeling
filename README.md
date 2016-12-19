# ml-modeling

Este proyecto servirá para las tareas de ml-modeling. El objetivo actual es lanzar varias instancias de un stack desde el catalogo de rancher con diferentes configuraciones que se darán mediante una lista.

Este proyecto tiene dos partes diferenciadas:
* Una es la parte donde se aloja el script de python y su correspondiente dockerizacion.
* La segunda es la carpeta que añadirá este servicio como stack del catalogo de rancher para que se pueda lanzar desde ahi.

Estas dos partes se describirán más en detalle a continuación.

### Notas sobre la version actual

Para pruebas, ahora mismo esta configurado el script de python de tal forma que se borran los stacks lanzados pasado un tiempo determinado. De momento solo queremos comprobar que lanza los stacks correctamente desde rancher y docker.
Este parametro puede ser configurable en el futuro. Queda como tarea pendiente

## Getting Started

El programa esta pensado para ser lanzado como un stack de rancher desde el catalogo.
En primer lugar debemos añadir a nuestro rancher como catalogo este repositorio. De esta forma tendremos acceso al servicio desde el catalogo.
A continuación, entraremos en nuestro catalogo y seleccionamos este stack. Debemos elegir la version (version actual: v0.1) y se mostrarán las preguntas a rellenar. Estas preguntas serán:

1. Url de los parametros de configuración
2. Acces key del rancher
3. Secret key del rancher
4. Url del rancher:
5. Url del stack del catalogo de rancher a lanzar. Esta url hace referencia a la API de rancher. Tendremos que buscar en esta el stack que queremos lanzar en la API. Tendrá la siguiente forma:
> http://url_de_ejemlo_donde_este_tu_rancher/v1-catalog/templates/nombre_del_catalogo:nobre_del_servicio:0

#### NOTA IMPORTANTE: Hay que tener en cuenta que las url del rancher y del stack del catalogo tienen que ser accesibles desde nuestro host.

Tras esto ya se puede lanzar nuestro stack

## Dockerizacion python script

En la carpeta service tenemos la dockerizacion del script en python con todo lo necesario para convertirlo en un container independiente que lance servicios. La carpeta contiene tando el programa python como el Dockerfile que se usa para construir la imagen. En la carpeta exec se encuentran los ejecutables del rancherCLI y el rancher-compose. Estos son los de la version para linux.

### Pruebas del script individuales

Si se quiere probar el funcionamiento del script individualmente se debe tener en cuenta que este recibe argumentos. Estos argumentos corresponden a los mismos que hay que introducir en las preguntas y siguen el mismo orden con el que los hemos citado anteriormente.
El comando por lo tanto tendrá la siguiente forma:

```
python lanzadorServicios.py http://ml-modeling.neocities.org/entradas.txt access_key secret_key http://185.24.5.232:8080/ http://185.24.5.232:8080/v1-catalog/templates/myRancher-Catalog:TestCatalog:0
```

## Template para el catalogo

En la carpeta service es donde almacenamos todo lo referente al catalogo que saldrá en nuestro rancher. Tendremos que agregar este repositorio al nuestro rancher y saldrá el servicio de ml-modeling-experiments. Contiene todo lo necesario para que se muestre correctamente.
