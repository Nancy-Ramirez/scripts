import bpy # módulo de Python que proporciona acceso a la API de Blender.
import random  # modulo de Python que proporciona funciones para generar número aleatorios.
#? BMesh = es una representación interna de una malla en Blender que permite acceder y manipular de forma eficiente de topología y geometía de una malla.
import bmesh #módulo de Blender que proporciona funciones y clases para realizar operaciones avanzadas en mallas (meshes) utilizando la estructura de datos BMesh.
import os # libreria que permite acceder a funciones con el sistema operativo.

utils = bpy.data.texts["utils.py"].as_module() # importamos el archivo "utils.py" para poder importar y trabajar con sus funciones.

def get_linked_faces(f): #! función que toma una cara "f" y devuelve una lista de caras conectadas a través de bordes compartidos. Utiliza un enfoque de búsqueda en profundidad para recorrer las caras conectadas.

    stack = [f] # creamos una pila vacía que inicializamos con la cara de malla de entrada "f"

    #? tag = en el contexto actual, se utiliza como marcador o idenficador booleado para rastrear las caras visitadas en el algoritmo "get_linked"_faces()"
    f.tag = True # marca la cara de entrada "f" como visitada, estableciendo su atributo "tag" en "True"

    f_linked = [] # inicializamos una lista vacía para almacenar las caras vinculadas durante el proceso del algoritmo "get_linked_faces()"
    while stack: # mientras la pila no esté vacía

        current = stack.pop() # con "stack.pop" sacamos un elemento de la pila, la cual guardaremos en la variable "current"

        f_linked.append(current) # llenamos la lista "f_linked" con el elemento dela pila que fue sacado anteriormente

        #? .link_faces = propiedad que devuelve una listas de caras vinculadas al objeto que se aplica. Estas caras son las caras adyacentes al borde del objeto que se aplica en la malla.
        #?  caras adyacentes = en el contexto de una malla tridimensional, dos caras se consideran adyacentes si comparten un borde en común
        #? .edges = aristas que tiene elemento.
        edges = [e for e in current.edges if len(e.link_faces) == 2] # en la variable "edges" se almacenan los objetos de bordes siempre y cuando el borde tenga exactamente dos caras vinculadas.

        for e in edges:  # itera sobre los objetos de bordes que se encuentran en "edges"
            faces = [elem for elem in e.link_faces if not elem.tag] # en la variable "faces" se almacenan los objetos primero, tenga caras vinculadas a la arista "e" y segundo no hayan sido procesadas con anterioridad.
            for face in faces: # itera sobre las caras que se encuentran en faces
                face.tag = True # se establece que esa cara ya ha sido procesada.
                stack.append(face) # se agrega a la pila la cara recien procesada.
    return f_linked # retorna la lista "f_linked"

