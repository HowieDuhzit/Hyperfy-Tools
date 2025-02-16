import bpy
from bpy.types import Operator
from ..utils.rigidbody_utils import process_rigidbody_hierarchy
from ..utils.collider_utils import (
    create_box_collider,
    create_sphere_collider,
    create_simple_collider,
    setup_collider
)
from ..utils.lod_utils import find_col_object

def get_lod_groups(objects):
    """Group objects by their base names (for LOD processing)"""
    lod_groups = {}
    
    for obj in objects:
        base_name = obj.name.lower()
        # Strip LOD and COL suffixes to get base name
        if 'lod' in base_name:
            base_name = base_name.split('lod')[0]
        elif 'col' in base_name:
            base_name = base_name.replace('col', '')
        base_name = base_name.strip()
        
        # Find existing group or create new one
        found_group = None
        for key in lod_groups.keys():
            key_base = key.name.lower()
            if 'lod' in key_base:
                key_base = key_base.split('lod')[0]
            elif 'col' in key_base:
                key_base = key_base.replace('col', '')
            key_base = key_base.strip()
            
            if key_base == base_name:
                found_group = key
                break
        
        if found_group:
            lod_groups[found_group].append(obj)
        else:
            # For new groups, prefer non-COL object as key
            if not obj.name.lower().endswith('col'):
                lod_groups[obj] = [obj]
            else:
                # If only COL object found so far, use it as key
                lod_groups[obj] = [obj]
    
    return lod_groups

class OBJECT_OT_create_rigidbody(Operator):
    """Create a new Rigidbody object"""
    bl_idname = "object.create_rigidbody"
    bl_label = "Create Rigidbody"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        selected_obj = context.active_object
        
        if not selected_obj:
            # Create default cube mesh and collider
            bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
            mesh_obj = context.active_object
            mesh_obj.name = "Mesh"
            collider = create_box_collider(context)
            
            # Create empty parent
            empty = bpy.data.objects.new("Rigidbody", None)
            empty.empty_display_type = 'PLAIN_AXES'
            empty.empty_display_size = 1
            context.scene.collection.objects.link(empty)
            
            # Add rigidbody properties
            empty["node"] = "rigidbody"
            empty["mass"] = props.mass
            empty["type"] = props.physics_type
            
            # Create LOD empty
            lod_empty = bpy.data.objects.new("LOD", None)
            lod_empty.empty_display_type = 'PLAIN_AXES'
            lod_empty.empty_display_size = 0.75
            lod_empty["node"] = "lod"
            context.scene.collection.objects.link(lod_empty)
            lod_empty.parent = empty
            
            # Parent objects
            mesh_obj.parent = lod_empty
            collider.parent = empty
            
        else:
            # Process hierarchy and get processed objects
            processed_objects = process_rigidbody_hierarchy(context, selected_obj)
            
            if not processed_objects:
                self.report({'WARNING'}, "No valid objects to process")
                return {'CANCELLED'}
            
            # Delete all processed original objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in processed_objects:
                obj.select_set(True)
            bpy.ops.object.delete()
        
        return {'FINISHED'}

class OBJECT_OT_create_rigidbodies(Operator):
    """Create rigidbodies for selected objects while maintaining hierarchy"""
    bl_idname = "object.create_rigidbodies"
    bl_label = "Create Rigidbodies"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get selected mesh objects
        selected_meshes = [obj for obj in context.selected_objects 
                         if obj.type == 'MESH' and 
                         (not obj.parent or obj.parent not in context.selected_objects)]
        
        if not selected_meshes:
            self.report({'WARNING'}, "No valid objects selected")
            return {'CANCELLED'}
        
        # Group objects by LOD
        lod_groups = get_lod_groups(selected_meshes)
        
        # Process each group
        all_processed_objects = []
        created_rigidbodies = []  # Store created rigidbody empties
        created_count = 0
        
        for main_obj, lod_variants in lod_groups.items():
            # Process the group with all its LOD variants
            processed = process_rigidbody_hierarchy(context, main_obj, lod_variants=lod_variants)
            if processed:
                all_processed_objects.extend(processed)
                # Find and store the created rigidbody empty
                for obj in context.scene.objects:
                    if (obj.get("node") == "rigidbody" and 
                        obj.name.startswith(main_obj.name.split('LOD')[0].replace('COL', ''))):
                        created_rigidbodies.append(obj)
                created_count += 1
        
        # Delete all processed original objects
        if all_processed_objects:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in all_processed_objects:
                if isinstance(obj, bpy.types.Object):
                    obj.select_set(True)
            bpy.ops.object.delete()
        
        # Select the created rigidbodies
        bpy.ops.object.select_all(action='DESELECT')
        for rb in created_rigidbodies:
            rb.select_set(True)
            context.view_layer.objects.active = rb  # Make the last one active
        
        self.report({'INFO'}, f"Created {created_count} rigidbodies")
        return {'FINISHED'} 