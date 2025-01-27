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

def setup_collider(obj, context):
    """Setup common collider properties"""
    obj.name = "Collider"
    obj.display_type = 'WIRE'
    obj.data.materials.clear()
    
    # Add only essential collider properties
    obj["node"] = "collider"
    obj["convex"] = context.scene.hyperfy_convex
    obj["trigger"] = context.scene.hyperfy_trigger
    
    return obj

def is_collider(obj):
    """Check if object is already a collider"""
    return obj.get("node") == "collider" and obj.display_type == 'WIRE'

def create_box_collider(context):
    """Create a box collider"""
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
    collider = context.active_object
    setup_collider(collider, context)
    
    # Set box size
    collider.scale.x = context.scene.hyperfy_box_width
    collider.scale.y = context.scene.hyperfy_box_height
    collider.scale.z = context.scene.hyperfy_box_depth
    
    return collider

def create_sphere_collider(context):
    """Create a sphere collider"""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=context.scene.hyperfy_sphere_radius,
        segments=32,
        ring_count=16,
        location=(0, 0, 0)
    )
    collider = context.active_object
    setup_collider(collider, context)
    return collider

def create_simple_collider(obj, context):
    """Create a simplified collision mesh"""
    collider = obj.copy()
    collider.data = obj.data.copy()
    context.scene.collection.objects.link(collider)
    collider.location = (0, 0, 0)
    setup_collider(collider, context)
    
    # First use voxel remesh to create a solid mesh
    remesh = collider.modifiers.new(name="Remesh", type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = max(collider.dimensions) / 4
    
    # Apply remesh
    context.view_layer.objects.active = collider
    bpy.ops.object.modifier_apply(modifier="Remesh")
    
    # Add decimate modifier
    decimate = collider.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.decimate_type = 'DISSOLVE'
    decimate.angle_limit = 0.5
    
    # Apply decimate
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    # Clean up mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.05)
    bpy.ops.mesh.dissolve_degenerate()
    bpy.ops.mesh.delete_loose()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return collider

class HYPERFY_OT_create_rigidbody(Operator):
    """Create a new Rigidbody object"""
    bl_idname = "hyperfy.create_rigidbody"
    bl_label = "Create Rigidbody"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_obj = context.active_object
        
        if not selected_obj:
            # Create default cube mesh and collider
            bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
            mesh_obj = context.active_object
            mesh_obj.name = "Mesh"
            collider = create_box_collider(context)
        else:
            # Store original location and parent
            orig_location = selected_obj.location.copy()
            orig_parent = selected_obj.parent
            
            # Create empty parent at original location
            empty = bpy.data.objects.new("Rigidbody", None)
            empty.empty_display_type = 'PLAIN_AXES'
            empty.empty_display_size = 1
            empty.location = orig_location
            context.scene.collection.objects.link(empty)
            
            # Check if selected object is already a collider
            if is_collider(selected_obj):
                # Create mesh from collider
                mesh_obj = selected_obj.copy()
                mesh_obj.data = selected_obj.data.copy()
                mesh_obj.name = "Mesh"
                context.scene.collection.objects.link(mesh_obj)
                mesh_obj.location = (0, 0, 0)
                mesh_obj.display_type = 'TEXTURED'  # Reset display type
                
                # Create collider from existing collider
                collider = selected_obj.copy()
                collider.data = selected_obj.data.copy()
                context.scene.collection.objects.link(collider)
                collider.location = (0, 0, 0)
                setup_collider(collider, context)
            else:
                # Create mesh from regular object
                mesh_obj = selected_obj.copy()
                mesh_obj.data = selected_obj.data.copy()
                mesh_obj.name = "Mesh"
                context.scene.collection.objects.link(mesh_obj)
                mesh_obj.location = (0, 0, 0)
                
                # Create appropriate collider
                if context.scene.hyperfy_collider_type == 'box':
                    collider = create_box_collider(context)
                elif context.scene.hyperfy_collider_type == 'sphere':
                    collider = create_sphere_collider(context)
                elif context.scene.hyperfy_collider_type == 'simple':
                    collider = create_simple_collider(selected_obj, context)
                else:  # geometry
                    collider = selected_obj.copy()
                    collider.data = selected_obj.data.copy()
                    context.scene.collection.objects.link(collider)
                    collider.location = (0, 0, 0)
                    setup_collider(collider, context)
            
            # Add mesh properties
            mesh_obj["castShadow"] = context.scene.hyperfy_cast_shadow
            mesh_obj["receiveShadow"] = context.scene.hyperfy_receive_shadow
            mesh_obj["node"] = "Mesh"
            
            # Delete original object and its hierarchy
            if orig_parent and orig_parent.get("node") == "rigidbody":
                # If part of existing rigidbody setup, delete the whole setup
                for child in orig_parent.children[:]:  # Use slice to avoid modification during iteration
                    bpy.data.objects.remove(child, do_unlink=True)
                bpy.data.objects.remove(orig_parent, do_unlink=True)
            else:
                # Just delete the original object
                bpy.data.objects.remove(selected_obj, do_unlink=True)
            
            # Add rigidbody properties
            empty["node"] = "rigidbody"
            empty["mass"] = context.scene.hyperfy_mass
            empty["type"] = context.scene.hyperfy_physics_type
            
            # Parent objects
            mesh_obj.parent = empty
            collider.parent = empty
            
            # Select the empty
            bpy.ops.object.select_all(action='DESELECT')
            empty.select_set(True)
            context.view_layer.objects.active = empty
        
        return {'FINISHED'}
    
    def draw(self, layout):
        layout.prop(self, "physics_type")

class HYPERFY_OT_export_glb(Operator):
    """Export selected objects as GLB with custom properties"""
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
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        # Export selected objects
        bpy.ops.export_scene.gltf(
            filepath=self.filepath,
            export_format='GLB',
            use_selection=True,
            export_extras=True
        )
        
        self.report({'INFO'}, f"Exported selected objects to: {self.filepath}")
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
        
        # Store current trigger state
        trigger_state = context.scene.hyperfy_trigger
        
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
            
            # Make sure trigger state is correctly set on the collider
            for child in new_empty.children:
                if child.name == "Collider":
                    child["trigger"] = trigger_state
            
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
        
        # Export section with gradient border
        export_box = layout.box()
        export_box.alert = True
        export_box.label(text="▸ EXPORT OPTIONS", icon='EXPORT')
        
        # Single object export
        row = export_box.row(align=True)
        row.scale_y = 1.4
        row.operator("hyperfy.export_glb", text="EXPORT OBJECT", icon='OBJECT_DATA')
        
        # Batch export
        row = export_box.row(align=True)
        row.scale_y = 1.4
        row.operator("hyperfy.export_all_glb", text="EXPORT ALL OBJECTS", icon='PACKAGE')
        
        # Info text
        info_box = export_box.box()
        col = info_box.column(align=True)
        col.scale_y = 0.8
        col.label(text="Object: Export selected objects", icon='INFO')
        col.label(text="All: Export each object separately", icon='INFO')

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