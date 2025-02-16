from . import main_panel
from . import credits_panel
from . import export_panel

__all__ = ['main_panel', 'credits_panel', 'export_panel']

def register():
    for module in modules:
        for cls in module.__dict__.values():
            if hasattr(cls, 'bl_rna'):
                bpy.utils.register_class(cls)

def unregister():
    for module in reversed(modules):
        for cls in module.__dict__.values():
            if hasattr(cls, 'bl_rna'):
                bpy.utils.unregister_class(cls) 