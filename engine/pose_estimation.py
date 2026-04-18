"""
Module for pose estimation using YOLO.
"""

import json

from ultralytics import YOLO

model = YOLO("yolo11n-pose.pt")
results = model.track("./data/video/deadlift_1.mp4", persist=True)

animation_data = []

for frame in results:
    if frame.keypoints is not None and len(frame.keypoints.xyn) > 0:
        # Get normalized coordinates for the first person
        kpts = frame.keypoints.xyn[0].cpu().numpy().tolist()
        animation_data.append(kpts)

# Save to a temporary file
with open("motion_data.json", "w", encoding="utf-8") as f:
    json.dump(animation_data, f)

print("Success: Motion data saved to motion_data.json")
