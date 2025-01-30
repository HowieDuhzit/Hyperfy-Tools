bl_info = {
    "name": "Hyperfy Tools",
    "author": "Howie Duhzit",
    "version": (1, 2, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Hyperfy",
    "description": "Tools for creating Hyperfy assets with physics and colliders",
    "category": "3D View",
}

import bpy
from bpy.types import Panel, Operator, Menu
import os

# Import all classes from HyperfyTools
from .HyperfyTools import (
    HYPERFY_PT_main_panel,
    HYPERFY_OT_create_rigidbody,
    HYPERFY_OT_create_multiple_rigidbodies,
    HYPERFY_OT_export_glb,
    HYPERFY_OT_export_all_glb,
    HYPERFY_OT_set_rigidbody_type,
    HYPERFY_OT_set_mesh_property,
    HYPERFY_OT_set_collider_property,
)

# Define classes tuple after imports
classes = (
    HYPERFY_OT_create_rigidbody,
    HYPERFY_OT_create_multiple_rigidbodies,
    HYPERFY_OT_export_glb,
    HYPERFY_OT_export_all_glb,
    HYPERFY_OT_set_rigidbody_type,
    HYPERFY_OT_set_mesh_property,
    HYPERFY_OT_set_collider_property,
    HYPERFY_PT_main_panel,
)

# Register properties function
def register_properties():
    # Register properties
    bpy.types.Scene.hyperfy_physics_type = bpy.props.EnumProperty(
        name="Type",
        description="Physics type for the rigidbody",
        items=[
            ('static', "Static", "Non-moving collision object"),
            ('dynamic', "Dynamic", "Physics-driven object"),
            ('kinematic', "Kinematic", "Animated collision object")
        ],
        default='static'
    )
    bpy.types.Scene.hyperfy_mass = bpy.props.FloatProperty(
        name="Mass",
        description="Mass of the rigidbody",
        default=1.0,
        min=0.0,
        max=1000.0
    )
    
    # Mesh properties
    bpy.types.Scene.hyperfy_cast_shadow = bpy.props.BoolProperty(
        name="Cast Shadow",
        description="Whether the mesh should cast shadows",
        default=True
    )
    bpy.types.Scene.hyperfy_receive_shadow = bpy.props.BoolProperty(
        name="Receive Shadow",
        description="Whether the mesh should receive shadows",
        default=True
    )
    
    # Collider properties
    bpy.types.Scene.hyperfy_collider_type = bpy.props.EnumProperty(
        name="Collider Type",
        description="Type of collision shape",
        items=[
            ('box', "Box", "Box collision shape"),
            ('sphere', "Sphere", "Sphere collision shape"),
            ('geometry', "Geometry", "Use exact mesh geometry for collision (complex)"),
            ('simple', "Simple Collision", "Generate simplified collision from mesh")
        ],
        default='box'
    )
    bpy.types.Scene.hyperfy_convex = bpy.props.BoolProperty(
        name="Convex",
        description="Use convex collision shape",
        default=True
    )
    bpy.types.Scene.hyperfy_trigger = bpy.props.BoolProperty(
        name="Trigger",
        description="Make this a trigger volume",
        default=False
    )
    
    # Box collider size properties
    bpy.types.Scene.hyperfy_box_width = bpy.props.FloatProperty(
        name="Width",
        description="Width of box collider",
        default=1.0,
        min=0.01
    )
    bpy.types.Scene.hyperfy_box_height = bpy.props.FloatProperty(
        name="Height", 
        description="Height of box collider",
        default=1.0,
        min=0.01
    )
    bpy.types.Scene.hyperfy_box_depth = bpy.props.FloatProperty(
        name="Depth",
        description="Depth of box collider",
        default=1.0,
        min=0.01
    )
    
    # Sphere collider properties
    bpy.types.Scene.hyperfy_sphere_radius = bpy.props.FloatProperty(
        name="Radius",
        description="Radius of sphere collider",
        default=0.5,
        min=0.01
    )

def unregister_properties():
    props = [
        "hyperfy_physics_type",
        "hyperfy_mass",
        "hyperfy_cast_shadow",
        "hyperfy_receive_shadow",
        "hyperfy_collider_type",
        "hyperfy_convex",
        "hyperfy_trigger",
        "hyperfy_box_width",
        "hyperfy_box_height",
        "hyperfy_box_depth",
        "hyperfy_sphere_radius",
    ]
    
    for prop in props:
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)

def register():
    # Register properties first
    register_properties()
    
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister properties
    unregister_properties()

if __name__ == "__main__":
    register()
