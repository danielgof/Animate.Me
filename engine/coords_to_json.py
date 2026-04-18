import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import json

# 1. Setup the Task
model_path = 'pose_landmarker_heavy.task' 
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO)

animation_data = []
cap = cv2.VideoCapture("./data/video/deadlift_1.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

# Get frame dimensions for coordinate scaling
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

with PoseLandmarker.create_from_options(options) as landmarker:
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        timestamp_ms = int((frame_count / fps) * 1000)
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # --- DRAWING AND DATA EXTRACTION ---
        if result.pose_landmarks:
            # 1. Save 3D World Landmarks for Blender/FBX
            world_kpts = [[lm.x, lm.y, lm.z] for lm in result.pose_world_landmarks[0]]
            animation_data.append(world_kpts)

            # 2. Draw 2D landmarks on the frame for visualization
            for landmark in result.pose_landmarks[0]:
                # Scale normalized coordinates to pixel values
                pixel_x = int(landmark.x * frame_width)
                pixel_y = int(landmark.y * frame_height)
                
                # Draw a small green circle at each joint
                cv2.circle(frame, (pixel_x, pixel_y), 5, (0, 255, 0), -1)

        # Show the frame with coordinates drawn
        cv2.imshow('Deadlift Processing...', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame_count += 1

cap.release()
cv2.destroyAllWindows()

with open("motion_data_3d.json", "w") as f:
    json.dump(animation_data, f)

print(f"Successfully saved {len(animation_data)} frames of 3D motion data.")
