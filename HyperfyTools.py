import bpy
from bpy.types import Panel, Operator, Menu
import os

# Create a global variable for custom icons
custom_icons = None

def setup_collider(obj, context):
    """Setup common collider properties"""
    props = context.scene.hyperfy_props  # Get the property group
    
    obj.name = "Collider"
    obj.display_type = 'WIRE'
    
    # Only clear materials if object is mesh
    if obj.type == 'MESH':
        obj.data.materials.clear()
    
    # Add only essential collider properties
    obj["node"] = "collider"
    obj["convex"] = props.convex  # Use props instead of scene
    obj["trigger"] = props.trigger  # Use props instead of scene
    
    return obj

def is_collider(obj):
    """Check if object is already a collider"""
    return obj.get("node") == "collider" and obj.display_type == 'WIRE'

def create_box_collider(context):
    """Create a box collider"""
    props = context.scene.hyperfy_props  # Get the property group
    
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
    collider = context.active_object
    setup_collider(collider, context)
    
    # Set box size using props
    collider.scale.x = props.box_width
    collider.scale.y = props.box_height
    collider.scale.z = props.box_depth
    
    return collider

def create_sphere_collider(context):
    """Create a sphere collider"""
    props = context.scene.hyperfy_props  # Get the property group
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=props.sphere_radius,  # Use props
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

# Create a PropertyGroup to collect all properties
class HyperfyProperties(bpy.types.PropertyGroup):
    physics_type: bpy.props.EnumProperty(
        items=[
            ('dynamic', 'Dynamic', 'Object is affected by physics'),
            ('static', 'Static', 'Object is immovable'),
            ('kinematic', 'Kinematic', 'Object is controlled by animation')
        ],
        default='dynamic',
        name="Physics Type"
    )
    mass: bpy.props.FloatProperty(
        name="Mass",
        default=1.0,
        min=0.0
    )
    convex: bpy.props.BoolProperty(
        name="Convex",
        default=True
    )
    trigger: bpy.props.BoolProperty(
        name="Trigger",
        default=False
    )
    cast_shadow: bpy.props.BoolProperty(
        name="Cast Shadow",
        default=True
    )
    receive_shadow: bpy.props.BoolProperty(
        name="Receive Shadow",
        default=True
    )
    collider_type: bpy.props.EnumProperty(
        items=[
            ('box', 'Box', 'Box collider'),
            ('sphere', 'Sphere', 'Sphere collider'),
            ('simple', 'Simple', 'Simplified mesh collider'),
            ('geometry', 'Geometry', 'Full geometry collider')
        ],
        default='box',
        name="Collider Type"
    )
    box_width: bpy.props.FloatProperty(
        name="Width",
        default=1.0,
        min=0.0
    )
    box_height: bpy.props.FloatProperty(
        name="Height",
        default=1.0,
        min=0.0
    )
    box_depth: bpy.props.FloatProperty(
        name="Depth",
        default=1.0,
        min=0.0
    )
    sphere_radius: bpy.props.FloatProperty(
        name="Radius",
        default=1.0,
        min=0.0
    )

# Update operator names to use standard tags
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
                if props.collider_type == 'box':
                    collider = create_box_collider(context)
                elif props.collider_type == 'sphere':
                    collider = create_sphere_collider(context)
                elif props.collider_type == 'simple':
                    collider = create_simple_collider(selected_obj, context)
                else:  # geometry
                    collider = selected_obj.copy()
                    collider.data = selected_obj.data.copy()
                    context.scene.collection.objects.link(collider)
                    collider.location = (0, 0, 0)
                    setup_collider(collider, context)
            
            # Add mesh properties
            mesh_obj["castShadow"] = props.cast_shadow
            mesh_obj["receiveShadow"] = props.receive_shadow
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
            empty["mass"] = props.mass
            empty["type"] = props.physics_type
            
            # Parent objects
            mesh_obj.parent = empty
            collider.parent = empty
            
            # Select the empty
            bpy.ops.object.select_all(action='DESELECT')
            empty.select_set(True)
            context.view_layer.objects.active = empty
        
        return {'FINISHED'}

