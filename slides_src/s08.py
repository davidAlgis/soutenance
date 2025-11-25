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


@slide(8)
def slide_08(self):
    # --- Top bar ---
    bar, footer = self._top_bar("InteropUnityCUDA")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---- Usable area below the bar ----
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    anchor_x = x_left + self.DEFAULT_PAD

    area_w = x_right - x_left
    area_h = y_top - y_bottom
    y_center = (y_top + y_bottom) * 0.5

    line1 = Tex(
        r"\mbox{Utiliser CUDA dans Unity à la place des \textit{compute shaders} : InteropUnityCUDA}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1.next_to(self._current_bar, DOWN, aligned_edge=LEFT)
    dx = anchor_x - line1.get_left()[0]
    line1.shift(RIGHT * dx)

    line2 = Tex(
        r"Un outil d'interopérabilité entre Unity et CUDA.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line2.next_to(line1, DOWN, aligned_edge=LEFT)
    dx2 = anchor_x - line2.get_left()[0]
    line2.shift(RIGHT * dx2)
    self.play(FadeIn(line1, line2, shift=RIGHT * self.SHIFT_SCALE))

    self.wait(0.1)
    self.next_slide()

    # ========= Three boxes: Unity (left), IUC (center), C++ lib (right) =========
    gap = area_w * 0.06
    cell_w = (area_w - 2 * gap) / 3.0
    cell_h = min(1.6, area_h * 0.28)

    cx_left = x_left + cell_w * 0.5
    cx_center = x_left + cell_w * 1.5 + gap
    cx_right = x_left + cell_w * 2.5 + 2 * gap
    cy = y_center + 0.25  # leave room below for image/captions

    def box(label, center_x):
        r = Rectangle(
            width=cell_w,
            height=cell_h,
            stroke_color=pc.blueGreen,
            stroke_width=6,
        ).move_to([center_x, cy, 0])
        txt = Text(
            label, color=BLACK, font_size=self.BODY_FONT_SIZE, weight=BOLD
        ).move_to(r.get_center())
        return VGroup(r, txt)

    box_unity = box("Unity", cx_left)
    box_iuc = box("IUC", cx_center)
    box_cpp = box("Librairie C++", cx_right)

    # Show only UNITY box initially
    self.play(Create(box_unity), run_time=1.0)

    # ========= Image + caption (initial state) =========
    img = ImageMobject("Figures/logo_images.png")
    img.set_height(min(cell_h * 0.75, 1.6))

    def img_center_under(box_group):
        box_rect = box_group[0]
        return np.array(
            [
                box_rect.get_center()[0],
                box_rect.get_bottom()[1] - img.height * 0.55 - 0.25,
                0.0,
            ]
        )

    # Initial placement (Unity)
    img.move_to(img_center_under(box_unity))

    cap = Text("texture.unity", color=BLACK, font_size=self.BODY_FONT_SIZE)
    cap.next_to(img, DOWN, buff=0.15)

    # Move image + caption together as a single unit
    ic_group = Group(img, cap)
    self.play(FadeIn(ic_group, shift=UP * self.SHIFT_SCALE, run_time=0.4))

    # ========= STEP 1 → 2 =========
    self.next_slide()

    arrow_1 = DoubleArrow(
        start=box_unity[0].get_right(),
        end=box_iuc[0].get_left(),
        buff=0.08,
        stroke_color=pc.blueGreen,
        stroke_width=6,
        tip_length=0.16,
    )
    self.play(Create(box_iuc, run_time=0.3), Create(arrow_1, run_time=0.6))

    target_img_center_2 = img_center_under(box_iuc)
    shift_vec_2 = target_img_center_2 - img.get_center()
    self.play(ic_group.animate.shift(shift_vec_2), run_time=0.6)

    new_cap_2 = Text(
        "conversion en texture.cuda",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    new_cap_2.move_to(cap)  # keep position; only glyphs change
    self.play(Transform(cap, new_cap_2), run_time=0.35)

    # ========= STEP 2 → 3 =========
    self.next_slide()

    arrow_2 = DoubleArrow(
        start=box_iuc[0].get_right(),
        end=box_cpp[0].get_left(),
        buff=0.08,
        stroke_color=pc.blueGreen,
        stroke_width=6,
        tip_length=0.16,
    )
    self.play(Create(box_cpp, run_time=0.3), Create(arrow_2, run_time=0.6))

    target_img_center_3 = img_center_under(box_cpp)
    shift_vec_3 = target_img_center_3 - img.get_center()
    self.play(ic_group.animate.shift(shift_vec_3), run_time=0.6)

    new_cap_3 = Text(
        "calcul dans cuda", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    new_cap_3.move_to(cap)
    self.play(Transform(cap, new_cap_3), run_time=0.35)
    self.wait(2.0)

    self.add_credit(r"Algis \textit{et al.}, \textit{SPE}, 2025")
    # End slide
    self.pause()
    self.clear()
    self.next_slide()
