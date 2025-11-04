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
    manim_seconds: float | None = None,  # visual duration (overrides run_time)
    # ROI
    roi_origin: tuple[float, float] | None = None,  # (ox, oy)
    roi_size: tuple[float, float] | None = None,  # (sx, sy)
    clip_outside: bool = True,
    center_on_roi: bool = False,  # kept for backward compat (ignored if fitting below is used)
    # NEW: layout mapping
    fit_roi_to_width: (
        float | None
    ) = None,  # map ROI width to this many Manim units
    fit_roi_to_height: (
        float | None
    ) = None,  # map ROI height to this many Manim units
    target_center: tuple[float, float] = (
        0.0,
        0.0,
    ),  # where ROI center should land
    cover: bool = False,  # if both width & height given: False=contain (min), True=cover (max)
):
    """
    Animate SPH particles in 2D (X,Y) on a Manim Slide, fluids-only by default.

    - No particle IDs; we use the filtered array each frame.
    - N dots = count in the start frame after ROI filtering.
    - On each frame, move dot j to the j-th filtered position; hide extras if fewer.

    Time control:
      We compute the frame range [i_start..i_end] that covers [t0..t1] and animate an
      index tracker from i_start to i_end (guarantees we render the last frame).

    ROI clipping:
      If roi_origin & roi_size and clip_outside=True -> keep only points inside.

    Layout mapping:
      If fit_roi_to_width/height are given (and ROI is provided), we compute a uniform scale
      's' so that the ROI is mapped to the requested on-screen size. The ROI center is placed
      at 'target_center'. If both width and height are provided, 'cover' decides min/max.
      If no fitting is requested, we keep coordinates unscaled and optionally recentre if
      center_on_roi=True.
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
    i_start = max(0, bisect.bisect_left(times, t0))
    if i_start >= len(frames):
        i_start = len(frames) - 1
    eps = 1e-9
    i_end = bisect.bisect_right(times, t1 + eps) - 1
    if i_end < i_start:
        i_end = i_start
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

    # --- Compute transform: (world -> screen)
    # Translation to use as "world center" (cx, cy)
    if roi_origin is not None and roi_size is not None:
        ox, oy = roi_origin
        sx, sy = roi_size
        world_cx = ox + sx * 0.5
        world_cy = oy + sy * 0.5
    else:
        # Fallback: use start-frame centroid if no ROI
        world_cx = float(np.mean(xy0[:, 0]))
        world_cy = float(np.mean(xy0[:, 1]))

    # Target center in screen
    tx, ty = target_center

    # Uniform scale factor
    s = 1.0
    if roi_origin is not None and roi_size is not None:
        sw = (
            (fit_roi_to_width / sx)
            if (fit_roi_to_width is not None and sx != 0.0)
            else None
        )
        sh = (
            (fit_roi_to_height / sy)
            if (fit_roi_to_height is not None and sy != 0.0)
            else None
        )
        if sw is not None and sh is not None:
            s = max(sw, sh) if cover else min(sw, sh)
        elif sw is not None:
            s = sw
        elif sh is not None:
            s = sh
        else:
            # no fitting requested: optionally recentre if legacy flag set
            if center_on_roi:
                s = 1.0
    else:
        # no ROI: keep s=1.0
        pass

    def world_to_screen(xy: np.ndarray) -> np.ndarray:
        # shift to ROI/world center, scale, then translate to target center
        if xy.size == 0:
            return xy
        xs = (xy[:, 0] - world_cx) * s + tx
        ys = (xy[:, 1] - world_cy) * s + ty
        return np.stack([xs, ys], axis=1)

    # Create dots at initial positions
    dots = VGroup()
    xy0_screen = world_to_screen(xy0)
    for i in range(n_dots):
        x, y = float(xy0_screen[i, 0]), float(xy0_screen[i, 1])
        dots.add(Dot(point=[x, y, 0.0], radius=dot_radius, color=pc.blueGreen))
    for d in dots:
        d.set_opacity(1.0)

    scene.add(dots)
    scene.wait(0.1)
    scene.next_slide()  # show initial state

    # Visual duration
    if manim_seconds is not None:
        anim_duration = float(manim_seconds)
    elif run_time is not None:
        anim_duration = float(run_time)
    else:
        window_len = times[i_end] - times[i_start]
        anim_duration = window_len if window_len > 0.0 else 5.0

    # Index-based tracker ensures we hit the last frame exactly
    idx_tracker = ValueTracker(float(i_start))

    def update(group: VGroup):
        fi = int(round(idx_tracker.get_value()))
        fi = max(i_start, min(fi, i_end))
        xy = filter_xy_for_frame(fi)
        m = int(xy.shape[0])

        xy_screen = world_to_screen(xy)

        lim = min(n_dots, m)
        for j in range(lim):
            group[j].move_to(
                [float(xy_screen[j, 0]), float(xy_screen[j, 1]), 0.0]
            )
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
