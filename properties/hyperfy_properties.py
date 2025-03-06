import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty, 
    FloatProperty, 
    BoolProperty, 
    CollectionProperty, 
    IntProperty,
    StringProperty,
    FloatVectorProperty
)

def update_rigidbody_type(self, context):
    active_obj = context.active_object
    if active_obj:
        # If we're looking at a rigidbody object directly
        if active_obj.get("node") == "rigidbody":
            active_obj["type"] = self.physics_type
        else:
            # Check if we're looking at a child of a rigidbody
            current = active_obj
            while current:
                if current.get("node") == "rigidbody":
                    current["type"] = self.physics_type
                    break
                current = current.parent

def update_rigidbody_mass(self, context):
    active_obj = context.active_object
    if active_obj and active_obj.get("node") == "rigidbody":
        active_obj["mass"] = self.mass

class HyperfyProperties(PropertyGroup):
    physics_type: EnumProperty(
        items=[
            ('dynamic', 'Dynamic', 'Object is affected by physics'),
            ('static', 'Static', 'Object is immovable'),
            ('kinematic', 'Kinematic', 'Object is controlled by animation')
        ],
        default='dynamic',
        name="Physics Type",
        update=update_rigidbody_type
    )
    
    mass: FloatProperty(
        name="Mass",
        default=1.0,
        min=0.0,
        update=update_rigidbody_mass
    )
    
    convex: BoolProperty(
        name="Convex",
        default=False
    )
    
    trigger: BoolProperty(
        name="Trigger",
        default=False
    )
    
    cast_shadow: BoolProperty(
        name="Cast Shadow",
        default=True
    )
    
    receive_shadow: BoolProperty(
        name="Receive Shadow",
        default=True
    )
    
    collider_type: EnumProperty(
        items=[
            ('box', 'Box', 'Box collider'),
            ('sphere', 'Sphere', 'Sphere collider'),
            ('simple', 'Simple', 'Simplified mesh collider'),
            ('geometry', 'Geometry', 'Full geometry collider')
        ],
        default='geometry',
        name="Collider Type"
    )
    
    box_width: FloatProperty(
        name="Width",
        default=1.0,
        min=0.0
    )
    
    box_height: FloatProperty(
        name="Height",
        default=1.0,
        min=0.0
    )
    
    box_depth: FloatProperty(
        name="Depth",
        default=1.0,
        min=0.0
    )
    
    sphere_radius: FloatProperty(
        name="Radius",
        default=1.0,
        min=0.0
    )
    
    # Hyperfy .hyp file properties
    hyp_name: StringProperty(
        name="Name",
        description="Name of the Hyperfy object",
        default=""
    )
    
    hyp_frozen: BoolProperty(
        name="Frozen",
        description="If true, object cannot be moved/rotated in-game",
        default=False
    )
    
    hyp_script: StringProperty(
        name="Script",
        description="JavaScript file to use",
        default="",
        subtype='NONE'
    )
    
    hyp_interact: BoolProperty(
        name="Interactable",
        description="If true, object can be interacted with",
        default=False
    )
    
    hyp_click_distance: FloatProperty(
        name="Click Distance",
        description="Maximum distance for interaction",
        default=10.0,
        min=0.0
    )
    
    hyp_collision: BoolProperty(
        name="Collision",
        description="If true, object has collision",
        default=True
    )
    
    hyp_visible: BoolProperty(
        name="Visible",
        description="If true, object is visible",
        default=True
    )
    
    # Metadata properties
    hyp_id: StringProperty(
        name="ID",
        description="Unique identifier of the object",
        default=""
    )
    
    hyp_version: IntProperty(
        name="Version",
        description="Version number of the object",
        default=0
    )
    
    hyp_author: StringProperty(
        name="Author",
        description="Creator of the object",
        default=""
    )
    
    hyp_created: StringProperty(
        name="Created",
        description="Creation date",
        default=""
    )
    
    hyp_modified: StringProperty(
        name="Modified",
        description="Last modified date",
        default=""
    ) 