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


@slide(2)
def slide_02(self):
    # --- Top bar + title (kept static, on top) ---
    bar, footer = self._top_bar("Contexte")
    self.add(bar)
    self.add_foreground_mobject(bar)  # keep the bar above everything

    intro = Tex(
        r"Arc Blanc : formation manœuvres complexes sur un navire",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    intro.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (-config.frame_width / 2 + self.DEFAULT_PAD) - intro.get_left()[0]
    intro.shift(RIGHT * (dx + 0.6))
    self.play(FadeIn(intro, run_time=0.3, shift=RIGHT * self.SHIFT_SCALE))
    self.wait(0.1)
    self.next_slide()

    # Optional background grid (behind everything else)
    # numberplane = NumberPlane(color=BLACK)
    # self.add(numberplane)

    # --- Left image (headset) - appears first (fade in) ---
    img_left = ImageMobject("Figures/man_head_set.png")
    img_left.to_edge(LEFT, buff=0.6)
    img_left.to_edge(DOWN, buff=0.1)
    img_left.scale(0.7)
    self.play(FadeIn(img_left, shift=RIGHT * self.SHIFT_SCALE, run_time=0.6))
    # --- Lines (draw from their start to end) ---
    line1 = Line([-4.5, 0, 0], [-1, -2, 0], color=pc.blueGreen)
    line2 = Line([-4.5, 0.5, 0], [-1, 2, 0], color=pc.blueGreen)
    # Draw them sequentially for clarity
    self.play(
        Create(line1, rate_func=smooth, run_time=0.9),
        Create(line2, rate_func=smooth, run_time=0.9),
    )

    # --- Right image placement (anchored to the two line endpoints) ---
    # Targets: left-lower = (-1, -2, 0), left-upper = (-1,  2, 0)
    img_boat = ImageMobject("Figures/inside_boat.jpeg")
    img_boat.set_height(4.0)  # span from y=-2 to y=+2
    img_boat.set_y(0.0)  # vertical center
    img_boat.set_x(-1.0 + img_boat.get_width() / 2.0)  # left edge at x = -1

    # Surrounding rectangle (tight fit), fade in AFTER the lines are drawn
    img_boat_box = SurroundingRectangle(
        img_boat, color=pc.blueGreen, buff=0.0, stroke_width=16
    )
    self.play(Create(img_boat_box, run_time=1.5))

    # Finally, fade in the image inside the rectangle
    self.play(FadeIn(img_boat, run_time=0.6))

    # End the slide
    self.pause()
    self.clear()
    self.next_slide()
