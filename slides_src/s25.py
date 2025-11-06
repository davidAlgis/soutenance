# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.

# flake8: noqa: F405
import os

import numpy as np
import palette_colors as pc
from manim import *
from manim import logger
from manim_slides import Slide
from manim_tikz import Tikz
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "25"
from slide_registry import slide


@slide(25)
def slide_25(self):
    """
    Slide 25 — Couplage avec des solides

    Visual result after zoom:
      • Only ~6 solid particles visible on the orange bottom strip (no corner).
      • 3 blue fluid particles, spread a bit randomly and clearly higher.
      • Band occupies most of the slide width.
      • Arrow Fp first points fluid -> solid, then reverses.
    """
    import random

    import numpy as np
    from manim import (AnimationGroup, Arrow, Create, Dot, FadeIn,
                       GrowFromCenter, LaggedStart, Line, Tex, VGroup)
    from manim.utils.rate_functions import linear

    # ---------- Top bar ----------
    bar = self._top_bar("Couplage avec des solides")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---------- Body area ----------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom

    # Colors
    orange = getattr(pc, "orange", ORANGE)
    temptress = getattr(pc, "temptress", MAROON_D)
    blueGreen = getattr(pc, "blueGreen", BLUE_D)

    # ---------- Sentence ----------
    body = Tex(
        "On considere le solide comme un ensemble de particules",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).move_to([x_left + 0.5 * area_w, y_top - 0.45, 0])
    self.play(FadeIn(body), run_time=0.45)

    # ---------- Rectangle geometry ----------
    pad_side = 0.35
    pad_top = 0.95
    rect_left = x_left + pad_side
    rect_right = x_right - pad_side
    rect_top = y_top - pad_top
    rect_bottom = y_bottom + 0.22

    pBL = np.array([rect_left, rect_bottom, 0.0])
    pBR = np.array([rect_right, rect_bottom, 0.0])
    pTR = np.array([rect_right, rect_top, 0.0])
    pTL = np.array([rect_left, rect_top, 0.0])

    edge_w = 22
    e_bottom = Line(pBL, pBR, color=orange, stroke_width=edge_w)
    e_right = Line(pBR, pTR, color=orange, stroke_width=edge_w)
    e_top = Line(pTR, pTL, color=orange, stroke_width=edge_w)
    e_left = Line(pTL, pBL, color=orange, stroke_width=edge_w)
    border_edges = VGroup(e_bottom, e_right, e_top, e_left)

    inset = 0.035 * min(area_w, area_h)
    gBL = pBL + np.array([+inset, +inset, 0])
    gBR = pBR + np.array([-inset, +inset, 0])
    gTR = pTR + np.array([-inset, -inset, 0])
    gTL = pTL + np.array([+inset, -inset, 0])
    guide = VGroup(
        Line(gBL, gBR, color=WHITE, stroke_width=3),
        Line(gBR, gTR, color=WHITE, stroke_width=3),
        Line(gTR, gTL, color=WHITE, stroke_width=3),
        Line(gTL, gBL, color=WHITE, stroke_width=3),
    )

    # PLAY #1 – draw rectangle + guide
    self.play(
        LaggedStart(
            *[Create(m) for m in [e_bottom, e_right, e_top, e_left]],
            lag_ratio=0.08,
            run_time=0.9,
            rate_func=linear
        ),
        Create(guide, run_time=0.35, rate_func=linear),
    )

    self.next_slide()

    # ---------- Border particles (larger) ----------
    def sample_segment(a, b, n):
        return [a + (b - a) * (i / (n - 1)) for i in range(n)]

    n_long, n_short = 28, 18
    pts_bottom = sample_segment(pBL, pBR, n_long)
    pts_left = sample_segment(pBL, pTL, n_short)
    pts_top = sample_segment(pTL, pTR, n_long)
    pts_right = sample_segment(pBR, pTR, n_short)

    chain = pts_bottom + pts_right[:-1] + pts_top[:-1] + pts_left[:-1]

    dot_r = min((rect_right - rect_left), (rect_top - rect_bottom)) / 45.0
    solid_dots = [
        Dot(p, radius=dot_r, color=temptress, fill_opacity=1.0) for p in chain
    ]

    # PLAY #2 – fade rectangle, grow dots
    self.play(
        border_edges.animate.set_opacity(0.65),
        LaggedStart(
            *[GrowFromCenter(d) for d in solid_dots],
            lag_ratio=0.02,
            run_time=0.9
        ),
        run_time=0.9,
    )

    self.next_slide()

    # ---------- Tight horizontal zoom on ~6 bottom particles ----------
    # Choose the bottom line dots and pick a central window of 6
    bottom_line = [
        d for d in solid_dots if abs(d.get_center()[1] - rect_bottom) < 1e-3
    ]
    bottom_line.sort(key=lambda d: d.get_center()[0])
    if len(bottom_line) < 6:
        window = bottom_line
    else:
        mid = len(bottom_line) // 2
        start = max(0, mid - 3)
        window = bottom_line[start : start + 6]

    # ROI: small horizontal window around those 6 dots; thin vertical band
    xs = [d.get_center()[0] for d in window]
    x_min, x_max = min(xs), max(xs)
    roi_w = (x_max - x_min) * 1.25  # small padding
    band_h = 0.28 * (rect_top - rect_bottom)
    roi_center = np.array(
        [(x_min + x_max) * 0.5, rect_bottom + 0.5 * band_h, 0.0]
    )

    # Compute scale so ROI fills ~86% of the current scene width
    target_w = 0.86 * (x_right - x_left)
    scale_factor = max(1.0, target_w / max(roi_w, 1e-6))

    # After scaling, shift upward to leave headroom for fluids
    shift_vec = np.array([0.0, +0.30, 0.0])

    world = VGroup(border_edges, guide, *solid_dots)
    # Hide non-window bottom dots so only ~6 remain perceptible
    hide = [d for d in bottom_line if d not in window]
    self.play(
        world.animate.scale(scale_factor, about_point=roi_center).shift(
            shift_vec
        ),
        AnimationGroup(
            *[d.animate.set_opacity(0.05) for d in hide], lag_ratio=0.0
        ),
        run_time=0.8,
    )
    # Keep only the visible subset for later logic clarity (they still exist visually)
    # but we use 'window' list when placing fluids/arrow.

    # ---------- Three fluid dots ABOVE strip, spread & higher ----------
    # Estimate local spacing
    if len(window) >= 2:
        spacing = abs(window[1].get_center()[0] - window[0].get_center()[0])
    else:
        spacing = (rect_right - rect_left) / 12.0

    # Pick 3 indices across the visible group and jitter x positions
    base_indices = (
        [0, len(window) // 2, len(window) - 1]
        if len(window) >= 3
        else list(range(len(window)))
    )
    fluid_dots = []
    rng = random.Random(42)
    for bi in base_indices:
        base_x = window[bi].get_center()[0]
        jx = rng.uniform(-0.22 * spacing, +0.22 * spacing)
        x = base_x + jx
        y = rect_bottom + band_h * 0.85  # clearly higher above the strip
        fluid_dots.append(
            Dot(
                [x, y, 0],
                radius=dot_r * 1.7,
                color=blueGreen,
                fill_opacity=1.0,
            )
        )

    # PLAY #3 – grow fluids
    if fluid_dots:
        self.play(
            LaggedStart(
                *[GrowFromCenter(d) for d in fluid_dots],
                lag_ratio=0.18,
                run_time=0.5
            )
        )

    self.next_slide()

    # ---------- Arrow Fp (downward), then reverse ----------
    # Choose the fluid closest (in x) to the center window, and the nearest solid (by x)
    if not fluid_dots or not window:
        # End gracefully if something went wrong
        self.pause()
        self.clear()
        self.next_slide()
        return

    f = min(fluid_dots, key=lambda d: abs(d.get_center()[0] - roi_center[0]))
    solid_neigh = min(
        window, key=lambda d: abs(d.get_center()[0] - f.get_center()[0])
    )

    start_pt = f.get_bottom() + np.array(
        [0, -0.55 * f.radius, 0]
    )  # from fluid downward
    end_pt = solid_neigh.get_top() + np.array(
        [0, 0.65 * solid_neigh.radius, 0]
    )

    arrow = Arrow(
        start_pt,
        end_pt,
        color=BLACK,
        stroke_width=6,
        buff=0.0,
        tip_length=0.18,
    )
    fp = Tex("Fp", color=BLACK, font_size=self.BODY_FONT_SIZE).next_to(
        arrow, LEFT, buff=0.08
    )

    # PLAY #4 – draw arrow + label
    self.play(
        AnimationGroup(Create(arrow, run_time=0.45), FadeIn(fp, run_time=0.2))
    )
    self.next_slide()

    # PLAY #5 – reverse
    self.play(
        AnimationGroup(
            arrow.animate.put_start_and_end_on(end_pt, start_pt),
            fp.animate.next_to(arrow, LEFT, buff=0.08),
            lag_ratio=0.0,
        ),
        run_time=0.55,
    )

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
