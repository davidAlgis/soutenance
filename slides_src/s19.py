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

@slide(19)
def slide_19(self):
        """
        Slide 19: Result of combining the three methods.
        Implements solid and dotted curved arrows with corrected placement:
        (1) Surface -> Fluide-vers-solide (ok),
        (2) Fluide-vers-solide -> Solide-vers-fluide now ends on RIGHT side of S->F,
        (3) Solide-vers-fluide -> Surface (ok),
        (4) DOTTED S->F -> F->S now inner and higher,
        (5) DOTTED S->F -> Surface inner and shifted to the right,
        (6) DOTTED F->S -> Surface inner and shifted to the left.
        Then: summary table, demo image, and final bullets.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Résultat de la combinaison des trois méthodes")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Ellipses (same spirit as slide 9) --------------------------------
        ell_w = 3.6
        ell_h = 2.8

        e_surface = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
        t_surface = Tex("Simulation de surface", font_size=self.BODY_FONT_SIZE, color=BLACK)
        t_surface.move_to(e_surface.get_center())
        g_surface = VGroup(e_surface, t_surface).move_to([0.0, 1.3, 0.0])

        e_f2s = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
        t_f2s = Tex("Fluide vers solide", font_size=self.BODY_FONT_SIZE, color=BLACK)
        t_f2s.move_to(e_f2s.get_center())
        g_f2s = VGroup(e_f2s, t_f2s).move_to([3.6, -1.7, 0.0])

        e_s2f = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
        t_s2f = Tex("Solide vers fluide", font_size=self.BODY_FONT_SIZE, color=BLACK)
        t_s2f.move_to(e_s2f.get_center())
        g_s2f = VGroup(e_s2f, t_s2f).move_to([-3.6, -1.7, 0.0])

        self.play(FadeIn(g_surface, run_time=0.4))
        self.play(FadeIn(g_f2s, run_time=0.4))
        self.play(FadeIn(g_s2f, run_time=0.4))

        # --- Arrow builders ----------------------------------------------------
        def _solid_curved_arrow(start_pt: np.ndarray, end_pt: np.ndarray, angle: float) -> CurvedArrow:
            """
            Solid curved arrow between two points with a signed curvature angle.
            Positive angle is counter-clockwise, negative is clockwise.
            """
            return CurvedArrow(
                start_point=start_pt,
                end_point=end_pt,
                angle=angle,
                color=BLACK,
                stroke_width=6,
                tip_length=0.16,
            )

        def _dotted_curved_arrow(start_pt: np.ndarray, end_pt: np.ndarray, angle: float, num_dashes = 60, dashed_ratio=0.5) -> VGroup:
            """
            Dotted curved arrow for Manim 0.19: dashed arc + triangular tip aligned
            to the end tangent. Uses num_dashes/dashed_ratio (no dash_length).
            """
            arc = ArcBetweenPoints(start_pt, end_pt, angle=angle, color=BLACK, stroke_width=6)
            dashed = DashedVMobject(arc, num_dashes, dashed_ratio)
            pts = arc.get_points()
            p_end = pts[-1]
            p_prev = pts[-2]
            v = p_end - p_prev
            theta = np.arctan2(v[1], v[0])
            tip = Triangle().scale(0.10).set_fill(BLACK, opacity=1.0).set_stroke(opacity=0.0)
            tip.move_to(p_end).rotate(theta)
            return VGroup(dashed, tip)

        def _right_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
            p = m.get_right().copy(); p[0] += dx; p[1] += dy; return p

        def _left_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
            p = m.get_left().copy(); p[0] += dx; p[1] += dy; return p

        def _top_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
            p = m.get_top().copy(); p[0] += dx; p[1] += dy; return p

        # ================= SOLID arrows =================
        # (1) Surface -> F->S (unchanged, correct)
        self.next_slide()
        a1 = _solid_curved_arrow(
            start_pt=_right_of(e_surface, dx=0.10, dy=-0.10),
            end_pt=_top_of(e_f2s, dx=-0.10, dy=0.10),
            angle=-1.0,
        )
        self.play(Create(a1, run_time=0.6))

        # (2) F->S -> S->F : origin ok, now end on RIGHT side of S->F
        self.next_slide()
        a2 = _solid_curved_arrow(
            start_pt=_left_of(e_f2s, dx=-0.10, dy=0.05),
            end_pt=_right_of(e_s2f, dx=0.15, dy=0.05),  # moved to right side
            angle=-1.0,  # under-arc clockwise
        )
        self.play(Create(a2, run_time=0.6))

        # (3) S->F -> Surface (unchanged, correct)
        self.next_slide()
        a3 = _solid_curved_arrow(
            start_pt=_top_of(e_s2f, dx=0.10, dy=0.10),
            end_pt=_left_of(e_surface, dx=-0.10, dy=-0.10),
            angle=-1.0,
        )
        self.play(Create(a3, run_time=0.6))

        # ================= DOTTED arrows =================
        # (4) S->F -> F->S : inner arc, higher
        self.next_slide()
        d1 = _dotted_curved_arrow(
            start_pt=_right_of(e_s2f, dx=0.10, dy=0.4),      # higher start
            end_pt=_left_of(e_f2s, dx=-0.10, dy=0.4),       # higher end
            angle=-0.8,                                     # inner bulge
        )
        self.play(FadeIn(d1, run_time=0.6))

        # (5) S->F -> Surface : inner, shifted right at both ends
        self.next_slide()
        d2 = _dotted_curved_arrow(
            start_pt=_top_of(e_s2f, dx=1.4, dy=-0.35),    # more to the right
            end_pt=_left_of(e_surface, dx=0.30, dy=-1.05), # more to the right
            angle=+0.6, 
            num_dashes=20,                                    
        )
        self.play(FadeIn(d2, run_time=0.6))

        # (6) F->S -> Surface : inner, shifted left
        self.next_slide()
        d3 = _dotted_curved_arrow(
            start_pt=_top_of(e_f2s, dx=-1.30, dy=-0.3),    # more to the left
            end_pt=_right_of(e_surface, dx=-0.30, dy=-1.05), # more to the left
            angle=-0.6,  
            num_dashes=20,                                   
        )
        self.play(FadeIn(d3, run_time=0.6))

        # --- Clear all except the bar -----------------------------------------
        self.next_slide()
        to_keep = {bar}
        self.remove(*[m for m in self.mobjects if m not in to_keep])

        # --- Summary table (BLACK text, pass-through for Tex) -------------------
        def _tx(s: str) -> Tex:
            return Tex(s, color=BLACK)

        headers = [
            _tx(""),
            _tx(""),
            _tx(r"\emph{un solide}"),
            _tx(r"\emph{dix solides}"),
        ]
        body = [
            [_tx("M\\'ethode de Tessendorf"), _tx("Hauteur"), _tx("0.4"), _tx("0.4")],
            [_tx(""), _tx("Vitesse"), _tx("1.1"), _tx("1.1")],
            [_tx(""), _tx("Total"), _tx("1.5"), _tx("1.5")],
            [_tx("Fluide-vers-Solide"), _tx("G\\'eom\\'etrie"), _tx("1.1"), _tx("4.6")],
            [_tx(""), _tx("Forces"), _tx("0.4"), _tx("3.6")],
            [_tx(""), _tx("Total"), _tx("1.5"), _tx("8.2")],
            [_tx("Solide-vers-Fluide"), _tx("MDF"), _tx("0.1"), _tx("0.8")],
            [_tx(""), _tx("Masque"), _tx("0.2"), _tx("1.6")],
            [_tx(""), _tx("Total"), _tx("0.3"), _tx("2.4")],
            [_tx(r"\textbf{Total}"), _tx(""), _tx(r"\textbf{3.4 ms}"), _tx(r"\textbf{12.2 ms}")],
        ]

        tbl = Table(
            body,
            col_labels=headers,
            include_outer_lines=True,
            line_config={"stroke_width": 2},
            h_buff=0.7,
            v_buff=0.35,
            element_to_mobject=lambda x: x,   # <- crucial: keep Tex as-is
        )
        tbl.set_color(BLACK)

        for line in tbl.get_horizontal_lines() + tbl.get_vertical_lines():
            line.set_stroke(width=2)

        last_row = len(body)
        for c in range(1, 5):
            tbl.get_cell((last_row, c)).set_fill(pc.blueGreen, opacity=0.15)

        max_w = config.frame_width * 0.92
        max_h = (config.frame_height * 0.92) - bar.height
        if tbl.width > max_w:
            tbl.scale_to_fit_width(max_w)
        if tbl.height > max_h:
            tbl.scale_to_fit_height(max_h)
        tbl.move_to([0.0, -0.1, 0.0])

        self.play(FadeIn(tbl, run_time=0.6))
        self.next_slide()
        self.remove(*[m for m in self.mobjects if m not in to_keep])

        # --- Demo image ---------------------------------------------------------
        img = ImageMobject("Figures/demo_arc_blanc.jpeg")
        s = min((config.frame_width * 0.92) / img.width,
                ((config.frame_height * 0.92) - bar.height - 0.2) / img.height,
                1.0)
        img.scale(s).move_to([0.0, -0.1, 0.0])
        self.play(FadeIn(img, run_time=0.6))

        self.next_slide()
        self.remove(*[m for m in self.mobjects if m not in to_keep])

        # --- Final bullets ------------------------------------------------------
        self.start_body()
        line = Tex("Néanmoins :", font_size=self.BODY_FONT_SIZE, color=BLACK)
        line.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        dx = (-config.frame_width / 2 + 0.6 + self.DEFAULT_PAD) - line.get_left()[0]
        line.shift(RIGHT * dx)
        self.add(line)

        bullet_items = [
            r"La méthode de Tessendorf repose sur de très nombreuses approximations",
            r"Les méthodes de couplage se basent sur des modéles phénoménologiques",
        ]
        rows = []
        for s in bullet_items:
            dot = Dot(radius=0.06, color=pc.blueGreen)
            txt = Tex(s, font_size=self.BODY_FONT_SIZE, color=BLACK)
            rows.append(VGroup(dot, txt).arrange(RIGHT, buff=0.25, aligned_edge=DOWN))
        bullets = VGroup(*rows).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        bullets.next_to(line, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        dx2 = (-config.frame_width / 2 + 0.6 + self.DEFAULT_PAD) - bullets.get_left()[0]
        bullets.shift(RIGHT * dx2)
        self.play(FadeIn(bullets, run_time=0.5))

        self.pause()
        self.clear()
        self.next_slide()
