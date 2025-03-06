from . import rigidbody_operators
from . import export_operators
from . import rig_operators
from . import snap_operators
from . import property_operators
from . import hyp_operators
from . import renamer_operators

__all__ = [
    'rigidbody_operators',
    'export_operators',
    'rig_operators',
    'snap_operators',
    'property_operators',
    'hyp_operators',
    'renamer_operators'
]

# List all operator classes explicitly
classes = (
    rigidbody_operators.OBJECT_OT_create_rigidbodies,
    export_operators.OBJECT_OT_export_glb,
    export_operators.OBJECT_OT_export_all_glb,
    rig_operators.OBJECT_OT_mixamo_to_vrm,
    rig_operators.OBJECT_OT_vrm_to_mixamo,
    rig_operators.OBJECT_OT_detect_and_convert_rig,
    snap_operators.OBJECT_OT_add_snap_point,
    property_operators.OBJECT_OT_set_rigidbody_type,
    property_operators.OBJECT_OT_set_mesh_property,
    property_operators.OBJECT_OT_set_collider_property,
    property_operators.OBJECT_OT_update_rigidbody_property,
    hyp_operators.OBJECT_OT_import_hyp,
    renamer_operators.OBJECT_OT_batch_rename,
    renamer_operators.OBJECT_OT_clean_names,
)

def register():
    # Register renamer properties first
    renamer_operators.register_renamer_properties()
    
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
    
    # Unregister renamer properties last
    renamer_operators.unregister_renamer_properties() 