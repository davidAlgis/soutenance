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

@slide(3)
def slide_03(self):
        # --- Top bar ---
        bar = self._top_bar("Objectifs")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Compute the area available below the bar ----
        bar_rect = bar.submobjects[0]  # the Rectangle of the top bar
        y_top = bar_rect.get_bottom()[1] - 0.15  # small gap below bar
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_center = np.array(
            [(x_left + x_right) * 0.5, (y_top + y_bottom) * 0.5, 0.0]
        )
        max_w = (x_right - x_left) * 0.95
        max_h = (y_top - y_bottom) * 0.95

        # ---- PNG image centered in the remaining area ----
        img = ImageMobject("Figures/thesis_goals.png")

        # Fit within the area while preserving aspect ratio (don't upscale beyond 1:1)
        scale_w = max_w / img.width
        scale_h = max_h / img.height
        scale_factor = min(scale_w, scale_h, 1.0)
        img.scale(scale_factor)

        img.move_to(area_center)
        self.add(img)

        # End the slide
        self.pause()
        self.clear()
        self.next_slide()
