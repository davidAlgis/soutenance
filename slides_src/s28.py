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


@slide(28)
def slide_28(self):
    """
    Slide 28 : Mémoire partagée (shared memory)
    Fixes requested:
      1) From "Mémoire globale" draw ONE vertical line down to mid-height,
         then two horizontal arrows from that point to each grid.
      2) Move the two "Mémoire partagée" rectangles so their centers are
         vertically halfway between the top rectangle and the grids.
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Mémoire partagée")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Usable area -------------------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom
    mid_x = 0.0

    # Helper: 4x4 grid
    def make_grid(center, w, h, stroke=6):
        outer = Rectangle(
            width=w, height=h, color=BLACK, stroke_width=stroke
        ).move_to(center)
        lines = []
        for i in range(1, 4):
            x = outer.get_left()[0] + i * (w / 4.0)
            lines.append(
                Line(
                    [x, outer.get_bottom()[1], 0],
                    [x, outer.get_top()[1], 0],
                    color=BLACK,
                    stroke_width=stroke,
                )
            )
        for i in range(1, 4):
            y = outer.get_bottom()[1] + i * (h / 4.0)
            lines.append(
                Line(
                    [outer.get_left()[0], y, 0],
                    [outer.get_right()[0], y, 0],
                    color=BLACK,
                    stroke_width=stroke,
                )
            )
        return VGroup(outer, *lines)

    # --- Top: large "Mémoire globale" rectangle ----------------------------
    top_rect_w = area_w * 0.55
    top_rect_h = area_h * 0.14
    top_rect_y = y_top - top_rect_h * 0.5 - 0.10
    global_rect = RoundedRectangle(
        width=top_rect_w,
        height=top_rect_h,
        corner_radius=0.18,
        stroke_color=BLACK,
        stroke_width=6,
        fill_opacity=0.0,
    ).move_to([mid_x, top_rect_y, 0.0])
    global_label = Tex(
        r"Mémoire globale", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
    ).move_to(global_rect.get_center())
    self.play(Create(global_rect), Create(global_label), run_time=0.5)
    self.wait(0.1)
    self.next_slide()
    # --- Grids (left and right) -------------------------------------------
    grid_w = min(5.2, area_w * 0.34)
    grid_h = min(3.8, area_h * 0.30)
    grids_y = y_bottom + grid_h * 0.5 + 0.60
    gap_lr = area_w * 0.10
    left_center = np.array([mid_x - (grid_w + gap_lr) * 0.6, grids_y, 0.0])
    right_center = np.array([mid_x + (grid_w + gap_lr) * 0.6, grids_y, 0.0])

    grid_left = make_grid(left_center, grid_w, grid_h)
    grid_right = make_grid(right_center, grid_w, grid_h)
    self.play(Create(grid_left), Create(grid_right), run_time=0.5)
    # --- Central vertical line + horizontal arrows (lent/large) ------------
    # Vertical line from bottom of global_rect to mid-height between rect and grids
    grid_top_y = grid_left[0].get_top()[1]
    y_mid = 0.5 * (global_rect.get_bottom()[1] + grid_top_y)
    # --- "Mémoire partagée" rectangles centered vertically between top+grids
    small_w = grid_w * 0.55
    small_h = grid_h * 0.28

    shared_y = y_mid  # centered vertically as requested

    shared_left = RoundedRectangle(
        width=small_w,
        height=small_h,
        corner_radius=0.18,
        stroke_color=BLACK,
        stroke_width=6,
        fill_opacity=0.0,
    ).move_to([left_center[0], shared_y, 0.0])

    shared_right = RoundedRectangle(
        width=small_w,
        height=small_h,
        corner_radius=0.18,
        stroke_color=BLACK,
        stroke_width=6,
        fill_opacity=0.0,
    ).move_to([right_center[0], shared_y, 0.0])

    txt_shared_l = Tex(
        r"Mémoire partagée", color=BLACK, font_size=self.BODY_FONT_SIZE
    ).move_to(shared_left.get_center())
    txt_shared_r = Tex(
        r"Mémoire partagée", color=BLACK, font_size=self.BODY_FONT_SIZE
    ).move_to(shared_right.get_center())

    self.play(
        Create(shared_left),
        Create(shared_right),
        FadeIn(txt_shared_l),
        FadeIn(txt_shared_r),
        run_time=1.0,
    )

    self.wait(0.1)
    self.next_slide()

    central_line = Line(
        [mid_x, global_rect.get_bottom()[1], 0.0],
        [mid_x, grids_y, 0.0],
        color=BLACK,
        stroke_width=6,
    )

    # Horizontal arrows from the end of the vertical line to each grid center (x)
    arrow_left = Arrow(
        start=[mid_x, grids_y, 0.0],
        end=[left_center[0] + 0.5 * grid_w, grids_y, 0.0],
        color=BLACK,
        stroke_width=6,
        buff=0.0,
    )
    arrow_right = Arrow(
        start=[mid_x, grids_y, 0.0],
        end=[right_center[0] - 0.5 * grid_w, grids_y, 0.0],
        color=BLACK,
        stroke_width=6,
        buff=0.0,
    )

    lbl_slow_l = Tex(
        r"Débit lent\\Stockage large",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).next_to(central_line, RIGHT, buff=0.12)
    # lbl_slow_r = Tex(r"Débit lent\\Stockage large", color=BLACK, font_size=self.BODY_FONT_SIZE)\
    # .next_to(central_line, LEFT, buff=0.12)

    self.play(
        Create(central_line),
        Create(arrow_left),
        Create(arrow_right),
        FadeIn(lbl_slow_l),
        run_time=0.5,
    )
    self.wait(0.1)

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Fast/small arrows from shared boxes down to grids -----------------
    fast_arrow_l = Arrow(
        start=[left_center[0], shared_left.get_bottom()[1] - 0.02, 0.0],
        end=[left_center[0], grid_left[0].get_top()[1] + 0.02, 0.0],
        stroke_width=6,
        color=BLACK,
        buff=0.0,
    )
    fast_arrow_r = Arrow(
        start=[right_center[0], shared_right.get_bottom()[1] - 0.02, 0.0],
        end=[right_center[0], grid_right[0].get_top()[1] + 0.02, 0.0],
        stroke_width=6,
        color=BLACK,
        buff=0.0,
    )

    lbl_fast_l = Tex(
        r"Débit rapide\\Stockage léger",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).next_to(fast_arrow_l, LEFT, buff=0.18)
    lbl_fast_r = Tex(
        r"Débit rapide\\Stockage léger",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).next_to(fast_arrow_r, RIGHT, buff=0.18)

    self.play(
        Create(fast_arrow_l),
        Create(fast_arrow_r),
        FadeIn(lbl_fast_l),
        FadeIn(lbl_fast_r),
        run_time=1.0,
    )

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
