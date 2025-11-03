import numpy as np
import palette_colors as pc
from manim import Dot, ValueTracker, VGroup
from manim.utils.rate_functions import linear
from sph_importer import import_sph_states


def show_sph_simulation(scene, csv_path: str, show_only_fluid: bool = False):
    frames = import_sph_states(csv_path)
    if not frames:
        print(f"[SPH] No frames found in {csv_path}")
        return

    # Map index -> position for each frame
    frame_maps = []
    for frame in frames:
        frame_map = {
            idx: pos[:2]
            for idx, pos in zip(frame.types.nonzero()[0], frame.pos)
        }
        frame_maps.append(frame_map)

    # --- Gather valid particle indices ---
    # Use frame[0] for filtering fluid particles (type == 0)
    frame0 = frames[0]
    valid_ids = [
        i
        for i in range(frame0.n)
        if (not show_only_fluid or frame0.types[i] == 0)
    ]
    # Use CSV 'index' field to ensure identity
    indices0 = [i for i in range(frame0.n)]
    ids0 = [
        i
        for i, t in enumerate(frame0.types)
        if (not show_only_fluid or t == 0)
    ]

    # Extract index field for each frame
    all_ids_per_frame = [set(range(frame.n)) for frame in frames]

    # Keep only indices present in all frames
    common_ids = set(ids0).intersection(*all_ids_per_frame)
    if not common_ids:
        print("[SPH] No common fluid particles across all frames.")
        return

    common_ids = sorted(common_ids)

    # --- Compute bounding box for centering ---
    all_positions = []
    for frame in frames:
        pos_map = {idx: pos[:2] for idx, pos in zip(range(frame.n), frame.pos)}
        for idx in common_ids:
            all_positions.append(pos_map[idx])
    all_positions = np.array(all_positions)
    mid_x, mid_y = np.mean(all_positions, axis=0)

    # --- Create Dots ---
    dots = VGroup()
    for idx in common_ids:
        pos = frames[0].pos[idx][:2] - np.array([mid_x, mid_y])
        color = pc.blueGreen if frames[0].types[idx] == 0 else pc.orange
        dot = Dot([*pos, 0.0], radius=0.05, color=color)
        dots.add(dot)

    scene.add(dots)
    scene.next_slide()

    # --- Animate using ValueTracker ---
    tracker = ValueTracker(0)

    def update(group):
        frame_idx = int(tracker.get_value())
        if frame_idx >= len(frames):
            frame_idx = len(frames) - 1
        frame = frames[frame_idx]
        for i, idx in enumerate(common_ids):
            pos = frame.pos[idx][:2] - np.array([mid_x, mid_y])
            group[i].move_to([*pos, 0.0])

    dots.add_updater(update)
    scene.play(
        tracker.animate.set_value(len(frames) - 1),
        run_time=5,
        rate_func=linear,
    )
    dots.remove_updater(update)
    scene.next_slide()
