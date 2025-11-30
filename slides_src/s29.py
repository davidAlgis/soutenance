# slides_src/s31.py
import csv
import random

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


def _load_XY_from_csv(path: str, max_count: int = 30) -> np.ndarray:
    """
    Load up to max_count (X,Y) particle positions from CSV.
    Strictly uses 'X' and 'Y' columns.
    Returns shape (N, 2); may be empty if columns missing.
    """
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        if (
            not reader.fieldnames
            or ("X" not in reader.fieldnames)
            or ("Y" not in reader.fieldnames)
        ):
            return np.zeros((0, 2), dtype=float)
        pts = []
        for row in reader:
            try:
                x = float(row["X"])
                y = float(row["Y"])
            except Exception:
                continue
            pts.append([x, y])
            if len(pts) >= max_count:
                break
    return np.array(pts, dtype=float)


@slide(29)
def slide_29(self):
    """
    Slide 31 — Lancer de rayon pour la RPPV

    Steps:
      - Top bar + intro text
      - Draw 30 particles (blueGreen), fill body area (Grow)
      - Pause
      - Recolor: target (3rd) -> jellyBean, others BLACK; draw dotted circle R=15*pr
      - Pause
      - Draw small dashed circles around EACH particle (replacing gates)
      - Pause
      - Emit 4 diagonal rays from target WHILE randomly revealing all particles
        inside the dotted circle to blueGreen (target stays jellyBean)
    """

    # --- Top bar ---
    bar, footer = self._top_bar("Lancer de rayon pour la RPPV")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Intro line ---
    self.start_body()
    intro = self.add_body_text(
        "Utiliser le lancer de rayon pour la RPPV :",
        font_size=self.BODY_FONT_SIZE,
    )

    # --- Layout/bounds (keep particles below text) ---
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.22
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    # reserve a bit below the intro line
    body_top = min(intro.get_bottom()[1] - 0.25, y_top - 0.25)
    area_left = x_left + 0.25
    area_right = x_right - 0.25
    area_bottom = y_bottom + 0.35
    area_top = body_top - 0.10
    body_w = max(0.5, area_right - area_left)
    body_h = max(0.5, area_top - area_bottom)

    # --- Load up to 30 particles from X,Y ---
    raw_xy = _load_XY_from_csv("states_sph/particles.csv", max_count=30)
    if raw_xy.shape[0] == 0:
        # fallback grid (6x5)
        cols_g, rows_g = 6, 5
        xs = np.linspace(area_left, area_right, cols_g + 2)[1:-1]
        ys = np.linspace(area_bottom, area_top, rows_g + 2)[1:-1][::-1]
        pts = []
        for j in range(rows_g):
            for i in range(cols_g):
                pts.append([xs[i], ys[j]])
        xy = np.array(pts[:30], dtype=float)
    else:
        # normalize raw XY to the body area
        xmin, ymin = np.min(raw_xy, axis=0)
        xmax, ymax = np.max(raw_xy, axis=0)
        sx = (raw_xy[:, 0] - xmin) / max(1e-8, (xmax - xmin))
        sy = (raw_xy[:, 1] - ymin) / max(1e-8, (ymax - ymin))
        px = area_left + 0.06 * body_w + sx * (0.88 * body_w)
        py = area_bottom + 0.06 * body_h + sy * (0.88 * body_h)
        xy = np.column_stack([px, py])

    N = len(xy)
    pr = min(body_w, body_h) / 45.0  # particle radius

    # --- Draw particles (blueGreen) ---
    particles = VGroup(
        *[
            Dot(point=[xy[i, 0], xy[i, 1], 0.0], radius=pr, color=pc.blueGreen)
            for i in range(N)
        ]
    )
    self.play(
        LaggedStart(
            *[GrowFromCenter(p) for p in particles],
            lag_ratio=0.04,
            run_time=0.9
        )
    )
    self.wait(0.1)
    self.next_slide()

    # --- Recolor: target = 3rd -> jellyBean; others BLACK ---
    target_idx = 2 if N >= 3 else (N - 1 if N > 0 else 0)
    bound_r = 6.0 * pr
    bounds_group = VGroup()

    for i, p in enumerate(particles):
        if i == target_idx:
            continue
        c = Circle(
            radius=bound_r,
            color=pc.uclaGold,
            stroke_width=2,
            stroke_opacity=0.8,
        )
        c.move_to(p.get_center())

        # Use fewer dashes for smaller circles to maintain readability
        d_c = DashedVMobject(c, num_dashes=16, dashed_ratio=0.5)
        bounds_group.add(d_c)

    self.play(Create(bounds_group, run_time=0.5))
    self.wait(0.1)
    self.next_slide()

    recolor = []
    for i, p in enumerate(particles):
        if i == target_idx:
            recolor.append(p.animate.set_color(pc.jellyBean))
        else:
            recolor.append(p.animate.set_color(BLACK))
    self.play(*recolor, run_time=0.35)

    # --- Dotted circle around target (NEIGHBORHOOD) R = 15*pr ---
    # We keep this one distinct: BLACK, Thicker, Larger
    R = 15.0 * pr
    target_center = (
        particles[target_idx].get_center()
        if N > 0
        else np.array([0.0, 0.0, 0.0])
    )
    neighborhood_circle = DashedVMobject(
        Circle(radius=R, color=BLACK, stroke_width=4).move_to(target_center),
        num_dashes=48,
        dashed_ratio=0.55,
    )
    self.play(Create(neighborhood_circle, run_time=0.5))

    self.wait(0.1)

    # --- Dashed circles around each particle (BOUNDING VOLUMES) ---
    # UPDATED: Replaced gates with circles.
    # Visual distinction strategy:
    # 1. Radius: Much smaller (3.5*pr) vs Neighborhood (15*pr)
    # 2. Color: GRAY vs BLACK
    # 3. Stroke: Thinner (2) vs Thicker (4)

    self.next_slide()

    # --- Emit 4 diagonal rays from target AND reveal inside-circle simultaneously ---

    # Ray directions
    dirs = [
        np.array([+1.0, +1.0, 0.0]),
        np.array([-1.0, +1.0, 0.0]),
        np.array([+1.0, -1.0, 0.0]),
        np.array([-1.0, -1.0, 0.0]),
    ]

    def far_end(origin, d, scale=1.2):
        d2 = d / max(1e-8, np.linalg.norm(d))
        # extend relative to frame size to ensure out-of-bounds
        return (
            origin
            + scale
            * np.array([config.frame_width, config.frame_height, 0.0])
            * d2
        )

    def draw_ray(start_pt, end_pt):
        seg = VMobject().set_stroke(pc.uclaGold, width=6)
        seg.set_points_as_corners(
            np.vstack([start_pt, start_pt]).astype(float)
        )

        def _update(
            mob, alpha, s=start_pt.astype(float), e=end_pt.astype(float)
        ):
            p = s + (e - s) * alpha
            mob.set_points_as_corners(np.vstack([s, p]))

        return Succession(
            FadeIn(seg, run_time=0.01),
            UpdateFromAlphaFunc(seg, _update, run_time=0.60, rate_func=smooth),
            FadeOut(seg, run_time=0.25),
        )

    # Rays sequence (LaggedStart)
    start_pt = target_center
    ray_anims = []
    for d in dirs:
        end_pt = far_end(start_pt, d, scale=1.2)
        ray_anims.append(draw_ray(start_pt, end_pt))
    rays_seq = LaggedStart(*ray_anims, lag_ratio=0.18)

    # Identify particles inside the dotted neighborhood circle (excluding target)
    centers = np.array([p.get_center() for p in particles])
    dists = np.linalg.norm(centers - target_center, axis=1)
    inside_idx = [
        i
        for i, dist in enumerate(dists)
        if dist <= R + 1e-6 and i != target_idx
    ]

    # Random reveal sequence, staggered
    order = inside_idx[:]
    random.shuffle(order)
    reveal_anims = []
    for i in order:
        delay = 0.05 + 0.10 * random.random()
        reveal_anims.append(
            Succession(
                Wait(delay), particles[i].animate.set_color(pc.blueGreen)
            )
        )
    reveals_seq = LaggedStart(*reveal_anims, lag_ratio=0.08)

    # Play both at the same time
    self.play(AnimationGroup(rays_seq, reveals_seq, lag_ratio=0.10))
    self.wait(2.0)
    self.add_credit(r"Algis et Bramas, IJACSA, 2025}")

    # End
    self.pause()
    self.clear()
    self.next_slide()
