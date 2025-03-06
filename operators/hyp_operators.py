import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
import json
import struct
import os

class OBJECT_OT_import_hyp(Operator, ImportHelper):
    """Import a Hyperfy .hyp file"""
    bl_idname = "object.import_hyp"
    bl_label = "Import HYP"
    filename_ext = ".hyp"
    
    filter_glob: StringProperty(
        default="*.hyp",
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        self.ctrl_pressed = event.ctrl
        return ImportHelper.invoke(self, context, event)
    
    def execute(self, context):
        try:
            with open(self.filepath, 'rb') as f:
                # 1. Read header size (4 bytes, uint32 little-endian)
                header_size = struct.unpack('<I', f.read(4))[0]
                print(f"Header size: {header_size}")
                
                # 2. Read and parse header JSON
                header_json = f.read(header_size).decode('utf-8')
                print(f"Header start: {header_json[:100]}...")
                header = json.loads(header_json)
                
                # Extract blueprint and assets
                blueprint = header.get('blueprint', {})
                assets = header.get('assets', [])
                
                # Get properties early
                props = context.scene.hyperfy_props
                
                # Find the model and script assets
                model_asset = None
                script_asset = None
                
                for asset in assets:
                    if asset['type'] == 'model':
                        model_asset = asset
                    elif asset['type'] == 'script':
                        script_asset = asset
                
                if not model_asset:
                    self.report({'ERROR'}, "No model found in .hyp file")
                    return {'CANCELLED'}
                
                # Check if frozen and no admin override
                is_frozen = blueprint.get('frozen', False)
                
                # Set basic properties early
                props.hyp_name = blueprint.get('name', '') or ''
                props.hyp_frozen = is_frozen
                
                if is_frozen and not self.ctrl_pressed:
                    # Load Suzanne instead of the actual model
                    bpy.ops.mesh.primitive_monkey_add(size=2.0)
                    suzanne = context.active_object
                    suzanne.name = f"FROZEN_{props.hyp_name or 'Object'}"
                    
                    # Add a material with red color to indicate frozen state
                    mat = bpy.data.materials.new(name=f"Frozen_{suzanne.name}")
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red color
                    suzanne.data.materials.append(mat)
                    
                    self.report({'WARNING'}, "This is a frozen file. Loading placeholder model.")
                else:
                    # Normal model loading
                    # Calculate total size of assets before the model
                    offset = 0
                    for asset in assets:
                        if asset == model_asset:
                            break
                        offset += asset['size']
                    
                    # Skip to model data if needed
                    if offset > 0:
                        f.read(offset)
                    
                    # Read model data
                    model_data = f.read(model_asset['size'])
                    
                    # Write temporary GLB file
                    temp_glb = self.filepath.replace('.hyp', '.glb')
                    with open(temp_glb, 'wb') as glb_file:
                        glb_file.write(model_data)
                    
                    try:
                        # Import GLB
                        bpy.ops.import_scene.gltf(filepath=temp_glb)
                        
                        if is_frozen:
                            self.report({'WARNING'}, "Admin Override Active")
                    finally:
                        # Clean up temp GLB
                        if os.path.exists(temp_glb):
                            os.remove(temp_glb)
                
                # Props object properties
                blueprint_props = blueprint.get('props', {})
                props.hyp_interact = bool(blueprint_props.get('interact', False))
                props.hyp_click_distance = float(blueprint_props.get('clickDistance', 10.0))
                props.hyp_collision = bool(blueprint_props.get('collision', True))
                props.hyp_visible = bool(blueprint_props.get('visible', True))
                
                # Handle script based on frozen state
                if script_asset and blueprint.get('script'):
                    # Get the hyp name or use the blueprint name as fallback
                    base_name = props.hyp_name or blueprint.get('name', 'script')
                    
                    # Check if frozen and ctrl not pressed
                    if is_frozen and not self.ctrl_pressed:
                        # Create frozen message
                        script_name = "frozen.js"
                        text = bpy.data.texts.get(script_name)
                        if text:
                            text.clear()
                        else:
                            text = bpy.data.texts.new(name=script_name)
                        
                        frozen_message = f"""// This file ({base_name}) is frozen
// Scripts cannot be viewed or edited on frozen files
// This is to prevent unauthorized modifications
//
// If you need to modify this file, please contact an administrator
"""
                        text.write(frozen_message)
                        props.hyp_script = text.name
                    else:
                        # Normal script handling for unfrozen files or ctrl pressed
                        script_name = f"{base_name}.js"
                        text = bpy.data.texts.get(script_name)
                        if text:
                            text.clear()
                        else:
                            text = bpy.data.texts.new(name=script_name)
                        
                        # Calculate script position
                        script_offset = 0
                        for asset in assets:
                            if asset == script_asset:
                                break
                            script_offset += asset['size']
                        
                        # Seek to start of file + header + script offset
                        f.seek(4 + header_size + script_offset)
                        
                        # Read script content
                        script_content = f.read(script_asset['size']).decode('utf-8')
                        text.write(script_content)
                        
                        # Set the script in properties
                        props.hyp_script = text.name
                
                # Set metadata properties
                props.hyp_id = blueprint.get('id', '')
                props.hyp_version = blueprint.get('version', 0)
                props.hyp_author = blueprint.get('author', '')
                props.hyp_created = blueprint.get('created', '')
                props.hyp_modified = blueprint.get('modified', '')
                
                self.report({'INFO'}, f"Successfully imported .hyp file: {self.filepath}")
                return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read .hyp file: {str(e)}")
            return {'CANCELLED'} 