def get_object_islands_bmesh(obj): # función que toma un objeto "obj" y devuelve una tupla que contiene un objeto BMesh y una lista de caras conectadas. Usamos BMesh para analizar las caras conectadas y determinar las islas.
    islands = [] # creamos una lista vacía para almacenar las islas de caras.
    #? .set() = se utiliza para crear un objeto tipo conjunto en Python. Un conjunto es una colección desordenada de elementos únicos.
    examined = set() # crea un conjunto vacío.

    bpy.ops.object.mode_set(mode='OBJECT') # cambia el modo edición del objeto actual a modo objeto en Blender.
    if bpy.ops.object.mode_set(mode='OBJECT'): # verifica que esté en modo OBJETO
        bm = bmesh.new() # crea un objeto "bmesh" vacío.
        #? from_mesh = metodo de "bmesh" que se utiliza para copiar la geometría de una malla existente en Blender al objeto "bmesh"
        bm.from_mesh(obj.data) # copiamos la geometría de una malla en el objeto "bmesh"
    else: # si no está en modo OBJETO.
        #? from_edit_mesh = método estático de la clase "bmesh" en Blender. Se utiliza para crear un objeto "bmesh" basado en la malla en modo edición de un objeto dado.
        bm = bmesh.from_edit_mesh(obj.data) # crea un objeto "bmesh" basado en la malla en modo de edición del objeto "obj" en Blender.

    #? ensure_lookup_table = se utiliza en Blender para asegurarse de que la tabla de busqueda de elementos de un objeto "bmesh" esté actualizada y sea válida
    bm.faces.ensure_lookup_table() # se asegura de que la tabla de búsqueda de cara "bm.faces" esté actualizada y sea válida.

    bm.verts.ensure_lookup_table # se asegura de que la tabla de busqueda de vertices "bm.verts" esté actualizada y sea válida

    for face in bm.faces: # itera sobre las caras que tiene la malla existente en Blender (bm)
        face.tag = False # establece que esta cara no se ha procesado. Esto permite posteriormente puedamos realizar operaciones como marcar o identificar caras especificas en función del valor de la propiedad "tag".

    for face in bm.faces: # itera sobre las caras que tiene la malla existente en Blender (bm)
        if face in examined: # verifica que la cara actual haya sido examinada con anterioridad.
            continue # si la condición anterior es verdadera, salta al for siguiente
        links = get_linked_faces(face) # si la cara actual no ha sido examinada con anterioridad, utilizamos "get_linked_faces" para obtener una lista de caras conectadas a la cara actual.
        for linked_face in links: # itera sobre cada cara conectada en la lista "links".
            # examined se utiliza para realizar un seguimiento de las caras que han sido examinadas. Esto se hace para evitar que una cara ya examinada se vuelva a examinar, lo que podría llevarnos a un bucle infinito en el proceso de búsquedaz de islas de caras.
            #? islas de caras: es un conjunto de caras conectadas entre sí a través de aristas compartidas. en 3d, las caras representan las superficies planas de un objeto y una isla de caras se refiere a un grupo de caras que están interconectadas directa o indirectamente.
            examined.add(linked_face) # agregar la cara conectada a "examined"
        islands.append(links) #se agrega la lista "links" a la lista "islands", lo que representa un grupo de caras conectadas.

    return (bm, islands)

#? hornear texturas = En el contexto del horneado de texturas, se aplican diferentes propiedades y configuraciones del material (como color, brillo, rugosidad, etc.) al objeto y luego se realiza el proceso de bake para generar las texturas resultantes. Durante el horneado, se calculan y asignan los valores de color y otros atributos a los píxeles de la textura, creando así una representación final de la apariencia del objeto.

def multiple_bake(obj, folder_path): #! función que realiza el proceso de horneado para múltiples materiales de un objeto. Itera sobre los materiales del objeto y crea un nuevo material para cada uno de ellos. Luego establece una nueva textura de imagen para cada material y realiza la cocción del objeto para cada material.

    for i, mat in enumerate(obj.data.materials): # itera sobre los materiales asociados al obeto "obj"
        #todo Creamos un nuevo material con un color random y con un nombre basado en el nombre de un material existente.
        new_material_name = mat.name + "_new" # crea un nuevo nombre para el nuevo material, apartir de una nombre de material ya existente.
        new_material = bpy.data.materials.new(name=new_material_name) # creamos un nuevo material en la base de datos de materiales de Blender y devuelve una referencia a ese material, se almacena con el nombre que se le asignó a "new_material_name"
        new_material.use_nodes = True # habilitamos el uso de nodos para la configuración del material.
        new_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (random.random(), random.random(), random.random(), random.random()) #default_value = (R, G, B, A) <-- le asigna un valor aleatorio a cada uno, generando por si un color random al nuevo material.

        # Swap the current material with the new material
        if mat:
            obj.data.materials[i] = new_material
        else:
            obj.data.materials.append(new_material)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.uv.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
    i = 0
    # Loop through the object's materials
    for material_slot in obj.material_slots:
        material = material_slot.material
        i += 1
        # Add a new image texture node for the material
        tree = material.node_tree

        texture_node = tree.nodes.new('ShaderNodeTexImage')
        tex_image = bpy.data.images.new(name= obj.name + "_" + str(i) + "_T_SegmentationMap", width=512, height=512)

        # Set the texture node to the diffuse channel
