from ultralytics import YOLO
import cv2
import numpy as np

# Load a model
model = YOLO("yolo26n-pose.pt")  # load an official model

# Predict with the model
results = model("https://ultralytics.com/images/bus.jpg")  # predict on an image

# Access the results
# COCO skeleton (pairs of keypoint indices)
skeleton = [
    (5, 7), (7, 9),     # left arm
    (6, 8), (8, 10),    # right arm
    (5, 6),             # shoulders
    (5, 11), (6, 12),   # torso
    (11, 13), (13, 15), # left leg
    (12, 14), (14, 16), # right leg
    (11, 12)            # hips
]

for result in results:
    img = result.orig_img.copy()
    keypoints = result.keypoints.xy.cpu().numpy()

    for person in keypoints:
        # Draw points
        for x, y in person:
            if x > 0 and y > 0:
                cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0), -1)

        # Draw skeleton
        for i, j in skeleton:
            if i < len(person) and j < len(person):
                x1, y1 = person[i]
                x2, y2 = person[j]
                if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                    cv2.line(
                        img,
                        (int(x1), int(y1)),
                        (int(x2), int(y2)),
                        (255, 0, 0),  # blue lines
                        2
                    )

    cv2.imshow("Pose", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()