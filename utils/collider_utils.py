import bpy

def setup_collider(obj, context):
    """Setup common collider properties"""
    props = context.scene.hyperfy_props
    
    # Always set name to "Collider"
    obj.name = "Collider"
    obj.display_type = 'WIRE'
    
    # Only clear materials if object is mesh
    if obj.type == 'MESH':
        obj.data.materials.clear()
    
    # Add only essential collider properties
    obj["node"] = "collider"
    obj["convex"] = props.convex
    obj["trigger"] = props.trigger
    
    # Reset transforms since it will be parented
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def is_collider(obj):
    """Check if object is already a collider"""
    return obj.get("node") == "collider" and obj.display_type == 'WIRE'

def create_box_collider(context):
    """Create a box collider"""
    props = context.scene.hyperfy_props
    
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
    collider = context.active_object
    setup_collider(collider, context)
    
    # Set box size using props
    collider.scale.x = props.box_width
    collider.scale.y = props.box_height
    collider.scale.z = props.box_depth
    
    return collider

def create_sphere_collider(context):
    """Create a sphere collider"""
    props = context.scene.hyperfy_props
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=props.sphere_radius,
        segments=32,
        ring_count=16,
        location=(0, 0, 0)
    )
    collider = context.active_object
    setup_collider(collider, context)
    return collider

def create_simple_collider(obj, context):
    """Create a simplified collision mesh"""
    collider = obj.copy()
    collider.data = obj.data.copy()
    context.scene.collection.objects.link(collider)
    collider.location = (0, 0, 0)
    setup_collider(collider, context)
    
    # First use voxel remesh to create a solid mesh
    remesh = collider.modifiers.new(name="Remesh", type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = max(collider.dimensions) / 4
    
    # Apply remesh
    context.view_layer.objects.active = collider
    bpy.ops.object.modifier_apply(modifier="Remesh")
    
    # Add decimate modifier
    decimate = collider.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.decimate_type = 'DISSOLVE'
    decimate.angle_limit = 0.5
    
    # Apply decimate
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    # Clean up mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.05)
    bpy.ops.mesh.dissolve_degenerate()
    bpy.ops.mesh.delete_loose()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return collider 