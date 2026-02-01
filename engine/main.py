import scipy.io as sio

data = sio.loadmat("data/FLIC/examples.mat")

print(data.keys())

examples = data["examples"]

print(type(examples))
print(examples.shape)

ex = examples[0, 0]
print(ex.dtype)

filepath = ex["filepath"][0]
print(filepath)

import cv2

img = cv2.imread("data/FLIC/12-oclock-high-special-edition-00006361.jpg")

# joints = ex["joints"]
# print(joints.shape)

import matplotlib.pyplot as plt

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

for i in range(joints.shape[1]):
    x, y = joints[:, i]
    if x > 0 and y > 0:
        cv2.circle(img, (int(x), int(y)), 4, (255, 0, 0), -1)

plt.imshow(img)
plt.axis("off")
plt.show()


# joints = data["joints"]



# if __name__ == "__main__":

#     KEYPOINT_DICT = {
#         'nose': 0,
#         'left_eye': 1,
#         'right_eye': 2,
#         'left_ear': 3,
#         'right_ear': 4,
#         'left_shoulder': 5,
#         'right_shoulder': 6,
#         'left_elbow': 7,
#         'right_elbow': 8,
#         'left_wrist': 9,
#         'right_wrist': 10,
#         'left_hip': 11,
#         'right_hip': 12,
#         'left_knee': 13,
#         'right_knee': 14,
#         'left_ankle': 15,
#         'right_ankle': 16
#     }

    