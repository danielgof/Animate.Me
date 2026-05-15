import json
import numpy as np
import os

SCALE = 100.0


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def write_bvh_no_hierarchy(json_path, output_path="output.bvh"):
    if not os.path.isabs(json_path):
        json_path = os.path.join(BASE_DIR, json_path)

    with open(json_path, "r") as f:
        frames = np.array(json.load(f))

    num_frames, num_joints, _ = frames.shape
    frames = frames * SCALE

    lines = []

    # --- HIERARCHY ---
    lines.append("HIERARCHY")
    lines.append("ROOT Joint0")
    lines.append("{")
    lines.append("\tOFFSET 0 0 0")
    lines.append("\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")

    # Add End Site for ROOT
    lines.append("\tEnd Site")
    lines.append("\t{")
    lines.append("\t\tOFFSET 0 0 0")
    lines.append("\t}")

    # Sibling joints
    for j in range(1, num_joints):
        lines.append(f"\tJOINT Joint{j}")
        lines.append("\t{")
        lines.append("\t\tOFFSET 0 0 0")
        lines.append("\t\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")

        # Required End Site
        lines.append("\t\tEnd Site")
        lines.append("\t\t{")
        lines.append("\t\t\tOFFSET 0 0 0")
        lines.append("\t\t}")

        lines.append("\t}")

    lines.append("}")

    # --- MOTION ---
    lines.append("MOTION")
    lines.append(f"Frames: {num_frames}")
    lines.append("Frame Time: 0.0333333")

    for frame in frames:
        values = []
        for joint in frame:
            x, y, z = joint
            values += [x, y, z, 0, 0, 0]  # rotations = 0
        lines.append(" ".join(f"{v:.6f}" for v in values))

    # Write to file
    text = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(text)

    return text
