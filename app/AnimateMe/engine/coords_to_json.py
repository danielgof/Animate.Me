"""
Module for converting coordinates to JSON format.
"""

import os
import json
import cv2
import mediapipe as mp

# Get the directory where THIS script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path to the model file
MODEL_PATH = os.path.join(SCRIPT_DIR, 'pose_landmarker_heavy.task')
# Build the absolute path to the video (if it's in the same folder)
VIDEO_PATH = os.path.join(SCRIPT_DIR, 'deadlift_1.mp4')
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode



def process_video(model_path):

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO
    )

    animation_data = []
    cap = cv2.VideoCapture(VIDEO_PATH)  # pylint: disable=no-member
    fps = cap.get(cv2.CAP_PROP_FPS)  # pylint: disable=no-member

    # Get frame dimensions for coordinate scaling
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # pylint: disable=no-member
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # pylint: disable=no-member

    with PoseLandmarker.create_from_options(options) as landmarker:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # pylint: disable=no-member

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
                    cv2.circle(frame, (pixel_x, pixel_y), 5, (0, 255, 0), -1)  # pylint: disable=no-member

            # Show the frame with coordinates drawn
            # cv2.imshow('Deadlift Processing...', frame)  # pylint: disable=no-member

            if cv2.waitKey(1) & 0xFF == ord('q'):  # pylint: disable=no-member
                break

            frame_count += 1

    cap.release()
    cv2.destroyAllWindows()  # pylint: disable=no-member
    with open(os.path.join(SCRIPT_DIR,"motion_data_3d.json"), "w", encoding="utf-8") as f:
        json.dump(animation_data, f)

    print(f"Successfully saved {len(animation_data)} frames of 3D motion data.")

process_video(MODEL_PATH)