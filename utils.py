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

            #? transform_apply = operador de Blender que aplica las transformaciones de ubicacion, rotacion y escala de un objeto
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

def export(output_dir):
    file_format = 'GLTF_SEPARATE'  # or 'GLTF' for a single file

    # Create a new folder if it doesn't exist
    export_dir = os.path.join(output_dir, 'export_temp')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Get a list of all the objects in the scene
    objects = bpy.context.scene.objects
    cleanup()

    # Iterate over the objects
    for obj in objects:
        # Make sure the object is a mesh
        if obj.type == 'MESH':
            # Select the object
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # Export the object to glTF format
            bpy.ops.export_scene.gltf(filepath=os.path.join(export_dir, obj.name), export_format=file_format, use_selection=True, export_texture_dir=export_dir)
            
            # Deselect the object
            obj.select_set(False)

def setup_uvmap(obj):

    # Select the currently processed object
    obj.select_set(True)
    
    # Set the currently processed object as the active object
    bpy.context.view_layer.objects.active = obj
    
    # Check if UV maps already exist
    uv_maps = obj.data.uv_layers
    if len(uv_maps) > 0:
        # Remove existing UV maps
        for uv_map in uv_maps:
            obj.data.uv_layers.remove(uv_map)
    
    # Create a new UV Map called "Prop_UVMap"
    uv_map = obj.data.uv_layers.new(name="Prop_UVMap")
    obj.data.uv_layers.active = uv_map

    # Switch to Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all the faces of the mesh
    bpy.ops.mesh.select_all(action='SELECT')

    # Make a Smart UV Project
    bpy.ops.uv.smart_project(angle_limit=1.151917, margin_method='SCALED', island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)

#    bpy.ops.uvpackeroperator.packbtn()
    
    # Return to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    print("[UVMAP] " + obj.name + " DONE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        
def UnlinkBaseColor():
    # Iterate through all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object has a material
        if obj.material_slots:
            # Iterate through the nodes of each material
            for slot in obj.material_slots:
                material = slot.material
                # Get the principled BSDF node and the image texture node
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
                image_texture = material.node_tree.nodes.get("Image Texture")
                # Check if the nodes are valid and if they are linked
                if principled_bsdf and image_texture and principled_bsdf.inputs["Base Color"].is_linked:
                    # Get the link between the nodes
                    link = principled_bsdf.inputs["Base Color"].links[0]
                    # Disconnect the link
                    material.node_tree.links.remove(link)


def unlink_node_from_metallic(obj):
    linked_nodes = []
    if obj.material_slots:
        # Iterate through the nodes of each material
        for slot in obj.material_slots:
            material = slot.material
            # Get the principled BSDF node and the metallic input
            principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
            if principled_bsdf.inputs["Metallic"].is_linked:
                link = principled_bsdf.inputs["Metallic"].links[0]
                metallic_node = link.from_node
                output_socket = link.from_socket
                # Disconnect the link
                material.node_tree.links.remove(link)
                linked_nodes.append((metallic_node, output_socket))
                print("Node unlinked from Metallic input")
            else:
                linked_nodes.append((None, None))
                print("No node linked to Metallic input")
    return linked_nodes


def link_node_to_metallic(obj, linked_nodes):
    if obj.material_slots and len(linked_nodes) == len(obj.material_slots):
        # Check if any nodes were unlinked from the Metallic channel
        if any(linked_node[0] is not None for linked_node in linked_nodes):
            # Iterate through the nodes of each material
            for i, slot in enumerate(obj.material_slots):
                material = slot.material
                # Get the principled BSDF node
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
                # Get the node and the output socket to be linked
                node, output_socket = linked_nodes[i]
                if node and output_socket:
                    # Link the output socket to the Metallic channel
                    material.node_tree.links.new(principled_bsdf.inputs['Metallic'], output_socket)
                    print("Node linked to Metallic input")
                else:
                    print("No node to link for this material or no output socket information available")
        else:
            print("No nodes were unlinked from the Metallic input")
    else:
        print("Number of linked nodes does not match number of material slots")

def unlink_image_from_metallic(obj):
    linked_images = []
    if obj.material_slots:
        # Iterate through the nodes of each material
        for slot in obj.material_slots:
            material = slot.material
            # Get the principled BSDF node and the image texture node
            principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
            if principled_bsdf.inputs["Metallic"].is_linked:
                metallic_node = principled_bsdf.inputs['Metallic'].links[0].from_node
                image_texture = None
                if metallic_node.type == 'TEX_IMAGE':
                    image_texture = metallic_node.image
                if image_texture and principled_bsdf.inputs["Metallic"].is_linked:
                    # Get the link between the nodes
                    link = principled_bsdf.inputs["Metallic"].links[0]
                    # Disconnect the link
                    material.node_tree.links.remove(link)
                    linked_images.append(image_texture.name)
                    print(linked_images, "Textures unlinked from Metallic input")
                else:
                    linked_images.append(None)
                    print("No input to unlink")
            else:
                linked_images.append(None)
                print("No texture linked to Metallic input")
    return linked_images


def link_image_to_metallic(obj, linked_images):
    if obj.material_slots and len(linked_images) == len(obj.material_slots):
        # Check if any textures were unlinked from the Metallic channel
        if any(linked_image is not None for linked_image in linked_images):
            # Iterate through the nodes of each material
            for i, slot in enumerate(obj.material_slots):
                material = slot.material
                # Get the principled BSDF node
                principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
                # Get the image texture node and the image name
                image_name = linked_images[i]
                if image_name:
                    image_texture = None
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image.name == image_name:
                            image_texture = node
                            break
                    if image_texture:
                        # Link the image texture node to the Metallic channel
                        material.node_tree.links.new(principled_bsdf.inputs['Metallic'], image_texture.outputs['Color'])
                    else:
                        print(f"Cannot find image texture node {image_name}")
                else:
                    print("No texture to link for this material")
        else:
            print("No textures were unlinked from the Metallic input")
    else:
        print("Number of linked images does not match number of material slots")


def restore_materials():
    # Set the active object to the first object in the scene
    if bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            # Loop through each material in the object
            for i, mat in enumerate(obj.data.materials):
                # Check if the material name ends with "_new"
                if mat.name.endswith("_new"):
                    # Get the prefix of the material name by removing "_new"
                    prefix = mat.name[:-4]
                    
                    # Loop through all materials in the scene and find one with the same prefix
                    for other_mat in bpy.data.materials:
                        if other_mat.name.startswith(prefix):
                            # Replace the current material with the new material
                            obj.data.materials[i] = other_mat
                            break

            slots_to_remove = []
            for i, slot in enumerate(obj.material_slots):
                if slot.material and slot.material.name.endswith("_new"):
                    slots_to_remove.append(i)
            for i in reversed(slots_to_remove):
                obj.active_material_index = i
                bpy.ops.object.material_slot_remove({'object': obj})

# Function to set a new metallic value for the Principled BSDF node
def set_metallic_value(new_value):
    # Get the active object
    obj = bpy.context.active_object

    # Get the active material of the object
    material = obj.active_material

    # Get the principled BSDF node
    principled_bsdf = material.node_tree.nodes.get("Principled BSDF")

    # Store the current value of the Metallic input
    current_value = principled_bsdf.inputs["Metallic"].default_value

    # Assign the new value to the Metallic input
    principled_bsdf.inputs["Metallic"].default_value = new_value

    # Return the current and new values
    return current_value, new_value

def restoreMaterial(mat):
    # Set the active object to the first object in the scene
    if bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]

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

