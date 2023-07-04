import bpy # módulo de Python que proporciona acceso a la API de Blender
import os  # libreria que permite acceder a funciones con el sistema operativo.

def cleanup():  #! función de limpieza 

    #si existe el atributo "control_nets" existe en el objeto "dream_textures_prompt" entonces se elimina el primer elemento (indice 0) de la lista.
    if bpy.context.scene.dream_textures_prompt.control_nets: 
        bpy.context.scene.dream_textures_prompt.control_nets.remove(0)

    #? bpy = modulo python
    #? ops = acceso a los operadores con funciones predefinidas que realizan acciones especificas en blender.
    #? shade = proporciona acceso a funciones y operadores relacionado a los shades y materiales
    bpy.ops.shade.dream_textures_history_clear() # limpia el historial de texturas
    
    #? data = datos asociados a un tipo de elemento o entidad en la escena
    #? bpy.data = contenedor global que almacena los datos de diferentes escenas.
    #? users = numero de referencias que hacen uso de un objeto en la escena especificada (mesh, material, texture, images)
    for block in bpy.data.meshes: 
        if block.users == 0: # si no existen referencias de algún objeto en las mallas, remueve la escena.
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0: # si no existen referencias de algún objeto en los materiales, remueve la escena.
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0: # si no existen referencias de algún objeto en las texturas, remueve la escena.
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0: # si no existen referencias de algún objeto en las imagenes, remueve la escena.
            bpy.data.images.remove(block)
           
def merge(obj): #!función para fusionar objetos
    
    merge_threshold = 0.0001 # establece el umbral (valor limite o punto de corte) de distancia para la fusión

    #? context = entorno actual en el que está ejecutando el código.
    #? view_layer = capa actual en la interfaz de usuario.
    bpy.context.view_layer.objects.active = obj # establece el objeto activo en el contexto de la capa de vista

    bpy.ops.object.select_all(action='DESELECT') # deselecciona todos los objetos de la escena. Es la mejor manera para asegurarse de que no haya objetos seleccionados antes de hacer la unión

    obj.select_set(True) # selecciona el objeto "obj". Establece su selección con "True"

    bpy.context.view_layer.objects.active = obj #establece a "obj" como un objeto activo en la capa de vista actual. Lo que significa que cualquier operacion que realicemos más adelante se le aplicará a este objeto.
    
    #? join() = función para combinar varios objetos seleccionados en uno solo, manteniendo la geometria y datos del obejto activo.
    bpy.ops.object.join() # une los objetos seleccionados, OJO: deben ser de mismo tipo de dato (meshes, curves, etc)

    #? mode_set = cambia el modo del objeto 
    bpy.ops.object.mode_set(mode='EDIT') # cambia al modo edición el objeto actual.

    bpy.ops.mesh.select_all(action='SELECT') # selecciona todos los elementos de malla del objeto en modo edición (es como dar clic en "A")

    #?remove_doubles = fusiona vertices duplicados en un objeto de maya de manera automatica
    #? merge_threshold = es el umbral que establecimos al principio.
    bpy.ops.mesh.remove_doubles(threshold=merge_threshold) # fusiona los vertices duplicados que se encuentren dentro de la distancia determinada en el "merge_threshold"

    bpy.ops.object.mode_set(mode='OBJECT') # salimos del modo edición y entramos al modo objeto.

    obj.select_set(False) # deselecciona el objeto "obj"
    
