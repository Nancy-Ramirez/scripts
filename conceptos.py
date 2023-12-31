# bpy = modulo python

# ops = acceso a los operadores con funciones predefinidas que realizan acciones especificas en blender.

# shade = proporciona acceso a funciones y operadores relacionado a los shades y materiales

# data = datos asociados a un tipo de elemento o entidad en la escena

# bpy.data = contenedor global que almacena los datos de diferentes escenas.

# users = numero de referencias que hacen uso de un objeto en la escena especificada (mesh, material, texture, images)

# context = entorno actual en el que está ejecutando el código.

# view_layer = capa actual en la interfaz de usuario.

# join() = función para combinar varios objetos seleccionados en uno solo, manteniendo la geometria y datos del obejto activo.

# mode_set = cambia el modo del objeto

# remove_doubles = fusiona vertices duplicados en un objeto de maya de manera automatica

# merge_threshold = es el umbral que establecimos al principio.

# GTLF (GL Transmission Format) = formato de archivo de texto basado en JSON que almacena información del modelado 3D (geometría, texturas, animaciones, etc).

# GLB (GL Binary): variante binaria del GTLF, pero este almacena los datos del modelo 3D y sus recursos(texturas, imagenes, etc) en un solo archivo binario.

# listdir = funcion de Python para obtener una lista de nombres de archivos y directorios contenidos en una ruta especifica.

# lower = convierte todos los caracteres de la cadena a minusculas.

# endswith = verifica si la cadena termina con un sufijo o conjutno de sufijos especificos.

# collections = contenedor que agrupa objetos relacionados

# unlink = permite gestionar pertenencia de los objetos a las colecciones en Blender, permitiendo agregar o quitar objetos de una coleccion sin eliminarlos de la escena.

# link = vincula objetos a una colección.

# transform_apply = operador de Blender que aplica las transformaciones de ubicacion, rotacion y escala de un objeto.

# material_slots = son espacios reservados (o ranuras) en un objeto donde se pueden asignar y administrar los materiales que se aplicarán a las partes individuales del objeto.

# material = material especifico asignado a un objeto.

# use_nodes = propiedad del material que indica si el material utiliza nodos para su configuracion.

# path.join = une diferentes partes de una ruta o archivo

# makedirs = crea los directorios intermedios necesarios para la ruta.

# UV = sistema de coordenada bidimensional que se utiliza para mapear texturas en una malla tridimensional.

# uv_layers = se utilza para acceder y manipular los mapas UV de un objeto.

# smart_project = realiza un mapeo UV inteligente en una malla, lo que facilita la asignación de texturas y la manipulación en el espacio UV.
                 # todo ****** PARAMETROS ****** todo #
    #? angle_limit = parametro que indica el ángulo máximo permitido entre las normales de las caras vecinas antes de que se realice una separación en el mapeo UV.

    #? margin_method = parametro que especifica el metod utilizado para calcular el margen al realizar la proyeccion del mapeo UV. Islas(grupos de caras conectadas)
        #* 'SCALED' = Calcula el margen alrededor de cada isla en función de la escala relativa de las caras en el espacio UV. Las islas más grandes tendrán un margen proporcionalmente más amplio que las islas pequeñas.

    #? island_margin = parametro que especifica el valor del margen (espacio) que se debe agregar alrededor de cada isla en el mapeo UV. Determina cuánto espacio adicional se agregará alrededor de cada isla.

    #? area_weight = parametro que controla la influencia del tanaño de las caras en el asignación del espacio.

    #? correct_aspect = parametro que determina si se debe mantener el aspecto correcto de las caras dureante la proyección del mapeo.
        #* True = las caras en el mapeo UV se ajustarán proporcionalmente según su forma en la malla 3D.

        #* False = las caras den el mapeo UV pueden deformarse para optimizar el uso del espacio disponible.

    #? scale_to_bounds = parametro que determina si el mapeo UV se debe escalar para ajustarse a los límites del espacio de textura disponible.
        #* True = el mapeo UV se ajustará proporcionalmente para ocupar todo el espacio de textura disponible SIN DEJAR ESPACIOS EN BLANCO.
        #* False =  el mapeo UV mantendrá su ESCALA ORIGINAL y puede haber espacios en blanco en el espacio de textura si el mapeo UV no se ajusta completamente.

# material_slot_remove = función encargada de eliminar un slot de material de un objeto.

# window.screen = propiedad de Blender que se utiliza para acceder a la pantalla activa de una ventana especifica.

# next() = es un iterador,avanza al siguiente elemento y lo devuelve.

# override = es un diccionario de Blender que se utiliza para proporcionar información adicional y configuraciones personalizadas al ejecutar una operación o una anulación. ("DICCIONARIO DE ANULACIÓN")
    #? window = representa la ventana en la que se realiza la operación.
    #? screen = representa a pantala en la que se realiza la operación.
    #? area = representa el área en la que se realiza la operación.

# BMesh = es una representación interna de una malla en Blender que permite acceder y manipular de forma eficiente de topología y geometía de una malla.

# .tag = en el contexto actual, se utiliza como marcador o idenficador booleado para rastrear las caras visitadas en el algoritmo "get_linked"_faces()"

#.link_faces = propiedad que devuelve una listas de caras vinculadas al objeto que se aplica. Estas caras son las caras adyacentes al borde del objeto que se aplica en la malla.
    #?  caras adyacentes = en el contexto de una malla tridimensional, dos caras se consideran adyacentes si comparten un borde en común.

# .edges = aristas que tiene elemento.

# .set() = se utiliza para crear un objeto tipo conjunto en Python. Un conjunto es una colección desordenada de elementos únicos.

# from_mesh = metodo de "bmesh" que se utiliza para copiar la geometría de una malla existente en Blender al objeto "bmesh"

# from_edit_mesh = método estático de la clase "bmesh" en Blender. Se utiliza para crear un objeto "bmesh" basado en la malla en modo edición de un objeto dado.

# ensure_lookup_table = se utiliza en Blender para asegurarse de que la tabla de busqueda de elementos de un objeto "bmesh" esté actualizada y sea válida

# examined se utiliza para realizar un seguimiento de las caras que han sido examinadas. Esto se hace para evitar que una cara ya examinada se vuelva a examinar, lo que podría llevarnos a un bucle infinito en el proceso de búsquedaz de islas de caras.
    #? islas de caras: es un conjunto de caras conectadas entre sí a través de aristas compartidas. en 3d, las caras representan las superficies planas de un objeto y una isla de caras se refiere a un grupo de caras que están interconectadas directa o indirectamente.

# hornear texturas = En el contexto del horneado de texturas, se aplican diferentes propiedades y configuraciones del material (como color, brillo, rugosidad, etc.) al objeto y luego se realiza el proceso de bake para generar las texturas resultantes. Durante el horneado, se calculan y asignan los valores de color y otros atributos a los píxeles de la textura, creando así una representación final de la apariencia del objeto.



