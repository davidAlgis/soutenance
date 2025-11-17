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


@slide(10)
def slide_10(self):
    """
    Airy wave theory demo – progressive reveal:
    cos(x) → cos(x+t) → A cos(x+t) → A cos(kx+t) → A cos(kx+ωt)
    Optimized rendering (single VMobject curve, no per-frame LaTeX) and
    constant amplitude while frequency changes (no "breathing").
    """
    # ---------- Top bar ----------
    bar = self._top_bar("La théorie des vagues d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---------- Layout ----------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    anchor_x = x_left + 0.2  # left lock for text/formulas

    # ---------- Colors ----------
    col_A = pc.apple
    col_k = pc.tiffanyBlue
    col_t = pc.bittersweet
    col_omega = pc.uclaGold

    # ---------- Intro ----------
    intro = Tex(
        "Modèle linéaire qui simule l'océan comme une simple vague :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    intro_y = y_top - 0.35
    intro.move_to([anchor_x + intro.width / 2.0, intro_y, 0.0])
    self.play(FadeIn(intro), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # Helper to lock a MathTex on the same left & y
    def lock_left(m: Mobject, y_ref: float) -> Mobject:
        dx = anchor_x - m.get_left()[0]
        m.shift(RIGHT * dx)
        m.set_y(y_ref)
        return m

    # ---------- Initial formula ----------
    formula = MathTex(r"h(x)=\cos(x)", color=BLACK)
    formula.next_to(intro, DOWN, buff=0.25, aligned_edge=LEFT)
    formula.shift(RIGHT * (anchor_x - formula.get_left()[0]))
    formula_y = formula.get_y()

    # ---------- Axes ----------
    axes_top = formula.get_bottom()[1] - 0.3
    axes_bottom = y_bottom + 0.2
    axes_height = max(1.8, min(3.8, axes_top - axes_bottom))
    axes_width = area_w
    axes = Axes(
        x_range=[-2 * PI, 2 * PI, PI],
        y_range=[-2.2, 2.2, 1],
        x_length=axes_width,
        y_length=axes_height,
        axis_config={"color": GRAY, "stroke_width": 2},
        tips=False,
    )
    axes.move_to([0, axes_bottom + axes_height / 2.0, 0])

    # ---------- Trackers ----------
    A = ValueTracker(1.0)
    k = ValueTracker(1.0)
    omega = ValueTracker(0.0)
    t = ValueTracker(0.0)

    # ---------- Curve (single VMobject, in-place update) ----------
    curve = VMobject(stroke_color=pc.oxfordBlue, stroke_width=4)

    def update_curve(m: VMobject):
        # Adaptive sampling tied to k; no smoothing to avoid amplitude artifacts
        k_val = max(1.0, float(k.get_value()))
        pts_per_period = 40
        dt = max(1e-3, min((2 * PI) / (k_val * pts_per_period), 0.05))

        xs = np.arange(-2 * PI, 2 * PI + dt, dt)
        ys = A.get_value() * np.cos(
            k.get_value() * xs - omega.get_value() * t.get_value()
        )
        m.set_points_as_corners([axes.c2p(x, y) for x, y in zip(xs, ys)])

    update_curve(curve)
    self.play(Create(curve), FadeIn(formula), run_time=1.0)
    curve.add_updater(update_curve)

    # ---------- Numeric label (no per-frame LaTeX) ----------
    # We build "A=  k=  ω=  t=" and only show introduced ones.
    def make_pair(sym_tex: str, color, tracker: ValueTracker):
        lab = MathTex(sym_tex, color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
        val = DecimalNumber(
            tracker.get_value(),
            num_decimal_places=2,
            color=color,
            font_size=self.BODY_FONT_SIZE + 10,
        )
        val.add_updater(lambda m: m.set_value(tracker.get_value()))
        return VGroup(lab, val).arrange(RIGHT, buff=0.15)

    pair_A = make_pair(r"A=", col_A, A)
    pair_k = make_pair(r"k=", col_k, k)
    pair_w = make_pair(r"\omega=", col_omega, omega)
    pair_t = make_pair(r"t=", col_t, t)

    label_box = VGroup(pair_A, pair_k, pair_w, pair_t).arrange(RIGHT, buff=0.6)
    label_box.next_to(axes, DOWN, buff=0.2)
    # Start hidden; reveal pieces as we introduce them
    for p in label_box:
        p.set_opacity(0.0)
    self.play(FadeIn(label_box), run_time=0.25)

    # ===================== Step 1: h = cos(x) ================================
    self.next_slide()

    # ===================== Step 2: h = cos(x+t) ==============================
    new_f = MathTex(
        r"h(x,t)=\cos(x-t)", color=BLACK, tex_to_color_map={"t": col_t}
    )
    lock_left(new_f, formula_y)
    self.play(ReplacementTransform(formula, new_f))
    formula = new_f
    self.wait(0.3)
    self.next_slide()

    omega.set_value(1.0)
    self.play(
        FadeToColor(pair_t, BLACK),
        pair_t.animate.set_opacity(1.0),
        run_time=0.2,
    )
    self.play(
        t.animate.set_value(2 * PI), rate_func=there_and_back, run_time=4.0
    )
    self.next_slide()

    # ===================== Step 3: h = A cos(x+t) ============================
    new_f = MathTex(
        r"h(x,t)=A\cos(x-t)",
        color=BLACK,
        tex_to_color_map={"A": col_A, "t": col_t},
    )
    lock_left(new_f, formula_y)
    self.play(ReplacementTransform(formula, new_f))
    formula = new_f
    self.wait(0.3)
    self.next_slide()

    # self.play(t.animate.set_value(0.0), run_time=0.3)
    self.play(
        FadeToColor(pair_A, BLACK),
        pair_A.animate.set_opacity(1.0),
        run_time=0.2,
    )
    self.play(A.animate.set_value(2.0), rate_func=there_and_back, run_time=4.0)
    self.next_slide()

    # ===================== Step 4: h = A cos(kx + t) =========================
    new_f = MathTex(
        r"h(x,t)=A\cos(kx-t)",
        color=BLACK,
        tex_to_color_map={"A": col_A, "k": col_k, "t": col_t},
    )
    lock_left(new_f, formula_y)
    self.play(ReplacementTransform(formula, new_f))
    formula = new_f
    self.wait(0.3)
    self.next_slide()

    self.play(A.animate.set_value(1.0), t.animate.set_value(0.0), run_time=0.3)
    self.play(
        FadeToColor(pair_k, BLACK),
        pair_k.animate.set_opacity(1.0),
        run_time=0.2,
    )
    # Frequency sweep with constant amplitude (no breathing thanks to set_points_as_corners)
    self.play(
        k.animate.set_value(10.0), rate_func=there_and_back, run_time=5.0
    )
    self.next_slide()

    # ===================== Step 5: h = A cos(kx + ω t) =======================
    new_f = MathTex(
        r"h(x,t)=A\cos(kx-\omega t)",
        color=BLACK,
        tex_to_color_map={
            "A": col_A,
            "k": col_k,
            r"\omega": col_omega,
            "t": col_t,
        },
    )
    lock_left(new_f, formula_y)
    self.play(ReplacementTransform(formula, new_f))
    formula = new_f
    self.wait(0.3)
    self.next_slide()

    self.play(A.animate.set_value(1.0), k.animate.set_value(1.0), run_time=0.3)
    self.play(
        FadeToColor(pair_w, BLACK),
        pair_w.animate.set_opacity(1.0),
        run_time=0.2,
    )
    self.play(
        AnimationGroup(
            omega.animate.set_value(10.0),
            t.animate.set_value(2 * PI),
            lag_ratio=0.0,
        ),
        rate_func=linear,
        run_time=5.0,
    )
    self.next_slide()

    # ---------- End ----------
    self.pause()
    self.clear()
    self.next_slide()
