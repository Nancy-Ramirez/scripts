import bpy

dream_textures = bpy.data.texts["dream_textures.py"].as_module()
smap = bpy.data.texts["segmentation_map.py"].as_module()
utils = bpy.data.texts["utils.py"].as_module()

def process_timer():
    if not bpy.context.scene.dream_texture_settings.done:
        if not bpy.context.scene.dream_texture_settings.started:
            print("[TEXTURE GENERATION] Starting Dream Textures...")
            bpy.context.scene.dream_texture_settings.started = True
            dream_textures.run_process()
        print("[DREAM TEXTURES] Processing...")
        return 1   
    
    utils.colortonormals()
    utils.export("C:/Users/Vertex Studio/Desktop/2023/250523/microverse-component-library-v0.0.2//")

    print("[TEXTURE GENERATION] Done!")
    return None

def run_process():
    bpy.app.timers.register(lambda: process_timer())

if __name__ == "__main__": 
    tile_collection, imported_collection= utils.import_gltf_files("C:/Users/Vertex Studio/Desktop/2023/250523/microverse-component-library-v0.0.2/archive_temp//") 
    dream_textures.register_dream_texture_settings()
    smap.segmentation_map()
    run_process()

