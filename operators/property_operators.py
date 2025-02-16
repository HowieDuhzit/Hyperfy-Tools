import bpy
from bpy.types import Operator

class OBJECT_OT_set_rigidbody_type(Operator):
    """Set type for multiple rigidbodies"""
    bl_idname = "object.set_rigidbody_type"
    bl_label = "Set Rigidbody Type"
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj["type"] = self.type
        return {'FINISHED'}

class OBJECT_OT_set_mesh_property(Operator):
    """Set property for multiple mesh objects"""
    bl_idname = "object.set_mesh_property"
    bl_label = "Set Mesh Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                # Toggle the property
                obj[self.property_name] = not obj.get(self.property_name, True)
        return {'FINISHED'}

class OBJECT_OT_set_collider_property(Operator):
    """Set property for multiple collider objects"""
    bl_idname = "object.set_collider_property"
    bl_label = "Set Collider Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    property_name: bpy.props.StringProperty()
    target_objects: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.hyperfy_props
        objects = self.target_objects.split(',')
        for obj_name in objects:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                # Toggle the property
                obj[self.property_name] = not obj.get(self.property_name, True)
        return {'FINISHED'}

class OBJECT_OT_update_rigidbody_property(Operator):
    """Update rigidbody properties"""
    bl_idname = "object.update_rigidbody_property"
    bl_label = "Update Rigidbody Property"
    bl_options = {'INTERNAL'}
    
    property_name: bpy.props.StringProperty()
    property_value: bpy.props.StringProperty()
    
    def execute(self, context):
        active_obj = context.active_object
        if active_obj and active_obj.get("node") == "rigidbody":
            # Update the property
            active_obj[self.property_name] = self.property_value
            
            # If changing type, update mass visibility
            if self.property_name == "type":
                context.scene.hyperfy_props.physics_type = self.property_value
                
        return {'FINISHED'} 