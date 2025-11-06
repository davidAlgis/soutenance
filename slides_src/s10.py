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

@slide(10)
def slide_10(self):
        """
        Airy wave theory demonstration with color highlights.
        Shows, in order: cos(x), cos(x+t), A cos(x+t), A cos(kx+t), A cos(kx+omega t).
        The evolving variables are colorized both in the formula and in the value label.
        """
        # --- Top bar --------------------------------------------------------------
        bar = self._top_bar("La théorie des vagues d'Airy")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area under the bar -------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left

        # Left anchor for intro/formulas to prevent horizontal drift
        anchor_x = x_left + 0.2

        # --- Colors for highlights ------------------------------------------------
        col_A = pc.apple
        col_k = pc.tiffanyBlue
        col_t = pc.bittersweet
        col_omega = pc.uclaGold

        # --- Intro line (left aligned, placed under the bar) ---------------------
        self.start_body()
        intro = Text(
            "Modèle linéaire qui simule l'océan comme une simple vague :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        intro_y = y_top - 0.35
        intro.move_to([anchor_x + intro.width / 2.0, intro_y, 0.0])
        self.add(intro)

        # --- Helper: build a formula and colorize given symbols -------------------
        def make_formula(tex_expr: str, highlight: dict) -> MathTex:
            m = MathTex(
                tex_expr,
                color=BLACK,
                substrings_to_isolate=(
                    list(highlight.keys()) if highlight else None
                ),
            )
            for key, col in (highlight or {}).items():
                m.set_color_by_tex(key, col)
            return m

        # --- Initial formula (left aligned under intro) --------------------------
        formula = make_formula(r"h(x,t)=\cos(x)", highlight={})
        formula.next_to(intro, DOWN, buff=0.25, aligned_edge=LEFT)
        dx0 = anchor_x - formula.get_left()[0]
        formula.shift(RIGHT * dx0)
        formula_y = formula.get_y()
        self.add(formula)

        # --- Axes below the formula ---------------------------------------------
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
        # self.add(axes)

        # --- Helper to lock any new formula to same left and y -------------------
        def _lock_left(mobj: Mobject) -> Mobject:
            dx = anchor_x - mobj.get_left()[0]
            mobj.shift(RIGHT * dx)
            mobj.set_y(formula_y)
            return mobj

        # --- Trackers ------------------------------------------------------------
        A = ValueTracker(1.0)
        k = ValueTracker(1.0)
        omega = ValueTracker(0.0)  # start with cos(x)
        t = ValueTracker(0.0)

        # --- Curve depending on trackers -----------------------------------------
        def f_y(xval: float) -> float:
            return A.get_value() * np.cos(
                k.get_value() * xval + omega.get_value() * t.get_value()
            )

        curve = always_redraw(
            lambda: axes.plot(
                lambda x: f_y(x),
                x_range=[-2 * PI, 2 * PI],
                stroke_width=4,
                color=pc.oxfordBlue,
            )
        )
        self.add(curve)

        # --- Adaptive label: show only introduced params (colorized) -------------
        show_t = False
        show_A = False
        show_k = False
        show_omega = False

        def label_text() -> Mobject:
            parts = []
            if show_A:
                parts.append(r"A=" + f"{A.get_value():.2f}")
            if show_k:
                parts.append(r"k=" + f"{k.get_value():.2f}")
            if show_omega:
                parts.append(r"\omega=" + f"{omega.get_value():.2f}")
            if show_t:
                parts.append(r"t=" + f"{t.get_value():.2f}")

            if not parts:
                # Transparent spacer to avoid TeX on empty label
                return Rectangle(
                    width=0.1, height=0.1, stroke_opacity=0.0, fill_opacity=0.0
                )

            expr = r"\quad ".join(parts)
            tex_colors = {
                "A": col_A,
                "k": col_k,
                r"\omega": col_omega,
                "t": col_t,
            }
            return MathTex(
                expr,
                font_size=self.BODY_FONT_SIZE + 10,
                color=BLACK,
                tex_to_color_map=tex_colors,
            )

        value_label = always_redraw(
            lambda: label_text().next_to(axes, DOWN, buff=0.2)
        )
        self.add(value_label)

        # ===================== Step 1: h = cos(x) =================================
        self.next_slide()

        # ===================== Step 2: h = cos(x + t) =============================
        new_formula = make_formula(r"h(x,t)=\cos(x+t)", highlight={"t": col_t})
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        omega.set_value(1.0)
        show_t = True
        self.play(t.animate.set_value(2 * PI), rate_func=linear, run_time=4.0)
        self.next_slide()

        # ===================== Step 3: h = A cos(x + t) ===========================
        new_formula = make_formula(
            r"h(x,t)=A\cos(x+t)", highlight={"A": col_A, "t": col_t}
        )
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        self.play(t.animate.set_value(0.0), run_time=0.3)
        show_A = True
        self.play(
            A.animate.set_value(2.0), rate_func=there_and_back, run_time=4.0
        )
        self.next_slide()

        # ===================== Step 4: h = A cos(kx + t) ==========================
        new_formula = make_formula(
            r"h(x,t)=A\cos(kx+t)",
            highlight={"A": col_A, "k": col_k, "t": col_t},
        )
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        self.play(
            A.animate.set_value(1.0), t.animate.set_value(0.0), run_time=0.3
        )
        show_k = True
        self.play(
            k.animate.set_value(10.0), rate_func=there_and_back, run_time=5.0
        )
        self.next_slide()

        # ===================== Step 5: h = A cos(kx + omega t) ====================
        new_formula = make_formula(
            r"h(x,t)=A\cos(kx+\omega t)",
            highlight={
                "A": col_A,
                "k": col_k,
                r"\omega": col_omega,
                "t": col_t,
            },
        )
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        self.play(
            A.animate.set_value(1.0), k.animate.set_value(1.0), run_time=0.3
        )
        show_omega = True
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

        # --- End of slide --------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()
