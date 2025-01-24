bl_info = {
    "name": "Hyperfy Tools",
    "author": "Howie Duhzit",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Hyperfy",
    "description": "Tools for creating Hyperfy assets",
    "category": "3D View",
}

import bpy
from bpy.types import Panel, Operator
import os

# Create a global variable for custom icons
custom_icons = None

class HYPERFY_OT_create_rigidbody(Operator):
    """Create a new Rigidbody object"""
    bl_idname = "hyperfy.create_rigidbody"
    bl_label = "Create Rigidbody"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_obj = context.active_object
        original_obj = selected_obj  # Store reference to delete later
        
        # Create empty parent
        empty = bpy.data.objects.new("Rigidbody", None)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.empty_display_size = 1
        context.scene.collection.objects.link(empty)
        
        if selected_obj:
            # Position empty at object's location
            empty.location = selected_obj.location.copy()
            
            # Duplicate the selected object for the mesh
            mesh_obj = selected_obj.copy()
            mesh_obj.data = selected_obj.data.copy()
            mesh_obj.name = "Mesh"
            context.scene.collection.objects.link(mesh_obj)
            
            # Reset mesh position relative to parent
            mesh_obj.location = (0, 0, 0)
            
        else:
            # Create default cube mesh
            bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
            mesh_obj = context.active_object
            mesh_obj.name = "Mesh"
        
        # Add mesh properties
        mesh_obj["castShadow"] = context.scene.hyperfy_cast_shadow
        mesh_obj["receiveShadow"] = context.scene.hyperfy_receive_shadow
        mesh_obj["node"] = "Mesh"
        
        # Create collider based on type
        if context.scene.hyperfy_collider_type == 'box':
            bpy.ops.mesh.primitive_cube_add(
                size=2.0,
                location=(0, 0, 0)
            )
            collider = context.active_object
            collider.name = "Collider"
            collider.display_type = 'WIRE'  # Set wireframe display
            
            # Set box size
            collider.scale.x = context.scene.hyperfy_box_width
            collider.scale.y = context.scene.hyperfy_box_height
            collider.scale.z = context.scene.hyperfy_box_depth
            
        elif context.scene.hyperfy_collider_type == 'sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=context.scene.hyperfy_sphere_radius,
                segments=32,
                ring_count=16,
                location=(0, 0, 0)
            )
            collider = context.active_object
            collider.name = "Collider"
            collider.display_type = 'WIRE'  # Set wireframe display
            
        elif context.scene.hyperfy_collider_type == 'simple' and selected_obj:
            # Create simplified collision mesh
            collider = selected_obj.copy()
            collider.data = selected_obj.data.copy()
            context.scene.collection.objects.link(collider)
            collider.location = (0, 0, 0)
            collider.name = "Collider"
            
            # First use voxel remesh to create a solid mesh
            remesh = collider.modifiers.new(name="Remesh", type='REMESH')
            remesh.mode = 'VOXEL'
            remesh.voxel_size = max(collider.dimensions) / 4  # Larger voxels for simpler shape
            
            # Apply remesh
            context.view_layer.objects.active = collider
            bpy.ops.object.modifier_apply(modifier="Remesh")
            
            # Add decimate modifier to reduce poly count dramatically
            decimate = collider.modifiers.new(name="Decimate", type='DECIMATE')
            decimate.decimate_type = 'DISSOLVE'  # Changed from PLANAR to DISSOLVE
            decimate.angle_limit = 0.5  # Larger angle for more reduction
            
            # Apply decimate
            bpy.ops.object.modifier_apply(modifier="Decimate")
            
            # Clean up mesh
            context.view_layer.objects.active = collider
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.05)  # Merge close vertices
            bpy.ops.mesh.dissolve_degenerate()  # Remove bad geometry
            bpy.ops.mesh.delete_loose()  # Remove any floating vertices
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Force non-convex since we're already simplifying
            context.scene.hyperfy_convex = False
            
            # Make sure it's wireframe
            collider.display_type = 'WIRE'
            
            # Parent to empty
            collider.parent = empty
        
        else:  # geometry or fallback
            if selected_obj:
                collider = selected_obj.copy()
                collider.data = selected_obj.data.copy()
                context.scene.collection.objects.link(collider)
                collider.location = (0, 0, 0)
                collider.name = "Collider"
                collider.display_type = 'WIRE'  # Set wireframe display
            else:
                bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
                collider = context.active_object
                collider.name = "Collider"
                collider.display_type = 'WIRE'  # Set wireframe display
        
        # Remove action properties section and only use rigidbody
        empty["node"] = "rigidbody"
        empty["mass"] = context.scene.hyperfy_mass
        empty["type"] = context.scene.hyperfy_physics_type
        
        # Add collider properties
        collider["node"] = "collider"
        collider["type"] = context.scene.hyperfy_collider_type
        collider["convex"] = context.scene.hyperfy_convex
        collider["trigger"] = context.scene.hyperfy_trigger
        
        if context.scene.hyperfy_collider_type == 'sphere':
            collider["radius"] = context.scene.hyperfy_sphere_radius
        
        # Parent objects to empty
        mesh_obj.parent = empty
        collider.parent = empty
        
        # Select the empty and make it active
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        context.view_layer.objects.active = empty
        
        # Delete the original object if it exists
        if original_obj:
            bpy.data.objects.remove(original_obj, do_unlink=True)
        
        return {'FINISHED'}
    
    def draw(self, layout):
        layout.prop(self, "physics_type")

