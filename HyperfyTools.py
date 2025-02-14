import bpy
from bpy.types import Panel, Operator, Menu
import os

# Create a global variable for custom icons
custom_icons = None

def setup_collider(obj, context):
    """Setup common collider properties"""
    props = context.scene.hyperfy_props  # Get the property group
    
    # Always set name to "Collider"
    obj.name = "Collider"
    obj.display_type = 'WIRE'
    
    # Only clear materials if object is mesh
    if obj.type == 'MESH':
        obj.data.materials.clear()
    
    # Add only essential collider properties
    obj["node"] = "collider"
    obj["convex"] = props.convex  # Use props instead of scene
    obj["trigger"] = props.trigger  # Use props instead of scene
    
    # Reset transforms since it will be parented
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
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

def update_rigidbody_type(self, context):
    active_obj = context.active_object
    if active_obj and active_obj.get("node") == "rigidbody":
        active_obj["type"] = self.physics_type

def update_rigidbody_mass(self, context):
    active_obj = context.active_object
    if active_obj and active_obj.get("node") == "rigidbody":
        active_obj["mass"] = self.mass

# Create a PropertyGroup to collect all properties
class HyperfyProperties(bpy.types.PropertyGroup):
    physics_type: bpy.props.EnumProperty(
        items=[
            ('dynamic', 'Dynamic', 'Object is affected by physics'),
            ('static', 'Static', 'Object is immovable'),
            ('kinematic', 'Kinematic', 'Object is controlled by animation')
        ],
        default='dynamic',
        name="Physics Type",
        update=update_rigidbody_type  # Add update callback
    )
    mass: bpy.props.FloatProperty(
        name="Mass",
        default=1.0,
        min=0.0,
        update=update_rigidbody_mass  # Add update callback
    )
    convex: bpy.props.BoolProperty(
        name="Convex",
        default=False
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
        default='geometry',
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

def find_col_object(obj_name, objects):
    """Find a matching collision object (with COL suffix) for the given object name"""
    base_name = obj_name.lower().replace('lod', '').replace('.', '').rstrip('0123456789')
    
    for obj in objects:
        if obj.name.lower().endswith('col') and obj.name.lower().replace('col', '') == base_name:
            return obj
    return None

def process_rigidbody_hierarchy(context, obj, parent_empty=None, lod_variants=None):
    """Process object and its children recursively to create rigidbody setup with LODs"""
    props = context.scene.hyperfy_props
    processed_objects = []
    
    # Process current object if it's a mesh
    if obj.type == 'MESH':
        # Get base name without LOD/COL suffix
        base_name = obj.name.split('LOD')[0].replace('COL', '')
        orig_world_location = obj.matrix_world.to_translation()
        
        # Create empty parent (rigidbody) - use exact base name
        empty = bpy.data.objects.new(base_name, None)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.empty_display_size = 1
        empty.matrix_world.translation = orig_world_location
        context.scene.collection.objects.link(empty)
        
        # Parent to previous rigidbody if exists
        if parent_empty:
            empty.parent = parent_empty
            empty.matrix_world.translation = orig_world_location
        
        # Add rigidbody properties
        empty["node"] = "rigidbody"
        empty["mass"] = props.mass
        empty["type"] = props.physics_type
        
        # Create LOD empty with base name convention
        lod_empty = bpy.data.objects.new(f"{base_name}LOD", None)  # e.g., "CubeLOD"
        lod_empty.empty_display_type = 'PLAIN_AXES'
        lod_empty.empty_display_size = 0.75
        lod_empty["node"] = "lod"
        context.scene.collection.objects.link(lod_empty)
        lod_empty.parent = empty
        
        # Process LOD variants
        if lod_variants:
            # Remove COL objects from variants
            col_obj = find_col_object(base_name, lod_variants)
            if col_obj:
                lod_variants.remove(col_obj)
            
            # Sort variants by LOD number
            sorted_variants = sorted(lod_variants, 
                key=lambda x: int(''.join(filter(str.isdigit, x.name.split('LOD')[-1])) or '0'))
            
            # Create mesh for each LOD variant
            for i, variant in enumerate(sorted_variants):
                lod_mesh = variant.copy()
                lod_mesh.data = variant.data.copy()
                
                # Use exact naming convention: CubeMeshLOD0, CubeMeshLOD1, etc.
                lod_mesh.name = f"{base_name}MeshLOD{i}"
                
                context.scene.collection.objects.link(lod_mesh)
                
                # Reset transforms
                lod_mesh.location = (0, 0, 0)
                lod_mesh.rotation_euler = (0, 0, 0)
                lod_mesh.scale = (1, 1, 1)
                
                # Add mesh properties
                lod_mesh["castShadow"] = props.cast_shadow
                lod_mesh["receiveShadow"] = props.receive_shadow
                lod_mesh["node"] = "Mesh"
                # Adjust LOD distances for world size 200 and max camera distance 75
                if i == 0:
                    lod_mesh["maxDistance"] = 25  # LOD0 is closest, for high detail up close
                else:
                    lod_mesh["maxDistance"] = 25 + (i * 25)  # Each subsequent LOD increases distance
                
                # Parent to LOD empty
                lod_mesh.parent = lod_empty
                
                processed_objects.append(variant)
        
        # Handle collider
        col_obj = find_col_object(base_name, context.selected_objects)
        if col_obj:
            # Use the COL object directly as the collider
            setup_collider(col_obj, context)
            col_obj.name = f"{base_name}Collider"  # Match naming convention
            col_obj.parent = empty
        else:
            # Create and setup collider as before
            bpy.ops.object.select_all(action='DESELECT')
            
            # Get the highest LOD mesh to use as collider base
            collider_base = None
            if lod_variants:
                # Sort variants by LOD number (highest to lowest)
                sorted_variants = sorted(lod_variants, 
                    key=lambda x: int(''.join(filter(str.isdigit, x.name.split('LOD')[-1])) or '0'),
                    reverse=True)
                collider_base = sorted_variants[0]  # Use highest LOD number
            else:
                collider_base = obj
            
            if props.collider_type == 'box':
                collider = create_box_collider(context)
            elif props.collider_type == 'sphere':
                collider = create_sphere_collider(context)
            elif props.collider_type == 'simple':
                collider = create_simple_collider(collider_base, context)
            else:  # geometry
                collider = collider_base.copy()
                collider.data = collider_base.data.copy()
                context.scene.collection.objects.link(collider)
                setup_collider(collider, context)
            
            # Ensure collider is properly set up with consistent naming
            collider.name = f"{base_name}Collider"  # Use same naming convention as COL objects
            collider["node"] = "collider"
            collider.parent = empty  # Parent directly to rigidbody empty
        
        # Process all children recursively
        for child in obj.children:
            child_processed = process_rigidbody_hierarchy(context, child, empty)
            processed_objects.extend(child_processed)
    
    return processed_objects

def is_lod_variant(name1, name2):
    """Check if two names represent LOD variants of the same object"""
    # Remove common LOD suffixes
    base1 = name1.lower().replace('lod', '').replace('.', '').rstrip('0123456789')
    base2 = name2.lower().replace('lod', '').replace('.', '').rstrip('0123456789')
    return base1 == base2

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
            empty.location = location
            
            # Add to scene
            context.scene.collection.objects.link(empty)
            
            # Add custom property
            empty["node"] = "snap"
            
            created_empties.append(empty)
        
        # Find rigidbody parent if a rigidbody setup is selected
        rigidbody_parent = None
        if active_obj:
            if active_obj.get("node") == "rigidbody":
                rigidbody_parent = active_obj
            elif active_obj.get("node") in ["Mesh", "collider"] and active_obj.parent:
                if active_obj.parent.get("node") == "rigidbody":
                    rigidbody_parent = active_obj.parent
        
        # Parent all created empties to rigidbody if found
        if rigidbody_parent:
            for empty in created_empties:
                world_loc = empty.location.copy()  # Store world location
                empty.parent = rigidbody_parent
                # Convert world location to local space relative to parent
                empty.location = rigidbody_parent.matrix_world.inverted() @ world_loc
        
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

def get_physics_types(self, context):
    return [
        ('dynamic', 'Dynamic', 'Object is affected by physics'),
        ('static', 'Static', 'Object is immovable'),
        ('kinematic', 'Kinematic', 'Object is controlled by animation')
    ]

class OBJECT_OT_update_rigidbody_property(Operator):
    """Update rigidbody properties"""
    bl_idname = "object.update_rigidbody_property"
    bl_label = "Update Rigidbody Property"
    bl_options = {'INTERNAL'}
    
    property_name: bpy.props.StringProperty()
    property_value: bpy.props.StringProperty()
    
    def execute(self, context):
        active_obj = context.active_object
        if active_obj and active_obj.get("node") == "rigidbody":
            active_obj[self.property_name] = self.property_value
        return {'FINISHED'}

def get_rigidbody_parent(obj):
    """Get the rigidbody parent of an object in the hierarchy"""
    current = obj
    while current:
        if current.get("node") == "rigidbody":
            return current
        current = current.parent
    return None

class HYPERFY_PT_main_panel(Panel):
    """Main Panel for Hyperfy Tools"""
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
        
        # Get rigidbody object (either selected or parent)
        rigidbody_obj = None
        if active_obj:
            if active_obj.get("node") == "rigidbody":
                rigidbody_obj = active_obj
            else:
                rigidbody_obj = get_rigidbody_parent(active_obj)
        
        # Draw rigidbody details if found
        if rigidbody_obj:
            rb_box = layout.box()
            rb_box.alert = True
            rb_box.label(text="▸ RIGIDBODY DETAILS", icon='OBJECT_DATA')
            
            # Physics type
            col = rb_box.column(align=True)
            row = col.row(align=True)
            row.prop(rigidbody_obj, '["type"]', text="Type")
            
            # Mass (only show for dynamic objects)
            if rigidbody_obj["type"] == "dynamic":
                row = col.row(align=True)
                row.prop(rigidbody_obj, '["mass"]', text="Mass")
            
            # Find collider in children
            collider_obj = None
            for child in rigidbody_obj.children:
                if child.get("node") == "collider":
                    collider_obj = child
                    break
            
            # Show collider properties if found
            if collider_obj:
                col_box = rb_box.box()
                col_box.label(text="Collider Properties:", icon='MESH_CUBE')
                col = col_box.column(align=True)
                row = col.row(align=True)
                row.prop(collider_obj, '["convex"]', text="Convex")
                row.prop(collider_obj, '["trigger"]', text="Trigger")
            
            # Find LOD empty and meshes
            lod_empty = None
            lod_meshes = []
            for child in rigidbody_obj.children:
                if child.get("node") == "lod":
                    lod_empty = child
                    # Get LOD meshes sorted by name
                    lod_meshes = sorted([mesh for mesh in child.children if mesh.get("node") == "Mesh"],
                                      key=lambda x: x.name)
                    break
            
            # Show LOD properties if found
            if lod_meshes:
                lod_box = rb_box.box()
                lod_box.label(text="LOD Distances:", icon='MESH_DATA')
                col = lod_box.column(align=True)
                
                for mesh in lod_meshes:
                    row = col.row(align=True)
                    row.label(text=mesh.name)
                    row.prop(mesh, '["maxDistance"]', text="Distance")
            
            rb_box.separator()
        
        # Show creation controls if no rigidbody is selected
        if not rigidbody_obj:
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
            
            # Create button with gradient effect
            main_box.separator()
            
            # Rigidbody creation
            create_row = main_box.row(align=True)
            create_row.scale_y = 1.8
            create_row.operator("object.create_rigidbodies", text="⚡ CREATE RIGIDBODIES ⚡", icon='ADD')
        
        # Snap Points section (moved above export)
        snap_box = layout.box()
        snap_box.alert = True
        snap_box.label(text="⚡ SNAP POINTS ⚡", icon='EMPTY_ARROWS')
        
        # Add snap point button
        row = snap_box.row(align=True)
        row.scale_y = 1.4
        row.operator("object.add_snap_point", text="ADD SNAP POINT", icon='ADD')
        
        # Info text
        info = snap_box.box()
        col = info.column(align=True)
        col.scale_y = 0.8
        col.label(text="All snap points snap to each other", icon='INFO')
            
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
        links.operator("wm.url_open", text="Blender Extensions", icon='BLENDER').url = "https://extensions.blender.org/author/25892/"
        links.operator("wm.url_open", text="GitHub", icon='FILE_SCRIPT').url = "https://github.com/HowieDuhzit"
        links.operator("wm.url_open", text="X", icon='X').url = "https://x.com/HowieDuhzit"
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
        links.operator("wm.url_open", text="GitHub", icon='FILE_SCRIPT').url = "https://t.co/j3o72CL2I9"
        links.operator("wm.url_open", text="Website", icon='WORLD').url = "https://hyperfy.xyz/"
        links.operator("wm.url_open", text="X", icon='X').url = "https://x.com/hyperfy_io"
        

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
    OBJECT_OT_create_rigidbodies,
    OBJECT_OT_export_glb,
    OBJECT_OT_export_all_glb,
    OBJECT_OT_set_rigidbody_type,
    OBJECT_OT_set_mesh_property,
    OBJECT_OT_set_collider_property,
    OBJECT_OT_update_rigidbody_property,
    HYPERFY_PT_rig_converter_panel,
    OBJECT_OT_mixamo_to_vrm,
    OBJECT_OT_vrm_to_mixamo,
    HYPERFY_PT_credits_panel,
    OBJECT_OT_add_snap_point,
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