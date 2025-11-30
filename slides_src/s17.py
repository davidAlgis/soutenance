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


@slide(17)
def slide_17(self):
    """
    Slide 18: Comment calculer l'entrée de la méthode ?
    - Top bar with title.
    - Three body lines (Tex; includes h(x,t)).
    - Wait for user.
    - Three-column gallery, each revealed step-by-step:
        1) Figures/Mask3D_theoric_view.jpeg + "Vue théorique"
        2) Figures/MaskHeightMap.jpeg       + "Vue du dessus dans le stockage"
        3) Figures/Mask3D-contrast.jpeg     + "Vue avec une mer plate"
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Comment calculer l'entrée de la méthode ?")
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

    # --- Body text (Tex, left-aligned to anchor) --------------------------
    self.start_body()

    line1 = Tex(
        r"\mbox{Lorsqu'un navire avance : une vague haute à l'avant et une vague basse à l'arrière.}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    line1.shift(RIGHT * (anchor_x - line1.get_left()[0]))
    self.play(FadeIn(line1, shift=RIGHT * self.SHIFT_SCALE), run_time=0.5)
    self.next_slide()

    line2 = Tex(
        r"\mbox{« masque du navire » : intersection entre solide et surface de l'eau $h(x,t)$",
        tex_template=self.french_template,
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line2.next_to(line1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    line2.shift(RIGHT * (anchor_x - line2.get_left()[0]))

    self.play(FadeIn(line2, shift=RIGHT * self.SHIFT_SCALE), run_time=0.5)

    # --- Wait for user before images --------------------------------------
    self.next_slide()

    # --- Columns layout ----------------------------------------------------
    content_top_y = line2.get_bottom()[1] - 0.35
    content_bottom_y = y_bottom + 0.2
    content_h = max(1.6, content_top_y - content_bottom_y)
    content_center_y = (content_top_y + content_bottom_y) * 0.5

    col_gap = area_w * 0.06
    col_w = (area_w - 2 * col_gap) / 2.0

    cx1 = x_left + col_w * 0.5
    cx2 = cx1 + col_w + col_gap

    caption_h = 0.35
    max_side_w = col_w * 0.92
    max_side_h = content_h * 0.92 - caption_h
    side_max = max(1.2, min(max_side_w, max_side_h))

    def place_image_with_caption(
        img_path: str, center_x: float, caption_tex: str
    ) -> Group:
        """
        Create an ImageMobject scaled to fit within a square of side 'side_max',
        centered at (center_x, content_center_y), with a Tex caption below.
        Uses Group since ImageMobject is a Mobject (not VMobject).
        """
        img = ImageMobject(img_path)
        scale = min(side_max / img.width, side_max / img.height, 1.0)
        img.scale(scale)
        img.move_to([center_x, content_center_y + 0.10, 0.0])

        cap = Tex(caption_tex, color=BLACK, font_size=self.BODY_FONT_SIZE - 5)
        cap.next_to(img, DOWN, buff=0.18)
        return Group(img, cap)

    # --- Column 1 ----------------------------------------------------------
    col1 = place_image_with_caption(
        "Figures/Mask3D_theoric_view.jpeg",
        cx1,
        r"Vue théorique",
    )
    self.play(FadeIn(col1, run_time=0.4))

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Column 3 ----------------------------------------------------------
    col3 = place_image_with_caption(
        "Figures/Mask3D-contrast.jpeg",
        cx2,
        r"Vue de l'entrée",
    )
    self.play(FadeIn(col3, run_time=0.4))

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