class OBJECT_OT_create_multiple_rigidbodies(Operator):
    """Create rigidbodies for all selected objects while maintaining hierarchy"""
    bl_idname = "object.create_multiple_rigidbodies"
    bl_label = "Create Multiple Rigidbodies"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        # Store selected objects, their original names and parents
        selected_objects = [(obj, obj.name, obj.parent) for obj in context.selected_objects if obj.type == 'MESH']
        
        # Store current trigger state
        trigger_state = props.trigger
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        created_count = 0
        for obj, original_name, original_parent in selected_objects:
            # Select and make active
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            # Create rigidbody
            bpy.ops.object.create_rigidbody()
            
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

class OBJECT_OT_export_glb(Operator):
    """Export selected objects as GLB with custom properties"""
    bl_idname = "object.export_glb"
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

class OBJECT_OT_export_all_glb(Operator):
    """Export all visible top-level objects as separate GLB files"""
    bl_idname = "object.export_all_glb"
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

class OBJECT_OT_set_rigidbody_type(Operator):
    """Set type for multiple rigidbodies"""
    bl_idname = "object.set_rigidbody_type"
    bl_label = "Set Rigidbody Type"
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj["type"] = self.type
        return {'FINISHED'}

class OBJECT_OT_set_mesh_property(Operator):
    """Set property for multiple mesh objects"""
    bl_idname = "object.set_mesh_property"
    bl_label = "Set Mesh Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                # Toggle the property
                obj[self.property_name] = not obj.get(self.property_name, True)
        return {'FINISHED'}

class OBJECT_OT_set_collider_property(Operator):
    """Set property for multiple collider objects"""
    bl_idname = "object.set_collider_property"
    bl_label = "Set Collider Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                # Toggle the property
                obj[self.property_name] = not obj.get(self.property_name, True)
        return {'FINISHED'}

