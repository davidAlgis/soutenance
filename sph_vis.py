#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import numpy as np
import palette_colors as pc
from manim import Dot, ValueTracker, VGroup
from manim.utils.rate_functions import linear
from sph_importer import import_sph_states

#!/usr/bin/env python3
# -*- coding: utf-8 -*-





def show_sph_simulation(
    scene,
    csv_path: str,
    only_fluid: bool = True,
    dot_radius: float = 0.04,
    run_time: float | None = None,
):
    """
    Animate SPH particles in 2D (X, Y) on a Manim Slide.

    Behavior:
    - No use of particle indices.
    - Per frame, take all rows with type == 0 if only_fluid else all rows.
    - Create exactly N dots (N taken from frame 0 after filtering).
    - On each frame, move dot j to the j-th filtered position.
    - If a frame has fewer items than N, hide the extra dots (opacity 0).
      If it has more, ignore the surplus (keep exactly N dots).
    """
    frames = import_sph_states(csv_path)
    if not frames:
        print(f"[SPH] No frames in {csv_path}")
        return

    def filter_xy(frame):
        """Return (M,2) positions filtered by type if only_fluid else all."""
        if only_fluid:
            mask = frame.types == 0
            return frame.pos[mask, :2]
        return frame.pos[:, :2]

    # Initial filtered positions
    xy0 = filter_xy(frames[0])
    if xy0.size == 0:
        print("[SPH] No particles selected in initial frame.")
        return

    n_dots = int(xy0.shape[0])

    # Create dots at initial positions
    dots = VGroup()
    for i in range(n_dots):
        x, y = float(xy0[i, 0]), float(xy0[i, 1])
        color0 = (
            pc.blueGreen if only_fluid else pc.blueGreen
        )  # solids not shown here
        dots.add(Dot(point=[x, y, 0.0], radius=dot_radius, color=color0))

    # Ensure fully visible at start
    for d in dots:
        d.set_opacity(1.0)

    scene.add(dots)
    scene.next_slide()  # show initial state

    # Determine animation duration
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

        # Move the overlapping part
        lim = min(n_dots, m)
        for j in range(lim):
            group[j].move_to([float(xy[j, 0]), float(xy[j, 1]), 0.0])
            group[j].set_opacity(1.0)

        # Hide any extra dots if current frame has fewer points than n_dots
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
