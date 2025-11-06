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

@slide(12)
def slide_12(self):
        """
        Slide 12: Ocean spectra.
        - Top bar "Spectres d'océans"
        - Intro sentence with inline LaTeX
        - Two bullet points mixing text and LaTeX
        - Then a central "bow-tie" shape
        - Then LaTeX labels on the left (U_10, F, theta)
        - Then an animation where labels move into the shape and disappear,
          while A_i appears on the right and slides a bit to the right.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Spectres d'océans")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area below bar --------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        numberplane = NumberPlane(color=BLACK)
        self.add(numberplane)
        # Left anchor to align body content with the bar
        anchor_x = x_left + self.DEFAULT_PAD

        # --- Intro sentence (Tex = text + math) -------------------------------
        self.start_body()
        intro = Tex(
            r"Comment calculer les $k_i$ et $A_i$ ?",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        intro.next_to(
            self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
        )
        dx = anchor_x - intro.get_left()[0]
        intro.shift(RIGHT * dx)
        self.add(intro)

        # --- Bullet points with LaTeX symbols --------------------------------
        # Helper to place a bullet row (dot + [math + text])
        def bullet_row(math_tex: str, tail_text: str) -> VGroup:
            dot = Dot(radius=0.05, color=pc.blueGreen)
            head = MathTex(
                math_tex, color=BLACK, font_size=self.BODY_FONT_SIZE
            )
            tail = Text(tail_text, color=BLACK, font_size=self.BODY_FONT_SIZE)
            line = VGroup(head, tail).arrange(
                RIGHT, buff=0.18, aligned_edge=DOWN
            )
            row = VGroup(dot, line).arrange(
                RIGHT, buff=0.25, aligned_edge=DOWN
            )
            return row

        b1 = bullet_row(r"k_i", "est echantillonné sur un intervalle")
        b2 = bullet_row(r"A_i", "est défini par un spectre d'océan")

        # Stack bullets under the intro, left-aligned to the same anchor
        bullets = VGroup(b1, b2).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        bullets.next_to(intro, DOWN, buff=0.28, aligned_edge=LEFT)
        dx_b = anchor_x - bullets.get_left()[0]
        bullets.shift(RIGHT * dx_b)
        self.add(bullets)

        # Wait for user
        self.next_slide()

        # --- Central "bow-tie" shape -----------------------------------------
        # Coordinates chosen to resemble the provided figure.
        left_tri = Polygon(
            [-2.0, -4, 0.0],
            [-1.0, -3.5, 0.0],
            [1.0, -3.5, 0.0],
            [2.0, -4, 0.0],
            [2.0, -2, 0.0],
            [1.0, -2.5, 0.0],
            [-1.0, -2.5, 0.0],
            [-2.0, -2, 0.0],
            fill_color=pc.blueGreen,
            fill_opacity=0.95,
            stroke_opacity=0.0,
        )
        shape = VGroup(left_tri)
        # Center the shape roughly in the middle of the free area
        cy = (y_top + y_bottom) * 0.5
        shape.move_to([0.0, cy, 0.0])
        self.play(FadeIn(shape, run_time=0.5))

        # Wait for user
        self.next_slide()

        # --- Labels on the left: U_10, F, theta --------------------------------
        left_x = shape.get_left()[0] - 1.0
        y_span = shape.height
        y_top_lbl = cy + y_span * 0.30
        y_mid_lbl = cy + y_span * 0.00
        y_bot_lbl = cy - y_span * 0.30

        lbl_u10 = MathTex(
            r"U_{10}", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
        )
        lbl_f = MathTex(r"F", color=BLACK, font_size=self.BODY_FONT_SIZE + 6)
        lbl_th = MathTex(
            r"\theta", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
        )

        lbl_u10.move_to([left_x, y_mid_lbl, 0.0])
        lbl_f.move_to([left_x, y_top_lbl, 0.0])
        lbl_th.move_to([left_x, y_bot_lbl, 0.0])

        labels_left = VGroup(lbl_f, lbl_u10, lbl_th)
        self.play(FadeIn(labels_left, run_time=0.4))

        # Wait for user
        self.next_slide()

        # --- Flow into the shape, disappear, and show A_i on the right ----------
        # Target just inside the left edge of the bow-tie.
        target_x_inside = (
            left_tri.get_vertices()[0][0] - 0.4
        )  # near the center tip
        flow_targets = [
            np.array([target_x_inside, y_top_lbl, 0.0]),
            np.array([target_x_inside, y_mid_lbl, 0.0]),
            np.array([target_x_inside, y_bot_lbl, 0.0]),
        ]

        self.play(
            lbl_f.animate.move_to(flow_targets[0]),
            lbl_u10.animate.move_to(flow_targets[1]),
            lbl_th.animate.move_to(flow_targets[2]),
            run_time=0.8,
        )
        # Disappear as if absorbed by the shape
        self.play(FadeOut(labels_left, run_time=0.35))

        # A_i appears on the right and slides slightly to the right
        ai_x = shape.get_right()[0] + 0.4
        ai = MathTex(r"A_i", color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
        ai.move_to([ai_x, cy, 0.0])
        self.play(FadeIn(ai, run_time=0.3))
        self.play(ai.animate.shift(RIGHT * 1.0), run_time=0.4)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()