def import_gltf_files(directory): #!función que importa archivos GTLF o GLB desde un directorio especifico de Blender (se utiliza en DREAM_TEXTURES.py)
    #? GTLF (GL Transmission Format) = formato de archivo de texto basado en JSON que almacena información del modelado 3D (geometría, texturas, animaciones, etc).
    #? GLB (GL Binary): variante binaria del GTLF, pero este almacena los datos del modelo 3D y sus recursos(texturas, imagenes, etc) en un solo archivo binario. 
      
    #? listdir = funcion de Python para obtener una lista de nombres de archivos y directorios contenidos en una ruta especifica.
    files = os.listdir(directory)

    #? lower = convierte todos los caracteres de la cadena a minusculas.
    #? endswith = verifica si la cadena termina con un sufijo o conjutno de sufijos especificos.
    gltf_files = [file for file in files if file.lower().endswith(('.gltf', '.glb'))] # Filtra los archivos según su formato (.gltf o .glb) y los guarda en un arreglo.

    name_imported = "Imported Objects" # definimos la variable "name_imported"

    #? collections = contenedor que agrupa objetos relacionados
    imported_collection = bpy.data.collections.get(name_imported)  #verifica si ya existe en el contexto de datos.

    
    if imported_collection is None: # si no existe "imported objects" en la escena, crea una colección con ese nombre.
        imported_collection = bpy.data.collections.new(name_imported)
        bpy.context.scene.collection.children.link(imported_collection) # la vincula como hija de la colección principal de la escena.
        print("Created 'Imported Objects' collection")
    else:
        print("Collection 'Imported Objects' already exists")
 
    name_tile = "Tileable Objects" # definimos la variable "name_tile"
    tile_collection = bpy.data.collections.get(name_tile)  # verifica si ya existe en el contexto de datos 1(azulejo)

    if tile_collection is None: # si no existe "Tileable Objects" en la escena, crea una colección con ese nombre.
        tile_collection = bpy.data.collections.new(name_tile)
        bpy.context.scene.collection.children.link(tile_collection) # la vincula como hija de la colección principal de la escena.
        print("Created 'Tileable Objects' collection")
    else:
        print("Collection 'Tileable Objects' already exists")

    # por cada archivo .GLTF o .GLB se realiza una importación
    for file in gltf_files: #gtlf es el arreglo donde se guardaran los archivos con extensión gtlf y glb encontrados en la ruta especificada.
        file_path = os.path.join(directory, file) # une el directorio con el nombre del archivo para crear una ruta completa
        bpy.ops.import_scene.gltf(filepath=file_path) # importa el archivo de la ruta completa.

        imported_objects = bpy.context.selected_objects # obtiene todos los objetos seleccionados en el contexto actual y los asigna a la variable.
        
        if len(imported_objects) == 0: # si no hay archivos para importar.
            print("Warning: No objects found in file:", file)
            continue #sale de la condicional pero no termina la secuencia del código.

        print("Imported file:", file) # imprime el nombre del archivo.
        print("Imported object names:", [obj.name for obj in imported_objects]) # imprime el nombre de los objetos que contiene el archivo.

        for imported_object in imported_objects: # de manera de bucle recibe el objeto
            imported_file_name = imported_object.name # del objeto recibido por el bucle se guarda el nombre en la variable "imported_file_name"

            suffix = 1 # genera un nombre unico para que se eviten conflictos en un futuro.
            unique_name = imported_file_name

            new_object_name = imported_file_name.replace(".", "_") # reemplaza los puntos (".") por barra baja ("_") en el nombre del objeto.

            imported_object.name = new_object_name # renombra el objeto importado con el nombre modificado

            print("Original object name:", imported_file_name) # nombre original del objeto.
            print("Modified object name:", new_object_name) # nombre modificado del objeto

            # Check if the file name or modified object name contains specific words
            if any(keyword in file.lower() or keyword in new_object_name.lower() for keyword in ['wall', 'ceiling', 'floor', 'tile']): # verifica si el nombre del archivo o el nombre modificado del objeto contiene palabras especificas.
                print("This is a tileable asset") 
                print(file)

                #? unlink = permite gestionar pertenencia de los objetos a las colecciones en Blender, permitiendo agregar o quitar objetos de una coleccion sin eliminarlos de la escena.
                for collection in imported_object.users_collection:
                    collection.objects.unlink(imported_object) # desvincula el objeto de las colecciones a las que está vinculado.
                #? link = vincula objetos a una colección.
                tile_collection.objects.link(imported_object)  # vincula el objeto a la colección de azulejo.
            else:
                for collection in imported_object.users_collection:
                    collection.objects.unlink(imported_object) # desvincula el objeto de las colecciones a las que está vinculado.

                imported_collection.objects.link(imported_object)  # vincula el objeto a la colección de importaciones.

            print()

            #? transform_apply = operador de Blender que aplica las transformaciones de ubicacion, rotacion y escala de un objeto.
            bpy.context.view_layer.objects.active = imported_object # establece elobjeto activo en la capa de vista actual, el cual asegura de que las operaciones sean para él.
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True) # aplica la transformación de escala al objeto activo.
            #Significa que cualquier escala no uniforme que se haya aplicado al objeto se convertirá en una escala uniforme de 1. en los ejes X, Y, Z.

            #? material_slots = son espacios reservados en un objeto donde se pueden asignar y administrar los materiales que se aplicarán a las partes individuales del objeto.
            #? material = material especifico asignado a un objeto.
            #? use_nodes = propiedad del material que indica si el material utiliza nodos para su configuracion. 
            for slot in imported_object.material_slots:
                material = slot.material
                material.use_nodes = True  # edición con nodos permitida.
                for node in material.node_tree.nodes:
                    node.select = False  # deselecciona cada nodo del arbol de nodos, preparandolos para futuras modificaciones.

    return tile_collection, imported_collection  # retorna las colecciones creadas en esta función.

