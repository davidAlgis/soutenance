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

    Phases:
      1) Draw a thick pc.orange rectangle (line-by-line).
      2) Replace it by 'solid' particles (pc.temptress) sampled along the border,
         keeping the rectangle faintly visible underneath.
      3) Clear, then draw a filled orange band covering full width and 20% height
         in the bottom half, add 6 large solid particles centered on the band and
         3 blueGreen fluid particles above.
      4) Draw a oxford-blue arrow from a fluid to a neighboring solid with label F^p,
         then reverse the arrow direction.
      5) End with pause/clear/next_slide.
    """
    import numpy as np
    from manim import (AnimationGroup, Arrow, Create, Dot, FadeIn, FadeOut,
                       GrowFromCenter, LaggedStart, Line, Rectangle, Tex,
                       VGroup)
    from manim.utils.rate_functions import linear

    # ---------- Top bar ----------
    bar = self._top_bar("Couplage avec des solides")
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
    orange = getattr(pc, "orange", ORANGE)
    temptress = getattr(pc, "temptress", MAROON_D)
    blueGreen = getattr(pc, "blueGreen", BLUE_D)
    oxford = getattr(pc, "oxford", BLACK)

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
    e_bottom = Line(pBL, pBR, color=orange, stroke_width=stroke_w)
    e_right = Line(pBR, pTR, color=orange, stroke_width=stroke_w)
    e_top = Line(pTR, pTL, color=orange, stroke_width=stroke_w)
    e_left = Line(pTL, pBL, color=orange, stroke_width=stroke_w)
    edges = VGroup(e_bottom, e_right, e_top, e_left)

    self.play(
        LaggedStart(
            *[Create(m) for m in [e_bottom, e_right, e_top, e_left]],
            lag_ratio=0.12,
            run_time=1.0,
            rate_func=linear
        )
    )

    # ---------- 2) Replace by border particles (keep faint rectangle) ----------
    def sample_segment(a, b, n):
        return [a + (b - a) * (i / (n - 1)) for i in range(n)]

    # Use moderate counts to avoid tiny-clip mux issues
    n_long, n_short = 22, 14
    pts_bottom = sample_segment(pBL, pBR, n_long)
    pts_right = sample_segment(pBR, pTR, n_short)
    pts_top = sample_segment(pTR, pTL, n_long)
    pts_left = sample_segment(pTL, pBL, n_short)

    chain_pts = pts_bottom + pts_right[:-1] + pts_top[:-1] + pts_left[:-1]
    dot_r = min((r_right - r_left), (r_top - r_bottom)) / 48.0
    border_dots = [
        Dot(p, radius=dot_r, color=temptress, fill_opacity=1.0)
        for p in chain_pts
    ]

    self.next_slide()
    self.play(
        edges.animate.set_opacity(0.5),
        LaggedStart(
            *[GrowFromCenter(d) for d in border_dots],
            lag_ratio=0.02,
            run_time=0.9
        ),
    )

    # ---------- 3) Clear, then draw filled band + 6 solids + 3 fluids ----------
    self.next_slide()
    self.play(
        FadeOut(VGroup(*border_dots, edges), run_time=0.35),
        FadeOut(txt, run_time=0.2),
    )

    # Orange band: full width, 20% of body height, in bottom half
    band_h = 0.20 * area_h
    band_y = y_bottom + 0.28 + 0.5 * band_h
    band = Rectangle(
        width=area_w,
        height=band_h,
        color=orange,
        fill_color=orange,
        fill_opacity=0.55,
        stroke_width=0,
    ).move_to([x_left + 0.5 * area_w, band_y, 0])
    self.play(FadeIn(band), run_time=0.25)

    # Six solid particles centered on band
    cx = x_left + 0.5 * area_w
    cy = band_y
    usable_w = area_w * 0.90
    n_solids = 6
    gap = usable_w / (n_solids - 1)
    start_x = cx - usable_w / 2.0
    solid_R = band_h * 0.24  # large enough to visually fill horizontally

    solids = []
    for i in range(n_solids):
        px = start_x + i * gap
        solids.append(
            Dot([px, cy, 0], radius=solid_R, color=temptress, fill_opacity=1.0)
        )

    # Three fluid particles above the band (top half), spread across
    top_half_y = band_y + band_h * 2.1
    fluid_xs = [start_x + 0.5 * gap, start_x + 3.0 * gap, start_x + 5.2 * gap]
    fluid_R = solid_R * 0.80
    fluids = [
        Dot(
            [fx, top_half_y, 0],
            radius=fluid_R,
            color=blueGreen,
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

    start = f.get_bottom() + np.array([0.0, -0.55 * f.radius, 0.0])
    end = s.get_top() + np.array([0.0, 0.55 * s.radius, 0.0])

    arrow = Arrow(
        start, end, color=oxford, stroke_width=6, buff=0.0, tip_length=0.18
    )
    label = Tex(r"$F^p$", color=BLACK, font_size=self.BODY_FONT_SIZE).next_to(
        arrow, LEFT, buff=0.08
    )

    self.play(
        AnimationGroup(
            Create(arrow, run_time=0.45),
            FadeIn(label, run_time=0.25),
            lag_ratio=0.0,
        )
    )
    self.next_slide()

    # Reverse tip to point toward the fluid
    self.play(
        AnimationGroup(
            arrow.animate.put_start_and_end_on(end, start),
            label.animate.next_to(arrow, LEFT, buff=0.08),
            lag_ratio=0.0,
        ),
        run_time=0.55,
    )

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
