import bpy
import json
import os

# Load the data we just created
data_path = os.path.join(os.getcwd(), "motion_data.json")
with open(data_path, "r") as f:
    animation_data = json.load(f)

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create Armature
bpy.ops.object.armature_add(enter_editmode=True)
arm_obj = bpy.context.object
arm_data = arm_obj.data

# We'll track the "Nose" (Index 0) as a starting point
bone = arm_data.edit_bones.new("Nose")
bone.head = (0, 0, 0)
bone.tail = (0, 0, 0.2)

bpy.ops.object.mode_set(mode='POSE')

# Apply animation
for frame_idx, frame_points in enumerate(animation_data):
    bpy.context.scene.frame_set(frame_idx)
    
    if len(frame_points) > 0:
        p_bone = arm_obj.pose.bones["Nose"]
        # Convert 2D YOLO (0 to 1) to Blender space
        # x is horizontal, -y becomes Z (up), and we set Y depth to 0
        x, y = frame_points[0][0], frame_points[0][1]
        p_bone.location = (x * 5, 0, (1 - y) * 5) 
        p_bone.keyframe_insert(data_path="location", index=-1)

# Export to FBX
export_path = os.path.join(os.getcwd(), "deadlift_animation.fbx")
bpy.ops.export_scene.fbx(filepath=export_path)