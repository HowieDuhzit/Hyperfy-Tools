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

class HYPERFY_PT_export_panel(Panel):
    """Export Panel for GLB files"""
    bl_label = "Export"
    bl_idname = "HYPERFY_PT_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'
    
    @classmethod
    def poll(cls, context):
        # Only show when a rigidbody or its child is selected
        active_obj = context.active_object
        if active_obj:
            if active_obj.get("node") == "rigidbody":
                return True
            return get_rigidbody_parent(active_obj) is not None
        return False
    
    def draw(self, context):
        layout = self.layout
        
        # Export section
        export_box = layout.box()
        export_box.alert = True
        export_box.label(text="⚡ GLB EXPORT ⚡", icon='EXPORT')
        
        # Export buttons
        col = export_box.column(align=True)
        
        # Single object export
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("object.export_glb", text="EXPORT", icon='EXPORT')
        
        # Batch export
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("object.export_all_glb", text="BATCH EXPORT", icon='FILE_REFRESH')
        
        # Info box
        info = export_box.box()
        col = info.column(align=True)
        col.scale_y = 0.8
        col.label(text="Export selected or all visible objects", icon='INFO')
        col.label(text="Preserves hierarchy and properties", icon='BLANK1') 