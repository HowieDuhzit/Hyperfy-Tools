import bpy

def find_col_object(obj_name, objects):
    """Find a matching collision object (with COL suffix) for the given object name"""
    base_name = obj_name.lower().replace('lod', '').replace('.', '').rstrip('0123456789')
    
    for obj in objects:
        if obj.name.lower().endswith('col') and obj.name.lower().replace('col', '') == base_name:
            return obj
    return None

def is_lod_variant(name1, name2):
    """Check if two names represent LOD variants of the same object"""
    # Remove common LOD suffixes
    base1 = name1.lower().replace('lod', '').replace('.', '').rstrip('0123456789')
    base2 = name2.lower().replace('lod', '').replace('.', '').rstrip('0123456789')
    return base1 == base2

def get_lod_groups(objects):
    """Group objects by their base names (for LOD processing)"""
    lod_groups = {}
    
    for obj in objects:
        base_name = obj.name.lower()
        # Strip LOD and COL suffixes to get base name
        if 'lod' in base_name:
            base_name = base_name.split('lod')[0]
        elif 'col' in base_name:
            base_name = base_name.replace('col', '')
        base_name = base_name.strip()
        
        # Find existing group or create new one
        found_group = None
        for key in lod_groups.keys():
            key_base = key.name.lower()
            if 'lod' in key_base:
                key_base = key_base.split('lod')[0]
            elif 'col' in key_base:
                key_base = key_base.replace('col', '')
            key_base = key_base.strip()
            
            if key_base == base_name:
                found_group = key
                break
        
        if found_group:
            lod_groups[found_group].append(obj)
        else:
            # For new groups, prefer non-COL object as key
            if not obj.name.lower().endswith('col'):
                lod_groups[obj] = [obj]
            else:
                # If only COL object found so far, use it as key
                lod_groups[obj] = [obj]
    
    return lod_groups

def get_lod_variants(obj, objects):
    """Get all LOD variants for a given object"""
    variants = []
    base_name = obj.name.split('LOD')[0].replace('COL', '')
    
    for other in objects:
        if other != obj:
            other_base = other.name.split('LOD')[0].replace('COL', '')
            if other_base == base_name:
                variants.append(other)
    
    return variants

def setup_lod_empty(context, parent_empty, base_name):
    """Create and setup a LOD empty object"""
    lod_empty = bpy.data.objects.new(f"{base_name}LOD", None)
    lod_empty.empty_display_type = 'PLAIN_AXES'
    lod_empty.empty_display_size = 0.75
    lod_empty["node"] = "lod"
    context.scene.collection.objects.link(lod_empty)
    lod_empty.parent = parent_empty
    return lod_empty

def setup_lod_mesh(context, mesh_obj, lod_empty, base_name, index, props):
    """Setup a LOD mesh object with proper properties"""
    lod_mesh = mesh_obj.copy()
    lod_mesh.data = mesh_obj.data.copy()
    lod_mesh.name = f"{base_name}MeshLOD{index}"
    context.scene.collection.objects.link(lod_mesh)
    
    # Reset transforms
    lod_mesh.location = (0, 0, 0)
    lod_mesh.rotation_euler = (0, 0, 0)
    lod_mesh.scale = (1, 1, 1)
    
    # Add mesh properties
    lod_mesh["castShadow"] = props.cast_shadow
    lod_mesh["receiveShadow"] = props.receive_shadow
    lod_mesh["node"] = "Mesh"
    
    # Adjust LOD distances for world size 200 and max camera distance 75
    if index == 0:
        lod_mesh["maxDistance"] = 25  # LOD0 is closest, for high detail up close
    else:
        lod_mesh["maxDistance"] = 25 + (index * 25)  # Each subsequent LOD increases distance
    
    # Parent to LOD empty
    lod_mesh.parent = lod_empty
    return lod_mesh 