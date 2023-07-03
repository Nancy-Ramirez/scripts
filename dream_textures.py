import bpy
import queue

smap = bpy.data.texts["segmentation_map.py"].as_module()
utils = bpy.data.texts["utils.py"].as_module()

class DreamTexturesSettings(bpy.types.PropertyGroup):
    model: bpy.props.StringProperty(name="Model", default="v1-5-pruned-emaonly")
    seamless_axes: bpy.props.StringProperty(name="Seamless Axes", default="xy")
    negative_prompt: bpy.props.StringProperty(name="Negative Prompt", default=" ")
    seed: bpy.props.StringProperty(name="Seed", default="1902589880")
    steps: bpy.props.IntProperty(name="Steps", default= 15)
    cfg_scale: bpy.props.IntProperty(name="CFG Scale", default=7)
    scheduler: bpy.props.StringProperty(name="Scheduler", default="KDPM2 Ancestral Discrete")
    started: bpy.props.BoolProperty(name="Started", default=False)
    in_process: bpy.props.BoolProperty(name="InProcess", default=False)
    done: bpy.props.BoolProperty(name="Status", default=False)


class DreamTaskManager:
    def __init__(self):
        self.current_material = None

# Define a function to generate a texture for a given material using Dream Textures
def dreamtextures_texture():
    
    settings = bpy.context.scene.dream_texture_settings
    # Set Dream Textures settings
    bpy.context.scene.dream_textures_prompt.model = settings.model

    bpy.context.scene.dream_textures_prompt.seamless_axes = settings.seamless_axes
    bpy.context.scene.dream_textures_prompt.negative_prompt = settings.negative_prompt
    bpy.context.scene.dream_textures_prompt.seed = settings.seed
    bpy.context.scene.dream_textures_prompt.steps = settings.steps
    bpy.context.scene.dream_textures_prompt.cfg_scale = settings.cfg_scale
    bpy.context.scene.dream_textures_prompt.scheduler = settings.scheduler
    bpy.context.scene.dream_textures_prompt.width = 768
    bpy.context.scene.dream_textures_prompt.height = 768
    
    # Generate Dream Texture Image 
    bpy.ops.shade.dream_texture()

def get_image_with_suffix(suffix):
    images = bpy.data.images
    for image in images:
        if image.filepath.lower().endswith(suffix.lower()):
            return image
    return None
def link_texture_to_material(material):

#    obj = bpy.context.active_object     
    objects = bpy.context.scene.objects
    dream_image = bpy.data.images["DreamTexture Output"]
    
          
    img = bpy.data.images.new(name=material.name + "_T_New_BaseColor", width=dream_image.size[0], height=dream_image.size[1])
    
    img.pixels = dream_image.pixels[:]
    
    try:
        bpy.data.images.remove(bpy.data.images["DreamTexture Output"])
    except:
        pass

    # Create a new image texture node and link it to the Principled BSDF node
    if material is None:
        print("[DREAM TEXTURES] No active material found.")
        return
    
    if material.node_tree is None:
        material.node_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name="NodeTree")
    image_texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
    image_texture_node.image = img
    principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
    
    material.node_tree.links.new(image_texture_node.outputs[0], principled_bsdf.inputs[0])
    bpy.context.scene.dream_texture_settings.in_process = False

# Define a function to process the texture generation queue
def process_texture_queue(task_queue, task_manager):
    print("[DREAM TEXTURES] In progress for material: ", task_manager.current_material)

    if bpy.data.images.get("DreamTexture Output") is not None and task_manager.current_material is not None:
#        print("[DREAM TEXTURES] Applying texture for material: {}".format(task_manager.current_material.name))
        link_texture_to_material(task_manager.current_material)
        return 1
    
    # Process the next texture generation task in the queue
    if not bpy.context.scene.dream_texture_settings.in_process:
        if not task_queue.empty():
            if not bpy.context.scene.dream_textures_prompt.control_nets:
                bpy.context.scene.dream_textures_prompt.control_nets.add()
                bpy.context.scene.dream_textures_prompt.control_nets[0].conditioning_scale = 5
                bpy.context.scene.dream_textures_prompt.control_nets[0].control_net = 'models--lllyasviel--control_v11p_sd15_seg'

            obj_name, material, i = task_queue.get()
            print(f"Processing... {obj_name} {material.name}")
            if material is not None:      
                image_name = f"{obj_name}_{i}_T_SegmentationMap"
                if bpy.data.images.get(image_name) is None and bpy.context.scene.dream_textures_prompt.control_nets:
                    bpy.context.scene.dream_textures_prompt.control_nets.remove(0)
                    bpy.context.scene.dream_textures_prompt.prompt_structure_token_subject = "a (realistic:1.0) style texture, (small texture:0.5), (wood texture:0.5), (old:0.5), octane render, unreal engine, redshift render"

                else:
                    bpy.context.scene.dream_textures_prompt.control_nets[0].control_image = bpy.data.images[image_name]
                    bpy.context.scene.dream_textures_prompt.prompt_structure_token_subject = "a (realistic:1.0) style texture, (concrete: 0.2), (damaged: 1.0), (wood:0.8), octane render, unreal engine, redshift render"

                bpy.context.scene.dream_texture_settings.in_process = True
                task_manager.current_material = material
                print("[DREAM TEXTURES] Generating texture for material: {}".format(material.name))
                dreamtextures_texture()
        else:
            bpy.context.scene.dream_texture_settings.done = True
            print("[DREAM TEXTURES] DONE XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            # All texture generation tasks are complete, unregister the timer
            return None

    # Return a value greater than zero to keep the timer running
    return 1

# Define a function to generate textures for all materials in the active object
def generate_textures_for_all_materials():
    try:
        bpy.data.images.remove(bpy.data.images["DreamTexture Output"])
    except:
        pass
    objects = bpy.context.scene.objects
    # Create a queue to hold the texture generation tasks
    task_queue = queue.Queue()
    task_manager = DreamTaskManager()
    i = 0
    
    for obj in objects:
        print(obj.name)
        if obj.type == 'MESH':
            materials = obj.data.materials
            
            print(obj.name)

            # Add each material and Dream Textures settings to the queue
            for i, material in enumerate(materials, start=1):

                task_queue.put((obj.name, material,i))
                print("[DREAM TEXTURES] Adding to queue:", material.name)
                # Register a timer to process the texture genernation queue
    bpy.app.timers.register(lambda: process_texture_queue(task_queue, task_manager))
    # task_queue.put((None, None, None))

def register_dream_texture_settings():
    try:
        bpy.utils.register_class(DreamTexturesSettings)
    except:
        pass

    bpy.types.Scene.dream_texture_settings = bpy.props.PointerProperty(type=DreamTexturesSettings)

    bpy.context.scene.dream_texture_settings.started = False
    bpy.context.scene.dream_texture_settings.in_process = False
    bpy.context.scene.dream_texture_settings.done = False

def run_process():
    generate_textures_for_all_materials()
    
if __name__ == "__main__":
    tile_collection, imported_collection= utils.import_gltf_files("C:/Users/Vertex Studio/Desktop/2023/250523/microverse-component-library-v0.0.2/archive_temp//") 
#    register_dream_texture_settings()
#    smap.segmentation_map()
#    run_process()
