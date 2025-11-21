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
    Action du solide sur le fluide.
    Texte d'intro, EDP 2D (equation* + cases), schéma DF,
    puis variante amortie avec d^n. Mise en page ancrée à gauche,
    espacements renforcés et largeur des équations limitée pour éviter
    tout chevauchement.
    """
    # --- Barre de titre -------------------------------------------------------
    bar, footer = self._top_bar("Action du solide sur le fluide")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Zone utile -----------------------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    anchor_x = x_left + self.DEFAULT_PAD  # ancre gauche stable

    # Utilitaires --------------------------------------------------------------
    def _lock_left_y(mob: Mobject, y_value: float) -> Mobject:
        dx = anchor_x - mob.get_left()[0]
        mob.shift(RIGHT * dx)
        mob.set_y(y_value)
        return mob

    def _shrink_to_width_if_needed(mob: Mobject, max_w: float) -> None:
        # Ne réduit que si l'objet dépasse la largeur cible
        if mob.width > max_w:
            mob.scale_to_fit_width(max_w)

    # --- Corps de texte (Tex) -------------------------------------------------
    self.start_body()

    line1 = Tex(
        "L'action du solide sur le fluide est approximée comme une simple « onde ».",
        tex_template=self.french_template,
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    line1_y = y_top - 0.42
    _lock_left_y(line1, line1_y)

    line2 = Tex(
        "Résolution de l'équation d'onde 2D avec la méthode des différences finies :",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    line2.next_to(line1, DOWN, buff=0.22, aligned_edge=LEFT)
    _lock_left_y(line2, line2.get_y())
    # --- EDP 2D (equation* + cases) ------------------------------------------
    eq_pde = Tex(
        r"""
            \begin{equation*}
            \begin{cases}
                \Delta h(\mathbf{x},t)-\dfrac{1}{c^{2}}\dfrac{\partial^{2} h(\mathbf{x},t)}{\partial t^{2}}=0
                \quad \text{for} \quad \mathbf{x}\in Z\\[6pt]
                h(\mathbf{x},t)=0 \quad \text{for} \quad \mathbf{x}\in\partial Z
            \end{cases}
            \end{equation*}
            """,
        font_size=self.BODY_FONT_SIZE + 4,
        color=BLACK,
    )
    eq_pde.next_to(line2, DOWN, buff=0.32, aligned_edge=LEFT)
    _lock_left_y(eq_pde, eq_pde.get_y())
    _shrink_to_width_if_needed(eq_pde, area_w * 0.90)

    line3 = Tex(
        r"Où $Z$ est un domaine carré centré autour du solide.",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    line3.next_to(eq_pde, DOWN, buff=0.26, aligned_edge=LEFT)
    _lock_left_y(line3, line3.get_y())

    self.play(
        FadeIn(line1, line2, eq_pde, line3, shift=RIGHT * self.SHIFT_SCALE),
        run_time=0.5,
    )
    self.wait(0.1)
    self.next_slide()

    # --- Transition : Nettoyage et Remontée de la ligne 2 ---
    to_remove = VGroup(line1, eq_pde, line3)

    # Calcul de la position cible pour line2 (remplace line1)
    # On garde la position X actuelle de line2, on change juste Y pour celui de line1
    target_pos = line2.get_center()
    target_pos[1] = line1.get_y()

    self.play(
        FadeOut(to_remove, shift=LEFT),
        line2.animate.move_to(target_pos),
        run_time=0.8,
    )

    # TODO

    # Fin de la slide ----------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
