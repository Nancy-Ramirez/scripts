import bpy
import os

# Set this to a folder path to load scripts from a specific folder
# Otherwise the folder containing the blend file will be used
folder_path = None

if folder_path is None:
    blend_file_path = bpy.data.filepath
    folder_path = os.path.dirname(blend_file_path)

# Get the name of the current script file
current_script = bpy.context.space_data.text.name

# Get a list of all script files in the blend file
script_files = [t for t in bpy.data.texts if t.is_in_memory == False]

# Delete all script files except the current one
for script_file in script_files:
    if script_file.name != current_script:
        bpy.data.texts.remove(script_file)

# Iterate through the files in the folder and load each script into a text block
for filename in os.listdir(folder_path):
    if filename.endswith(".py"):
        script_path = os.path.join(folder_path, filename)
        script_name = filename
        if script_name not in bpy.data.texts:
            bpy.data.texts.load(script_path)
            bpy.data.texts[script_name].name = script_name

print("[IMPORT SCRIPTS] All scripts were updated.")
