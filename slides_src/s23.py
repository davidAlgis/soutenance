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


@slide(23)
def slide_23(self):
    """
    Slide 23 — Incompressibilité et forces de pressions
    CSV expected at states_sph/particles.csv with columns:
      Particle,X,Y,color r,color g,color b,"X quincunx","Y quincunx"
    All X/Y/quincunx in [0,1].
    """
    import csv

    import numpy as np
    from manim.utils.color import interpolate_color, rgb_to_color
    from manim.utils.rate_functions import linear

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

    # ---------- Equation (center under bar) ----------
    eq_center = np.array([x_left + 0.5 * area_w, y_top - 0.35, 0.0])
    eq = MathTex(
        r"\left|\hat{\rho}-\rho_0\right| \;=\; ?",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    ).move_to(eq_center)
    self.play(Write(eq), run_time=0.45)
    self.wait(0.1)
    self.next_slide()

    eq2 = MathTex(
        r"\left|\hat{\rho}-1027\right| \;=\; ?",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    ).move_to(eq_center)
    self.play(Transform(eq, eq2), run_time=0.45)
    # self.wait(0.1)
    # self.next_slide()
    # self.remove(eq, eq2)
    # ---------- Load particles (cap to 30) ----------
    pts, cols, qxqy = [], [], []

    with open(
        "states_sph/particles.csv", "r", encoding="utf-8", newline=""
    ) as f:
        rd = csv.DictReader(f)
        for row in rd:
            if len(pts) >= 30:
                break
            x = float(row["X"])
            y = float(row["Y"])
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

    dots = [
        Dot(Pw[i], radius=r_vis, color=pc.blueGreen, fill_opacity=1.0)
        for i in range(len(Pw))
    ]

    # Grow particles in
    self.play(
        LaggedStart(
            *[GrowFromCenter(d) for d in dots], lag_ratio=0.03, run_time=0.9
        )
    )
    self.next_slide()

    # ---------- Transform color to CSV colors ----------
    self.play(
        *[
            dots[i]
            .animate.set_color(rgb_to_color(cols[i]))
            .set_fill(rgb_to_color(cols[i]), 1.0)
            for i in range(len(dots))
        ],
        run_time=0.6,
    )

    # ---------- Build live equation with Integers (no overlapping MathTex) ---
    # Start from 875 and |875-1027| = 152
    left_tex = Tex(
        r"\left|",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    minus_tex = Tex(
        r"-1,027\right| \;=\;",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )

    rho_int = Integer(
        875,
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    diff_int = Integer(
        abs(875 - 1027),
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )

    eq_group = VGroup(left_tex, rho_int, minus_tex, diff_int).arrange(
        RIGHT, buff=0.12, aligned_edge=DOWN
    )
    eq_group.move_to(eq_center)
    rho_int.next_to(left_tex, RIGHT, buff=0.1)
    minus_tex.next_to(rho_int, RIGHT, buff=0.3)
    diff_int.next_to(minus_tex, RIGHT, buff=0.1)

    # Clean switch: old MathTex out, new group in
    self.wait(0.1)
    self.next_slide()

    self.remove(eq, eq2)
    self.add(eq_group)

    # ---------- Coupled animation --------------------------------------------
    progress = ValueTracker(0.0)
    rho_tracker = ValueTracker(875.0)

    # Updaters only touch the Integer glyphs
    def update_rho(m: Integer):
        m.set_value(int(round(rho_tracker.get_value())))

    def update_diff(m: Integer):
        v = int(round(rho_tracker.get_value()))
        m.set_value(abs(v - 1027))

    rho_int.add_updater(update_rho)
    diff_int.add_updater(update_diff)

    # Cache start/end + colors for dots
    start_pos = [d.get_center() for d in dots]
    end_pos = Qw
    start_col = [rgb_to_color(cols[i]) for i in range(len(dots))]
    end_col = [pc.blueGreen for _ in dots]

    def make_dot_updater(i):
        def _upd(d: Dot):
            t = progress.get_value()
            d.move_to(start_pos[i] * (1.0 - t) + end_pos[i] * t)
            col = interpolate_color(start_col[i], end_col[i], t)
            d.set_color(col)
            d.set_fill(col, 1.0)

        return _upd

    for i, d in enumerate(dots):
        d.add_updater(make_dot_updater(i))

    # Force arrow for one particle (index 5) that shrinks to 0
    fp_idx = 7 if len(dots) > 0 else None
    if fp_idx is not None:

        def make_force_arrow():
            t = progress.get_value()
            start = start_pos[fp_idx] * (1.0 - t) + end_pos[fp_idx] * t
            target = end_pos[fp_idx]
            curr_end = start + (target - start) * (1.0 - t)
            arr = Arrow(
                start,
                curr_end,
                color=BLACK,
                stroke_width=6,
                buff=0.0,
                tip_length=0.16,
            )
            arr.set_opacity(1.0 - t)
            return arr

        force_arrow = always_redraw(make_force_arrow)

        fp_label = Tex(
            r"$F^p$", color=BLACK, font_size=self.BODY_FONT_SIZE
        ).add_updater(
            lambda m: m.next_to(force_arrow, UP, buff=0.05).set_opacity(
                1.0 - progress.get_value()
            )
        )
        self.add(force_arrow, fp_label)

    # Drive everything together for 10 seconds
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
    rho_int.clear_updaters()
    diff_int.clear_updaters()

    self.pause()
    self.clear()
    self.next_slide()
