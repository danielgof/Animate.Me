import json
import numpy as np

SCALE = 100.0

def write_bvh_no_hierarchy(json_path, output_path="output.bvh"):
    with open(json_path, "r") as f:
        frames = np.array(json.load(f))

    num_frames, num_joints, _ = frames.shape
    frames = frames * SCALE

    lines = []  # <--- collect all output here

    # --- HIERARCHY ---
    lines.append("HIERARCHY")
    lines.append("ROOT Joint0")
    lines.append("{")
    lines.append("\tOFFSET 0 0 0")
    lines.append("\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")

    # Write each joint as a sibling, not nested
    for j in range(1, num_joints):
        lines.append(f"\tJOINT Joint{j}")
        lines.append("\t{")
        lines.append("\t\tOFFSET 0 0 0")
        lines.append("\t\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")
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
            values += [x, y, z, 0, 0, 0]
        lines.append(" ".join(f"{v:.6f}" for v in values))

    # Write to file
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    # Return the full BVH text as a string
    return "\n".join(lines)
