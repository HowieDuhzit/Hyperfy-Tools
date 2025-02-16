import bpy
from bpy.types import Operator

class OBJECT_OT_mixamo_to_vrm(Operator):
    """Convert Mixamo rig to VRM rig"""
    bl_idname = "object.mixamo_to_vrm"
    bl_label = "Convert to VRM"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in context.active_object.data.edit_bones:
            if "Hips" in bone.name: bone.name = "hips"
            elif "Spine1" in bone.name: bone.name = "chest"
            elif "Spine2" in bone.name: bone.name = "upper_chest"
            elif "Neck" in bone.name: bone.name = "neck"
            elif "Head" in bone.name: bone.name = "head"
            elif "LeftEye" in bone.name: bone.name = "eye.L"
            elif "RightEye" in bone.name: bone.name = "eye.R"
            elif "LeftShoulder" in bone.name: bone.name = "shoulder.L"
            elif "LeftArm" in bone.name: bone.name = "upper_arm.L"
            elif "LeftForeArm" in bone.name: bone.name = "lower_arm.L"
            elif "LeftHandThumb1" in bone.name: bone.name = "thumb_proximal.L"
            elif "LeftHandThumb2" in bone.name: bone.name = "thumb_intermediate.L"
            elif "LeftHandThumb3" in bone.name: bone.name = "thumb_distal.L"
            elif "LeftHandIndex1" in bone.name: bone.name = "index_proximal.L"
            elif "LeftHandIndex2" in bone.name: bone.name = "index_intermediate.L"
            elif "LeftHandIndex3" in bone.name: bone.name = "index_distal.L"
            elif "LeftHandMiddle1" in bone.name: bone.name = "middle_proximal.L"
            elif "LeftHandMiddle2" in bone.name: bone.name = "middle_intermediate.L"
            elif "LeftHandMiddle3" in bone.name: bone.name = "middle_distal.L"
            elif "LeftHandRing1" in bone.name: bone.name = "ring_proximal.L"
            elif "LeftHandRing2" in bone.name: bone.name = "ring_intermediate.L"
            elif "LeftHandRing3" in bone.name: bone.name = "ring_distal.L"
            elif "LeftHandPinky1" in bone.name: bone.name = "little_proximal.L"
            elif "LeftHandPinky2" in bone.name: bone.name = "little_intermediate.L"
            elif "LeftHandPinky3" in bone.name: bone.name = "little_distal.L"
            elif "RightShoulder" in bone.name: bone.name = "shoulder.R"
            elif "RightArm" in bone.name: bone.name = "upper_arm.R"
            elif "RightForeArm" in bone.name: bone.name = "lower_arm.R"
            elif "RightHandThumb1" in bone.name: bone.name = "thumb_proximal.R"
            elif "RightHandThumb2" in bone.name: bone.name = "thumb_intermediate.R"
            elif "RightHandThumb3" in bone.name: bone.name = "thumb_distal.R"
            elif "RightHandIndex1" in bone.name: bone.name = "index_proximal.R"
            elif "RightHandIndex2" in bone.name: bone.name = "index_intermediate.R"
            elif "RightHandIndex3" in bone.name: bone.name = "index_distal.R"
            elif "RightHandMiddle1" in bone.name: bone.name = "middle_proximal.R"
            elif "RightHandMiddle2" in bone.name: bone.name = "middle_intermediate.R"
            elif "RightHandMiddle3" in bone.name: bone.name = "middle_distal.R"
            elif "RightHandRing1" in bone.name: bone.name = "ring_proximal.R"
            elif "RightHandRing2" in bone.name: bone.name = "ring_intermediate.R"
            elif "RightHandRing3" in bone.name: bone.name = "ring_distal.R"
            elif "RightHandPinky1" in bone.name: bone.name = "little_proximal.R"
            elif "RightHandPinky2" in bone.name: bone.name = "little_intermediate.R"
            elif "RightHandPinky3" in bone.name: bone.name = "little_distal.R"
            elif "LeftUpLeg" in bone.name: bone.name = "upper_leg.L"
            elif "LeftLeg" in bone.name: bone.name = "lower_leg.L"
            elif "LeftFoot" in bone.name: bone.name = "foot.L"
            elif "LeftToeBase" in bone.name: bone.name = "toes.L"
            elif "RightUpLeg" in bone.name: bone.name = "upper_leg.R"
            elif "RightLeg" in bone.name: bone.name = "lower_leg.R"
            elif "RightFoot" in bone.name: bone.name = "foot.R"
            elif "RightToeBase" in bone.name: bone.name = "toes.R"
            elif "LeftHand" in bone.name: bone.name = "hand.L"
            elif "RightHand" in bone.name: bone.name = "hand.R"
            elif "Spine" in bone.name: bone.name = "spine"
        
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.name = "VRM RIG"
        self.report({'INFO'}, "Successfully converted to VRM rig")
        return {'FINISHED'}