def export(output_dir): #!exportar objetos de la escena en formato gITF
    file_format = 'GLTF_SEPARATE'  # generar archivos gITF separados por objetos.

    #? path.join = une diferentes partes de una ruta o archivo
    export_dir = os.path.join(output_dir, 'export_temp') # crear un nuevo directorio si es que no existe.
    if not os.path.exists(export_dir):
        #? makedirs = crea los directorios intermedios necesarios para la ruta.
        os.makedirs(export_dir) 

    objects = bpy.context.scene.objects # obtiene todos los objetos de la escena actual y los asigna a la variable "objects".
    cleanup() # limpia y prepara la escena antes de exportar.

    for obj in objects:
        if obj.type == 'MESH': # si el ripo de objeto es una malla
            #? view_layer = capa actual en la interfaz de usuario.
            bpy.context.view_layer.objects.active = obj # establece el objeto activo en la capa de vista actual.
            obj.select_set(True) # establece la selección del objeto.

            bpy.ops.export_scene.gltf(filepath=os.path.join(export_dir, obj.name), export_format=file_format, use_selection=True, export_texture_dir=export_dir) #exporta el objeto en formato gITF
            
            obj.select_set(False) #deselecciona el objeto.
#? UV = sistema de coordenada bidimensional que se utiliza para mapear texturas en una malla tridimensional.

def setup_uvmap(obj): #! Configura el mapeado de coordenadas UV de un objeto

    obj.select_set(True) # establece la selección del objeto.

    bpy.context.view_layer.objects.active = obj # establece el objeto activo en la capa de vista actual.
    
    #? uv_layers = se utilza para acceder y manipular los mapas UV de un objeto.
    uv_maps = obj.data.uv_layers # se inicializa "uv_maps" con la lista de mapas UV del objeto "obj".
    if len(uv_maps) > 0: # verifica si hay algun mapa UV existente, comprobando la longitud de la lista.
        for uv_map in uv_maps: # si hay mapas existentes se itera una por una en la lista.
            obj.data.uv_layers.remove(uv_map) # elimina el mapa UV.
    
    uv_map = obj.data.uv_layers.new(name="Prop_UVMap") # crea un nuevo mapa UV llamado "Prop_UVMap"
    obj.data.uv_layers.active = uv_map # establece el mapa UV recien creado como el mapa UV activo del objeto.

    bpy.ops.object.mode_set(mode='EDIT') # cambia el modo objeto al modo edición.

    bpy.ops.mesh.select_all(action='SELECT') # selecciona todas las caras de la malla en el modo edición.

    #? smart_project = realiza un mapeo UV inteligente en una malla, lo que facilita la asignación de texturas y la manipulación en el espacio UV.
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

    bpy.ops.uv.smart_project(angle_limit=1.151917, margin_method='SCALED', island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False) # se realiza un mapeo inteligente a la malla, utlizando los parametros.