class HYPERFY_OT_export_glb(Operator):
    """Export visible objects as GLB with custom properties"""
    bl_idname = "hyperfy.export_glb"
    bl_label = "Export GLB"
    
    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH',
        default="untitled.glb"
    )
    
    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = "untitled.glb"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    def execute(self, context):
        # Store original visibility states
        visibility_states = {}
        
        # Hide objects that shouldn't be exported
        for obj in bpy.data.objects:
            # Store original states
            visibility_states[obj] = {
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'original_visible': obj.visible_get()  # Store original visibility
            }
            
            # Hide objects that are:
            # 1. Not visible in viewport
            # 2. Display type is wire (colliders)
            # 3. Not mesh objects
            if (not obj.visible_get() or 
                obj.display_type == 'WIRE' or 
                obj.type != 'MESH'):
                obj.hide_viewport = True
                obj.hide_render = True
        
        # Export only visible objects
        bpy.ops.export_scene.gltf(
            filepath=self.filepath,
            export_format='GLB',
            use_selection=False,  # Export all visible objects
            export_extras=True,   # Export custom properties
            export_apply=False
        )
        
        # Restore original visibility states
        for obj in bpy.data.objects:
            if obj in visibility_states:
                state = visibility_states[obj]
                obj.hide_viewport = state['hide_viewport']
                obj.hide_render = state['hide_render']
        
        self.report({'INFO'}, f"Exported visible objects to: {self.filepath}")
        return {'FINISHED'}

