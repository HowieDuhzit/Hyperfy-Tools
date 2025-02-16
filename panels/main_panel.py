import bpy
from bpy.types import Panel

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

    def draw(self, context):
        layout = self.layout
        active_obj = context.active_object
        props = context.scene.hyperfy_props
        
        # Show rig converter if armature is selected
        if active_obj and active_obj.type == 'ARMATURE':
            # Rig Converter section
            rig_box = layout.box()
            rig_box.alert = True
            rig_box.label(text="⚡ RIG CONVERTER ⚡", icon='ARMATURE_DATA')
            
            # Single smart conversion button
            col = rig_box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.5
            
            # Detect rig type and show appropriate conversion
            is_mixamo = False
            is_vrm = False
            
            if active_obj and active_obj.type == 'ARMATURE':
                for bone in active_obj.data.bones:
                    if "mixamo" in bone.name.lower():
                        is_mixamo = True
                        break
                    elif any(key in bone.name.lower() for key in ["hips", "spine", "chest", "neck", "head"]):
                        is_vrm = True
                        break
            
            if is_mixamo:
                row.operator("object.mixamo_to_vrm", text="Convert to VRM", icon='POSE_HLT')
            elif is_vrm:
                row.operator("object.vrm_to_mixamo", text="Convert to Mixamo", icon='POSE_HLT')
            else:
                row.operator("object.detect_and_convert_rig", text="Convert Rig", icon='POSE_HLT')
            
            # Info box
            info = rig_box.box()
            col = info.column(align=True)
            col.scale_y = 0.8
            col.label(text="Automatically detects and converts rig type", icon='INFO')
            col.label(text="Select an armature and click to convert", icon='BLANK1')
            return
        
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
            
            # Physics type - Use dropdown like creation menu
            col = rb_box.column(align=True)
            row = col.row(align=True)
            
            # Get current type
            current_type = rigidbody_obj.get("type", "dynamic")
            
            # Show dropdown using the same enum as creation menu
            row.prop(props, "physics_type", text="Type")
            
            # Mass (only show for dynamic objects)
            if current_type == "dynamic":
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
            
            # Snap Points section
            snap_box = rb_box.box()
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
            
            rb_box.separator()
        
        # Show creation controls if no rigidbody is selected
        if not rigidbody_obj:
            # Physics section
            main_box = layout.box()
            main_box.alert = True
            main_box.label(text="⚡ RIGIDBODY CREATION ⚡", icon='PHYSICS')
            
            # Physics type
            col = main_box.column(align=True)
            col.prop(props, "physics_type", text="Type")
            
            # Mass (only show for dynamic objects)
            if props.physics_type == 'dynamic':
                col.prop(props, "mass", text="Mass")
            
            # Collider settings
            col_box = main_box.box()
            col_box.label(text="Collider Settings:", icon='MESH_CUBE')
            col = col_box.column(align=True)
            
            # Collider type
            col.prop(props, "collider_type", text="Type")
            
            # Box dimensions
            if props.collider_type == 'box':
                box_col = col.column(align=True)
                box_col.prop(props, "box_width", text="Width")
                box_col.prop(props, "box_height", text="Height")
                box_col.prop(props, "box_depth", text="Depth")
            
            # Sphere radius
            elif props.collider_type == 'sphere':
                col.prop(props, "sphere_radius", text="Radius")
            
            # Collider properties
            prop_col = col.column(align=True)
            row = prop_col.row(align=True)
            row.prop(props, "convex", text="Convex")
            row.prop(props, "trigger", text="Trigger")
            
            # Mesh properties
            mesh_box = main_box.box()
            mesh_box.label(text="Mesh Settings:", icon='MESH_DATA')
            col = mesh_box.column(align=True)
            row = col.row(align=True)
            row.prop(props, "cast_shadow", text="Cast Shadow")
            row.prop(props, "receive_shadow", text="Receive Shadow")
            
            # Create button
            create_row = main_box.row(align=True)
            create_row.scale_y = 1.5
            create_row.operator("object.create_rigidbodies", text="CREATE RIGIDBODY", icon='PHYSICS') 