#    bpy.ops.uvpackeroperator.packbtn()

    bpy.ops.object.mode_set(mode='OBJECT') # regresa al modo objeto.

    bpy.ops.object.select_all(action='DESELECT') # deselecciona los objetos

    print("[UVMAP] " + obj.name + " DONE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX") # imprimiria esto por ejemplo : "[UVMAP] Cube DONE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

def UnlinkBaseColor(): #! Elimina el color base del material

    # Iterate through all objects in the scene
    for obj in bpy.context.scene.objects: # obtiene todos los objetos de la escena actual y se lo asigna a obj
        #? material_slots = son espacios reservados (o ranuras) en un objeto donde se pueden asignar y administrar los materiales que se aplicarán a las partes individuales del objeto.
        if obj.material_slots: # verifica si el objeto tienen ranuras de material asignadas.
            for slot in obj.material_slots: # recorre cada ranura de material del objeto "obj" dentro del bucle.
                material = slot.material # accede al material asignado a cada ranura.
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF") # busca y devuelve el nodo con el nombre "Principled BSDF" en el árbol de nodos del materias.
                image_texture = material.node_tree.nodes.get("Image Texture") # busca y devuelve el nodo con el nombre "Image Texture" en el árbol de nodos del materias.

                if principled_bsdf and image_texture and principled_bsdf.inputs["Base Color"].is_linked: #si existen los nodos "principled_bsdf", "image_texture" y verifica que la entrada "Base Color" del nodo "Principled BSDF" está conectada a algún otro nodo en el árbol de nodos.

                    link = principled_bsdf.inputs["Base Color"].links[0] # accede a la lista de enlaces de la entrada "Base Color" del nodo "Principled BDSF", esperando que  esté conectada en al menos un enlace. La expresión [0] se utiliza para acceder al primer enlace de la lista.

                    material.node_tree.links.remove(link) # elimina el enlace especificado de la red de nodos del material.


def unlink_node_from_metallic(obj): #! desconecta un nodo vincula con la entrada "Metallic" de un material

    linked_nodes = [] # declaramos una lista que almacenará los nodos vinculados y sus respectivas salidas.
    if obj.material_slots: # verifica si el objeto tienen ranuras de material asignadas.

        for slot in obj.material_slots: # recorre cada ranura de material del objeto "obj" dentro del bucle.
            material = slot.material # accede al material asignado a cada ranura.

            principled_bsdf = material.node_tree.nodes.get("Principled BSDF")  # busca y devuelve el nodo con el nombre "Principled BSDF" en el árbol de nodos del materias.

            if principled_bsdf.inputs["Metallic"].is_linked: # verifica que la entrada "Metallic " del nodo "Principled BSDF" está conectada a algún otro nodo en el árbol de nodos.

                link = principled_bsdf.inputs["Metallic"].links[0] # accede a la lista de enlaces de la entrada "Metallic " del nodo "Principled BDSF", esperando que  esté conectada en al menos un enlace. La expresión [0] se utiliza para acceder al primer enlace de la lista.

                #? from_node = se utiliza para acceder al nodo de origen de un enlace.
                metallic_node = link.from_node # se accede al nodo de origen de un enlace, devuelve el nodo desde el cual se está tomando el valor de salida para el enlace en cuestión y se lo asigna a "metallic_node".

                #? from_socket = enchufe de salida del nodo de origen de un enlace.
                output_socket = link.from_socket # accede al socket de salida del nodo de origen de un enlace y se lo asigna a "output_socket".

                material.node_tree.links.remove(link) #elimina el enlace.
                linked_nodes.append((metallic_node, output_socket)) # se agrega el nodo y el socket de salida a la lista "linked_nodes"
                print("Node unlinked from Metallic input")
            else:
                linked_nodes.append((None, None)) # no hay nodo enlazado "Metallic", por lo tanto no se agrega nada a "linked_nodes"
                print("No node linked to Metallic input")
    return linked_nodes