class HYPERFY_OT_export_all_glb(Operator):
    """Export all visible top-level objects as separate GLB files"""
    bl_idname = "hyperfy.export_all_glb"
    bl_label = "Export All GLBs"
    
    directory: bpy.props.StringProperty(
        subtype='DIR_PATH',
        default=""
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    def execute(self, context):
        export_dir = self.directory
        
        # Store original selection
        orig_selected = context.selected_objects
        orig_active = context.active_object
        
        bpy.ops.object.select_all(action='DESELECT')
        
        exported_count = 0
        for obj in context.scene.objects:
            if not obj.parent and obj.visible_get():  # Only visible top-level objects
                # Store original location
                orig_location = obj.location.copy()
                obj.location = (0, 0, 0)
                
                # Select object and its children
                obj.select_set(True)
                for child in obj.children_recursive:
                    child.select_set(True)
                
                context.view_layer.objects.active = obj
                
                # Export GLB
                export_path = os.path.join(export_dir, f"{obj.name}.glb")
                bpy.ops.export_scene.gltf(
                    filepath=export_path,
                    use_selection=True,
                    export_format='GLB',
                    export_extras=True,  # Enables custom properties export
                    export_apply=False
                )
                
                # Restore location and deselect
                obj.location = orig_location
                bpy.ops.object.select_all(action='DESELECT')
                exported_count += 1
        
        # Restore original selection
        for obj in orig_selected:
            obj.select_set(True)
        context.view_layer.objects.active = orig_active
        
        self.report({'INFO'}, f"Exported {exported_count} objects to GLB files")
        return {'FINISHED'}

class HYPERFY_OT_create_multiple_rigidbodies(Operator):
    """Create rigidbodies for all selected objects while maintaining hierarchy"""
    bl_idname = "hyperfy.create_multiple_rigidbodies"
    bl_label = "Create Multiple Rigidbodies"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Store selected objects and their original parents
        selected_objects = [(obj, obj.parent) for obj in context.selected_objects if obj.type == 'MESH']
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        created_count = 0
        for obj, original_parent in selected_objects:
            # Select and make active
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            # Create rigidbody
            bpy.ops.hyperfy.create_rigidbody()
            
            # Get the newly created rigidbody empty
            new_empty = context.active_object
            
            # If original had a parent, parent the new empty to it
            if original_parent:
                new_empty.parent = original_parent
            
            created_count += 1
            
            # Deselect for next iteration
            bpy.ops.object.select_all(action='DESELECT')
        
        self.report({'INFO'}, f"Created {created_count} rigidbodies")
        return {'FINISHED'}

class HYPERFY_PT_main_panel(Panel):
    """Hyperfy Tools Panel"""
    bl_label = "Hyperfy Tools"
    bl_idname = "HYPERFY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'

    def draw(self, context):
        layout = self.layout
        
        # Physics section
        main_box = layout.box()
        main_box.alert = True
        main_box.label(text="⚡ PHYSICS SYSTEM ⚡", icon='PHYSICS')
        
        # Rigidbody Settings with neon effect
        rb_box = main_box.box()
        rb_box.label(text="▸ RIGIDBODY", icon='OUTLINER_OB_EMPTY')
        col = rb_box.column(align=True)
        col.scale_y = 1.1
        col.use_property_split = True
        col.use_property_decorate = False  # No animation dots
        col.prop(context.scene, "hyperfy_physics_type", text="")
        col.prop(context.scene, "hyperfy_mass")
        
        # Mesh Settings with purple tint
        mesh_box = main_box.box()
        mesh_box.alert = True  # Will use purple color
        mesh_box.label(text="▸ MESH", icon='MESH_DATA')
        col = mesh_box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, "hyperfy_cast_shadow")
        row.prop(context.scene, "hyperfy_receive_shadow")
        
        # Collider Settings with blue tint
        col_box = main_box.box()
        col_box.alert = True  # Will use blue color
        col_box.label(text="▸ COLLIDER", icon='MOD_MESHDEFORM')
        col = col_box.column(align=True)
        col.scale_y = 1.1
        col.prop(context.scene, "hyperfy_collider_type", text="")
        
        # Show relevant properties based on collider type
        if context.scene.hyperfy_collider_type == 'box':
            box_col = col.column(align=True)
            box_col.scale_y = 1.1
            box_col.use_property_split = True
            box_col.prop(context.scene, "hyperfy_box_width")
            box_col.prop(context.scene, "hyperfy_box_height")
            box_col.prop(context.scene, "hyperfy_box_depth")
        elif context.scene.hyperfy_collider_type == 'sphere':
            col.use_property_split = True
            col.prop(context.scene, "hyperfy_sphere_radius")
        
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, "hyperfy_convex", icon='MESH_ICOSPHERE')
        row.prop(context.scene, "hyperfy_trigger", icon='GHOST_ENABLED')
        
        # Create buttons with gradient effect
        main_box.separator()
        
        # Single rigidbody creation
        create_row = main_box.row(align=True)
        create_row.scale_y = 1.8
        create_row.operator("hyperfy.create_rigidbody", text="⚡ CREATE RIGIDBODY ⚡", icon='ADD')
        
        # Multiple rigidbody creation
        create_multi_row = main_box.row(align=True)
        create_multi_row.scale_y = 1.4
        create_multi_row.operator("hyperfy.create_multiple_rigidbodies", 
            text="⚡ CREATE MULTIPLE RIGIDBODIES ⚡", icon='GROUP')
        
        # Export section
        export_box = layout.box()
        export_box.alert = True
        export_box.label(text="▸ EXPORT OPTIONS", icon='EXPORT')
        
        # Single GLB export
        row = export_box.row(align=True)
        row.scale_y = 1.4
        row.operator("hyperfy.export_glb", text="EXPORT SCENE", icon='FILE_BLEND')
        
        # Batch GLB export
        row = export_box.row(align=True)
        row.scale_y = 1.4
        row.operator("hyperfy.export_all_glb", text="EXPORT OBJECTS", icon='PACKAGE')
        
        # Info text
        info_box = export_box.box()
        col = info_box.column(align=True)
        col.scale_y = 0.8
        col.label(text="Scene: Export entire scene as single GLB", icon='INFO')
        col.label(text="Objects: Export each object as separate GLB", icon='INFO')

