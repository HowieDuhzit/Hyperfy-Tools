from . import hyperfy_properties

__all__ = ['hyperfy_properties']

def register():
    bpy.utils.register_class(hyperfy_properties.HyperfyProperties)
    bpy.types.Scene.hyperfy_props = bpy.props.PointerProperty(type=hyperfy_properties.HyperfyProperties)

def unregister():
    del bpy.types.Scene.hyperfy_props
    bpy.utils.unregister_class(hyperfy_properties.HyperfyProperties) 