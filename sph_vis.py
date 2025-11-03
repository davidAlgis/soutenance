# sph_vis.py (only the function updated)
from __future__ import annotations

import numpy as np
import palette_colors as pc
from manim import Dot, ValueTracker, VGroup
from manim.utils.rate_functions import linear
from sph_importer import import_sph_states


def show_sph_simulation(
    scene,
    csv_path: str,
    only_fluid: bool = True,
    dot_radius: float = 0.04,
    run_time: float | None = None,
    # --- NEW: ROI controls ---
    roi_origin: tuple[float, float] | None = None,  # (ox, oy)
    roi_size: tuple[float, float] | None = None,  # (sx, sy)
    clip_outside: bool = True,  # hide particles outside ROI
    center_on_roi: bool = False,  # translate so ROI center is at (0,0)
):
    """
    Animate SPH particles in 2D (X,Y) on a Manim Slide.

    - No use of particle indices.
    - Per frame, take rows with type==0 if only_fluid else all rows.
    - Create exactly N dots from frame 0 (after optional ROI filtering if clip_outside=True).
    - On each frame, move dot j to j-th filtered position; hide extra dots when fewer points exist.

    ROI:
      If roi_origin & roi_size provided and clip_outside=True -> only show points inside.
      If center_on_roi=True, subtract ROI center (cx,cy) from displayed coordinates.
    """
    frames = import_sph_states(csv_path)
    if not frames:
        print(f"[SPH] No frames in {csv_path}")
        return

    def filter_xy(frame):
        """Return (M,2) positions filtered by type if only_fluid else all."""
        if only_fluid:
            mask = frame.types == 0
            xy = frame.pos[mask, :2]
        else:
            xy = frame.pos[:, :2]
        # ROI clipping (keep only inside) if requested
        if roi_origin is not None and roi_size is not None and clip_outside:
            ox, oy = roi_origin
            sx, sy = roi_size
            inside = (
                (xy[:, 0] >= ox)
                & (xy[:, 0] <= ox + sx)
                & (xy[:, 1] >= oy)
                & (xy[:, 1] <= oy + sy)
            )
            xy = xy[inside]
        return xy

    # Initial filtered positions (this defines N)
    xy0 = filter_xy(frames[0])
    if xy0.size == 0:
        print("[SPH] No particles selected in initial frame.")
        return

    n_dots = int(xy0.shape[0])

    # Optional translation so ROI is centered
    if center_on_roi and roi_origin is not None and roi_size is not None:
        cx = roi_origin[0] + roi_size[0] * 0.5
        cy = roi_origin[1] + roi_size[1] * 0.5
    else:
        cx = 0.0
        cy = 0.0

    # Create dots at initial positions
    dots = VGroup()
    for i in range(n_dots):
        x, y = float(xy0[i, 0] - cx), float(xy0[i, 1] - cy)
        dots.add(Dot(point=[x, y, 0.0], radius=dot_radius, color=pc.blueGreen))

    # Ensure visible at start
    for d in dots:
        d.set_opacity(1.0)

    scene.add(dots)
    scene.next_slide()  # show initial state

    # Duration
    sim_t0 = float(frames[0].current_time)
    sim_t1 = float(frames[-1].current_time)
    total_sim = sim_t1 - sim_t0
    if run_time is None:
        run_time = total_sim if total_sim > 0.0 else 5.0

    tracker = ValueTracker(0.0)

    def update(group: VGroup):
        i_frame = int(tracker.get_value())
        if i_frame >= len(frames):
            i_frame = len(frames) - 1

        xy = filter_xy(frames[i_frame])
        m = int(xy.shape[0])

        lim = min(n_dots, m)
        # move visible
        for j in range(lim):
            group[j].move_to([float(xy[j, 0] - cx), float(xy[j, 1] - cy), 0.0])
            group[j].set_opacity(1.0)
        # hide extras if current frame has fewer points
        for j in range(lim, n_dots):
            group[j].set_opacity(0.0)

    dots.add_updater(update)
    scene.play(
        tracker.animate.set_value(len(frames) - 1),
        run_time=run_time,
        rate_func=linear,
    )
    dots.remove_updater(update)

    # Keep final state
    scene.next_slide()