class OBJECT_OT_vrm_to_mixamo(Operator):
    """Convert VRM rig to Mixamo rig"""
    bl_idname = "object.vrm_to_mixamo"
    bl_label = "Convert to Mixamo"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in context.active_object.data.edit_bones:
            if "hips" in bone.name: bone.name = "mixamorig:Hips"
            elif "chest" in bone.name: bone.name = "mixamorig:Spine1"
            elif "upper_chest" in bone.name: bone.name = "mixamorig:Spine2"
            elif "neck" in bone.name: bone.name = "mixamorig:Neck"
            elif "head" in bone.name: bone.name = "mixamorig:Head"
            elif "eye.L" in bone.name: bone.name = "mixamorig:LeftEye"
            elif "eye.R" in bone.name: bone.name = "mixamorig:RightEye"
            elif "shoulder.L" in bone.name: bone.name = "mixamorig:LeftShoulder"
            elif "upper_arm.L" in bone.name: bone.name = "mixamorig:LeftArm"
            elif "lower_arm.L" in bone.name: bone.name = "mixamorig:LeftForeArm"
            elif "thumb_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandThumb1"
            elif "thumb_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandThumb2"
            elif "thumb_distal.L" in bone.name: bone.name = "mixamorig:LeftHandThumb3"
            elif "index_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandIndex1"
            elif "index_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandIndex2"
            elif "index_distal.L" in bone.name: bone.name = "mixamorig:LeftHandIndex3"
            elif "middle_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandMiddle1"
            elif "middle_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandMiddle2"
            elif "middle_distal.L" in bone.name: bone.name = "mixamorig:LeftHandMiddle3"
            elif "ring_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandRing1"
            elif "ring_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandRing2"
            elif "ring_distal.L" in bone.name: bone.name = "mixamorig:LeftHandRing3"
            elif "little_proximal.L" in bone.name: bone.name = "mixamorig:LeftHandPinky1"
            elif "little_intermediate.L" in bone.name: bone.name = "mixamorig:LeftHandPinky2"
            elif "little_distal.L" in bone.name: bone.name = "mixamorig:LeftHandPinky3"
            elif "shoulder.R" in bone.name: bone.name = "mixamorig:RightShoulder"
            elif "upper_arm.R" in bone.name: bone.name = "mixamorig:RightArm"
            elif "lower_arm.R" in bone.name: bone.name = "mixamorig:RightForeArm"
            elif "thumb_proximal.R" in bone.name: bone.name = "mixamorig:RightHandThumb1"
            elif "thumb_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandThumb2"
            elif "thumb_distal.R" in bone.name: bone.name = "mixamorig:RightHandThumb3"
            elif "index_proximal.R" in bone.name: bone.name = "mixamorig:RightHandIndex1"
            elif "index_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandIndex2"
            elif "index_distal.R" in bone.name: bone.name = "mixamorig:RightHandIndex3"
            elif "middle_proximal.R" in bone.name: bone.name = "mixamorig:RightHandMiddle1"
            elif "middle_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandMiddle2"
            elif "middle_distal.R" in bone.name: bone.name = "mixamorig:RightHandMiddle3"
            elif "ring_proximal.R" in bone.name: bone.name = "mixamorig:RightHandRing1"
            elif "ring_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandRing2"
            elif "ring_distal.R" in bone.name: bone.name = "mixamorig:RightHandRing3"
            elif "little_proximal.R" in bone.name: bone.name = "mixamorig:RightHandPinky1"
            elif "little_intermediate.R" in bone.name: bone.name = "mixamorig:RightHandPinky2"
            elif "little_distal.R" in bone.name: bone.name = "mixamorig:RightHandPinky3"
            elif "upper_leg.L" in bone.name: bone.name = "mixamorig:LeftUpLeg"
            elif "lower_leg.L" in bone.name: bone.name = "mixamorig:LeftLeg"
            elif "foot.L" in bone.name: bone.name = "mixamorig:LeftFoot"
            elif "toes.L" in bone.name: bone.name = "mixamorig:LeftToeBase"
            elif "upper_leg.R" in bone.name: bone.name = "mixamorig:RightUpLeg"
            elif "lower_leg.R" in bone.name: bone.name = "mixamorig:RightLeg"
            elif "foot.R" in bone.name: bone.name = "mixamorig:RightFoot"
            elif "toes.R" in bone.name: bone.name = "mixamorig:RightToeBase"
            elif "hand.L" in bone.name: bone.name = "mixamorig:LeftHand"
            elif "hand.R" in bone.name: bone.name = "mixamorig:RightHand"
            elif "spine" in bone.name: bone.name = "mixamorig:Spine"
        
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.name = "Mixamo RIG"
        self.report({'INFO'}, "Successfully converted to Mixamo rig")
        return {'FINISHED'}

class OBJECT_OT_detect_and_convert_rig(Operator):
    """Detect rig type and convert accordingly"""
    bl_idname = "object.detect_and_convert_rig"
    bl_label = "Convert Rig"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        active_obj = context.active_object
        
        if not active_obj or active_obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature")
            return {'CANCELLED'}
        
        # Detect rig type
        is_mixamo = False
        is_vrm = False
        
        for bone in active_obj.data.bones:
            if "mixamo" in bone.name.lower():
                is_mixamo = True
                break
            elif any(key in bone.name.lower() for key in ["hips", "spine", "chest", "neck", "head"]):
                is_vrm = True
                break
        
        # Convert based on detected type
        if is_mixamo:
            bpy.ops.object.mixamo_to_vrm()
            self.report({'INFO'}, "Converted Mixamo rig to VRM")
        elif is_vrm:
            bpy.ops.object.vrm_to_mixamo()
            self.report({'INFO'}, "Converted VRM rig to Mixamo")
        else:
            self.report({'WARNING'}, "Could not detect rig type")
            return {'CANCELLED'}
        
        return {'FINISHED'} 