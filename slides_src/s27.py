# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.
# flake8: noqa: F405

import csv
import os

import numpy as np
import palette_colors as pc
from manim import *
from manim import logger
from manim_slides import Slide
from manim_tikz import Tikz
from slide_registry import slide
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)


@slide(27)
def slide_27(self):
    """
    Slide 27 : Recherche du plus proche voisin (RPPV)

    CSV expected header:
        Particle,X,Y
        1,0.2075,0.7779
        2,0.7110,0.3041
        3,0.4963,0.4596
    Positions are in [0,1]x[0,1].
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Recherche des plus proches voisins (RPPV)")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---- Usable area below the bar ---------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom

    pts = []
    try:
        with open(
            "states_sph/particles.csv", "r", newline="", encoding="utf-8"
        ) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "X" in row and "Y" in row:
                    pts.append((float(row["X"]), float(row["Y"])))
                if len(pts) >= 30:
                    break
    except Exception:
        rng = np.random.default_rng(7)
        for _ in range(30):
            pts.append((float(rng.uniform()), float(rng.uniform())))
    if not pts:
        pts = [(0.5, 0.5)]

    # --- Map [0,1]^2 into the slide body ----------------------------------
    pad_x = 0.6
    pad_y = 0.55
    tgt_left = x_left + pad_x
    tgt_right = x_right - pad_x
    tgt_bottom = y_bottom + pad_y
    tgt_top = y_top - pad_y
    tgt_w = max(0.1, tgt_right - tgt_left)
    tgt_h = max(0.1, tgt_top - tgt_bottom)

    def to_world(p01):
        return np.array(
            [tgt_left + p01[0] * tgt_w, tgt_bottom + p01[1] * tgt_h, 0.0]
        )

    Pw = [to_world(p) for p in pts]

    # Visual radius for particle dots
    r_vis = min(tgt_w, tgt_h) / 60.0

    # --- Particles ---------------------------------------------------------
    particles = [
        Dot(point=p, radius=r_vis, color=pc.blueGreen, fill_opacity=1.0)
        for p in Pw
    ]

    # [Grow animation]
    self.play(
        LaggedStart(
            *[GrowFromCenter(p) for p in particles],
            lag_ratio=0.05,
            run_time=0.9
        )
    )

    self.wait(0.1)
    self.next_slide()

    # --- Target selection (third) and recolor others to black --------------
    target_idx = min(2, len(particles) - 1)
    recolors = []
    for i, p in enumerate(particles):
        if i == target_idx:
            recolors.append(
                p.animate.set_color(pc.jellyBean).set_fill(
                    pc.jellyBean, opacity=1.0
                )
            )
        else:
            recolors.append(
                p.animate.set_color(BLACK).set_fill(BLACK, opacity=1.0)
            )
    self.play(*recolors, run_time=0.6)
    self.wait(0.1)
    self.next_slide()

    # --- Dashed circle (radius = 15*r_vis) + arrow/label h -----------------
    center = particles[target_idx].get_center()
    h_radius = 17.0 * r_vis

    circle = DashedVMobject(
        Circle(
            radius=h_radius, arc_center=center, color=BLACK, stroke_width=4
        ),
        num_dashes=80,
        dashed_ratio=0.55,
    )
    # [animation of draw]
    self.play(Create(circle), run_time=0.5)
    diag = np.array(
        [(np.sqrt(2)) / 2 * h_radius, (np.sqrt(2)) / 2 * h_radius, 0.0]
    )
    h_arrow = DoubleArrow(
        start=center,
        end=center + diag,
        stroke_width=6,
        color=BLACK,
        tip_length=0.16,
        buff=0.0,
    )
    self.play(Create(h_arrow), run_time=0.35)
    h_text = Tex("h", color=BLACK, font_size=self.BODY_FONT_SIZE)

    # h_text.next_to(h_arrow, DOWN, buff=0.06)

    h_text.move_to(center + 0.5 * diag + [0.3, -0.2, 0.0])
    self.play(FadeIn(h_text), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # Remove only the label "h" (keep arrow)
    self.play(FadeOut(h_text), run_time=0.2)

    # --- Five probe lines to random particles ------------------------------
    rng = np.random.default_rng(1)
    pool = [i for i in range(len(particles)) if i != target_idx]
    for _ in range(min(29, len(pool))):
        j = int(rng.choice(pool))
        pool.remove(j)
        pj = particles[j].get_center()
        L = Line(center, pj, color=GRAY, stroke_width=4)
        # [draw each line from its start to its end]
        self.play(Create(L), run_time=0.25)
        d = float(np.linalg.norm(pj - center))
        if d <= h_radius:
            self.play(
                particles[j]
                .animate.set_color(pc.blueGreen)
                .set_fill(pc.blueGreen, opacity=1.0),
                run_time=0.15,
            )
        else:
            self.play(
                particles[j]
                .animate.set_color(pc.fernGreen)
                .set_fill(pc.fernGreen, opacity=1.0),
                run_time=0.15,
            )
        # remove the line [reverse draw]
        self.play(Uncreate(L), run_time=0.18)
    self.wait(0.1)
    self.next_slide()

    # --- Color all by in/out + show O(30^2) --------------------------------
    anims = []
    for i, p in enumerate(particles):
        if i == target_idx:
            continue
        d = float(np.linalg.norm(p.get_center() - center))
        if d <= h_radius:
            anims.append(
                p.animate.set_color(pc.blueGreen).set_fill(
                    pc.blueGreen, opacity=1.0
                )
            )
        else:
            anims.append(
                p.animate.set_color(pc.fernGreen).set_fill(
                    pc.fernGreen, opacity=1.0
                )
            )
    self.play(LaggedStart(*anims, lag_ratio=0.03), run_time=0.7)

    complex_pos = np.array(
        [x_right - 2.4, (y_top + y_bottom) * 0.5 + 0.2, 0.0]
    )
    t_n2 = MathTex(
        r"\mathcal{O}(N^{2})", color=BLACK, font_size=self.BODY_FONT_SIZE + 10
    ).move_to(complex_pos)
    self.play(Write(t_n2), run_time=0.35)
    self.next_slide()

    # Remove complexity label and the dotted circle + arrow
    self.play(FadeOut(t_n2), run_time=0.25)
    self.play(FadeOut(circle), FadeOut(h_arrow), run_time=0.25)

    # Back to black for non-target points
    anims = []
    for i, p in enumerate(particles):
        if i != target_idx:
            anims.append(
                p.animate.set_color(BLACK).set_fill(BLACK, opacity=1.0)
            )
    self.play(*anims, run_time=0.45)
    self.next_slide()

    # --- Grid with cell size = h (h = h_radius) in background --------------
    grid_w = tgt_w
    grid_h = tgt_h
    grid_center = np.array(
        [(tgt_left + tgt_right) * 0.5, (tgt_bottom + tgt_top) * 0.5, 0.0]
    )

    border = Rectangle(
        width=grid_w, height=grid_h, color=BLACK, stroke_width=6
    ).move_to(grid_center)
    border.set_z_index(-10)

    self.play(Create(border), run_time=0.25)

    left_x = border.get_left()[0]
    right_x = border.get_right()[0]
    bottom_y = border.get_bottom()[1]
    top_y = border.get_top()[1]

    # Build vertical / horizontal lines spaced by h_radius
    v_lines = []
    x = left_x + h_radius
    while x <= right_x - 1e-6:
        l = Line(
            [x, bottom_y, 0], [x, top_y, 0], color=BLACK, stroke_width=6
        ).set_z_index(-9)
        v_lines.append(l)
        x += h_radius

    h_lines = []
    y = bottom_y + h_radius
    while y <= top_y - 1e-6:
        l = Line(
            [left_x, y, 0], [right_x, y, 0], color=BLACK, stroke_width=6
        ).set_z_index(-9)
        h_lines.append(l)
        y += h_radius

    # [draw each lines one after the other from its start to its end]
    # self.play(
    #     Succession(*[Create(l, run_time=0.2) for l in v_lines], lag_ratio=0.0)
    # )
    for l in v_lines:
        self.play(Create(l), run_time=0.2)
    for l in h_lines:
        self.play(Create(l), run_time=0.2)
    dim_y = bottom_y - 0.15
    cell_arrow = DoubleArrow(
        start=np.array([left_x, dim_y, 0]),
        end=np.array([left_x + h_radius, dim_y, 0]),
        color=BLACK,
        stroke_width=4,
        tip_length=0.15,
        buff=0.0,
    )
    cell_label = Tex("h", color=BLACK, font_size=self.BODY_FONT_SIZE).next_to(
        cell_arrow, DOWN, buff=0.1
    )

    self.play(Create(cell_arrow), Write(cell_label))
    # -----------------------------------------------------------------------
    self.wait(0.1)
    self.next_slide()

    # --- NEW: Fill target cell and its 8 neighbors -------------------------
    # Compute cell indices for target; origin at left_x / bottom_y
    cx, cy, _ = center
    i0 = int(np.floor((cx - left_x) / h_radius))
    j0 = int(np.floor((cy - bottom_y) / h_radius))

    def cell_rect(ii: int, jj: int, color, alpha: float) -> Rectangle | None:
        x0 = left_x + ii * h_radius
        y0 = bottom_y + jj * h_radius
        # bounds check: ensure the cell lies inside the border
        if x0 < left_x - 1e-6 or (x0 + h_radius) > right_x + 1e-6:
            return None
        if y0 < bottom_y - 1e-6 or (y0 + h_radius) > top_y + 1e-6:
            return None
        r = Rectangle(width=h_radius, height=h_radius, stroke_opacity=0.0)
        r.set_fill(color, opacity=alpha)
        r.move_to([x0 + 0.5 * h_radius, y0 + 0.5 * h_radius, 0.0])
        r.set_z_index(-9.5)  # behind grid lines, above border
        return r

    fills = []

    # Center cell
    c = cell_rect(i0, j0, pc.sunny, 0.45)
    if c is not None:
        fills.append(c)

    # 8-neighborhood
    # for di in (-1, 0, 1):
    #     for dj in (-1, 0, 1):
    #         if di == 0 and dj == 0:
    #             continue
    #         rct = cell_rect(i0 + di, j0 + dj, pc.cornflower, 0.35)
    #         if rct is not None:
    #             fills.append(rct)

    # 8-neighborhood
    neighbor_cells_idx = []  # Keep track of valid neighbor cells (i, j)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            # Store indices
            ni, nj = i0 + di, j0 + dj
            rct = cell_rect(ni, nj, pc.cornflower, 0.35)
            if rct is not None:
                fills.append(rct)
                neighbor_cells_idx.append((ni, nj))

    # Also add the center cell to valid search list
    neighbor_cells_idx.append((i0, j0))

    if fills:
        self.play(
            LaggedStart(
                *[FadeIn(r) for r in fills], lag_ratio=0.05, run_time=0.5
            )
        )

    circle2 = DashedVMobject(
        Circle(
            radius=h_radius, arc_center=center, color=BLACK, stroke_width=4
        ),
        num_dashes=80,
        dashed_ratio=0.55,
    )
    # [animation of draw]
    self.play(Create(circle2), run_time=0.5)
    self.wait(0.1)
    # -----------------------------------------------------------------------

    self.next_slide()

    # --- Recolor by in/out again (with opacity) ----------------------------
    anims = []
    for i, p in enumerate(particles):
        if i == target_idx:
            continue
        pos = p.get_center()
        d = float(np.linalg.norm(p.get_center() - center))
        # Calculate which grid cell this particle is in
        pi = int(np.floor((pos[0] - left_x) / h_radius))
        pj = int(np.floor((pos[1] - bottom_y) / h_radius))

        in_neighbor_cell = (pi, pj) in neighbor_cells_idx

        if d <= h_radius:
            anims.append(
                p.animate.set_color(pc.blueGreen).set_fill(
                    pc.blueGreen, opacity=0.85
                )
            )
        elif in_neighbor_cell:
            # Case 2: In Neighbor Grid Cell BUT Outside Radius (Gold)
            anims.append(
                p.animate.set_color(pc.uclaGold).set_fill(
                    pc.uclaGold, opacity=0.85
                )
            )
        else:
            anims.append(
                p.animate.set_color(pc.fernGreen).set_fill(
                    pc.fernGreen, opacity=0.65
                )
            )
    self.play(LaggedStart(*anims, lag_ratio=0.03), run_time=0.7)
    self.next_slide()

    # --- Write O(1) --------------------------------------------------------
    complex_pos = np.array([x_right - 2.4, (y_top + y_bottom) * 0.5, 0.0])
    t_o1 = MathTex(
        r"\mathcal{O}(N)", color=BLACK, font_size=self.BODY_FONT_SIZE + 10
    ).move_to(complex_pos)
    self.play(Write(t_o1), run_time=0.35)

    # End
    self.pause()
    self.clear()
    self.next_slide()
