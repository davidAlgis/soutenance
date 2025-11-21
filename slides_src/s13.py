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


@slide(13)
def slide_13(self):
    """
    Transformée de Fourier rapide (IFFT) slide:
    - Top bar "Transformée de Fourier rapide"
    - Two body lines under the bar (same, larger font size; LaTeX for h_T)
    - Two-column area below:
        * LEFT  column: squared image 'Figures/fourier_space.png' with a pc.blueGreen
          square border and caption "Espace de Fourier ($h(k,t)$)"
        * Wait for user: draw arrow from RIGHT EDGE of left image toward the **left edge**
          of the right column; label above: IFFT O(N log N)
        * RIGHT column: squared image 'Figures/real_space.jpeg' with a pc.blueGreen
          square border and caption "Espace réel ($h(x,t)$)"
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Transformée de Fourier rapide")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Usable area below the bar ----------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    area_w = x_right - x_left
    area_h = y_top - y_bottom
    anchor_x = x_left + self.DEFAULT_PAD

    line1 = Tex(
        r"\mbox{Le calcul de la somme $h_T(x,t)$ est coûteux, donc on va utiliser une transformée }",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx1 = anchor_x - line1.get_left()[0]
    line1.shift(RIGHT * dx1)

    line2 = Tex(
        r"de Fourier rapide inverse (IFFT) :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line2.next_to(line1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    dx2 = anchor_x - line2.get_left()[0]
    line2.shift(RIGHT * dx2)

    self.play(
        FadeIn(line1, line2, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25
    )

    # --- Two-column layout (below body text) ------------------------------
    content_top_y = line2.get_bottom()[1] - 0.35
    content_bottom_y = y_bottom + 0.2
    content_h = max(2.0, content_top_y - content_bottom_y)
    content_center_y = (content_top_y + content_bottom_y) * 0.5

    col_gap = area_w * 0.08
    col_w = (area_w - col_gap) * 0.5
    cx_left_col = x_left + col_w * 0.5  # LEFT column center (Fourier)
    cx_right_col = x_right - col_w * 0.5  # RIGHT column center (Real)

    caption_h = 0.35
    max_side_w = col_w * 0.82
    max_side_h = content_h * 0.82 - caption_h
    side = max(1.2, min(max_side_w, max_side_h))

    # --- LEFT column: Fourier space ---------------------------------------
    fourier_img = ImageMobject("Figures/fourier_space.png")
    scale_f = min(side / fourier_img.width, side / fourier_img.height, 1.0)
    fourier_img.scale(scale_f)
    fourier_img.move_to([cx_left_col, content_center_y + 0.10, 0.0])

    border_f = Square(side_length=side, color=pc.blueGreen, stroke_width=6)
    border_f.move_to(fourier_img.get_center())

    cap_f = Tex(
        r"Espace de Fourier ($h(k,t)$)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    cap_f.next_to(fourier_img, DOWN, buff=0.18)
    self.next_slide()
    self.play(
        FadeIn(border_f, fourier_img, cap_f, shift=UP * self.SHIFT_SCALE),
        run_time=1.0,
    )

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Arrow to the LEFT EDGE of the right image ------------------------
    # We'll end the arrow slightly before the expected left edge of the right square.
    gap_arrow_end = 0.12
    # Compute the intended left-edge x of the right square if it were centered on cx_right_col:
    intended_left_edge_x = cx_right_col - side / 2.0
    # Arrow endpoints:
    start = border_f.get_right() + np.array([0.15, 0.0, 0.0])
    end = np.array(
        [
            intended_left_edge_x - gap_arrow_end,
            fourier_img.get_center()[1],
            0.0,
        ]
    )

    arrow = Arrow(
        start=start,
        end=end,
        buff=0.0,  # we manage the gap ourselves
        stroke_color=pc.blueGreen,
        stroke_width=6,
        tip_length=0.16,
    )
    arrow_label = MathTex(
        r"IFFT~\mathcal{O}(N\log(N))",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE - 4,
    )
    arrow_label.next_to(arrow, UP, buff=0.18)

    self.play(Create(arrow, run_time=0.7))
    self.play(FadeIn(arrow_label, run_time=0.3))

    # --- RIGHT column: Real space -----------------------------------------
    real_img = ImageMobject("Figures/real_space.jpeg")
    scale_r = min(side / real_img.width, side / real_img.height, 1.0)
    real_img.scale(scale_r)

    # Place the real image so that its LEFT EDGE is just to the right of the arrow end.
    left_edge_x = end[0] + gap_arrow_end
    center_x = left_edge_x + side / 2.0
    real_center = np.array([center_x, fourier_img.get_center()[1], 0.0])
    real_img.move_to(real_center)

    border_r = Square(side_length=side, color=pc.blueGreen, stroke_width=6)
    border_r.move_to(real_img.get_center())

    cap_r = Tex(
        r"Espace réel ($h(x,t)$)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    cap_r.next_to(real_img, DOWN, buff=0.18)

    self.play(FadeIn(border_r, real_img, cap_r, run_time=1.0))

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
