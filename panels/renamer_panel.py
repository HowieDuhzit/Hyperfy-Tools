import bpy

class HYPERFY_PT_renamer_panel(bpy.types.Panel):
    """Object Renamer Panel"""
    bl_label = "Renamer"
    bl_idname = "HYPERFY_PT_renamer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hyperfy'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Selected objects counter
        box = layout.box()
        row = box.row()
        row.label(text=f"Selected: {len(context.selected_objects)} objects")
        
        # Find and replace
        box = layout.box()
        row = box.row()
        row.prop(scene, "use_find_replace", text="Find & Replace")
        
        if scene.use_find_replace:
            row = box.row()
            row.prop(scene, "find_text", text="Find")
            row = box.row()
            row.prop(scene, "replace_text", text="Replace")
        
        # Prefix
        box = layout.box()
        row = box.row()
        row.prop(scene, "use_prefix", text="Prefix Operations")
        
        if scene.use_prefix:
            row = box.row()
            row.prop(scene, "prefix_operation", text="")
            row = box.row()
            row.prop(scene, "prefix_text", text="Prefix Text")
        
        # Suffix
        box = layout.box()
        row = box.row()
        row.prop(scene, "use_suffix", text="Suffix Operations")
        
        if scene.use_suffix:
            row = box.row()
            row.prop(scene, "suffix_operation", text="")
            row = box.row()
            row.prop(scene, "suffix_text", text="Suffix Text")
        
        # Case conversion
        box = layout.box()
        row = box.row()
        row.prop(scene, "use_case_conversion", text="Case Conversion")
        
        if scene.use_case_conversion:
            row = box.row()
            row.prop(scene, "case_conversion", text="")
        
        # Numbering
        box = layout.box()
        row = box.row()
        row.prop(scene, "use_numbering", text="Add Numbering")
        
        if scene.use_numbering:
            row = box.row()
            row.prop(scene, "numbering_position", expand=True)
            
            row = box.row(align=True)
            row.prop(scene, "numbering_base", text="Start")
            row.prop(scene, "numbering_increment", text="Step")
            
            row = box.row(align=True)
            row.prop(scene, "numbering_padding", text="Padding")
            row.prop(scene, "numbering_separator", text="Separator")
        
        # Execute buttons
        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("object.batch_rename")
        
        row = box.row()
        row.operator("object.clean_names") 