#        tex_image = bpy.data.images.new("{}_diffuse.png".format(material.name), width=512, height=512)
        texture_node.image = tex_image
        texture_node.image.colorspace_settings.name = 'sRGB'
        texture_node.image.filepath_raw = texture_node.image.name

        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_clear = False

        bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
        tex_image.pack()
        filepath = folder_path
        tex_image.save_render(filepath + material.name + "_BakedTexture.png")
        bpy.ops.image.pack()
        print("Baking Done")


def single_bake(obj, folder_path):

    bpy.context.view_layer.objects.active = obj
    bm, islands = get_object_islands_bmesh(obj)

    tex_image = bpy.data.images.new(name= obj.name + "_1" + "_T_SegmentationMap", width=512, height=512)


    # create new materials and image textures for each island and assign them to the mesh
    for i, island in enumerate(islands):
        mat = bpy.data.materials.new(name="Island_{}_{}".format(obj.name, i)+ "_new")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (random.random(), random.random(), random.random(), random.random())

        # add a new ShaderNodeTexImage node to the material
        nodes = mat.node_tree.nodes
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = tex_image

        # assign the material to the island
        obj.data.materials.append(mat)
        mat_index = len(obj.data.materials) - 1
        for face in island:
            face.material_index = mat_index


    # update the object's mesh from the bmesh
    if obj.mode == 'OBJECT':
        bm.to_mesh(obj.data)
        bm.free()
    else:
        bmesh.update_edit_mesh(obj.data)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    print("baking")

    # Select the object

    obj.select_set(True)

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_clear = False

    bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
    print("image packed")
    tex_image.pack()
    filepath = folder_path
    tex_image.save_render(filepath + obj.name + "_BakedTexture.png")
    print("baking done")
    # Deselect the object
    obj.select_set(False)


def generate_segmentation_map(obj):
    blend_file_path = bpy.data.filepath
    folder_path = os.path.dirname(blend_file_path)

    export_folder_path = os.path.join(folder_path, "segmentation_maps")
    if not os.path.exists(export_folder_path):
        os.makedirs(export_folder_path)

    mat = obj.active_material
    #    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    print("------------------------------------------")
    # Set the active UV map
    uv_map = obj.data.uv_layers.active

    num_materials = len(obj.material_slots)

    bpy.context.scene.tool_settings.use_uv_select_sync = True

    # Select all UV islands that overlap with the current selection
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.uv.select_all(action='DESELECT')
    bpy.ops.uv.select_overlap()

    if num_materials == 0:
        bpy.ops.object.mode_set(mode='OBJECT')
        new_material_name = "Material" + obj.name
        new_material = bpy.data.materials.new(name=new_material_name)
        new_material.use_nodes = True
        obj.data.materials.append(new_material)
        utils.merge(obj)
        bpy.context.view_layer.objects.active = obj
        utils.setup_uvmap(obj)


    # Unlink image textures from Metallic channel
    linked_images = utils.unlink_image_from_metallic(obj)
    # Set a new Metallic value of 0.8 for the active object's material
    previous_value, _ = utils.set_metallic_value(0.0)

    if num_materials > 1:
        multiple_bake(obj, export_folder_path)
    else:
        single_bake(obj, export_folder_path)

    utils.restore_materials()
    utils.revert_metallic_value(previous_value)
    # Link previously unlinked image textures back to Metallic channel
    utils.link_image_to_metallic(obj, linked_images)

def Material(obj):

        bpy.ops.object.mode_set(mode='OBJECT')
        new_material_name = "Material_" + obj.name
        new_material = bpy.data.materials.new(name=new_material_name)
        new_material.use_nodes = True
        obj.data.materials.append(new_material)

