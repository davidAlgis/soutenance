#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
):
    """
    Animate SPH particles in 2D (X, Y) on a Manim Slide.

    Rules:
    - We DO NOT use particle indices.
    - At each frame, we take all particles with type == 0 if only_fluid is True,
      else we take all particles.
    - We create N dots where N equals the count in the first frame (for stability),
      and move dot j to position j of the current frame’s filtered array.
    - No sorting, no ROI.

    Parameters
    ----------
    scene : Manim Scene or Slide (e.g., `self`)
    csv_path : str
        Path to CSV exported by your SPH tool.
    only_fluid : bool
        If True (default), show only fluid particles (type == 0).
    dot_radius : float
        Dot radius.
    run_time : float | None
        Duration of the animation. If None, uses the physical total time from CSV
        (last_time - first_time), and falls back to 5.0 if that’s <= 0.
    """
    frames = import_sph_states(csv_path)
    if not frames:
        print(f"[SPH] No frames in {csv_path}")
        return

    def filter_xy(frame):
        """Return Nx2 positions filtered by type if only_fluid else all."""
        if only_fluid:
            mask = frame.types == 0
            return frame.pos[mask, :2]
        return frame.pos[:, :2]

    # Determine dot count from first frame
    xy0 = filter_xy(frames[0])
    if xy0.size == 0:
        print("[SPH] No particles selected in initial frame.")
        return

    n_dots = xy0.shape[0]

    # Create the dots at initial positions (no centering, no ROI)
    dots = VGroup()
    for i in range(n_dots):
        x, y = xy0[i, 0], xy0[i, 1]
        color0 = (
            pc.blueGreen if only_fluid else pc.blueGreen
        )  # solids not shown here
        dots.add(Dot(point=[x, y, 0.0], radius=dot_radius, color=color0))

    scene.add(dots)
    scene.next_slide()

    # Time mapping
    sim_t0 = frames[0].current_time
    sim_t1 = frames[-1].current_time
    total_sim = float(sim_t1 - sim_t0)
    if run_time is None:
        run_time = total_sim if total_sim > 0.0 else 5.0

    tracker = ValueTracker(0.0)

    def update(group: VGroup):
        idx = int(tracker.get_value())
        if idx >= len(frames):
            idx = len(frames) - 1
        xy = filter_xy(frames[idx])

        # If the count changes (it shouldn't per your note), clamp to min.
        m = min(n_dots, xy.shape[0])
        for j in range(m):
            group[j].move_to([xy[j, 0], xy[j, 1], 0.0])
        # If xy has fewer points than n_dots, keep the extra dots where they are,
        # or optionally fade them; here we keep them.
        # If xy has more points than n_dots, we ignore extras (consistent with frame 0).

    dots.add_updater(update)
    scene.play(
        tracker.animate.set_value(len(frames) - 1),
        run_time=run_time,
        rate_func=linear,
    )
    dots.remove_updater(update)

    # Keep final state
    scene.next_slide()
