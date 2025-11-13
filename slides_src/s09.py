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


@slide(9)
def slide_09(self):
    """
    Present three major ocean-simulation approaches with centered labels.
    Each ellipse appears after user input. Layout: one centered on top,
    two at the bottom (left and right).
    """
    # --- Top bar ---------------------------------------------------------
    bar = self._top_bar(
        "Trois méthodes de l'état de l'art pour la simulation d'océan"
    )
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Ellipse geometry (closer to circles) ----------------------------
    ell_w = 3.6
    ell_h = 2.8

    # --- First ellipse: ocean surface simulation (higher) ----------------
    e1 = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
    t1 = Paragraph(
        "Simulation de",
        "surface de l'océan",
        alignment="center",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
        line_spacing=0.6,
    )
    t1.move_to(e1.get_center())
    g1 = VGroup(e1, t1)
    g1.move_to([0.0, 1.3, 0.0])

    self.play(Create(e1, run_time=0.6))
    self.play(FadeIn(t1, run_time=0.2))
    self.wait(0.1)
    self.next_slide()

    # --- Second ellipse: fluid -> solid ----------------------------------
    e2 = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
    t2 = Paragraph(
        "Action du fluide",
        "sur le solide",
        alignment="center",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
        line_spacing=0.6,
    )
    t2.move_to(e2.get_center())
    g2 = VGroup(e2, t2)
    g2.move_to([-3.6, -1.7, 0.0])

    self.play(Create(e2, run_time=0.6))
    self.play(FadeIn(t2, run_time=0.2))
    self.wait(0.1)
    self.next_slide()

    # --- Third ellipse: solid -> fluid -----------------------------------
    e3 = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
    t3 = Paragraph(
        "Action du solide",
        "sur le fluide",
        alignment="center",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
        line_spacing=0.6,
    )
    t3.move_to(e3.get_center())
    g3 = VGroup(e3, t3)
    g3.move_to([3.6, -1.7, 0.0])

    self.play(Create(e3, run_time=0.6))
    self.play(FadeIn(t3, run_time=0.2))
    self.wait(0.1)

    # --- End slide --------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
