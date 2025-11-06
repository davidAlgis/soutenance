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
        max_logo_w = area_w * 0.22
        max_logo_h = area_h * 0.34
        scale = min(max_logo_w / logo.width, max_logo_h / logo.height, 1.0)
        logo.scale(scale)

        right_margin = 0.35
        top_margin = 0.20
        logo_x = x_right - right_margin - logo.width * 0.5
        logo_y = y_top - top_margin - logo.height * 0.5
        logo.move_to([logo_x, logo_y, 0])
        self.add(logo)

        # ========= Left: text column =========
        # Heading
        h1 = Text(
            "CUDA un langage pour programmation sur GPU :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )

        # (vspace in LaTeX → vertical gap here)
        vgap = 0.55

        # Subheading
        h2 = Text(
            "Les avantages et les inconvénients :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )

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

        # Pack left column; place under bar, left-aligned
        left_group = VGroup(h1, h2, pc_list)
        h1.set_x(x_left + 0.2)
        h1.set_y(y_top - 0.2)
        h2.align_to(h1, LEFT).next_to(h1, DOWN, buff=vgap, aligned_edge=LEFT)
        pc_list.align_to(h2, LEFT).next_to(
            h2, DOWN, buff=0.22, aligned_edge=LEFT
        )

        # ---- Avoid overlap with logo / bounds ----
        gap_to_logo = 0.6
        max_left_w = (logo.get_left()[0] - gap_to_logo) - x_left
        max_left_h = area_h * 0.92

        # Compute bounding box of left_group
        # (already positioned; now clamp size if needed)
        if left_group.width > max_left_w or left_group.height > max_left_h:
            s = min(
                max_left_w / left_group.width,
                max_left_h / left_group.height,
                1.0,
            )
            left_group.scale(s, about_point=h1.get_top())
            # Re-anchor after scaling
            dx = (x_left + 0.2) - left_group.get_left()[0]
            dy = (y_top - 0.2) - left_group[0].get_top()[
                1
            ]  # align h1 top again
            left_group.shift(RIGHT * dx + UP * dy)

        self.add(left_group)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()
