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

@slide(23)
def slide_23(self):
        """
        Slide 23 — Incompressibilité et forces de pressions
        CSV expected at states_sph/particles.csv with columns:
          Particle,X,Y,color r,color g,color b,"X quincunx","Y quincunx"
        All X/Y/quincunx in [0,1].
        """
        from manim.utils.rate_functions import linear
        from manim.utils.color import rgb_to_color, interpolate_color
        import csv
        import numpy as np

        # ---------- Top bar ----------
        bar = self._top_bar("Incompressibilité et forces de pressions")
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

        # ---- Colors ----
        blueGreen = getattr(pc, "blueGreen", BLUE_D)

        # ---------- Equation (center under bar) ----------
        eq_center = np.array([x_left + 0.5 * area_w, y_top - 0.35, 0])
        eq = MathTex(r"\left|\hat{\rho}-\rho_0\right| \;=\; ?", color=BLACK,
                     font_size=self.BODY_FONT_SIZE + 10).move_to(eq_center)
        self.play(Write(eq), run_time=0.45)
        self.next_slide()

        eq2 = MathTex(r"\left|\hat{\rho}-1027\right| \;=\; ?", color=BLACK,
                      font_size=self.BODY_FONT_SIZE + 10).move_to(eq_center)
        self.play(Transform(eq, eq2), run_time=0.45)

        # ---------- Load particles (cap to 30) ----------
        pts, cols, qxqy = [], [], []
        try:
            with open("states_sph/particles.csv", "r", encoding="utf-8", newline="") as f:
                rd = csv.DictReader(f)
                for row in rd:
                    if len(pts) >= 30:
                        break
                    x = float(row["X"]); y = float(row["Y"])
                    pts.append((x, y))

                    cr = float(row.get("color r", "0.0"))
                    cg = float(row.get("color g", "0.0"))
                    cb = float(row.get("color b", "0.0"))
                    if max(cr, cg, cb) > 1.0:
                        cr, cg, cb = cr / 255.0, cg / 255.0, cb / 255.0
                    cols.append((cr, cg, cb))

                    qx = float(row.get("X quincunx", x))
                    qy = float(row.get("Y quincunx", y))
                    qxqy.append((qx, qy))
        except Exception:
            rng = np.random.default_rng(23)
            pts = [(float(rng.uniform()), float(rng.uniform())) for _ in range(30)]
            cols = [(rng.uniform(), rng.uniform(), rng.uniform()) for _ in range(30)]
            qxqy = [(p[0], p[1]) for p in pts]

        # ---------- Field rect (below equation) ----------
        field_top = eq_center[1] - 0.45
        field_bottom = y_bottom
        field_left = x_left
        field_right = x_right
        fw = field_right - field_left
        fh = field_top - field_bottom

        pad = 0.12
        fL, fR = field_left + pad, field_right - pad
        fB, fT = field_bottom + pad, field_top - pad
        fW, fH = fR - fL, fT - fB

        def to_field(p01):
            return np.array([fL + p01[0] * fW, fB + p01[1] * fH, 0.0])

        Pw = [to_field(p) for p in pts]
        Qw = [to_field(p) for p in qxqy]
        r_vis = min(fW, fH) / 70.0

        # Dots
        dots = [Dot(Pw[i], radius=r_vis, color=blueGreen, fill_opacity=1.0)
                for i in range(len(Pw))]

        # Grow particles in
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots],
                              lag_ratio=0.03, run_time=0.9))
        self.next_slide()

        # ---------- Transform color to CSV colors ----------
        self.play(*[
            dots[i].animate.set_color(rgb_to_color(cols[i])).set_fill(rgb_to_color(cols[i]), 1.0)
            for i in range(len(dots))
        ], run_time=0.6)

        # -> |875-1027| = 152
        eq3 = MathTex(r"\left|875-1027\right| \;=\; 152", color=BLACK,
                      font_size=self.BODY_FONT_SIZE + 10).move_to(eq_center)
        self.play(Transform(eq, eq3), run_time=0.5)
        self.next_slide()

        # ---------- Coupled animation (10s): move to quincunx + recolor to blueGreen + equation to |1027-1027|=0 + F^p arrow ----------
        from manim import Arrow, Tex, ValueTracker, always_redraw

        # Single progress tracker drives motions/colors
        progress = ValueTracker(0.0)

        # Density tracker drives the equation numbers
        rho_tracker = ValueTracker(875.0)

        # One live MathTex for the whole equation (no overlapping numbers)
        def make_live_eq():
            # Use integers to keep layout stable
            a = int(round(rho_tracker.get_value()))
            b = abs(a - 1027)
            m = MathTex(rf"\left|{a}-1027\right|\;=\;{b}",
                        color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
            m.move_to(eq_center)
            return m

        eq_live = always_redraw(make_live_eq)
        # Replace the static eq with the live one
        self.play(FadeTransform(eq3, eq_live), run_time=0.4)

        # Cache start/end + start color for each dot, add updaters
        start_pos = [d.get_center() for d in dots]
        end_pos   = Qw
        start_col = [rgb_to_color(cols[i]) for i in range(len(dots))]
        end_col   = [blueGreen for _ in dots]

        def make_dot_updater(i):
            def _upd(d: Dot):
                t = progress.get_value()
                d.move_to(start_pos[i] * (1 - t) + end_pos[i] * t)
                d.set_color(interpolate_color(start_col[i], end_col[i], t))
                d.set_fill(interpolate_color(start_col[i], end_col[i], t), 1.0)
            return _upd

        for i, d in enumerate(dots):
            d.add_updater(make_dot_updater(i))

        # Force arrow for one particle (index 0) that shrinks to 0
        fp_idx = 0 if len(dots) > 0 else None
        if fp_idx is not None:
            def make_force_arrow():
                t = progress.get_value()
                start = start_pos[fp_idx] * (1 - t) + end_pos[fp_idx] * t
                target = end_pos[fp_idx]
                curr_end = start + (target - start) * (1.0 - t)  # length reduces to 0
                arr = Arrow(start, curr_end, color=BLACK, stroke_width=6, buff=0.0, tip_length=0.16)
                arr.set_opacity(1.0 - t)
                return arr
            force_arrow = always_redraw(make_force_arrow)
            fp_label = Tex(r"$F^p$", color=BLACK, font_size=self.BODY_FONT_SIZE).add_updater(
                lambda m: m.next_to(force_arrow, UP, buff=0.05).set_opacity(1.0 - progress.get_value())
            )
            self.add(force_arrow, fp_label)

        # Drive everything together for 10 seconds (you can keep your adjusted duration here)
        self.play(
            progress.animate.set_value(1.0),
            rho_tracker.animate.set_value(1027.0),
            run_time=10.0,
            rate_func=linear,
        )

        # Cleanup updaters
        for d in dots:
            d.clear_updaters()
        if fp_idx is not None:
            self.remove(force_arrow, fp_label)

        self.pause()
        self.clear()
        self.next_slide()