classes = (
    HYPERFY_OT_create_rigidbody,
    HYPERFY_OT_create_multiple_rigidbodies,
    HYPERFY_OT_export_glb,
    HYPERFY_OT_export_all_glb,
    HYPERFY_PT_main_panel,
)

def register():
    # Remove icon loading code
    bpy.types.Scene.hyperfy_physics_type = bpy.props.EnumProperty(
        name="Type",
        description="Physics type for the rigidbody",
        items=[
            ('static', "Static", "Non-moving collision object"),
            ('dynamic', "Dynamic", "Physics-driven object"),
            ('kinematic', "Kinematic", "Animated collision object")
        ],
        default='static'
    )
    bpy.types.Scene.hyperfy_mass = bpy.props.FloatProperty(
        name="Mass",
        description="Mass of the rigidbody",
        default=1.0,
        min=0.0,
        max=1000.0
    )
    
    # Mesh properties
    bpy.types.Scene.hyperfy_cast_shadow = bpy.props.BoolProperty(
        name="Cast Shadow",
        description="Whether the mesh should cast shadows",
        default=True
    )
    bpy.types.Scene.hyperfy_receive_shadow = bpy.props.BoolProperty(
        name="Receive Shadow",
        description="Whether the mesh should receive shadows",
        default=True
    )
    
    # Collider properties
    bpy.types.Scene.hyperfy_collider_type = bpy.props.EnumProperty(
        name="Collider Type",
        description="Type of collision shape",
        items=[
            ('box', "Box", "Box collision shape"),
            ('sphere', "Sphere", "Sphere collision shape"),
            ('geometry', "Geometry", "Use exact mesh geometry for collision (complex)"),
            ('simple', "Simple Collision", "Generate simplified collision from mesh")
        ],
        default='box'
    )
    bpy.types.Scene.hyperfy_convex = bpy.props.BoolProperty(
        name="Convex",
        description="Use convex collision shape (more performant, allows dynamic-dynamic collisions)",
        default=True
    )
    bpy.types.Scene.hyperfy_trigger = bpy.props.BoolProperty(
        name="Trigger",
        description="Make this a trigger volume (no physical collisions)",
        default=False
    )
    
    # Box collider size properties
    bpy.types.Scene.hyperfy_box_width = bpy.props.FloatProperty(
        name="Width",
        description="Width of box collider",
        default=1.0,
        min=0.01
    )
    bpy.types.Scene.hyperfy_box_height = bpy.props.FloatProperty(
        name="Height", 
        description="Height of box collider",
        default=1.0,
        min=0.01
    )
    bpy.types.Scene.hyperfy_box_depth = bpy.props.FloatProperty(
        name="Depth",
        description="Depth of box collider",
        default=1.0,
        min=0.01
    )
    
    # Sphere collider properties
    bpy.types.Scene.hyperfy_sphere_radius = bpy.props.FloatProperty(
        name="Radius",
        description="Radius of sphere collider",
        default=0.5,
        min=0.01
    )
    
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Remove icon unloading code
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.hyperfy_physics_type
    del bpy.types.Scene.hyperfy_mass
    del bpy.types.Scene.hyperfy_cast_shadow
    del bpy.types.Scene.hyperfy_receive_shadow
    del bpy.types.Scene.hyperfy_collider_type
    del bpy.types.Scene.hyperfy_convex
    del bpy.types.Scene.hyperfy_trigger
    del bpy.types.Scene.hyperfy_box_width
    del bpy.types.Scene.hyperfy_box_height
    del bpy.types.Scene.hyperfy_box_depth
    del bpy.types.Scene.hyperfy_sphere_radius

if __name__ == "__main__":
    register() 