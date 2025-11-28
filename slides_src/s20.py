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


@slide(20)
def slide_20(self):
    """
    Slide 20: Principe de l'hybridation
    - Phase 1: State of the art (Text + Bullets + Image)
    - Phase 2: Tessendorf Domain (BlueGreen Rect)
    - Phase 3: SPH Domains (JellyBean Squares around boats)
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Principe de l'hybridation")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Layout Calculations -----------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    # Text alignment
    text_anchor_x = x_left + 0.2

    # =======================================================================
    # PHASE 1: État de l'art (Intro)
    # =======================================================================

    # 1. Title
    title = Tex(
        "État de l'art de l'hybridation :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    title.next_to(bar_rect, DOWN, buff=0.4, aligned_edge=LEFT)
    dx = text_anchor_x - title.get_left()[0]
    title.shift(RIGHT * dx)

    # 2. Bullets
    bullet_items = [
        "Kassiotis \\textit{et al.}, \\textit{SPHERIC}, 2011",
        "Chentanez \\textit{et al.}, \\textit{IEEE TVCG}, 2015",
        "Schreck et Wojtan, \\textit{Computer Graphics Forum}, 2022",
    ]
    bullets = make_bullet_list(
        bullet_items,
        bullet_color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
        line_gap=0.18,
        left_pad=0.22,
    )
    bullets.next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)
    bullets.shift(RIGHT * 0.2)  # Indent slightly relative to title

    # Image alignment (Right side)
    img_center = np.array([0.0, (y_top + y_bottom) / 2 - 1.5, 0])

    # 3. Image
    img_path = "Figures/chentanez_hybrid.jpeg"
    if os.path.exists(img_path):
        img = ImageMobject(img_path)
        img.move_to(img_center)
    else:
        img = VMobject()

    # Animation: Text fades in from Right (shift=RIGHT), Image from Left (shift=LEFT)
    self.play(
        FadeIn(title, shift=RIGHT * self.SHIFT_SCALE),
        FadeIn(bullets, shift=RIGHT * self.SHIFT_SCALE),
        FadeIn(img, shift=UP * self.SHIFT_SCALE),
    )

    self.next_slide()

    # Fade Out: Image to Right, Text to Left
    self.play(
        FadeOut(img, shift=DOWN * self.SHIFT_SCALE),
        FadeOut(bullets, shift=LEFT * self.SHIFT_SCALE),
        FadeOut(title, shift=LEFT * self.SHIFT_SCALE),
        run_time=0.5,
    )
    # --- Usable area below the bar ----------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom
    anchor_x = x_left + self.DEFAULT_PAD

    # 2. Bullets
    bullet_items_2 = [
        "Méthode de Tessendorf pour les grandes étendues",
        r"Méthode \textit{smoothed particles hydrodynamics} (SPH) pour couplage avec solides",
    ]
    bullets_2 = make_bullet_list(
        bullet_items_2,
        bullet_color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
        line_gap=0.18,
        left_pad=0.22,
    )
    bullets_2.next_to(bar_rect, DOWN, buff=0.4, aligned_edge=LEFT)

    bullets_2.shift(RIGHT * dx)  # Indent slightly relative to title

    # l1 = Tex(
    #     r"\mbox{Méthode de Tessendorf pour les grandes étendues, méthode \textit{smoothed}}",
    #     color=BLACK,
    #     font_size=self.BODY_FONT_SIZE,
    # )
    # l1.next_to(
    #     self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    # )
    # l1.shift(RIGHT * (anchor_x - l1.get_left()[0]))

    # l2 = Tex(
    #     r"\textit{particles hydrodynamics} (SPH) pour couplage avec les solides",
    #     color=BLACK,
    #     font_size=self.BODY_FONT_SIZE,
    # )
    # l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    # l2.shift(RIGHT * (anchor_x - l2.get_left()[0]))

    self.play(FadeIn(bullets_2, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25)

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Big blueGreen rectangle (most of remaining space) -----------------
    content_top_y = bullets_2.get_bottom()[1] - 0.35
    content_bottom_y = y_bottom + 0.2
    rect_h = max(2.0, content_top_y - content_bottom_y)
    rect_w = area_w * 0.96
    rect_margin_x = area_w * 0.02

    ocean_rect = Rectangle(
        width=rect_w,
        height=rect_h,
        stroke_color=pc.blueGreen,
        stroke_width=6,
        fill_opacity=0.0,
    )
    rect_center = np.array(
        [
            (x_left + x_right) * 0.5,
            (content_top_y + content_bottom_y) * 0.5,
            0.0,
        ]
    )
    ocean_rect.move_to(rect_center)

    # Label inside rectangle (top-left, with small padding)
    pad_x = 0.25
    pad_y = 0.20
    ocean_label = Tex(
        r"Oc\'ean - M\'ethode de Tessendorf",
        color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
    )
    # Place near top-left inside the rectangle
    tl = ocean_rect.get_corner(UL)
    ocean_label.move_to(
        [
            tl[0] + pad_x + ocean_label.width * 0.5,
            tl[1] - pad_y - ocean_label.height * 0.5,
            0.0,
        ]
    )
    self.play(Create(ocean_rect), FadeIn(ocean_label), run_time=0.5)

    # --- Boats (very small, top view) --------------------------------------
    boat_coords = [
        [0.0, -1.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 4.0, 0.0],
        [0.0, 5.0, 0.0],
        [-1.0, 4.0, 0.0],
        [-1.0, 0.0, 0.0],
    ]

    def make_boat(scale_factor: float = 0.20) -> Polygon:
        pts = [np.array(p) for p in boat_coords]
        poly = Polygon(*pts, color=pc.uclaGold, stroke_width=4)
        poly.set_fill(pc.uclaGold, opacity=1.0)
        poly.scale(scale_factor)
        return poly

    # Compute inner placement bounds with a gap
    gap_x = max(0.5, rect_w * 0.05)
    gap_y = max(0.4, rect_h * 0.06)
    inner_left = ocean_rect.get_left()[0] + gap_x
    inner_right = ocean_rect.get_right()[0] - gap_x
    inner_top = ocean_rect.get_top()[1] - gap_y
    inner_bottom = ocean_rect.get_bottom()[1] + gap_y

    # Target positions: left and right halves
    left_center = np.array(
        [
            (inner_left + (inner_left + inner_right) * 0.5) * 0.5,
            (inner_top + inner_bottom) * 0.5,
            0.0,
        ]
    )
    right_center = np.array(
        [
            (inner_right + (inner_left + inner_right) * 0.5) * 0.5,
            (inner_top + inner_bottom) * 0.5,
            0.0,
        ]
    )

    boat1 = make_boat()
    boat2 = make_boat()
    boat1.move_to(left_center + np.array([-0.2, 0.1, 0.0]))
    boat2.move_to(right_center + np.array([0.2, -0.1, 0.0]))

    self.play(FadeIn(boat1, boat2), run_time=0.5)

    # --- SPH squares around each boat + "SPH" labels -----------------------
    def surround_with_sph(mob: Mobject):
        # Padding around boat
        pad = 0.6
        w = mob.width + 2 * pad
        h = mob.height + 2 * pad
        side = max(w, h)  # make it square
        sq = Rectangle(
            width=side, height=side, stroke_color=pc.jellyBean, stroke_width=6
        )
        sq.move_to(mob.get_center())

        # "SPH" label inside square, top-left with a small inner offset
        lbl = Tex("SPH", color=pc.jellyBean, font_size=self.BODY_FONT_SIZE)
        tl = sq.get_corner(UL)
        lbl.move_to(
            [
                tl[0] + 0.18 + lbl.width * 0.5,
                tl[1] - 0.14 - lbl.height * 0.5,
                0.0,
            ]
        )

        return sq, lbl

    sph1_sq, sph1_lbl = surround_with_sph(boat1)
    sph2_sq, sph2_lbl = surround_with_sph(boat2)

    self.play(
        Create(sph1_sq),
        Create(sph2_sq),
        FadeIn(sph1_lbl, sph2_lbl),
        run_time=1.0,
    )

    # --- End slide
    # ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
