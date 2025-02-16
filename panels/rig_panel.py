import bpy
from bpy.types import Panel

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
        main_box.alert = True
        
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
        row.alert = True
        row.operator("object.mixamo_to_vrm", text="MIXAMO → VRM", icon='OUTLINER_OB_ARMATURE')
        
        # Separator with cyber style
        sep = button_box.row()
        sep.scale_y = 0.5
        sep.alert = True
        
        # VRM to Mixamo button with neon effect
        row = button_box.row(align=True)
        row.scale_y = 1.8
        row.alert = True
        row.operator("object.vrm_to_mixamo", text="VRM → MIXAMO", icon='OUTLINER_OB_ARMATURE')
        
        # Info box with cyber style
        info_box = main_box.box()
        info_box.alert = True
        info_col = info_box.column(align=True)
        info_col.scale_y = 0.8
        info_col.label(text="Select armature before converting", icon='INFO')
        info_col.label(text="Converts between naming conventions", icon='KEYTYPE_KEYFRAME_VEC') 