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
    bar, footer = self._top_bar(
        "Trois méthodes de l'état de l'art pour la simulation d'océan"
    )
    self.add(bar)
    self.add_foreground_mobject(bar)
    # --- Ellipses (same spirit as slide 9) --------------------------------
    ell_w = 3.6
    ell_h = 2.8

    e_surface = Ellipse(
        width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
    )
    t_surface = Tex(
        "Simulation de surface", font_size=self.BODY_FONT_SIZE, color=BLACK
    )
    t_surface.move_to(e_surface.get_center())
    g_surface = VGroup(e_surface, t_surface).move_to([0.0, 1.3, 0.0])

    e_f2s = Ellipse(
        width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
    )
    t_f2s = Tex(
        "Solide vers fluide", font_size=self.BODY_FONT_SIZE, color=BLACK
    )
    t_f2s.move_to(e_f2s.get_center())
    g_f2s = VGroup(e_f2s, t_f2s).move_to([3.6, -1.7, 0.0])

    e_s2f = Ellipse(
        width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
    )
    t_s2f = Tex(
        "Fluide vers solide", font_size=self.BODY_FONT_SIZE, color=BLACK
    )
    t_s2f.move_to(e_s2f.get_center())
    g_s2f = VGroup(e_s2f, t_s2f).move_to([-3.6, -1.7, 0.0])

    self.play(Create(e_surface), FadeIn(t_surface), run_time=0.4)
    self.play(Create(e_f2s), FadeIn(t_f2s), run_time=0.4)
    self.play(Create(e_s2f), FadeIn(t_s2f), run_time=0.4)

    # --- Arrow builders ----------------------------------------------------
    def _solid_curved_question(
        start_pt: np.ndarray, end_pt: np.ndarray, angle: float
    ) -> VGroup:
        """
        Solid curved line between two points with a '?' at the center.
        Includes a white background behind the '?' to mask the line.
        """
        # 1. Create the curved line (Arc)
        arc = ArcBetweenPoints(
            start=start_pt,
            end=end_pt,
            angle=angle,
            color=BLACK,
            stroke_width=6,
        )

        # 2. Create the question mark
        # Using Text for a standard font, or use MathTex("?") for LaTeX font
        label = Text("?", font_size=24, color=BLACK, weight=BOLD)

        # 3. Position the label exactly at the center of the arc path
        label.move_to(arc.point_from_proportion(0.5))

        # 4. Create a small background to hide the line behind the text
        # This assumes your slide background is WHITE.
        bg = BackgroundRectangle(
            label, color=WHITE, fill_opacity=1.0, buff=0.05
        )

        # 5. Return a Group (Order matters: Arc -> Background -> Label)
        return VGroup(arc, bg, label)

    def _right_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
        p = m.get_right().copy()
        p[0] += dx
        p[1] += dy
        return p

    def _left_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
        p = m.get_left().copy()
        p[0] += dx
        p[1] += dy
        return p

    def _top_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
        p = m.get_top().copy()
        p[0] += dx
        p[1] += dy
        return p

    # ================= SOLID arrows =================
    # (1) Surface -> F->S (unchanged, correct)
    a1 = _solid_curved_question(
        end_pt=_top_of(e_s2f, dx=0.10, dy=0.10),
        start_pt=_left_of(e_surface, dx=-0.10, dy=-0.10),
        angle=1.0,
    )

    # (2) F->S -> S->F : origin ok, now end on RIGHT side of S->F
    a2 = _solid_curved_question(
        start_pt=_right_of(e_s2f, dx=0.0, dy=-0.6),  # moved to right side
        end_pt=_left_of(e_f2s, dx=-0.0, dy=-0.6),
        angle=1.0,  # under-arc clockwise
    )

    # (3) S->F -> Surface (unchanged, correct)
    a3 = _solid_curved_question(
        start_pt=_top_of(e_f2s, dx=-0.10, dy=0.10),
        end_pt=_right_of(e_surface, dx=0.10, dy=-0.10),
        angle=1.0,
    )
    self.play(Create(a1), Create(a2), Create(a3), run_time=0.6)

    # --- End slide --------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
