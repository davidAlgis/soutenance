# sph_vis.py
from typing import Optional, Tuple

import numpy as np
from manim import *
from sph_importer import import_sph_states


def play_sph_particles_from_csv(
    scene: Scene,
    csv_path: str,
    *,
    only_fluids: bool = True,
    projection: str = "xy",
    scale: float = 1.0,
    center: np.ndarray = np.array([0.0, 0.0, 0.0]),
    view_origin: Optional[Tuple[float, float]] = None,
    view_size: Optional[Tuple[float, float]] = None,
    particle_radius: float = 0.02,
    particle_color=WHITE,
    particle_opacity: float = 1.0,
    particle_stride: int = 1,
    frame_range: Optional[Tuple[int, int]] = None,
    frame_step: int = 1,
    run_time_per_frame: float = 0.05,
    fade_in_time: float = 0.25,
):
    """
    Fast SPH animation using a single PointCloud.
    After first frame is drawn, waits for scene.next_slide().
    """

    frames = import_sph_states(csv_path)
    if not frames:
        scene.add(Tex("Aucune donnée SPH", color=RED))
        scene.wait(0.5)
        return None

    # frame selection
    ids = list(range(len(frames)))
    if frame_range is not None:
        a, b = frame_range
        a = max(0, a)
        b = min(len(frames) - 1, b)
        ids = list(range(a, b + 1))
    ids = ids[:: max(1, frame_step)]
    if not ids:
        return None

    # ------------------------------------------------------------------
    # Projection helper
    # ------------------------------------------------------------------
    def _project(p3: np.ndarray) -> np.ndarray:
        if projection == "xy":
            arr = p3[:, [0, 1]]
        elif projection == "yz":
            arr = p3[:, [1, 2]]
        else:
            arr = p3[:, [0, 2]]

        # crop
        if view_origin is not None and view_size is not None:
            ox, oy = view_origin
            sx, sy = view_size
            m = (
                (arr[:, 0] >= ox)
                & (arr[:, 0] <= ox + sx)
                & (arr[:, 1] >= oy)
                & (arr[:, 1] <= oy + sy)
            )
            arr = arr[m]

        if particle_stride > 1:
            arr = arr[::particle_stride]

        arr = arr * scale
        z = np.zeros((arr.shape[0], 1), dtype=np.float32)
        pts = np.hstack([arr, z]) + center
        return pts.astype(np.float32, copy=False)

    def _pts(i: int) -> np.ndarray:
        fr = frames[i]
        p = fr.pos
        if only_fluids:
            mask = (fr.types == 0) | (fr.mass_solid == 0.0)
            p = p[mask]
        if p.size == 0:
            return np.zeros((0, 3), dtype=np.float32)
        return _project(p)

    # ------------------------------------------------------------------
    # Build initial cloud
    # ------------------------------------------------------------------
    init = _pts(ids[0])

    cloud = PointCloud(color=particle_color, opacity=particle_opacity)
    cloud.points = init
    scene.add(cloud)
    scene.play(FadeIn(cloud), run_time=fade_in_time)

    # Wait slide click
    scene.next_slide()

    # ------------------------------------------------------------------
    # Animate
    # ------------------------------------------------------------------
    for fi in ids[1:]:
        pN = _pts(fi)
        cloud.points = pN
        scene.play(
            cloud.animate,  # triggers redraw
            run_time=run_time_per_frame,
            rate_func=linear,
        )

    return cloud
