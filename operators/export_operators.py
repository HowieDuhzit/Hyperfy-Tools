import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
import os

class OBJECT_OT_export_glb(Operator, ExportHelper):
    """Export selected objects as GLB with custom properties"""
    bl_idname = "object.export_glb"
    bl_label = "Export GLB"
    filename_ext = ".glb"
    
    filter_glob: StringProperty(
        default="*.glb",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        # Export selected objects
        bpy.ops.export_scene.gltf(
            filepath=self.filepath,
            export_format='GLB',
            use_selection=True,
            export_extras=True  # Enables custom properties export
        )
        
        self.report({'INFO'}, f"Exported selected objects to: {self.filepath}")
        return {'FINISHED'}

class OBJECT_OT_export_all_glb(Operator, ExportHelper):
    """Export all visible top-level objects as separate GLB files"""
    bl_idname = "object.export_all_glb"
    bl_label = "Export All GLBs"
    filename_ext = ".glb"
    
    directory: StringProperty(
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