def link_node_to_metallic(obj, linked_nodes): #! enlaza un nodo previamente desenlazado al canal "Metallic" del nodo "Principled BSDF" a cada uno de los materiales de un objeto.

    if obj.material_slots and len(linked_nodes) == len(obj.material_slots): # verifica si el objeto tiene ranuras de material y verifica si la longitud de la lista "linked_nodes" es igual a la cantidad de ranuras de material del objeto.

        if any(linked_node[0] is not None for linked_node in linked_nodes): # verifica si hay algun nodo enlazado a la lista "linked_node" que no sea "None"

            #? enumerate = se utiliza para iterar sobre una secuencia.
            #? material_slots = son espacios reservados (o ranuras) en un objeto donde se pueden asignar y administrar los materiales que se aplicarán a las partes individuales del objeto.
            for i, slot in enumerate(obj.material_slots): # itera sobre los elementos de "obj.material" 
                material = slot.material # asignamos el material asosciado a una ranura de material especifica a la variable "material".

                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")  # busca y devuelve el nodo con el nombre "Principled BSDF" en el árbol de nodos del materias.

                node, output_socket = linked_nodes[i] # asignación simultanea de los valores almacenados en "linked_nodes"[i] a la variables "node" y "output_socket"
                if node and output_socket: #verifica que si son validos y no son None
                    
                    material.node_tree.links.new(principled_bsdf.inputs['Metallic'], output_socket) # crea un nuevo enlace (link) entre un socket de entrada y un socket de salida en el árbol de nodos del material, permitiendo que la salida de un nodo se utilice como entrada en otro nodo.
                    print("Node linked to Metallic input")
                else: # si node o output_socket son invalidos o None
                    print("No node to link for this material or no output socket information available")
        else: # si no hay nodo enlazado a la lista "linked_node" o es none
            print("No nodes were unlinked from the Metallic input")
    else: # si no tiene ranuras de material o si la longitud de la lista "linked_nodes" es diferente a la cantidad de ranuras de material del objeto 
        print("Number of linked nodes does not match number of material slots")

def unlink_image_from_metallic(obj): #! desvincula una textura de un nodo Principled BSDF en el canal metalico de un material.

    linked_images = [] # declaramos una lista que almacenará los nodos vinculados y sus respectivas salidas.
    if obj.material_slots:# verifica si el objeto tienen ranuras de material asignadas.

        for slot in obj.material_slots: # recorre cada ranura de material del objeto "obj" dentro del bucle.
            material = slot.material # accede al material asignado a cada ranura.

            principled_bsdf = material.node_tree.nodes.get("Principled BSDF")  # busca y devuelve el nodo con el nombre "Principled BSDF" en el árbol de nodos del materias.

            if principled_bsdf.inputs["Metallic"].is_linked: # verifica que la entrada "Metallic " del nodo "Principled BSDF" está conectada a algún otro nodo en el árbol de nodos.

                #? from_node = se utiliza para acceder al nodo de origen de un enlace.
                metallic_node = principled_bsdf.inputs['Metallic'].links[0].from_node  #forma más resumida para acceder a la lista de enlaces de la entrada "Metallic" de nodo "Principled BDSF" y que se pueda acceder aql nodo de origen de un enlace, devolviendo el nodo desde el cual está tomando el valor de salida y se lo asigna a "metallic_node"

                image_texture = None # se inicializa para asegurarnos de que tenga un valor si no se encuentra una textura de imagen vinculada en el nodo metalico.
                if metallic_node.type == 'TEX_IMAGE': # verifica si el tipo de nodo al que está vinculado el canal metalico sea un nodo de textura de imagen.
                    image_texture = metallic_node.image #se le asigna el objeto de imagen de la textura a la variable "image_texture"
                if image_texture and principled_bsdf.inputs["Metallic"].is_linked: # verifica si existe una textura de imagen y si el canal metalico sigue vinculado.
                    link = principled_bsdf.inputs["Metallic"].links[0] # accede a la lista de enlaces de la entrada "Metallic " del nodo "Principled BDSF", esperando que  esté conectada en al menos un enlace. La expresión [0] se utiliza para acceder al primer enlace de la lista.

                    material.node_tree.links.remove(link) #elimina el enlace
                    linked_images.append(image_texture.name) # se agrega el nombre de la textura desvinculada a "linked_images"
                    print(linked_images, "Textures unlinked from Metallic input")
                else: # si no existe textura de imagen o si el canal metalico no está vinculado
                    linked_images.append(None) # se agrega "None" a la lista "linked_images"
                    print("No input to unlink")
            else: # si la entrada "Metallic" del nodo "Principled BSDF" no está conectada a ningún nodo en el árbol de nodos.
                linked_images.append(None)
                print("No texture linked to Metallic input")
    return linked_images


