"""
Module for converting coordinates to JSON format.
"""

import os
import json
import cv2
import mediapipe as mp
# from mediapipe import solutions
# from mediapipe.framework.formats import landmark_pb2


# Get the directory where THIS script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path to the model file

MODEL_PATH = os.path.join(SCRIPT_DIR, 'pose_landmarker_heavy.task')
# # Build the absolute path to the video (if it's in the same folder)
VIDEO_PATH = os.path.join(SCRIPT_DIR, 'video/deadlift_1.mp4')

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

POSE_CONNECTIONS = [
    # Face
    [0, 1],
    [1, 2],
    [2, 3],
    [0, 4],
    [4, 5],
    [5, 6],
    # Torso
    [11, 12],
    [11, 23],
    [12, 24],
    [23, 24],
    # Left arm
    [11, 13],
    [13, 15],
    [15, 17],
    [15, 19],
    [15, 21],
    # Right arm
    [12, 14],
    [14, 16],
    [16, 18],
    [16, 20],
    [16, 22],
    # Left leg
    [23, 25],
    [25, 27],
    [27, 29],
    [27, 31],
    # Right leg
    [24, 26],
    [26, 28],
    [28, 30],
    [28, 32],
]

POSE_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,7),
    (0,4),(4,5),(5,6),(6,8),
    (9,10),
    (11,12),
    (11,13),(13,15),(15,17),(15,19),(15,21),
    (17,19),
    (12,14),(14,16),(16,18),(16,20),(16,22),
    (18,20),
    (11,23),(12,24),
    (23,24),
    (23,25),(25,27),(27,29),(29,31),
    (24,26),(26,28),(28,30),(30,32),
    (27,31),
    (28,32),
]

def process_video(video_path, model_path):

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
    )

    animation_data = []
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    with PoseLandmarker.create_from_options(options) as landmarker:
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )

            timestamp_ms = int((frame_count / fps) * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            if result.pose_landmarks:
                # Save 3D landmarks
                world_kpts = [
                    [lm.x, lm.y, lm.z]
                    for lm in result.pose_world_landmarks[0]
                ]
                animation_data.append(world_kpts)

                landmarks = result.pose_landmarks[0]

                # Convert normalized coordinates to pixel coordinates
                points = []
                for lm in landmarks:
                    x = int(lm.x * frame_width)
                    y = int(lm.y * frame_height)
                    points.append((x, y))

                # Draw skeleton (bones)
                for start, end in POSE_CONNECTIONS:
                    if start < len(points) and end < len(points):
                        cv2.line(
                            frame,
                            points[start],
                            points[end],
                            (255, 255, 255),
                            2
                        )

                # Draw joints
                for x, y in points:
                    cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            # cv2.imshow("Deadlift Processing...", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            frame_count += 1

    cap.release()
    cv2.destroyAllWindows()


    with open(os.path.join(SCRIPT_DIR,"motion_data_3d.json"), "w", encoding="utf-8") as f:
        json.dump(animation_data, f)

    return {"skeleton": POSE_CONNECTIONS, "frames": animation_data}




# def process_video(video_path, model_path):

#     options = PoseLandmarkerOptions(
#         base_options=BaseOptions(model_asset_path=model_path),
#         running_mode=VisionRunningMode.VIDEO
#     )


#     animation_data = []
#     cap = cv2.VideoCapture(video_path)  # pylint: disable=no-member
#     fps = cap.get(cv2.CAP_PROP_FPS)  # pylint: disable=no-member

#     # Get frame dimensions for coordinate scaling
#     frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # pylint: disable=no-member
#     frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # pylint: disable=no-member

#     with PoseLandmarker.create_from_options(options) as landmarker:
#         frame_count = 0
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             mp_image = mp.Image(
#                 image_format=mp.ImageFormat.SRGB,
#                 data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # pylint: disable=no-member

#             timestamp_ms = int((frame_count / fps) * 1000)
#             result = landmarker.detect_for_video(mp_image, timestamp_ms)

#             # --- DRAWING AND DATA EXTRACTION ---
#             if result.pose_landmarks:
#                 # 1. Save 3D World Landmarks for Blender/FBX
#                 world_kpts = [[lm.x, lm.y, lm.z] for lm in result.pose_world_landmarks[0]]
#                 animation_data.append(world_kpts)

#                 # 2. Draw 2D landmarks on the frame for visualization
#                 # Draw the complete MediaPipe pose skeleton
#                 pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
#                 pose_landmarks_proto.landmark.extend([
#                     landmark_pb2.NormalizedLandmark(
#                         x=lm.x,
#                         y=lm.y,
#                         z=lm.z,
#                         visibility=lm.visibility,
#                         presence=lm.presence,
#                     )
#                     for lm in result.pose_landmarks[0]
#                 ])

#                 solutions.drawing_utils.draw_landmarks(
#                     frame,
#                     pose_landmarks_proto,
#                     solutions.pose.POSE_CONNECTIONS,
#                     landmark_drawing_spec=solutions.drawing_styles.get_default_pose_landmarks_style(),
#                     connection_drawing_spec=solutions.drawing_styles.get_default_pose_landmarks_style(),
#                 )
#                 # for landmark in result.pose_landmarks[0]:
#                 #     # Scale normalized coordinates to pixel values
#                 #     pixel_x = int(landmark.x * frame_width)
#                 #     pixel_y = int(landmark.y * frame_height)

#                 #     # Draw a small green circle at each joint
#                 #     cv2.circle(frame, (pixel_x, pixel_y), 5, (0, 255, 0), -1)  # pylint: disable=no-member

#             # Show the frame with coordinates drawn
#             cv2.imshow('Deadlift Processing...', frame)  # pylint: disable=no-member

#             if cv2.waitKey(1) & 0xFF == ord('q'):  # pylint: disable=no-member
#                 break

#             frame_count += 1

#     # cap.release()
#     # cv2.destroyAllWindows()  # pylint: disable=no-member

#     # with open(os.path.join(SCRIPT_DIR,"motion_data_3d.json"), "w", encoding="utf-8") as f:
#     #     json.dump(animation_data, f)

#     # print(f"Successfully saved {len(animation_data)} frames of 3D motion data.")

#     return animation_data

# process_video(VIDEO_PATH, MODEL_PATH)

