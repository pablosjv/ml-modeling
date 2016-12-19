# ML-Modeling Experiments

### Info:

  Esta template lanza en diferentes stacks los otras plantillas del catalogo. Después de un tiempo determinado son destruidas.

### Usage

  Selecciona ml-modeling del catalogo.
  Selecciona la version
  Introduce los parametros en las preguntas:
    * Url de los parametros de configuración: una url donde se encuentren los parametros de configuracion para las preguntas del stack sobre el que lanzar los experimentos. Debe estar en formato yaml
    * Acces key del rancher
    * Secret key del rancher
    * Url del rancher:
    * Url del stack del catalogo de rancher a lanzar. Esta url hace referencia a la API de rancher. Tendremos que buscar en esta el stack que queremos lanzar en la API. Tendrá la siguiente forma: http://url_de_ejemlo_donde_este_tu_rancher/v1-catalog/templates/nombre_del_catalogo:nobre_del_servicio:0
##### NOTA IMPORTANTE: Hay que tener en cuenta que las url del rancher y del stack del catalogo tienen que ser accesibles desde nuestro host.