def link_image_to_metallic(obj, linked_images): #! enlaza un nodo de textura de imagen previamente desenlazado al canal "Metallic" del nodo "Principled BSDF" a cada uno de los materiales de un objeto.

    if obj.material_slots and len(linked_images) == len(obj.material_slots): # verifica si el objeto tiene ranuras de material y verifica si la longitud de la lista "linked_images" es igual a la cantidad de ranuras de material del objeto.

        if any(linked_image is not None for linked_image in linked_images): # verifica si hay algun nodo enlazado a la lista "linked_images" que no sea "None"

            #? enumerate = se utiliza para iterar sobre una secuencia.
            #? material_slots = son espacios reservados (o ranuras) en un objeto donde se pueden asignar y administrar los materiales que se aplicarán a las partes individuales del objeto.
            for i, slot in enumerate(obj.material_slots): # itera sobre los elementos de "obj.material"
                material = slot.material # asignamos el material asosciado a una ranura de material especifica a la variable "material".

                principled_bsdf = material.node_tree.nodes.get("Principled BSDF") # busca y devuelve el nodo con el nombre "Principled BSDF" en el árbol de nodos del materias.

                image_name = linked_images[i] # se almacena el nombre de la textura de imagen i en "image_name"
                if image_name: # verifica  si "image_name" tiene un valor válido
                    image_texture = None  # inicializamos "image_texture" con None
                    for node in material.node_tree.nodes: # iteramos "image_texture" a través de todos los nodos del árbol de nodos del material.
                        if node.type == 'TEX_IMAGE' and node.image.name == image_name: # para cada nodo verificamos si es un nodo de textura de imagen y si el nombre de la  imagen del nodo coincide con "image_name"
                            image_texture = node # si se encuentra un nodo de textura, se asigna a "image_texture" y se rompe el bucle.
                            break
                    if image_texture: # verificamos si "image_texture" es válido.

                        material.node_tree.links.new(principled_bsdf.inputs['Metallic'], image_texture.outputs['Color']) # se enlaza el nodo de textura de imagen al canal metalico.
                    else: # si "image_texture" resulta no ser válido.
                        print(f"Cannot find image texture node {image_name}")
                else:
                    print("No texture to link for this material")
        else:
            print("No textures were unlinked from the Metallic input")
    else:
        print("Number of linked images does not match number of material slots")

