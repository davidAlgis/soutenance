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
    bar = self._top_bar("InteropUnityCUDA (IUC)")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---- Usable area below the bar ----
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    area_w = x_right - x_left
    area_h = y_top - y_bottom
    y_center = (y_top + y_bottom) * 0.5

    # ---- Intro texts (fit to bounds, then place) ----
    self.start_body()
    self.add_body_text(
        r"\mbox{Afin d'utiliser CUDA dans Unity à la place des compute shaders : InteropUnityCUDA}",
        font_size=self.BODY_FONT_SIZE,
    )
    self.add_body_text(
        "Un outil d'interopérabilité entre Unity et CUDA.",
        font_size=self.BODY_FONT_SIZE,
    )

    self.wait(0.1)
    self.next_slide()

    # ========= Bottom-right credit =========
    credit = Tex(
        r"Algis \textit{et al.} (2025), \textit{InteropUnityCUDA}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE - 6,
    )
    credit.to_edge(DOWN, buff=0.5)
    credit.to_edge(RIGHT, buff=0.5)

    dot = Dot(color=pc.blueGreen)
    dot.next_to(credit, LEFT, buff=0.3)
    self.play(FadeIn(credit), run_time=0.5)
    self.play(Flash(dot, color=pc.blueGreen), run_time=2.0)

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
    self.add(box_unity)

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
    self.play(FadeIn(ic_group, run_time=0.4))

    # ========= STEP 1 → 2 =========
    self.next_slide()

    arrow_1 = Arrow(
        start=box_unity[0].get_right(),
        end=box_iuc[0].get_left(),
        buff=0.08,
        stroke_color=pc.blueGreen,
        stroke_width=6,
        tip_length=0.16,
    )
    self.play(FadeIn(box_iuc, run_time=0.3), Create(arrow_1, run_time=0.6))

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

    arrow_2 = Arrow(
        start=box_iuc[0].get_right(),
        end=box_cpp[0].get_left(),
        buff=0.08,
        stroke_color=pc.blueGreen,
        stroke_width=6,
        tip_length=0.16,
    )
    self.play(FadeIn(box_cpp, run_time=0.3), Create(arrow_2, run_time=0.6))

    target_img_center_3 = img_center_under(box_cpp)
    shift_vec_3 = target_img_center_3 - img.get_center()
    self.play(ic_group.animate.shift(shift_vec_3), run_time=0.6)

    new_cap_3 = Text(
        "écriture dans cuda", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    new_cap_3.move_to(cap)
    self.play(Transform(cap, new_cap_3), run_time=0.35)

    # End slide
    self.pause()
    self.clear()
    self.next_slide()
