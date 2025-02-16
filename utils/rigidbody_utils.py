import bpy
from .collider_utils import (
    create_box_collider,
    create_sphere_collider,
    create_simple_collider,
    setup_collider
)
from .lod_utils import find_col_object

def get_rigidbody_parent(obj):
    """Get the rigidbody parent of an object in the hierarchy"""
    current = obj
    while current:
        if current.get("node") == "rigidbody":
            return current
        current = current.parent
    return None

def process_rigidbody_hierarchy(context, main_obj, lod_variants=None):
    """Process an object and its variants into a rigidbody hierarchy"""
    props = context.scene.hyperfy_props
    processed_objects = []
    
    # If main_obj is a COL object, find a non-COL object to use as main
    if main_obj.name.lower().endswith('col'):
        base_name = main_obj.name.lower().replace('col', '').strip()
        for obj in context.selected_objects:
            if not obj.name.lower().endswith('col') and obj.name.lower().startswith(base_name):
                main_obj = obj
                break
    
    # Create empty parent
    empty = bpy.data.objects.new(f"{main_obj.name.split('LOD')[0].replace('COL', '')}", None)
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 1
    context.scene.collection.objects.link(empty)
    
    # Add rigidbody properties
    empty["node"] = "rigidbody"
    empty["mass"] = props.mass
    empty["type"] = props.physics_type
    
    # Create LOD empty
    lod_empty = bpy.data.objects.new("LOD", None)
    lod_empty.empty_display_type = 'PLAIN_AXES'
    lod_empty.empty_display_size = 0.75
    lod_empty["node"] = "lod"
    context.scene.collection.objects.link(lod_empty)
    lod_empty.parent = empty
    
    # Process LOD variants
    if lod_variants:
        # Sort variants by LOD number or name if no LOD number
        def get_lod_number(obj):
            if 'LOD' in obj.name:
                try:
                    return int(obj.name.split('LOD')[-1])
                except ValueError:
                    return float('inf')
            return float('inf')
        
        sorted_variants = sorted([v for v in lod_variants if not v.name.lower().endswith('col')], 
                               key=get_lod_number)
        
        for i, variant in enumerate(sorted_variants):
            # Create LOD mesh
            lod_mesh = variant.copy()
            lod_mesh.data = variant.data.copy()
            lod_mesh.name = f"{empty.name}MeshLOD{i}"  # Will start at LOD0
            context.scene.collection.objects.link(lod_mesh)
            
            # Reset transforms
            lod_mesh.location = (0, 0, 0)
            lod_mesh.rotation_euler = (0, 0, 0)
            lod_mesh.scale = (1, 1, 1)
            
            # Add mesh properties
            lod_mesh["castShadow"] = props.cast_shadow
            lod_mesh["receiveShadow"] = props.receive_shadow
            lod_mesh["node"] = "Mesh"
            
            # Set LOD distance
            if i == 0:
                lod_mesh["maxDistance"] = 25  # LOD0 is closest
            else:
                lod_mesh["maxDistance"] = 25 + (i * 25)  # Increase with each LOD
            
            # Parent to LOD empty
            lod_mesh.parent = lod_empty
            processed_objects.append(variant)
    
    # Create collider
    collider = None
    col_obj = next((obj for obj in lod_variants if obj.name.lower().endswith('col')), None) if lod_variants else None
    
    if col_obj:
        # Use existing COL object
        collider = col_obj.copy()
        collider.data = col_obj.data.copy()
        context.scene.collection.objects.link(collider)
        setup_collider(collider, context)
        processed_objects.append(col_obj)
    else:
        # Create new collider based on type
        if props.collider_type == 'box':
            collider = create_box_collider(context)
        elif props.collider_type == 'sphere':
            collider = create_sphere_collider(context)
        elif props.collider_type == 'simple':
            collider = create_simple_collider(main_obj, context)
        else:  # geometry
            collider = main_obj.copy()
            collider.data = main_obj.data.copy()
            context.scene.collection.objects.link(collider)
            setup_collider(collider, context)
    
    # Parent collider
    if collider:
        collider.parent = empty
    
    return processed_objects

__all__ = ['get_rigidbody_parent', 'process_rigidbody_hierarchy'] 