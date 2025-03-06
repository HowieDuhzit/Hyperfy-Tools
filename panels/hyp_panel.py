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

class HYPERFY_PT_hyp_panel(Panel):
    """HYP File Panel for Hyperfy Tools"""
    bl_label = "HYP Files"
    bl_idname = "HYPERFY_PT_hyp"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.hyperfy_props
        
        # Import button at the top
        box = layout.box()
        box.alert = True
        box.label(text="⚡ HYP FILE ⚡", icon='FILE_BLEND')
        
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("object.import_hyp", text="IMPORT HYP", icon='IMPORT')
        
        # Metadata section
        meta_box = layout.box()
        meta_box.label(text="Metadata", icon='FILE_TEXT')
        
        # Use grid layout for metadata
        meta_grid = meta_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        # Left column - Labels
        col1 = meta_grid.column()
        col1.label(text="ID:")
        col1.label(text="Version:")
        col1.label(text="Name:")
        if props.hyp_author:
            col1.label(text="Author:")
        if props.hyp_created:
            col1.label(text="Created:")
        if props.hyp_modified:
            col1.label(text="Modified:")
        
        # Right column - Values
        col2 = meta_grid.column()
        col2.label(text=props.hyp_id if props.hyp_id else "Not Set")
        col2.label(text=str(props.hyp_version) if props.hyp_version else "Not Set")
        col2.label(text=props.hyp_name if props.hyp_name else "Not Set")
        if props.hyp_author:
            col2.label(text=props.hyp_author)
        if props.hyp_created:
            col2.label(text=props.hyp_created)
        if props.hyp_modified:
            col2.label(text=props.hyp_modified)
        
        # Script section
        script_box = layout.box()
        script_box.label(text="Script", icon='TEXT')
        
        # Script display
        script_col = script_box.column(align=True)
        if props.hyp_script:
            script_col.label(text=props.hyp_script)
        else:
            script_col.label(text="No Script", icon='INFO')
        
        # Properties section
        prop_box = layout.box()
        prop_box.label(text="Properties", icon='PROPERTIES')
        
        # Use grid layout for properties
        grid = prop_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        # Left column - Labels
        col1 = grid.column()
        col1.label(text="Frozen:")
        col1.label(text="Collision:")
        col1.label(text="Interactable:")
        col1.label(text="Visible:")
        
        # Right column - Values
        col2 = grid.column()
        col2.label(text="Yes" if props.hyp_frozen else "No")
        col2.label(text="Yes" if props.hyp_collision else "No")
        col2.label(text="Yes" if props.hyp_interact else "No")
        col2.label(text="Yes" if props.hyp_visible else "No")
        
        # Click distance (only show if interactable)
        if props.hyp_interact:
            click_box = prop_box.box()
            click_box.label(text="Click Distance:", icon='MOD_PHYSICS')
            click_box.label(text=str(props.hyp_click_distance))
        
        # Info box at bottom
        info = layout.box()
        info.scale_y = 0.8
        col = info.column(align=True)
        col.label(text="Hyperfy .hyp File Format", icon='INFO')
        col.label(text="Import Hyperfy world objects", icon='BLANK1')
        col.label(text="Includes model, script, and properties", icon='BLANK1') 