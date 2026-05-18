# import json
# import numpy as np
# import os

# SCALE = 100.0


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# def write_bvh_no_hierarchy(json_path, output_path="output.bvh"):
#     if not os.path.isabs(json_path):
#         json_path = os.path.join(BASE_DIR, json_path)

#     with open(json_path, "r") as f:
#         frames = np.array(json.load(f))

#     num_frames, num_joints, _ = frames.shape
#     frames = frames * SCALE

#     lines = []

#     # --- HIERARCHY ---
#     lines.append("HIERARCHY")
#     lines.append("ROOT Joint0")
#     lines.append("{")
#     lines.append("\tOFFSET 0 0 0")
#     lines.append("\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")

#     # Add End Site for ROOT
#     lines.append("\tEnd Site")
#     lines.append("\t{")
#     lines.append("\t\tOFFSET 0 0 0")
#     lines.append("\t}")

#     # Sibling joints
#     for j in range(1, num_joints):
#         lines.append(f"\tJOINT Joint{j}")
#         lines.append("\t{")
#         lines.append("\t\tOFFSET 0 0 0")
#         lines.append("\t\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")

#         # Required End Site
#         lines.append("\t\tEnd Site")
#         lines.append("\t\t{")
#         lines.append("\t\t\tOFFSET 0 0 0")
#         lines.append("\t\t}")

#         lines.append("\t}")

#     lines.append("}")

#     # --- MOTION ---
#     lines.append("MOTION")
#     lines.append(f"Frames: {num_frames}")
#     lines.append("Frame Time: 0.0333333")

#     for frame in frames:
#         values = []
#         for joint in frame:
#             x, y, z = joint
#             values += [x, y, z, 0, 0, 0]  # rotations = 0
#         lines.append(" ".join(f"{v:.6f}" for v in values))

#     # Write to file
#     text = "\n".join(lines)
#     with open(output_path, "w") as f:
#         f.write(text)

#     return text


import json
import numpy as np
import os

SCALE = 100.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# MediaPipe Skeleton Hierarchy
# parent -> children
# =========================================================

DEFAULT_SKELETON = {

    # ROOT
    0: [1, 4, 11, 12, 23, 24],

    # Left face
    1: [2],
    2: [3],
    3: [7],

    # Right face
    4: [5],
    5: [6],
    6: [8],

    # Left arm
    11: [13],
    13: [15],
    15: [17, 19, 21],

    # Right arm
    12: [14],
    14: [16],
    16: [18, 20, 22],

    # Left leg
    23: [25],
    25: [27],
    27: [29, 31],

    # Right leg
    24: [26],
    26: [28],
    28: [30, 32],
}


def build_skeleton_tree(skeleton_data, root=0, num_joints=None):
    """Build a parent->children hierarchy from JSON skeleton connections."""

    # Support either adjacency dict or list of connection pairs
    if isinstance(skeleton_data, dict):
        edges = [
            (int(parent), int(child))
            for parent, children in skeleton_data.items()
            for child in children
        ]
    else:
        edges = [tuple(map(int, pair)) for pair in skeleton_data]

    nodes = set()
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)

    if num_joints is not None:
        nodes.update(range(num_joints))

    if root is None or root not in nodes:
        root = min(nodes) if nodes else 0

    adjacency = {node: set() for node in nodes}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    visited = set()
    children = {}

    def dfs(node):
        visited.add(node)
        children.setdefault(node, [])
        for neighbor in sorted(adjacency.get(node, [])):
            if neighbor not in visited:
                children[node].append(neighbor)
                dfs(neighbor)

    dfs(root)

    for node in sorted(nodes):
        if node not in visited:
            children.setdefault(root, []).append(node)
            dfs(node)

    return children

# =========================================================
# Recursive hierarchy writer
# =========================================================

def write_joint(
    lines,
    frame,
    joint_idx,
    skeleton,
    parent_idx=None,
    indent=0
):

    tabs = "\t" * indent

    # -----------------------------------------------------
    # ROOT / JOINT
    # -----------------------------------------------------

    if parent_idx is None:
        lines.append(f"{tabs}ROOT Joint{joint_idx}")
    else:
        lines.append(f"{tabs}JOINT Joint{joint_idx}")

    lines.append(f"{tabs}{{")

    # -----------------------------------------------------
    # OFFSET
    # -----------------------------------------------------

    if parent_idx is None:

        offset = np.array([0, 0, 0])

    else:

        offset = frame[joint_idx] - frame[parent_idx]

    ox, oy, oz = offset

    lines.append(
        f"{tabs}\tOFFSET "
        f"{ox:.6f} {oy:.6f} {oz:.6f}"
    )

    # -----------------------------------------------------
    # CHANNELS
    # Keep original behavior:
    # ALL joints get translation channels
    # -----------------------------------------------------

    lines.append(
        f"{tabs}\tCHANNELS 6 "
        f"Xposition Yposition Zposition "
        f"Zrotation Xrotation Yrotation"
    )

    # -----------------------------------------------------
    # CHILDREN
    # -----------------------------------------------------

    hierarchy = skeleton or DEFAULT_SKELETON
    children = hierarchy.get(joint_idx, [])

    if len(children) == 0:

        lines.append(f"{tabs}\tEnd Site")
        lines.append(f"{tabs}\t{{")
        lines.append(f"{tabs}\t\tOFFSET 0 0 0")
        lines.append(f"{tabs}\t}}")

    else:

        for child in children:

            write_joint(
                lines,
                frame,
                child,
                skeleton,
                joint_idx,
                indent + 1
            )

    lines.append(f"{tabs}}}")


# =========================================================
# Main BVH Writer
# =========================================================

def write_bvh_no_hierarchy(
    json_path,
    output_path="output.bvh"
):

    if not os.path.isabs(json_path):
        json_path = os.path.join(BASE_DIR, json_path)

    with open(json_path, "r") as f:
        data = json.load(f)

    frames = np.array(data["frames"], dtype=np.float32)
    skeleton_data = data.get("skeleton")

    # -----------------------------------------------------
    # Coordinate conversion
    # -----------------------------------------------------

    frames[:, :, 0] *= SCALE
    frames[:, :, 1] *= -SCALE
    frames[:, :, 2] *= SCALE

    num_frames, num_joints, _ = frames.shape

    hierarchy = None
    if skeleton_data is not None:
        hierarchy = build_skeleton_tree(
            skeleton_data,
            root=0,
            num_joints=num_joints,
        )

    lines = []

    # =====================================================
    # HIERARCHY
    # =====================================================

    lines.append("HIERARCHY")

    # Use first frame as bind pose
    bind_pose = frames[0]

    write_joint(
        lines,
        bind_pose,
        joint_idx=0,
        skeleton=hierarchy,
        parent_idx=None,
        indent=0
    )

    # =====================================================
    # MOTION
    # =====================================================

    lines.append("MOTION")
    lines.append(f"Frames: {num_frames}")
    lines.append("Frame Time: 0.0333333")

    for frame in frames:

        values = []

        for joint in frame:

            x, y, z = joint

            # Keep ORIGINAL movement behavior
            values += [
                x,
                y,
                z,
                0,
                0,
                0
            ]

        lines.append(
            " ".join(
                f"{v:.6f}" for v in values
            )
        )

    # =====================================================
    # Write file
    # =====================================================

    text = "\n".join(lines)

    output_path = os.path.join(BASE_DIR, output_path)

    with open(output_path, "w") as f:
        f.write(text)

    return text
