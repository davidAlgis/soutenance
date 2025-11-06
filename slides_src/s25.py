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

@slide(25)
def slide_25(self):
        """
        Slide 25 — Couplage avec des solides (based on the provided sketch)

        Flow:
        - Top bar + sentence
        - Draw thick orange rectangle edge-by-edge + thin inner guide
        - Spawn dark 'solid' particles along the border; keep border slightly visible
        - "Zoom" to lower-left corner by transforming a group (no camera API)
          and keep < 10 solids visible
        - Add 3 blueGreen 'fluid' particles just above bottom edge near corner
        - Draw a black arrow from fluid -> solid with label 'Fp'
        - Next slide: reverse the arrow direction
        - Finish with pause/clear/next_slide
        """
        import numpy as np
        from manim import (
            VGroup, Line, Dot, Arrow, Tex,
            GrowFromCenter, Create, FadeIn, FadeOut, Transform, LaggedStart
        )
        from manim.utils.rate_functions import linear

        # ---------- Top bar ----------
        bar = self._top_bar("Couplage avec des solides")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---------- Layout (usable body below bar) ----------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_w = x_right - x_left
        area_h = y_top - y_bottom

        # ---------- Palette ----------
        orange     = getattr(pc, "orange", ORANGE)
        temptress  = getattr(pc, "temptress", MAROON_D)   # dark border particles
        blueGreen  = getattr(pc, "blueGreen", BLUE_D)     # fluid particles

        # ---------- Sentence ----------
        body = Tex(
            "On considere le solide comme un ensemble de particules",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        ).move_to(np.array([x_left + 0.5 * area_w, y_top - 0.45, 0]))
        self.play(FadeIn(body), run_time=0.45)

        # ---------- Outer rectangle geometry ----------
        pad_side = 0.35
        pad_top = 0.95
        rect_left   = x_left  + pad_side
        rect_right  = x_right - pad_side
        rect_top    = y_top   - pad_top
        rect_bottom = y_bottom + 0.22

        pBL = np.array([rect_left,  rect_bottom, 0.0])
        pBR = np.array([rect_right, rect_bottom, 0.0])
        pTR = np.array([rect_right, rect_top,    0.0])
        pTL = np.array([rect_left,  rect_top,    0.0])

        # Thick orange border (draw edge-by-edge)
        edge_w = 18
        e_bottom = Line(pBL, pBR, color=orange, stroke_width=edge_w)
        e_right  = Line(pBR, pTR, color=orange, stroke_width=edge_w)
        e_top    = Line(pTR, pTL, color=orange, stroke_width=edge_w)
        e_left   = Line(pTL, pBL, color=orange, stroke_width=edge_w)
        border_edges = VGroup(e_bottom, e_right, e_top, e_left)

        self.play(Create(e_bottom), run_time=0.25, rate_func=linear)
        self.play(Create(e_right),  run_time=0.25, rate_func=linear)
        self.play(Create(e_top),    run_time=0.25, rate_func=linear)
        self.play(Create(e_left),   run_time=0.25, rate_func=linear)

        # Thin inner guide line (slightly inset)
        inset = 0.035 * min(area_w, area_h)
        gBL = pBL + np.array([+inset, +inset, 0])
        gBR = pBR + np.array([-inset, +inset, 0])
        gTR = pTR + np.array([-inset, -inset, 0])
        gTL = pTL + np.array([+inset, -inset, 0])
        guide = VGroup(
            Line(gBL, gBR, color=WHITE, stroke_width=3),
            Line(gBR, gTR, color=WHITE, stroke_width=3),
            Line(gTR, gTL, color=WHITE, stroke_width=3),
            Line(gTL, gBL, color=WHITE, stroke_width=3),
        )
        self.play(Create(guide), run_time=0.25, rate_func=linear)

        self.next_slide()

        # ---------- Border particles (keep border slightly visible) ----------
        def sample_segment(a, b, n):
            return [a + (b - a) * (i / (n - 1)) for i in range(n)]

        n_long, n_short = 24, 14
        pts_bottom = sample_segment(pBL, pBR, n_long)
        pts_left   = sample_segment(pBL, pTL, n_short)
        pts_top    = sample_segment(pTL, pTR, n_long)
        pts_right  = sample_segment(pBR, pTR, n_short)

        # Avoid duplicate corners, chain around the frame
        chain = (
            pts_left[::-1][:-1] +      # up the left
            pts_bottom +               # along bottom
            pts_right[:-1] +           # up the right
            pts_top[:-1]               # along top
        )

        dot_r = min((rect_right - rect_left), (rect_top - rect_bottom)) / 90.0
        solid_dots = [Dot(p, radius=dot_r, color=temptress, fill_opacity=1.0) for p in chain]

        # Fade the border a bit and grow the particles
        self.play(
            border_edges.animate.set_opacity(0.85),
            LaggedStart(*[GrowFromCenter(d) for d in solid_dots], lag_ratio=0.02, run_time=0.9),
            run_time=0.9
        )

        self.next_slide()

        # ---------- "Zoom" to lower-left corner (content transform) ----------
        world = VGroup(border_edges, guide, *solid_dots)

        box_w = (rect_right - rect_left) * 0.55
        box_h = (rect_top   - rect_bottom) * 0.42
        box_x_min = rect_left
        box_y_min = rect_bottom
        box_x_max = rect_left + box_w
        box_y_max = rect_bottom + box_h

        # Keep solids in the corner; fade the rest
        keep, drop = [], []
        for d in solid_dots:
            x, y, _ = d.get_center()
            if (box_x_min <= x <= box_x_max) and (box_y_min <= y <= box_y_max):
                keep.append(d)
            else:
                drop.append(d)
        if drop:
            self.play(*[FadeOut(d, run_time=0.15) for d in drop], run_time=0.15)
            for d in drop:
                world.remove(d)
        solid_dots = keep

        target_center = np.array([-0.6, -0.3, 0.0])
        scale_factor = 1.9
        self.play(world.animate.scale(scale_factor).shift(target_center - world.get_center()),
                  run_time=0.8)

        # Ensure < 10 remain visible
        if len(solid_dots) > 9:
            extra = solid_dots[9:]
            self.play(*[FadeOut(d, run_time=0.12) for d in extra], run_time=0.12)
            for d in extra:
                world.remove(d)
            solid_dots = solid_dots[:9]

        # ---------- 3 fluid particles just above the bottom edge ----------
        bottom_edge_pts = sorted(
            [d for d in solid_dots if abs(d.get_center()[1] - pBL[1]) < (2.5 * dot_r)],
            key=lambda d: d.get_center()[0]
        )

        fluid_dots = []
        if bottom_edge_pts:
            picks = [0, len(bottom_edge_pts)//2, -1] if len(bottom_edge_pts) >= 3 else list(range(len(bottom_edge_pts)))
            for idx in picks[:3]:
                base = bottom_edge_pts[idx].get_center()
                fluid_dots.append(Dot(base + np.array([0.0, 3.0 * dot_r, 0.0]),
                                      radius=dot_r, color=blueGreen, fill_opacity=1.0))
        else:
            # Fallback: place 3 fluids near the bottom-left corner region
            bases = [
                pBL + np.array([4*dot_r, 4*dot_r, 0]),
                pBL + np.array([8*dot_r, 4*dot_r, 0]),
                pBL + np.array([12*dot_r, 4*dot_r, 0]),
            ]
            fluid_dots = [Dot(b, radius=dot_r, color=blueGreen, fill_opacity=1.0) for b in bases]

        if fluid_dots:
            self.play(LaggedStart(*[GrowFromCenter(d) for d in fluid_dots], lag_ratio=0.18, run_time=0.5))
        else:
            # Extremely defensive; should not happen
            pass

        self.next_slide()

        # ---------- Arrow (black) fluid -> solid, label 'Fp' ----------
        if not fluid_dots or not solid_dots:
            # --- End slide ---------------------------------------------------------
            self.pause()
            self.clear()
            self.next_slide()
            return

        f = fluid_dots[0]
        # choose neighboring solid (closest)
        solid_neigh = min(solid_dots, key=lambda d: np.linalg.norm(d.get_center() - f.get_center()))
        start_pt = f.get_bottom() + np.array([0, -0.4*dot_r, 0])
        end_pt   = solid_neigh.get_top() + np.array([0, 0.4*dot_r, 0])

        arrow = Arrow(start_pt, end_pt, color=BLACK, stroke_width=6, buff=0.0, tip_length=0.16)
        self.play(Create(arrow), run_time=0.45)

        fp = Tex("Fp", color=BLACK, font_size=self.BODY_FONT_SIZE).next_to(arrow, LEFT, buff=0.06)
        self.play(FadeIn(fp), run_time=0.2)

        self.next_slide()

        # ---------- Reverse arrow (toward fluid) ----------
        self.play(arrow.animate.put_start_and_end_on(end_pt, start_pt), run_time=0.55)
        self.play(fp.animate.next_to(arrow, LEFT, buff=0.06), run_time=0.2)

        # --- End slide ---------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()
