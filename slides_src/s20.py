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

@slide(20)
def slide_20(self):
        """
        Slide 20: Principe de l'hybridation
        - Top bar + 3 body lines (Tex).
        - Wait for user.
        - Draw a pc.blueGreen rectangle filling most of remaining space.
        - Title inside rectangle (top-left): "Océan - Méthode de Tessendorf" in pc.blueGreen.
        - Two very small top-view boats (given polygon coords), placed apart with border gap.
        - Wait for user.
        - Draw two pc.uclaGold squares around each boat and add "SPH" label in their top-left.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Principe de l'hybridation")
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

        # --- Body text (Tex) ---------------------------------------------------
        self.start_body()
        l1 = Tex(
            r"On conserve la m\'ethode de Tessendorf pour les grandes \'etendues et pour la couplage avec les solides",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        l1.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        l1.shift(RIGHT * (anchor_x - l1.get_left()[0]))

        l2 = Tex(
            r"et pour la couplage avec les solides on utilise la m\'ethode ",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        l2.shift(RIGHT * (anchor_x - l2.get_left()[0]))

        l3 = Tex(
            r"\textit{smoothed particles hydrodynamics} (SPH)",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        l3.next_to(l2, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        l3.shift(RIGHT * (anchor_x - l3.get_left()[0]))

        self.add(l1, l2, l3)

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- Big blueGreen rectangle (most of remaining space) -----------------
        content_top_y = l3.get_bottom()[1] - 0.35
        content_bottom_y = y_bottom + 0.2
        rect_h = max(2.0, content_top_y - content_bottom_y)
        rect_w = area_w * 0.96
        rect_margin_x = area_w * 0.02

        ocean_rect = Rectangle(
            width=rect_w, height=rect_h,
            stroke_color=pc.blueGreen, stroke_width=6,
            fill_opacity=0.0
        )
        rect_center = np.array([ (x_left + x_right) * 0.5, (content_top_y + content_bottom_y) * 0.5, 0.0 ])
        ocean_rect.move_to(rect_center)
        self.add(ocean_rect)

        # Label inside rectangle (top-left, with small padding)
        pad_x = 0.25
        pad_y = 0.20
        ocean_label = Tex(
            r"Oc\'ean - M\'ethode de Tessendorf",
            color=pc.blueGreen, font_size=self.BODY_FONT_SIZE
        )
        # Place near top-left inside the rectangle
        tl = ocean_rect.get_corner(UL)
        ocean_label.move_to([tl[0] + pad_x + ocean_label.width * 0.5, tl[1] - pad_y - ocean_label.height * 0.5, 0.0])
        self.add(ocean_label)

        # --- Boats (very small, top view) --------------------------------------
        boat_coords = [
            [ 0.0, -1.0, 0.0],
            [ 1.0,  0.0, 0.0],
            [ 1.0,  4.0, 0.0],
            [ 0.0,  5.0, 0.0],
            [-1.0,  4.0, 0.0],
            [-1.0,  0.0, 0.0],
        ]

        def make_boat(scale_factor: float = 0.20) -> Polygon:
            pts = [np.array(p) for p in boat_coords]
            poly = Polygon(*pts, color=pc.oxfordBlue, stroke_width=4)
            poly.set_fill(pc.oxfordBlue, opacity=1.0)
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
        left_center = np.array([ (inner_left + (inner_left + inner_right) * 0.5) * 0.5, (inner_top + inner_bottom) * 0.5, 0.0 ])
        right_center = np.array([ (inner_right + (inner_left + inner_right) * 0.5) * 0.5, (inner_top + inner_bottom) * 0.5, 0.0 ])

        boat1 = make_boat()
        boat2 = make_boat()
        boat1.move_to(left_center + np.array([-0.2, 0.1, 0.0]))
        boat2.move_to(right_center + np.array([0.2, -0.1, 0.0]))

        self.add(boat1, boat2)

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- SPH squares around each boat + "SPH" labels -----------------------
        def surround_with_sph(mob: Mobject) -> Group:
            # Padding around boat
            pad = 0.6
            w = mob.width + 2 * pad
            h = mob.height + 2 * pad
            side = max(w, h)  # make it square
            sq = Rectangle(width=side, height=side, stroke_color=pc.uclaGold, stroke_width=6)
            sq.move_to(mob.get_center())

            # "SPH" label inside square, top-left with a small inner offset
            lbl = Tex("SPH", color=pc.uclaGold, font_size=self.BODY_FONT_SIZE)
            tl = sq.get_corner(UL)
            lbl.move_to([tl[0] + 0.18 + lbl.width * 0.5, tl[1] - 0.14 - lbl.height * 0.5, 0.0])

            return Group(sq, lbl)

        sph1 = surround_with_sph(boat1)
        sph2 = surround_with_sph(boat2)

        self.play(FadeIn(sph1, run_time=0.3), FadeIn(sph2, run_time=0.3))

        # --- End slide
        # ---------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()
