import bpy
from bpy.types import Operator
import math

def get_rigidbody_parent(obj):
    """Get the rigidbody parent of an object in the hierarchy"""
    current = obj
    while current:
        if current.get("node") == "rigidbody":
            return current
        current = current.parent
    return None

class OBJECT_OT_add_snap_point(Operator):
    """Add a snap point empty object"""
    bl_idname = "object.add_snap_point"
    bl_label = "Add Snap Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get active object and store current mode
        active_obj = context.active_object
        original_mode = context.mode
        locations = [(0, 0, 0)]  # Default location
        
        # Find rigidbody parent
        rigidbody_obj = None
        if active_obj:
            if active_obj.get("node") == "rigidbody":
                rigidbody_obj = active_obj
            else:
                rigidbody_obj = get_rigidbody_parent(active_obj)
        
        if not rigidbody_obj:
            self.report({'WARNING'}, "No rigidbody object selected")
            return {'CANCELLED'}
        
        # Check if we're in edit mode with a mesh object
        if active_obj and active_obj.type == 'MESH' and context.mode == 'EDIT_MESH':
            # Get the selected vertex locations
            bpy.ops.object.mode_set(mode='OBJECT')  # Need to toggle to object mode to get selection
            selected_verts = [v for v in active_obj.data.vertices if v.select]
            if selected_verts:
                # Get world space locations of all selected vertices
                world_matrix = active_obj.matrix_world
                locations = [world_matrix @ v.co.copy() for v in selected_verts]
        
        # Ensure we're in object mode for creating empties
        if original_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        created_empties = []
        # Create empty objects at each location
        for i, location in enumerate(locations):
            # Create empty object at the determined location
            empty = bpy.data.objects.new(f"SnapPoint.{i+1:03d}", None)
            empty.empty_display_type = 'SPHERE'
            empty.empty_display_size = 0.2
            
            # Add to scene
            context.scene.collection.objects.link(empty)
            
            # Add custom property
            empty["node"] = "snap"
            
            # Parent to rigidbody and set location
            empty.parent = rigidbody_obj
            if original_mode == 'EDIT_MESH':
                # Convert world location to local space relative to parent
                empty.location = rigidbody_obj.matrix_world.inverted() @ location
            else:
                empty.location = (0, 0, 0)  # Default at rigidbody origin
            
            created_empties.append(empty)
        
        # Select all created empties and make the last one active
        bpy.ops.object.select_all(action='DESELECT')
        for empty in created_empties:
            empty.select_set(True)
        if created_empties:
            context.view_layer.objects.active = created_empties[-1]
        
        # Restore original mode if it was edit mode and we have a mesh object
        if original_mode == 'EDIT_MESH' and active_obj and active_obj.type == 'MESH':
            # Restore the original active object
            context.view_layer.objects.active = active_obj
            active_obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, f"Added {len(created_empties)} snap point{'s' if len(created_empties) > 1 else ''}")
        return {'FINISHED'} 