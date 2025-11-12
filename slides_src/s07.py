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


@slide(7)
def slide_07(self):
    # --- Top bar ---
    bar = self._top_bar("CUDA")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---- Usable area below the bar ----
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15  # small gap under bar
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    area_w = x_right - x_left
    area_h = y_top - y_bottom

    # ========= Right: CUDA logo (TOP-RIGHT) =========
    logo = ImageMobject("Figures/cuda_blue_green.png")
    max_logo_w = area_w * 0.44
    max_logo_h = area_h * 0.68
    scale = min(max_logo_w / logo.width, max_logo_h / logo.height, 1.0)
    logo.scale(scale)

    right_margin = 0.35
    top_margin = 0.35
    logo_x = x_right - right_margin - logo.width * 0.5
    logo_y = y_bottom + top_margin + logo.height * 0.5
    logo.move_to([logo_x, logo_y, 0])
    self.add(logo)

    # ========= Left: text column =========
    # Heading
    h1 = Tex(
        "CUDA un langage pour programmation sur GPU.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    h1.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (-config.frame_width / 2 + self.DEFAULT_PAD) - h1.get_left()[0]
    h1.shift(RIGHT * (dx + 0.6))

    self.play(FadeIn(logo), FadeIn(h1), run_time=0.25)

    self.next_slide()
    # (vspace in LaTeX → vertical gap here)
    vgap = 0.55

    # Subheading
    h2 = Tex(
        "Les avantages et les inconvénients :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    h2.align_to(h1, LEFT)
    h2.next_to(h1, DOWN, buff=0.5, aligned_edge=LEFT)
    self.play(FadeIn(h2), run_time=0.25)
    self.next_slide()

    # Pros / Cons
    pros = [
        "Intuitif à programmer",
        "Outils de débogage",
        "Performants",
        "Bénéficie des dernières technologies",
    ]
    cons = [
        "Utilisable uniquement sur carte Nvidia",
        "Pas accessible dans Unity",
    ]
    pc_list = make_pro_cons(
        pros,
        cons,
        pro_color=pc.apple,
        con_color=pc.bittersweet,
        font_size=self.BODY_FONT_SIZE,
        icon_size=self.BODY_FONT_SIZE + 2,
        col_gap=0.9,
        row_gap=0.18,
        left_pad=0.18,
    )
    pc_list.align_to(h2, LEFT)
    pc_list.next_to(h2, DOWN, buff=0.22, aligned_edge=LEFT)
    self.play(FadeIn(pc_list), run_time=0.25)
    self.next_slide()

    # End slide
    self.pause()
    self.clear()
    self.next_slide()
