import bpy
from bpy.types import Panel

class HYPERFY_PT_credits_panel(Panel):
    """Credits Panel"""
    bl_label = "Credits"
    bl_idname = "HYPERFY_PT_credits_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 100  # High number ensures it stays at bottom
    
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