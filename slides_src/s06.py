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

@slide(6)
def slide_06(self):
        # --- Top bar ---
        bar = self._top_bar("Unity et les compute shaders")
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

        # ========= Right: Unity logo (TOP-RIGHT, reduced) =========
        logo = ImageMobject("Figures/unity_oxford_blue.png")

        # Smaller cap than before
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
        # Headings + lists
        h1 = Text(
            "Unity un moteur de jeu polyvalent :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )

        bullet_items = [
            "Physique",
            "Rendu",
            "Réalité virtuelle",
            "Interface avec le GPU : les compute shaders",
            "...",
        ]
        lst = make_bullet_list(
            bullet_items,
            bullet_color=pc.blueGreen,
            font_size=self.BODY_FONT_SIZE,
            line_gap=0.18,
            left_pad=0.22,
        )
        # stack under h1
        lst.align_to(h1, LEFT)
        lst.next_to(h1, DOWN, buff=0.22, aligned_edge=LEFT)

        h2 = Text(
            "Les avantages et les inconvénients des compute shaders:",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )
        h2.align_to(h1, LEFT)
        h2.next_to(lst, DOWN, buff=0.55, aligned_edge=LEFT)

        pros = ["Multi-support"]
        cons = [
            "Ne bénéficie pas des dernières technologies",
            "Lourd à programmer",
            "Pas simple à débogger",
            "...",
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

        # Pack left column
        left_group = VGroup(h1, lst, h2, pc_list)

        # ---- Layout box for the left column (avoid overflow) ----
        # Reserve some spacing from the logo
        gap_to_logo = 0.6
        max_left_w = (logo.get_left()[0] - gap_to_logo) - x_left
        max_left_h = area_h * 0.92

        # Initial position (top-left anchor)
        left_group.arrange(DOWN, buff=0.18, center=False, aligned_edge=LEFT)
        left_group.move_to(
            [
                x_left + 0.2 + left_group.width * 0.5,
                y_top - 0.2 - left_group.height * 0.5,
                0,
            ]
        )

        # Auto-scale if too wide or too tall
        if left_group.width > max_left_w or left_group.height > max_left_h:
            s = min(
                max_left_w / left_group.width,
                max_left_h / left_group.height,
                1.0,
            )
            left_group.scale(s, about_point=left_group.get_top())
            # Re-anchor after scaling to keep inside bounds
            left_group.move_to(
                [
                    x_left + 0.2 + left_group.width * 0.5,
                    y_top - 0.2 - left_group.height * 0.5,
                    0,
                ]
            )

        self.add(left_group)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()