def restore_materials(): #! restaura los materiales de los objetos en la escena que han sido renombrados temporalmente.

    if bpy.context.scene.objects: # verifica si la lista de objetos no está vacía, es decir, si hay al menos un objeto en la escena.
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0] # establece el objeto activo en la vista actual.

    for obj in bpy.context.scene.objects: # recorre todos los objetos en la escena.
        if obj.type == 'MESH': # verifica si el tipo del objeto es "MESH"

            for i, mat in enumerate(obj.data.materials): # recorremos cada material en el objeto.

                if mat.name.endswith("_new"): # verifica si el nombre del material termina con "_new"

                    prefix = mat.name[:-4] # se elimina "_new" y se obtiene el prefijo del material.

                    for other_mat in bpy.data.materials: # bucle hasta obtener un material con el mismo prefijo.
                        if other_mat.name.startswith(prefix):
                            # reemplaza el material actual del objeto por el nuevo material encontrado.
                            obj.data.materials[i] = other_mat
                            break

            slots_to_remove = [] # se inicializa la lista "slots_to_remove" para almacenar los índices de los slots de material que deben ser eliminados.
            for i, slot in enumerate(obj.material_slots): # itera sobre los slots de material del objeto actual ("obj")
                if slot.material and slot.material.name.endswith("_new"): # verifica si el slot de material tiene un material asignado y si el nombre del material termina con "_new".
                    slots_to_remove.append(i) # se agrega el indice pertenceinte al material a la lista "slots_to_remove"
            for i in reversed(slots_to_remove): # itera sobre a lista en orden inverso, para que no afecte el orden de los índices al eliminar.
                obj.active_material_index = i # establece el índice del material activo del objeto "obj" al valor "i". Esto para asegurarse de que seleccione el material correcto antes de eliminar el slot de material

                #? material_slot_remove = función encargada de eliminar un slot de material de un objeto.
                bpy.ops.object.material_slot_remove({'object': obj}) # elimina el slot de material en el índice especificado, es decir, elimina el material asociado al slot del objeto.

def set_metallic_value(new_value): #! establece un nuevo valor para el parámetro "Metallic" en el nodo "Principled BSDF"

    obj = bpy.context.active_object # obtenemos el objeto activo.

    material = obj.active_material # obtenemos el mtaerial activo del objeto.

    principled_bsdf = material.node_tree.nodes.get("Principled BSDF") # obtenemos el nodo Principled BSDF

    current_value = principled_bsdf.inputs["Metallic"].default_value # almacenamos el valor actual del parámetro "Metallic" 

    # Assign the new value to the Metallic input
    principled_bsdf.inputs["Metallic"].default_value = new_value # asigna el valor "new_value" al parámetro "Metallic"

    # Return the current and new values
    return current_value, new_value # retornamos "current_value" y "new_value"

def restoreMaterial(mat): #! función que se encarga de buscar y reemplazar los materiales que terminan por "_new" por materiales previamente existentes

    if bpy.context.scene.objects: # si a escena contiene objetos.
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0] # activa el primer objeto de la escena.

    for obj in bpy.context.scene.objects:
        num_materials = len(obj.material_slots)
        if obj.type == 'MESH' and obj.active_material:
            mat = obj.active_material
            # Loop through each material in the object
            # Check if the material name ends with "_new"
            if mat.name.endswith("_new"):
                # Get the prefix of the material name by removing "_new"
                prefix = mat.name[:-4]
                
                # Loop through all materials in the scene and find one with the same prefix
                for other_mat in bpy.data.materials:
                    if other_mat.name.startswith(prefix):
                        # Replace the current material with the new material
                        obj.data.materials[obj.active_material_index] = other_mat
                        break

        slots_to_remove = []
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name.endswith("_new"):
                slots_to_remove.append(i)
        for i in reversed(slots_to_remove):
            obj.active_material_index = i
            bpy.ops.object.material_slot_remove({'object': obj})


def revert_metallic_value(previous_value):
    # Get the active object
    obj = bpy.context.active_object

    # Get the active material of the object
    material = obj.active_material

    # Check if the material exists and has a node tree
    if material and material.use_nodes and material.node_tree:
        # Get the principled BSDF node
        principled_bsdf = material.node_tree.nodes.get("Principled BSDF")

        # Check if the principled BSDF node exists
        if principled_bsdf:
            # Revert the value of the Metallic input back to the previous value
            principled_bsdf.inputs["Metallic"].default_value = previous_value
    else:
        print("Material or its node tree does not exist.")

