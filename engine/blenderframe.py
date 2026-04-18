"""
Module for creating Blender frames from motion data.
"""

import json
import os

import bpy

# Load your joint data
data_path = os.path.join(os.getcwd(), "motion_data.json")
with open(data_path, "r", encoding="utf-8") as f:
    frames = json.load(f)

bpy.ops.wm.read_homefile(use_empty=True)

num_joints = len(frames[0])

joint_objs = []

# Create a sphere for each joint
for i in range(num_joints):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05)

    # Background mode fix: get the last created object manually
    obj = bpy.data.objects[-1]
    obj.name = f"Joint_{i}"

    joint_objs.append(obj)

# Animate
for frame_idx, joints in enumerate(frames):
    bpy.context.scene.frame_set(frame_idx)

    for j, (x, y) in enumerate(joints):
        obj = joint_objs[j]

        # Convert 2D → 3D
        obj.location = (x * 5, 0, (1 - y) * 5)

        obj.keyframe_insert(data_path="location")