class HYPERFY_PT_main_panel(Panel):
    """Hyperfy Tools Panel"""
    bl_label = "Hyperfy Tools"
    bl_idname = "HYPERFY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'

    @classmethod
    def poll(cls, context):
        # Only show panel when no armature is selected
        return not (context.active_object and context.active_object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        props = context.scene.hyperfy_props
        active_obj = context.active_object
        selected_objects = context.selected_objects
        
        # Get all selected rigidbody setups
        rigidbody_objects = []
        if active_obj:  # Check active object first
            if active_obj.get("node") == "rigidbody":
                rigidbody_objects.append(active_obj)
            elif active_obj.get("node") in ["Mesh", "collider"] and active_obj.parent:
                if active_obj.parent.get("node") == "rigidbody":
                    rigidbody_objects.append(active_obj.parent)
        
        # Show creation controls if no rigidbody is selected
        if not rigidbody_objects:
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
            col.prop(props, "physics_type", text="")
            col.prop(props, "mass")
            
            # Mesh Settings with purple tint
            mesh_box = main_box.box()
            mesh_box.alert = True  # Will use purple color
            mesh_box.label(text="▸ MESH", icon='MESH_DATA')
            col = mesh_box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(props, "cast_shadow")
            row.prop(props, "receive_shadow")
            
            # Collider Settings with blue tint
            col_box = main_box.box()
            col_box.alert = True  # Will use blue color
            col_box.label(text="▸ COLLIDER", icon='MOD_MESHDEFORM')
            col = col_box.column(align=True)
            col.scale_y = 1.1
            col.prop(props, "collider_type", text="")
            
            # Show relevant properties based on collider type
            if props.collider_type == 'box':
                box_col = col.column(align=True)
                box_col.scale_y = 1.1
                box_col.use_property_split = True
                box_col.prop(props, "box_width")
                box_col.prop(props, "box_height")
                box_col.prop(props, "box_depth")
            elif props.collider_type == 'sphere':
                col.use_property_split = True
                col.prop(props, "sphere_radius")
            
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(props, "convex", icon='MESH_ICOSPHERE')
            row.prop(props, "trigger", icon='GHOST_ENABLED')
            
            # Create buttons with gradient effect
            main_box.separator()
            
            # Single rigidbody creation
            create_row = main_box.row(align=True)
            create_row.scale_y = 1.8
            create_row.operator("object.create_rigidbody", text="⚡ CREATE RIGIDBODY ⚡", icon='ADD')
            
            # Multiple rigidbody creation
            create_multi_row = main_box.row(align=True)
            create_multi_row.scale_y = 1.4
            create_multi_row.operator("object.create_multiple_rigidbodies", 
                text="⚡ CREATE MULTIPLE RIGIDBODIES ⚡", icon='GROUP')
        
        else:  # Show details and export if rigidbody is selected
            # Details section
            details_box = layout.box()
            details_box.alert = True
            details_box.label(text="⚡ RIGIDBODY DETAILS ⚡", icon='PROPERTIES')
            
            # Rigidbody properties
            col = details_box.column(align=True)
            col.scale_y = 1.1
            col.use_property_split = True
            
            # Type and mass
            col.prop(rigidbody_objects[0], '["type"]', text="Type")
            col.prop(rigidbody_objects[0], '["mass"]', text="Mass")
            
            # Find mesh and collider children
            mesh_obj = None
            collider_obj = None
            for child in rigidbody_objects[0].children:
                if child.get("node") == "Mesh":
                    mesh_obj = child
                elif child.get("node") == "collider":
                    collider_obj = child
            
            if mesh_obj:
                # Mesh properties
                mesh_box = details_box.box()
                mesh_box.label(text="▸ MESH PROPERTIES", icon='MESH_DATA')
                col = mesh_box.column(align=True)
                row = col.row(align=True)
                row.prop(mesh_obj, '["castShadow"]', text="Cast Shadow")
                row.prop(mesh_obj, '["receiveShadow"]', text="Receive Shadow")
            
            if collider_obj:
                # Collider properties
                col_box = details_box.box()
                col_box.label(text="▸ COLLIDER PROPERTIES", icon='MOD_MESHDEFORM')
                col = col_box.column(align=True)
                row = col.row(align=True)
                row.prop(collider_obj, '["convex"]', text="Convex")
                row.prop(collider_obj, '["trigger"]', text="Trigger")
            
            details_box.separator()
            
            # Export section
            export_box = layout.box()
            export_box.alert = True
            export_box.label(text="▸ EXPORT OPTIONS", icon='EXPORT')
            
            # Single object export
            row = export_box.row(align=True)
            row.scale_y = 1.4
            row.operator("object.export_glb", text="EXPORT OBJECT", icon='OBJECT_DATA')
            
            # Batch export
            row = export_box.row(align=True)
            row.scale_y = 1.4
            row.operator("object.export_all_glb", text="EXPORT ALL OBJECTS", icon='PACKAGE')
            
            # Info text
            info_box = export_box.box()
            col = info_box.column(align=True)
            col.scale_y = 0.8
            col.label(text="Object: Export selected objects", icon='INFO')
            col.label(text="All: Export each object separately", icon='INFO')

class HYPERFY_PT_rig_converter_panel(Panel):
    """Rig Converter Panel for converting between Mixamo and VRM rigs"""
    bl_label = "Rig Converter"
    bl_idname = "HYPERFY_PT_rig_converter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        
        # Main container box with neon effect
        main_box = layout.box()
        main_box.alert = True  # Gives red tint
        
        # Title with neon effect
        title_row = main_box.row(align=True)
        title_row.scale_y = 1.2
        title_row.alert = True
        title_row.label(text="⚡ RIG CONVERSION ⚡", icon='ARMATURE_DATA')
        
        # Button container with cyber effect
        button_box = main_box.box()
        button_box.scale_y = 1.0
        
        # Mixamo to VRM button with neon effect
        row = button_box.row(align=True)
        row.scale_y = 1.8
        row.alert = True  # Gives red tint
        op = row.operator("object.mixamo_to_vrm", text="MIXAMO → VRM", icon='OUTLINER_OB_ARMATURE')
        
        # Separator with cyber style
        sep = button_box.row()
        sep.scale_y = 0.5
        sep.alert = True
        
        # VRM to Mixamo button with neon effect
        row = button_box.row(align=True)
        row.scale_y = 1.8
        row.alert = True  # Gives red tint
        op = row.operator("object.vrm_to_mixamo", text="VRM → MIXAMO", icon='OUTLINER_OB_ARMATURE')
        
        # Info box with cyber style
        info_box = main_box.box()
        info_box.alert = True  # Matches theme
        info_col = info_box.column(align=True)
        info_col.scale_y = 0.8
        info_col.label(text="Select armature before converting", icon='INFO')
        info_col.label(text="Converts between naming conventions", icon='KEYTYPE_KEYFRAME_VEC')

class HYPERFY_PT_credits_panel(Panel):
    """Credits Panel"""
    bl_label = "Credits"
    bl_idname = "HYPERFY_PT_credits_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Main container with neon effect
        main_box = layout.box()
        main_box.alert = True
        
        # Developers section
        dev_title = main_box.row(align=True)
        dev_title.scale_y = 1.2
        dev_title.alignment = 'CENTER'
        dev_title.label(text="⚡ DEVELOPERS ⚡")
        
        # Howie's section
        dev_box = main_box.box()
        col = dev_box.column(align=True)
        col.scale_y = 0.9
        col.label(text="Howie Duhzit", icon='USER')
        
        # Links
        links = col.column(align=True)
        links.scale_y = 0.8
        links.operator("wm.url_open", text="GitHub", icon='FILE_SCRIPT').url = "https://github.com/HowieDuhzit"
        links.operator("wm.url_open", text="X", icon='X').url = "https://x.com/HowieDuhzit"
        links.operator("wm.url_open", text="Blender Extensions", icon='BLENDER').url = "https://extensions.blender.org/author/25892/"
        links.label(text="Discord: howieduhzit", icon='PLUGIN')
        
        # Engine title
        eng_title = main_box.row(align=True)
        eng_title.scale_y = 1.2
        eng_title.alignment = 'CENTER'
        eng_title.label(text="⚡ ENGINE ⚡")
        
        # Engine section
        eng_box = main_box.box()
        col = eng_box.column(align=True)
        col.scale_y = 0.9
        col.label(text="Hyperfy Engine", icon='WORLD')
        
        # Engine Links
        links = col.column(align=True)
        links.scale_y = 0.8
        links.operator("wm.url_open", text="Website", icon='WORLD').url = "https://hyperfy.xyz/"
        links.operator("wm.url_open", text="X", icon='X').url = "https://x.com/hyperfy_io"
        links.operator("wm.url_open", text="GitHub", icon='FILE_SCRIPT').url = "https://t.co/j3o72CL2I9"

class OBJECT_OT_mixamo_to_vrm(Operator):
    """Convert Mixamo rig to VRM rig"""
    bl_idname = "object.mixamo_to_vrm"
    bl_label = "Convert to VRM"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in context.active_object.data.edit_bones:
            if "Hips" in bone.name: bone.name = "hips"
            elif "Spine1" in bone.name: bone.name = "chest"
            elif "Spine2" in bone.name: bone.name = "upper_chest"
            elif "Neck" in bone.name: bone.name = "neck"
            elif "Head" in bone.name: bone.name = "head"
            elif "LeftEye" in bone.name: bone.name = "eye.L"
            elif "RightEye" in bone.name: bone.name = "eye.R"
            elif "LeftShoulder" in bone.name: bone.name = "shoulder.L"
            elif "LeftArm" in bone.name: bone.name = "upper_arm.L"
            elif "LeftForeArm" in bone.name: bone.name = "lower_arm.L"
            elif "LeftHandThumb1" in bone.name: bone.name = "thumb_proximal.L"
            elif "LeftHandThumb2" in bone.name: bone.name = "thumb_intermediate.L"
            elif "LeftHandThumb3" in bone.name: bone.name = "thumb_distal.L"
            elif "LeftHandIndex1" in bone.name: bone.name = "index_proximal.L"
            elif "LeftHandIndex2" in bone.name: bone.name = "index_intermediate.L"
            elif "LeftHandIndex3" in bone.name: bone.name = "index_distal.L"
            elif "LeftHandMiddle1" in bone.name: bone.name = "middle_proximal.L"
            elif "LeftHandMiddle2" in bone.name: bone.name = "middle_intermediate.L"
            elif "LeftHandMiddle3" in bone.name: bone.name = "middle_distal.L"
            elif "LeftHandRing1" in bone.name: bone.name = "ring_proximal.L"
            elif "LeftHandRing2" in bone.name: bone.name = "ring_intermediate.L"
            elif "LeftHandRing3" in bone.name: bone.name = "ring_distal.L"
            elif "LeftHandPinky1" in bone.name: bone.name = "little_proximal.L"
            elif "LeftHandPinky2" in bone.name: bone.name = "little_intermediate.L"
            elif "LeftHandPinky3" in bone.name: bone.name = "little_distal.L"
            elif "RightShoulder" in bone.name: bone.name = "shoulder.R"
            elif "RightArm" in bone.name: bone.name = "upper_arm.R"
            elif "RightForeArm" in bone.name: bone.name = "lower_arm.R"
            elif "RightHandThumb1" in bone.name: bone.name = "thumb_proximal.R"
            elif "RightHandThumb2" in bone.name: bone.name = "thumb_intermediate.R"
            elif "RightHandThumb3" in bone.name: bone.name = "thumb_distal.R"
            elif "RightHandIndex1" in bone.name: bone.name = "index_proximal.R"
            elif "RightHandIndex2" in bone.name: bone.name = "index_intermediate.R"
            elif "RightHandIndex3" in bone.name: bone.name = "index_distal.R"
            elif "RightHandMiddle1" in bone.name: bone.name = "middle_proximal.R"
            elif "RightHandMiddle2" in bone.name: bone.name = "middle_intermediate.R"
            elif "RightHandMiddle3" in bone.name: bone.name = "middle_distal.R"
            elif "RightHandRing1" in bone.name: bone.name = "ring_proximal.R"
            elif "RightHandRing2" in bone.name: bone.name = "ring_intermediate.R"
            elif "RightHandRing3" in bone.name: bone.name = "ring_distal.R"
            elif "RightHandPinky1" in bone.name: bone.name = "little_proximal.R"
            elif "RightHandPinky2" in bone.name: bone.name = "little_intermediate.R"
            elif "RightHandPinky3" in bone.name: bone.name = "little_distal.R"
            elif "LeftUpLeg" in bone.name: bone.name = "upper_leg.L"
            elif "LeftLeg" in bone.name: bone.name = "lower_leg.L"
            elif "LeftFoot" in bone.name: bone.name = "foot.L"
            elif "LeftToeBase" in bone.name: bone.name = "toes.L"
            elif "RightUpLeg" in bone.name: bone.name = "upper_leg.R"
            elif "RightLeg" in bone.name: bone.name = "lower_leg.R"
            elif "RightFoot" in bone.name: bone.name = "foot.R"
            elif "RightToeBase" in bone.name: bone.name = "toes.R"
            elif "LeftHand" in bone.name: bone.name = "hand.L"
            elif "RightHand" in bone.name: bone.name = "hand.R"
            elif "Spine" in bone.name: bone.name = "spine"
        
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.name = "VRM RIG"
        self.report({'INFO'}, "Successfully converted to VRM rig")
        return {'FINISHED'}

class OBJECT_OT_vrm_to_mixamo(Operator):
    """Convert VRM rig to Mixamo rig"""
    bl_idname = "object.vrm_to_mixamo"
    bl_label = "Convert to Mixamo"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in context.active_object.data.edit_bones:
            if "hips" in bone.name: bone.name = "mixamorig:Hips"
            elif "chest" in bone.name: bone.name = "mixamorig:Spine1"
            elif "upper_chest" in bone.name: bone.name = "mixamorig:Spine2"
            elif "neck" in bone.name: bone.name = "mixamorig:Neck"
            elif "head" in bone.name: bone.name = "mixamorig:Head"
            elif "eye.L" in bone.name: bone.name = "mixamorig:LeftEye"
            elif "eye.R" in bone.name: bone.name = "mixamorig:RightEye"
            elif "shoulder.L" in bone.name: bone.name = "mixamorig:LeftShoulder"
            elif "upper_arm.L" in bone.name: bone.name = "mixamorig:LeftArm"
            elif "lower_arm.L" in bone.name: bone.name = "mixamorig:LeftForeArm"
            elif "thumb_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandThumb1"
            elif "thumb_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandThumb2"
            elif "thumb_distal.L" in bone.name: bone.name = "mixamorig:LeftHandThumb3"
            elif "index_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandIndex1"
            elif "index_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandIndex2"
            elif "index_distal.L" in bone.name: bone.name = "mixamorig:LeftHandIndex3"
            elif "middle_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandMiddle1"
            elif "middle_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandMiddle2"
            elif "middle_distal.L" in bone.name: bone.name = "mixamorig:LeftHandMiddle3"
            elif "ring_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandRing1"
            elif "ring_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandRing2"
            elif "ring_distal.L" in bone.name: bone.name = "mixamorig:LeftHandRing3"
            elif "little_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandPinky1"
            elif "little_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandPinky2"
            elif "little_distal.L" in bone.name: bone.name = "mixamorig:LeftHandPinky3"
            elif "shoulder.R" in bone.name: bone.name = "mixamorig:RightShoulder"
            elif "upper_arm.R" in bone.name: bone.name = "mixamorig:RightArm"
            elif "lower_arm.R" in bone.name: bone.name = "mixamorig:RightForeArm"
            elif "thumb_proximal.R" in bone.name: bone.name = "mixamorig:RightHandThumb1"
            elif "thumb_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandThumb2"
            elif "thumb_distal.R" in bone.name: bone.name = "mixamorig:RightHandThumb3"
            elif "index_proximal.R" in bone.name: bone.name = "mixamorig:RightHandIndex1"
            elif "index_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandIndex2"
            elif "index_distal.R" in bone.name: bone.name = "mixamorig:RightHandIndex3"
            elif "middle_proximal.R" in bone.name: bone.name = "mixamorig:RightHandMiddle1"
            elif "middle_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandMiddle2"
            elif "middle_distal.R" in bone.name: bone.name = "mixamorig:RightHandMiddle3"
            elif "ring_proximal.R" in bone.name: bone.name = "mixamorig:RightHandRing1"
            elif "ring_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandRing2"
            elif "ring_distal.R" in bone.name: bone.name = "mixamorig:RightHandRing3"
            elif "little_proximal.R" in bone.name: bone.name = "mixamorig:RightHandPinky1"
            elif "little_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandPinky2"
            elif "little_distal.R" in bone.name: bone.name = "mixamorig:RightHandPinky3"
            elif "upper_leg.L" in bone.name: bone.name = "mixamorig:LeftUpLeg"
            elif "lower_leg.L" in bone.name: bone.name = "mixamorig:LeftLeg"
            elif "foot.L" in bone.name: bone.name = "mixamorig:LeftFoot"
            elif "toes.L" in bone.name: bone.name = "mixamorig:LeftToeBase"
            elif "upper_leg.R" in bone.name: bone.name = "mixamorig:RightUpLeg"
            elif "lower_leg.R" in bone.name: bone.name = "mixamorig:RightLeg"
            elif "foot.R" in bone.name: bone.name = "mixamorig:RightFoot"
            elif "toes.R" in bone.name: bone.name = "mixamorig:RightToeBase"
            elif "hand.L" in bone.name: bone.name = "mixamorig:LeftHand"
            elif "hand.R" in bone.name: bone.name = "mixamorig:RightHand"
            elif "spine" in bone.name: bone.name = "mixamorig:Spine"
        
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.name = "Mixamo RIG"
        self.report({'INFO'}, "Successfully converted to Mixamo rig")
        return {'FINISHED'}

classes = (
    HyperfyProperties,
    HYPERFY_PT_main_panel,
    OBJECT_OT_create_rigidbody,
    OBJECT_OT_create_multiple_rigidbodies,
    OBJECT_OT_export_glb,
    OBJECT_OT_export_all_glb,
    OBJECT_OT_set_rigidbody_type,
    OBJECT_OT_set_mesh_property,
    OBJECT_OT_set_collider_property,
    HYPERFY_PT_rig_converter_panel,
    OBJECT_OT_mixamo_to_vrm,
    OBJECT_OT_vrm_to_mixamo,
    HYPERFY_PT_credits_panel,
)

def register():
    # Register property group
    bpy.utils.register_class(HyperfyProperties)
    bpy.types.Scene.hyperfy_props = bpy.props.PointerProperty(type=HyperfyProperties)
    
    # Register other classes
    for cls in classes:
        if cls != HyperfyProperties:  # Already registered
            bpy.utils.register_class(cls)

def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove property group
    del bpy.types.Scene.hyperfy_props

if __name__ == "__main__":
    register() 