def select_all_meshes():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Get the collection named "Tileable Objects"
    collection = bpy.data.collections.get("Tileable Objects")

    if collection is not None:
        # Select all mesh objects in the collection
        for obj in collection.objects:
            if obj.type == 'MESH':
                obj.select_set(True)

def select_image_texture_node():
    
    select_all_meshes()
    
    # Get the selected objects
    selected_objects = bpy.context.selected_objects
    
    for selected_obj in selected_objects:
        # Check if an object is selected
        if selected_obj is None:
            print("No object selected.")
            continue
        
        # Check if the object has a material
        if len(selected_obj.data.materials) == 0:
            print("The selected object has no material.")
            continue
        
        # Get the active material
        active_material = selected_obj.active_material
        print(active_material)
        
        # Check if the active material has nodes
        if active_material.node_tree is None:
            print("The active material has no node tree.")
            continue
        
        # Get the material node tree
        node_tree = active_material.node_tree
        
        # Get the image texture nodes
        image_texture_nodes = [node for node in node_tree.nodes if node.type == 'TEX_IMAGE']
        
        # Check if there are image texture nodes
        if len(image_texture_nodes) == 0:
            print("The material has no image texture nodes.")
            continue
        
        # Deselect all nodes
        for node in node_tree.nodes:
            node.select = False

        # Select the first image texture node
        image_texture_node = image_texture_nodes[0]
        image_texture_node.select = True
        
        # Set the active node
        node_tree.nodes.active = image_texture_node
        
        print("Image Texture node selected and set as active.")


def colortonormals():
    select_image_texture_node()

    # Get the selected objects
    selected_objects = bpy.context.selected_objects

    for obj in selected_objects:
        # Set the currently processed object as the active object
        bpy.context.view_layer.objects.active = obj

        # Get the materials of the object
        materials = obj.data.materials

        # Iterate over the materials
        for material in materials:
            # Get the material node tree
            node_tree = material.node_tree

            # Check if the node tree exists
            if node_tree is None:
                print("No node tree found for material:", material.name)
                continue

            # Get the names of the nodes
            node_names = [node.name for node in node_tree.nodes]
            print("MATERIAL:", material.name + ":", "NODE TREE: " + node_tree.name, node_names)

            # Find the area of type 'NODE_EDITOR' in the active window
            for window in bpy.context.window_manager.windows:
                screen = window.screen

                for area in screen.areas:
                    if area.type == 'NODE_EDITOR':
                        override = {'window': window, 'screen': screen, 'area': area}

                        # Get the image texture node
                        image_texture_node = next((node for node in node_tree.nodes if node.type == 'TEX_IMAGE'), None)

                        if image_texture_node is None:
                            print("No image texture node found in material:", material.name)
                            break

                        # Specify the material to override
                        override['material'] = bpy.data.materials.get(material.name)

                        # Get the texture of the image texture node
                        texture = image_texture_node.image
                        image = image_texture_node.image.name

                        if texture is None:
                            print("No texture found in image texture node:", image_texture_node.name)
                            continue

                        if image_texture_node is not None:
                            image = bpy.data.images.get(image)

                        image_texture_node.select = True

                        # Set the active node
                        node_tree.nodes.active = image_texture_node

                        # Override the operator with the image texture node and new image
                        override['active_node'] = image_texture_node
                        override['texture'] = image

                        # Override the operator with the image texture node and texture
                        override['node'] = node_tree.nodes.active
                        override['tex'] = texture

                        bpy.ops.deepbump.colortonormals(override, 'INVOKE_DEFAULT')

                        print("[Material name after override]:", material.name, "[Active Node:]", node_tree.nodes.active, "[Image Texture Name:]", texture.name)

                        break
                else:
                    # No 'NODE_EDITOR' area found
                    print("Error: 'NODE_EDITOR' area not found.")
                    break

        print("[NORMAL MAP]: XXXXXXXXXXXXXXXXXXXXXXXXX DONE")

