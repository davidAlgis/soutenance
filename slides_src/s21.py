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


@slide(21)
def slide_21(self):
    # --- Top bar ---
    bar = self._top_bar("SPH pas à pas")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Intro line ---
    self.start_body()
    intro = Tex(
        r"SPH est une méthode qui simule le fluide comme des particules :",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    intro.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (-config.frame_width / 2 + 0.6 + self.DEFAULT_PAD) - intro.get_left()[
        0
    ]
    intro.shift(RIGHT * dx)
    self.play(FadeIn(intro, run_time=0.3))
    self.next_slide()
    # --- SPH animation (fluids only) with ROI crop ---

    # --- Define what to draw after SPH dots appear (before playback) ---
    def annotate_g_and_mi(scene, dots_group: VGroup):
        # 1) Show m_i at top-left (under the intro line), bigger font
        left_margin = (
            -config.frame_width / 2 + 0.9
        )  # same feel as your text padding
        right_margin = (
            config.frame_width / 2 - 0.9
        )  # same feel as your text padding
        top_y = (
            self._body_last.get_top()[1]
            if hasattr(self, "_body_last") and self._body_last
            else (self._current_bar.get_bottom()[1] - self.BODY_TOP_BUFF)
        )
        mi = Tex(r"$m_i$", color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
        mi.move_to(np.array([right_margin - 2.0, top_y - 2.0, 0.0]))
        scene.play(FadeIn(mi, run_time=0.25))
        scene.add_foreground_mobject(mi)

        # Wait for user input before drawing g and the arrow
        scene.next_slide()

        # 2) Draw a vertical arrow pointing down in oxfordBlue, below m_i
        arrow_len = 1.8
        start = np.array([left_margin + 1.5, top_y - 1.0, 0.0])
        end = start + np.array([0.0, -arrow_len, 0.0])
        grav_arrow = Arrow(
            start, end, buff=0.0, stroke_width=6, color=pc.oxfordBlue
        )

        # Label: \vec{g} (g with arrow above) in oxfordBlue, to the right of the arrow mid
        g_label = Tex(
            r"$\vec{g}$",
            color=pc.oxfordBlue,
            font_size=self.BODY_FONT_SIZE + 10,
        )
        mid = 0.5 * (start + end)
        g_label.move_to(mid + RIGHT * 0.6)

        scene.play(
            FadeIn(grav_arrow, run_time=0.25), FadeIn(g_label, run_time=0.25)
        )
        scene.add_foreground_mobject(grav_arrow)
        scene.add_foreground_mobject(g_label)

    show_sph_simulation(
        self,
        "states_sph/sph_gravity.csv",
        only_fluid=True,
        dot_radius=0.08,
        manim_seconds=3.0,
        roi_origin=(-1.5, -3.0),
        roi_size=(3.0, 5.0),
        clip_outside=True,
        fit_roi_to_height=None,
        fit_roi_to_width=11.0,
        target_center=(0.0, -1.0),
        cover=False,
        grow_time=1.0,
        grow_lag=0.0,
        on_after_init=annotate_g_and_mi,
    )

    self.pause()
    self.clear()
    self.next_slide()
