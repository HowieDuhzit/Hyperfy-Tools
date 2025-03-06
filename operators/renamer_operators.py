import bpy
import re
from bpy.props import (StringProperty, 
                       BoolProperty,
                       IntProperty,
                       EnumProperty)

class OBJECT_OT_batch_rename(bpy.types.Operator):
    """Batch rename selected objects with various options"""
    bl_idname = "object.batch_rename"
    bl_label = "Batch Rename"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        selected_objects = context.selected_objects
        
        # Skip if no objects selected
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        # Apply operations based on user selection
        for obj in selected_objects:
            new_name = obj.name
            
            # 1. Find and replace
            if scene.use_find_replace:
                if scene.find_text in new_name:
                    new_name = new_name.replace(scene.find_text, scene.replace_text)
            
            # 2. Add/remove prefix
            if scene.use_prefix:
                if scene.prefix_operation == 'ADD':
                    new_name = scene.prefix_text + new_name
                elif scene.prefix_operation == 'REMOVE':
                    prefix_len = len(scene.prefix_text)
                    if new_name.startswith(scene.prefix_text):
                        new_name = new_name[prefix_len:]
            
            # 3. Add/remove suffix
            if scene.use_suffix:
                if scene.suffix_operation == 'ADD':
                    new_name = new_name + scene.suffix_text
                elif scene.suffix_operation == 'REMOVE':
                    suffix_len = len(scene.suffix_text)
                    if new_name.endswith(scene.suffix_text):
                        new_name = new_name[:-suffix_len]
            
            # 4. Case conversion
            if scene.use_case_conversion:
                if scene.case_conversion == 'UPPER':
                    new_name = new_name.upper()
                elif scene.case_conversion == 'LOWER':
                    new_name = new_name.lower()
                elif scene.case_conversion == 'TITLE':
                    new_name = new_name.title()
            
            # 5. Numbering
            if scene.use_numbering:
                # Get the base name without existing numbering
                base_name = re.sub(r'[0-9]+$', '', new_name).rstrip('._- ')
                
                if scene.numbering_position == 'PREFIX':
                    new_name = f"{scene.numbering_base + scene.numbering_increment * selected_objects.index(obj):0{scene.numbering_padding}d}{scene.numbering_separator}{base_name}"
                else:  # SUFFIX
                    new_name = f"{base_name}{scene.numbering_separator}{scene.numbering_base + scene.numbering_increment * selected_objects.index(obj):0{scene.numbering_padding}d}"
            
            # Apply new name
            obj.name = new_name
        
        return {'FINISHED'}


class OBJECT_OT_clean_names(bpy.types.Operator):
    """Remove special characters from object names"""
    bl_idname = "object.clean_names"
    bl_label = "Clean Names"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            # Replace special characters with underscores
            new_name = re.sub(r'[^\w\s]', '_', obj.name)
            # Remove multiple consecutive underscores
            new_name = re.sub(r'_+', '_', new_name)
            # Strip leading/trailing underscores
            new_name = new_name.strip('_')
            
            obj.name = new_name
        
        return {'FINISHED'}

# Register renamer properties
def register_renamer_properties():
    # Find and replace
    bpy.types.Scene.use_find_replace = BoolProperty(
        name="Use Find & Replace",
        default=False
    )
    bpy.types.Scene.find_text = StringProperty(
        name="Find",
        default=""
    )
    bpy.types.Scene.replace_text = StringProperty(
        name="Replace",
        default=""
    )
    
    # Prefix
    bpy.types.Scene.use_prefix = BoolProperty(
        name="Use Prefix",
        default=False
    )
    bpy.types.Scene.prefix_operation = EnumProperty(
        name="Prefix Operation",
        items=[
            ('ADD', "Add", "Add prefix to name"),
            ('REMOVE', "Remove", "Remove prefix from name")
        ],
        default='ADD'
    )
    bpy.types.Scene.prefix_text = StringProperty(
        name="Prefix Text",
        default=""
    )
    
    # Suffix
    bpy.types.Scene.use_suffix = BoolProperty(
        name="Use Suffix",
        default=False
    )
    bpy.types.Scene.suffix_operation = EnumProperty(
        name="Suffix Operation",
        items=[
            ('ADD', "Add", "Add suffix to name"),
            ('REMOVE', "Remove", "Remove suffix from name")
        ],
        default='ADD'
    )
    bpy.types.Scene.suffix_text = StringProperty(
        name="Suffix Text",
        default=""
    )
    
    # Case conversion
    bpy.types.Scene.use_case_conversion = BoolProperty(
        name="Use Case Conversion",
        default=False
    )
    bpy.types.Scene.case_conversion = EnumProperty(
        name="Case",
        items=[
            ('UPPER', "UPPERCASE", "Convert to uppercase"),
            ('LOWER', "lowercase", "Convert to lowercase"),
            ('TITLE', "Title Case", "Convert to title case")
        ],
        default='UPPER'
    )
    
    # Numbering
    bpy.types.Scene.use_numbering = BoolProperty(
        name="Use Numbering",
        default=False
    )
    bpy.types.Scene.numbering_position = EnumProperty(
        name="Position",
        items=[
            ('PREFIX', "Before Name", "Add number before name"),
            ('SUFFIX', "After Name", "Add number after name")
        ],
        default='SUFFIX'
    )
    bpy.types.Scene.numbering_base = IntProperty(
        name="Start At",
        default=1,
        min=0
    )
    bpy.types.Scene.numbering_increment = IntProperty(
        name="Step",
        default=1,
        min=1
    )
    bpy.types.Scene.numbering_padding = IntProperty(
        name="Padding",
        default=2,
        min=1,
        max=10,
        description="Number of digits in the numbering"
    )
    bpy.types.Scene.numbering_separator = StringProperty(
        name="Separator",
        default="_",
        description="Character between number and name"
    )

# Unregister renamer properties
def unregister_renamer_properties():
    del bpy.types.Scene.use_find_replace
    del bpy.types.Scene.find_text
    del bpy.types.Scene.replace_text
    del bpy.types.Scene.use_prefix
    del bpy.types.Scene.prefix_operation
    del bpy.types.Scene.prefix_text
    del bpy.types.Scene.use_suffix
    del bpy.types.Scene.suffix_operation
    del bpy.types.Scene.suffix_text
    del bpy.types.Scene.use_case_conversion
    del bpy.types.Scene.case_conversion
    del bpy.types.Scene.use_numbering
    del bpy.types.Scene.numbering_position
    del bpy.types.Scene.numbering_base
    del bpy.types.Scene.numbering_increment
    del bpy.types.Scene.numbering_padding
    del bpy.types.Scene.numbering_separator 