import bpy
from bpy.types import Panel, Operator, Menu
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
            # Store original name and location
            orig_name = selected_obj.name
            orig_location = selected_obj.location.copy()
            orig_parent = selected_obj.parent
            
            # Create empty parent at original location with original name
            empty = bpy.data.objects.new(orig_name, None)
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

class HYPERFY_OT_create_multiple_rigidbodies(Operator):
    """Create rigidbodies for all selected objects while maintaining hierarchy"""
    bl_idname = "hyperfy.create_multiple_rigidbodies"
    bl_label = "Create Multiple Rigidbodies"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Store selected objects, their original names and parents
        selected_objects = [(obj, obj.name, obj.parent) for obj in context.selected_objects if obj.type == 'MESH']
        
        # Store current trigger state
        trigger_state = context.scene.hyperfy_trigger
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        created_count = 0
        for obj, original_name, original_parent in selected_objects:
            # Select and make active
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            # Create rigidbody
            bpy.ops.hyperfy.create_rigidbody()
            
            # Get the newly created rigidbody empty and rename it
            new_empty = context.active_object
            new_empty.name = original_name
            
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

class HYPERFY_PT_main_panel(Panel):
    """Hyperfy Tools Panel"""
    bl_label = "Hyperfy Tools"
    bl_idname = "HYPERFY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'

    def draw(self, context):
        layout = self.layout
        active_obj = context.active_object
        selected_objects = context.selected_objects
        
        # Get all selected rigidbody setups
        rigidbody_objects = []
        for obj in selected_objects:
            if obj.get("node") == "rigidbody":
                rigidbody_objects.append(obj)
            elif obj.get("node") in ["Mesh", "collider"] and obj.parent:
                if obj.parent.get("node") == "rigidbody" and obj.parent not in rigidbody_objects:
                    rigidbody_objects.append(obj.parent)
        
        # Show details if any rigidbody setup is selected
        if rigidbody_objects:
            details_box = layout.box()
            details_box.alert = True
            if len(rigidbody_objects) > 1:
                details_box.label(text=f"⚡ MULTIPLE RIGIDBODIES ({len(rigidbody_objects)}) ⚡", icon='PROPERTIES')
            else:
                details_box.label(text="⚡ RIGIDBODY DETAILS ⚡", icon='PROPERTIES')
            
            # Rigidbody properties
            col = details_box.column(align=True)
            col.scale_y = 1.1
            col.use_property_split = True
            
            # Create operators for batch property editing
            row = col.row(align=True)
            row.label(text="Type:")
            for type_option in [('static', "Static"), ('dynamic', "Dynamic"), ('kinematic', "Kinematic")]:
                op = row.operator("hyperfy.set_rigidbody_type", text=type_option[1])
                op.type = type_option[0]
                op.target_objects = [obj.name for obj in rigidbody_objects]
            
            # Mass (use first object's value as default)
            col.prop(rigidbody_objects[0], '["mass"]', text="Mass")
            
            # Get all mesh and collider children
            all_mesh_objects = []
            all_collider_objects = []
            for rb in rigidbody_objects:
                for child in rb.children:
                    if child.get("node") == "Mesh":
                        all_mesh_objects.append(child)
                    elif child.get("node") == "collider":
                        all_collider_objects.append(child)
            
            if all_mesh_objects:
                # Mesh properties
                mesh_box = details_box.box()
                mesh_box.label(text="▸ MESH PROPERTIES", icon='MESH_DATA')
                col = mesh_box.column(align=True)
                row = col.row(align=True)
                
                # Create operators for batch mesh property editing
                op = row.operator("hyperfy.set_mesh_property", text="Cast Shadow")
                op.property_name = "castShadow"
                op.target_objects = [obj.name for obj in all_mesh_objects]
                
                op = row.operator("hyperfy.set_mesh_property", text="Receive Shadow")
                op.property_name = "receiveShadow"
                op.target_objects = [obj.name for obj in all_mesh_objects]
            
            if all_collider_objects:
                # Collider properties
                col_box = details_box.box()
                col_box.label(text="▸ COLLIDER PROPERTIES", icon='MOD_MESHDEFORM')
                col = col_box.column(align=True)
                row = col.row(align=True)
                
                # Create operators for batch collider property editing
                op = row.operator("hyperfy.set_collider_property", text="Convex")
                op.property_name = "convex"
                op.target_objects = [obj.name for obj in all_collider_objects]
                
                op = row.operator("hyperfy.set_collider_property", text="Trigger")
                op.property_name = "trigger"
                op.target_objects = [obj.name for obj in all_collider_objects]
            
            details_box.separator()
        
        # Show creation controls if nothing is selected or if selected object is not part of a rigidbody
        if not active_obj or not rigidbody_objects:
            # Physics section
            main_box = layout.box()
            main_box.alert = True
            main_box.label(text="⚡ RIGIDBODY CREATION ⚡", icon='PHYSICS')
            
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
        
        # Only show export section when viewing rigidbody details
        if rigidbody_objects:
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

# Add these new operators for batch editing
class HYPERFY_OT_set_rigidbody_type(Operator):
    """Set type for multiple rigidbodies"""
    bl_idname = "hyperfy.set_rigidbody_type"
    bl_label = "Set Rigidbody Type"
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj["type"] = self.type
        return {'FINISHED'}

class HYPERFY_OT_set_mesh_property(Operator):
    """Set property for multiple mesh objects"""
    bl_idname = "hyperfy.set_mesh_property"
    bl_label = "Set Mesh Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                # Toggle the property
                obj[self.property_name] = not obj.get(self.property_name, True)
        return {'FINISHED'}

class HYPERFY_OT_set_collider_property(Operator):
    """Set property for multiple collider objects"""
    bl_idname = "hyperfy.set_collider_property"
    bl_label = "Set Collider Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                # Toggle the property
                obj[self.property_name] = not obj.get(self.property_name, True)
        return {'FINISHED'} 