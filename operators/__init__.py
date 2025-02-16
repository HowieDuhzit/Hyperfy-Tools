from . import rigidbody_operators
from . import export_operators
from . import rig_operators
from . import snap_operators
from . import property_operators

__all__ = [
    'rigidbody_operators',
    'export_operators',
    'rig_operators',
    'snap_operators',
    'property_operators'
]

# List all operator classes explicitly
classes = (
    rigidbody_operators.OBJECT_OT_create_rigidbodies,
    export_operators.OBJECT_OT_export_glb,
    export_operators.OBJECT_OT_export_all_glb,
    rig_operators.OBJECT_OT_mixamo_to_vrm,
    rig_operators.OBJECT_OT_vrm_to_mixamo,
)

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError as e:
            print(f"Error registering {cls}: {e}")

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except ValueError as e:
            print(f"Error unregistering {cls}: {e}") 