import bpy # módulo de Python que proporciona acceso a la API de Blender
import random  #
import bmesh
import os # libreria que permite acceder a funciones con el sistema operativo.

utils = bpy.data.texts["utils.py"].as_module()

def get_linked_faces(f):
    stack = [f]
    f.tag = True
    f_linked = []
    while stack:
        current = stack.pop()
        f_linked.append(current)
        edges = [e for e in current.edges if len(e.link_faces) == 2]
        for e in edges:
            faces = [elem for elem in e.link_faces if not elem.tag]
            for face in faces:
                face.tag = True
                stack.append(face)
    return f_linked

def get_object_islands_bmesh(obj):
    islands = []
    examined = set()

    bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.ops.object.mode_set(mode='OBJECT'):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    else:
        bm = bmesh.from_edit_mesh(obj.data)

    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table

    for face in bm.faces:
        face.tag = False

    for face in bm.faces:
        if face in examined:
            continue
        links = get_linked_faces(face)
        for linked_face in links:
            examined.add(linked_face)
        islands.append(links)

    return (bm, islands)

def multiple_bake(obj, folder_path):

    # Loop through each material in the object
    for i, mat in enumerate(obj.data.materials): 
        # Create a new material with a random color and a name based on the name of the existing material
        new_material_name = mat.name + "_new"
        new_material = bpy.data.materials.new(name=new_material_name)
        new_material.use_nodes = True
        new_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (random.random(), random.random(), random.random(), random.random())

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