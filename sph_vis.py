from __future__ import annotations

import bisect

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
    # visual duration (Manim time)
    run_time: float | None = None,
    # physical time control (SPH time)
    sim_seconds: float | None = None,  # duration to play in SPH seconds
    sim_start: float | None = None,  # start time (SPH seconds since 0)
    manim_seconds: (
        float | None
    ) = None,  # visual duration in Manim seconds (overrides run_time)
    # ROI
    roi_origin: tuple[float, float] | None = None,  # (ox, oy)
    roi_size: tuple[float, float] | None = None,  # (sx, sy)
    clip_outside: bool = True,
    center_on_roi: bool = False,
):
    """
    Animate SPH particles in 2D (X,Y) on a Manim Slide, fluids-only by default.

    - No use of particle IDs; we take the filtered array each frame.
    - N dots = count in the start frame after ROI filtering.
    - On each frame, move dot j to the j-th filtered position; hide extras if fewer.

    Time control:
      - sim_start: SPH start time (defaults to first frame time).
      - sim_seconds: SPH duration to play (e.g., 0.5).
      We compute the frame range [i_start..i_end] that covers [t0..t1]
      and animate an index tracker from i_start to i_end (so the last frame is guaranteed).

    ROI:
      If roi_origin & roi_size and clip_outside=True -> keep only points inside.
      If center_on_roi=True -> subtract ROI center from coordinates.
    """
    frames = import_sph_states(csv_path)
    if not frames:
        print(f"[SPH] No frames in {csv_path}")
        return

    times = [float(f.current_time) for f in frames]
    t_first, t_last = times[0], times[-1]

    # Determine physical window [t0, t1]
    t0 = t_first if sim_start is None else max(t_first, float(sim_start))
    if sim_seconds is None:
        t1 = t_last
    else:
        t1 = min(t_last, t0 + float(sim_seconds))
    if t1 <= t0:
        print(f"[SPH] Empty time window: t0={t0}, t1={t1}")
        return

    # Convert to frame range [i_start .. i_end], inclusive
    # i_start = first frame with time >= t0
    i_start = max(0, bisect.bisect_left(times, t0))
    if i_start >= len(frames):
        i_start = len(frames) - 1
    # i_end = last frame with time <= t1  (epsilon to include exact matches)
    eps = 1e-9
    i_end = bisect.bisect_right(times, t1 + eps) - 1
    if i_end < i_start:
        i_end = i_start
    # Sanity clamp
    i_start = max(0, min(i_start, len(frames) - 1))
    i_end = max(0, min(i_end, len(frames) - 1))

    def filter_xy_for_frame(fi: int) -> np.ndarray:
        f = frames[fi]
        if only_fluid:
            mask = f.types == 0
            xy = f.pos[mask, :2]
        else:
            xy = f.pos[:, :2]
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

    # Initial filtered positions from start frame define N
    xy0 = filter_xy_for_frame(i_start)
    if xy0.size == 0:
        print("[SPH] No particles selected in start frame after filtering.")
        return
    n_dots = int(xy0.shape[0])

    # Optional centering on ROI center
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
    for d in dots:
        d.set_opacity(1.0)

    scene.add(dots)
    scene.next_slide()  # show initial state

    # Visual duration
    if manim_seconds is not None:
        anim_duration = float(manim_seconds)
    elif run_time is not None:
        anim_duration = float(run_time)
    else:
        # proportional to physical window (fallback to 5s)
        window_len = times[i_end] - times[i_start]
        anim_duration = window_len if window_len > 0.0 else 5.0

    # Index-based tracker guarantees hitting last frame exactly
    idx_tracker = ValueTracker(float(i_start))

    def update(group: VGroup):
        fi = int(round(idx_tracker.get_value()))
        fi = max(i_start, min(fi, i_end))
        xy = filter_xy_for_frame(fi)
        m = int(xy.shape[0])

        lim = min(n_dots, m)
        for j in range(lim):
            group[j].move_to([float(xy[j, 0] - cx), float(xy[j, 1] - cy), 0.0])
            group[j].set_opacity(1.0)
        for j in range(lim, n_dots):
            group[j].set_opacity(0.0)

    dots.add_updater(update)
    scene.play(
        idx_tracker.animate.set_value(float(i_end)),
        run_time=anim_duration,
        rate_func=linear,
    )
    dots.remove_updater(update)

    scene.next_slide()