def segmentation_map():
    bpy.context.scene.render.bake.margin = 0

    # Create an empty dictionary to store material names and their associated objects
    material_objects = {}

    # Dictionary to store the UVs of each object
    uv_dict = {}

    # Get the "Imported Objects" collection
    imported_collection = bpy.data.collections.get("Imported Objects")

    # Get the "Imported Objects" collection
    tile_collection = bpy.data.collections.get("Tileable Objects")

    if imported_collection is None:
        print("Collection 'Imported Objects' not found")
        return

    if tile_collection is None:
        print("Collection 'Imported Objects' not found")
        return

    # Loop through each object in the "Imported Objects" collection
    tile_collection = tile_collection.objects

    for obj in tile_collection:
        num_materials = len(obj.material_slots)
        if num_materials < 1 :
            obj.select_set(True)
            utils.merge(obj)
            bpy.context.view_layer.objects.active = obj
            Material(obj)
            utils.setup_uvmap(obj)
        else:
            print("tileable object has one material or more")

    # Loop through each object
    for obj in imported_collection.objects:
        if obj.type == 'MESH':
            # Get the mesh data of the object
            mesh = obj.data

            # Check if the object has UV data
            if mesh.uv_layers.active is not None:
                # Get the UV coordinates of the object
                uvs = mesh.uv_layers.active.data
                uv_coords = [uv.uv for uv in uvs]

                # Check if this UV set has already been encountered
                if str(uv_coords) in uv_dict:
                    # Add the object to the list of objects with the same UV
                    uv_dict[str(uv_coords)].append(obj)
                else:
                    # Add the UV set to the dictionary
                    uv_dict[str(uv_coords)] = [obj]


    # Loop through all objects in the scene
    for obj in imported_collection.objects:
        # Loop through all material slots in the object
        for material_slot in obj.material_slots:
            material = material_slot.material
            if material:
                # Check if the material name is already in the dictionary
                if material.name in material_objects:
                    # If it is, add the object to the list of objects associated with the material
                    material_objects[material.name].append(obj)
                else:
                    # If it's not, add the material name to the dictionary and create a list with the object
                    material_objects[material.name] = [obj]

    # Create a list of material groups, where each group is a list of objects that share the same material
    material_groups = [objs for objs in material_objects.values() if len(objs) > 1]

    # Track whether we've already executed our code for objects that share multiple materials
    code_executed = False

    for uv_set in uv_dict:
            if len(uv_dict[uv_set]) > 1:
                print("Objects with the same UV: ", uv_dict[uv_set])

    # Loop through the material groups and check if all objects in each group are using the same material
    for group in material_groups:
        materials_used = set([material_slot.material for obj in group for material_slot in obj.material_slots])
        # Print the objects with the same UV
        if len(materials_used) == 1:
            print("Objects {} are sharing a single material: {}".format(group, list(materials_used)[0].name))
            obj= group[0]
            generate_segmentation_map(obj)
            bpy.ops.object.select_all(action='DESELECT')

        else:
            # Only execute our code once, for the first group of objects that share multiple materials
            if not code_executed and len(uv_dict[uv_set]) > 1:
                print("Objects are sharing multiple materials")
                # Do something here for objects that share multiple materials
                # For example, print a list of the materials used by the objects
                print("Materials used: {}".format([material.name for material in materials_used]))
                code_executed = True
                obj= group[0]
                generate_segmentation_map(obj)
                bpy.ops.object.select_all(action='DESELECT')

    # Loop through all objects in the scene again, and do something for objects that do not share any materials with another object
    for obj in imported_collection.objects:
        if obj.type == 'MESH' and obj not in [o for group in material_groups for o in group]:
            # Do something here for objects that do not share any materials with another object
            generate_segmentation_map(obj)
            bpy.ops.object.select_all(action='DESELECT')

if __name__ == "__main__":
    tex_image = segmentation_map()