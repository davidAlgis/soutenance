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
from slide_registry import slide
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)


@slide(25)
def slide_25(self):
    """
    Slide 25 — Couplage avec des solides
    - Draw thick pc.orange frame, then replace by border particles.
    - Clear and show a full-width orange band (20% height) at the bottom half,
      with 6 large solid particles and 3 pc.blueGreen fluid particles above.
    - Draw arrow F^p from a fluid toward a solid, then reverse it.
    - Finish with pause/clear/next_slide.
    """
    import numpy as np
    from manim import (AnimationGroup, Arrow, Create, Dot, FadeIn, FadeOut,
                       GrowFromCenter, LaggedStart, Line, Rectangle, Tex,
                       VGroup)
    from manim.utils.rate_functions import linear

    # ---------- Top bar ----------
    bar, footer = self._top_bar("Couplage avec des solides")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---------- Body frame ----------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom

    # Colors
    # ---------- Intro sentence ----------
    txt = Tex(
        "On considère le solide comme un ensemble de particules",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).move_to([x_left + 0.5 * area_w, y_top - 0.45, 0])
    self.play(FadeIn(txt), run_time=0.45)

    # ---------- 1) Thick rectangle (draw each edge) ----------
    pad_side = 0.35
    pad_top = 0.90
    r_left = x_left + pad_side
    r_right = x_right - pad_side
    r_top = y_top - pad_top
    r_bottom = y_bottom + 0.28

    pBL = np.array([r_left, r_bottom, 0])
    pBR = np.array([r_right, r_bottom, 0])
    pTR = np.array([r_right, r_top, 0])
    pTL = np.array([r_left, r_top, 0])

    stroke_w = 22
    # Single rectangle instead of 4 separate lines
    x_vals = [pBL[0], pBR[0], pTR[0], pTL[0]]
    y_vals = [pBL[1], pBR[1], pTR[1], pTL[1]]
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)

    rect_w = x_max - x_min
    rect_h = y_max - y_min
    rect_center = [(x_min + x_max) * 0.5, (y_min + y_max) * 0.5, 0.0]

    rect = Rectangle(
        width=rect_w,
        height=rect_h,
        stroke_color=pc.orange,
        stroke_width=stroke_w,
    ).move_to(rect_center)

    self.play(Create(rect, run_time=1.0, rate_func=linear))

    # ---------- 2) Replace by border particles (keep faint rectangle) ----------
    def sample_segment(a, b, n):
        return [a + (b - a) * (i / (n - 1)) for i in range(n)]

    n_long, n_short = 22, 14
    pts_bottom = sample_segment(pBL, pBR, n_long)
    pts_right = sample_segment(pBR, pTR, n_short)
    pts_top = sample_segment(pTR, pTL, n_long)
    pts_left = sample_segment(pTL, pBL, n_short)

    chain_pts = pts_bottom + pts_right[:-1] + pts_top[:-1] + pts_left[:-1]
    dot_r = min((r_right - r_left), (r_top - r_bottom)) / 40.0  # larger
    border_dots = [
        Dot(p, radius=dot_r, color=pc.temptress, fill_opacity=1.0)
        for p in chain_pts
    ]
    self.wait(0.1)
    self.next_slide()
    self.play(
        rect.animate.set_opacity(0.5),
        LaggedStart(
            *[GrowFromCenter(d) for d in border_dots],
            lag_ratio=0.02,
            run_time=0.9
        ),
    )

    # ---------- 3) Clear, then draw filled band + 6 larger solids + 3 fluids ----------
    self.next_slide()
    self.play(
        FadeOut(VGroup(*border_dots, rect), run_time=0.35),
        FadeOut(txt, run_time=0.2),
    )

    # Full-width orange band (entire slide width, no padding)
    band_h = 0.20 * area_h
    band_y = y_bottom + 0.28 + 0.5 * band_h
    band = Rectangle(
        width=config.frame_width,
        height=band_h,
        color=pc.orange,
        fill_color=pc.orange,
        fill_opacity=0.55,
        stroke_width=0,
    ).move_to(
        [0.0, band_y, 0.0]
    )  # centered at x=0 so it spans whole slide
    self.play(FadeIn(band), run_time=0.25)

    # Six solid particles centered on the band (larger)
    n_solids = 6
    cx = 0.0
    cy = band_y
    usable_w = config.frame_width * 0.88
    gap = usable_w / (n_solids - 1)
    start_x = cx - usable_w / 2.0
    solid_R = band_h * 0.30  # bigger than before

    solids = []
    for i in range(n_solids):
        px = start_x + i * gap
        solids.append(
            Dot(
                [px, cy, 0],
                radius=solid_R,
                color=pc.temptress,
                fill_opacity=1.0,
            )
        )

    # Three fluid particles above the band, spread and bigger
    top_half_y = band_y + band_h * 2.25
    fluid_xs = [
        start_x + 0.45 * gap,
        start_x + 2.1 * gap,
        start_x + 4.35 * gap,
    ]
    fluid_R = solid_R * 0.95  # a bit larger than before
    fluids = [
        Dot(
            [fx, top_half_y, 0],
            radius=fluid_R,
            color=pc.blueGreen,
            fill_opacity=1.0,
        )
        for fx in fluid_xs
    ]

    self.play(
        LaggedStart(
            *[GrowFromCenter(d) for d in solids], lag_ratio=0.10, run_time=0.6
        ),
        LaggedStart(
            *[GrowFromCenter(d) for d in fluids], lag_ratio=0.15, run_time=0.6
        ),
    )

    # ---------- 4) Arrow and label, then reverse ----------
    self.next_slide()

    # choose the leftmost fluid and the nearest solid on its right
    f = fluids[0]
    s = solids[1] if len(solids) > 1 else solids[0]

    # Aim toward particle centers, but clamp to their rims
    fc = f.get_center()
    sc = s.get_center()
    v = sc - fc
    vn = v / np.linalg.norm(v)
    start = fc + vn * (fluid_R * 0.92)  # just inside fluid rim toward solid
    end = sc - vn * (solid_R * 0.92)  # just inside solid rim toward fluid

    arrow = Arrow(
        start,
        end,
        color=pc.oxfordBlue,
        stroke_width=6,
        buff=0.0,
        tip_length=0.18,
    )
    label = Tex(
        r"$F^p$", color=BLACK, font_size=self.BODY_FONT_SIZE + 10
    ).next_to(arrow, LEFT, buff=0.08)

    self.play(
        AnimationGroup(
            Create(arrow, run_time=0.45),
            FadeIn(label, run_time=0.25),
            lag_ratio=0.0,
        )
    )
    self.next_slide()

    # Reverse tip to point toward the fluid (keep center-aimed)
    arrow_rev_start = end
    arrow_rev_end = start
    self.play(
        AnimationGroup(
            arrow.animate.put_start_and_end_on(arrow_rev_start, arrow_rev_end),
            label.animate.next_to(arrow, LEFT, buff=0.08),
            lag_ratio=0.0,
        ),
        run_time=0.55,
    )

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
