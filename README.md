# ml-modeling

Este proyecto servirá para las tareas de ml-modeling en el Lab del BBVA. El objetivo actual es lanzar varias instancias de un programa en rancher con diferentes configuraciones.

##Version actual

Actualmente el scrip de python que ejecuta las instancias en rancher solo funciona para un determinado servicio. Este servicio se encuentra en el catalogo: https://github.com/pablosjv/rancher-catalog.git
Debes añadir este catalogo a tu rancher. El servicio se llama TestCatalog y la version es la 0

## Getting Started

Para conseguir que funcione el programa se deben de añadir a la carpeta configuration los siguientes archivos

### Rancher CLI y rancher-compose

Es necesario añadir a la carpeta configuration la version compatible con tu sistema operativo de la rancher CLI y rancher-compose. Puedes descargar estos archivos desde la pagina de tu rancher. En la esquina inferior derecha haz click en RancherCLI y selecciona tu sistema operativo para el rancherCLI y el rancher-compose


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

Por defecto en la version actual esta añadido.
