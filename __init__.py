bl_info = {
    "name": "Hyperfy Tools",
    "author": "Howie Duhzit",
    "version": (1, 5, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Hyperfy",
    "description": "Tools for creating Hyperfy assets",
    "warning": "",
    "doc_url": "https://github.com/HowieDuhzit/HyperfyTools",
    "category": "3D View",
}

import bpy
from .operators import rigidbody_operators, export_operators, rig_operators, snap_operators, property_operators, hyp_operators, renamer_operators
from .panels import main_panel, credits_panel, export_panel, hyp_panel, renamer_panel
from .properties import hyperfy_properties

# Collect all classes to register
classes = (
    # Properties
    hyperfy_properties.HyperfyProperties,
    
    # Operators
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
    
    # Panels
    main_panel.HYPERFY_PT_main_panel,
    export_panel.HYPERFY_PT_export_panel,
    hyp_panel.HYPERFY_PT_hyp_panel,
    renamer_panel.HYPERFY_PT_renamer_panel,
    credits_panel.HYPERFY_PT_credits_panel,
)

def register():
    # Register renamer properties first
    renamer_operators.register_renamer_properties()
    
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError as e:
            print(f"Error registering {cls}: {e}")
    
    # Register properties
    bpy.types.Scene.hyperfy_props = bpy.props.PointerProperty(type=hyperfy_properties.HyperfyProperties)

def unregister():
    # Unregister properties
    del bpy.types.Scene.hyperfy_props
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except ValueError as e:
            print(f"Error unregistering {cls}: {e}")
    
    # Unregister renamer properties last
    renamer_operators.unregister_renamer_properties()

if __name__ == "__main__":
    register()
