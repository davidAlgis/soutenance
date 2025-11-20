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


@slide(11)
def slide_11(self):
    """
    Methode de Tessendorf: one curve per row.

    Minimal changes:
      - Color the TOP index (N) by selecting the MathTex part that matches the
        string of N and has the highest y (superscript), avoiding the bottom i=0.
      - Move the sigma label from RIGHT to BELOW using generate_target + MoveToTarget
        to avoid any teleport/snap-back due to grouping.
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Méthode de Tessendorf")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Usable area -------------------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom

    subtitle = Tex(
        "« Généralisation » des vagues d'Airy :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    subtitle.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx_sub = (bar_rect.get_left()[0] + self.DEFAULT_PAD) - subtitle.get_left()[
        0
    ]
    subtitle.shift(RIGHT * dx_sub)
    self.play(FadeIn(subtitle, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # --- Layout (two rows, no axes) ---------------------------------------
    row_gap = 0.55
    plot_w = min(area_w * 0.55, 8.8)
    plot_h = min((area_h - 1.6) * 0.35, 2.2)

    row1_y = y_top - 0.95 - plot_h / 2.0
    row2_y = row1_y - plot_h - row_gap
    plot_x = x_left + 0.9 + plot_w / 2.0

    # Helper: draw a smooth curve from sampled points (no axes)
    def make_function_curve(center, width, height, func):
        x_min, x_max = -10.0, 10.0
        n = 300
        X = np.linspace(x_min, x_max, n)
        sx = width / (x_max - x_min)
        y_vis = 4.0
        sy = (height / 2.0) / y_vis

        path = VMobject()
        pts = []
        for x in X:
            y = float(func(x))
            px = (x - x_min) * sx - width / 2.0
            py = np.clip(y, -y_vis, y_vis) * sy
            pts.append([center[0] + px, center[1] + py, 0.0])
        path.set_points_smoothly(pts)
        path.set_stroke(color=pc.blueGreen, width=4)
        return path

    # ===================== Row 1: ONE Airy wave curve ======================
    A1 = ValueTracker(0.7)
    k1 = ValueTracker(1.5)

    def airy_y(x):
        return A1.get_value() * np.cos(k1.get_value() * x)

    curve1 = always_redraw(
        lambda: make_function_curve(
            center=np.array([plot_x, row1_y, 0.0]),
            width=plot_w,
            height=plot_h,
            func=airy_y,
        )
    )

    f1_initial = MathTex(
        r"h_A(x,t) = 0.7\cos\!\left(1.5\,x + \omega t\right)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 2,
    )
    f1_initial.next_to(curve1, RIGHT, buff=0.35, aligned_edge=UP)
    # self.add(curve1, f1_initial)
    self.play(Create(curve1), Create(f1_initial), run_time=1.0)
    self.wait(0.1)
    self.next_slide()
    # ===================== Row 2: ONE sum curve ============================
    row2_anchor = Dot(
        [plot_x, row2_y, 0.0],
        radius=0.001,
        fill_opacity=0.0,
        stroke_opacity=0.0,
    )
    row2_scale = ValueTracker(1.0)
    self.add(row2_anchor)

    components = [(0.7, 1.5)]  # (A, k) initial

    def sum_y_up_to(m, x):
        s = 0.0
        m_int = int(max(0, min(m, len(components))))
        for i in range(m_int):
            A, k = components[i]
            s += A * np.cos(k * x)
        return s

    n_comp = ValueTracker(len(components))  # number of components included

    curve_sum = always_redraw(
        lambda: make_function_curve(
            center=row2_anchor.get_center(),
            width=plot_w * row2_scale.get_value(),
            height=plot_h * row2_scale.get_value(),
            func=lambda x: sum_y_up_to(int(np.floor(n_comp.get_value())), x),
        )
    )

    f2 = MathTex(
        r"h_T(x,t) = 0.7\cos\!\left(1.5\,x + \omega t\right)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 2,
    )
    f2.next_to(curve_sum, RIGHT, buff=0.35, aligned_edge=UP)
    # self.add(curve_sum, f2)
    self.play(Create(curve_sum), Create(f2), run_time=1.0)
    self.wait(0.1)
    self.next_slide()

    # Row 1: same curve, new params
    f1_new = MathTex(
        r"h_A(x,t) = 0.8\cos\!\left(0.9\,x + \omega t\right)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 2,
    )
    f1_new.next_to(curve1, RIGHT, buff=0.35, aligned_edge=UP)

    self.play(
        A1.animate.set_value(0.8),
        k1.animate.set_value(0.9),
        ReplacementTransform(f1_initial, f1_new),
        run_time=0.7,
    )

    # ----------------------------------------------------------------------
    self.next_slide()

    # Symbolize addition: ghost flies and fades to row2
    ghost = f1_initial.copy().set_opacity(0.85)
    ghost.move_to(f1_new.get_center())
    self.add(ghost)
    self.play(
        ghost.animate.move_to(f2.get_center()).set_opacity(0.15),
        run_time=0.6,
    )

    # Two-line explicit sum to stay in bounds
    f2_sum = MathTex(
        r"h_T(x,t) = 0.7\cos\!\left(1.5\,x + \omega t\right)"
        r" \\ + 0.8\cos\!\left(0.9\,x + \omega t\right)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 2,
    )
    f2_sum.next_to(curve_sum, RIGHT, buff=0.35, aligned_edge=UP)

    components.append((0.8, 0.9))
    n_comp.set_value(len(components))

    self.play(ReplacementTransform(f2, f2_sum), FadeOut(ghost), run_time=0.6)

    # ----------------------------------------------------------------------
    self.next_slide()

    # Remove Row 1; center and enlarge Row 2
    self.play(FadeOut(VGroup(curve1, f1_new)), run_time=0.4)

    target_center_y = (y_top + y_bottom) * 0.5 + 0.2

    # --- Sigma label: build once, then move RIGHT -> BELOW and keep N colored ---
    def build_sigma(n_val: int) -> MathTex:
        """
        Build MathTex and color ONLY the top index 'N' (numeric) by:
          - selecting parts that match the string of N,
          - keeping the one with the highest y (superscript),
          - coloring it pc.uclaGold.
        """
        n_txt = str(int(max(0, n_val)))
        m = MathTex(
            r"h_T(x,t) = ",
            r"\sum",
            r"_{i=1}",
            r"^{",
            n_txt,
            r"} A_i\cos\!\left(k_i x - \omega t\right)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 6,
        )
        # m[1].set_color(pc.blueGreen)
        return m

    sigma = build_sigma(int(n_comp.get_value()))
    sigma.next_to(curve_sum, DOWN, buff=0.35, aligned_edge=UP)
    sigma.move_to([0.0, -2.0, 0.0])
    # self.play(, run_time=0.5)

    self.play(
        AnimationGroup(
            row2_anchor.animate.move_to([0.0, target_center_y, 0.0]),
            row2_scale.animate.set_value(1.15),
            lag_ratio=0.0,
        ),
        ReplacementTransform(f2_sum, sigma),
        run_time=0.5,
    )

    # Create sigma at RIGHT of the curve (replace the two-line sum)

    # Move sigma smoothly BELOW the curve (no teleport)
    # sigma.generate_target()
    # sigma.target.next_to(curve_sum, DOWN, buff=0.25)
    # self.play(MoveToTarget(sigma), run_time=0.35)

    # Live update of N while preserving the current position
    def sigma_updater(mobj: Mobject) -> None:
        pos = mobj.get_center()
        new = build_sigma(int(np.floor(n_comp.get_value())))
        new.move_to(pos)
        mobj.become(new)

    sigma.add_updater(sigma_updater)

    # Progressive addition in one clip; curve updates via n_comp
    rng = np.random.default_rng(42)
    extra = []
    add_count = 28
    for _ in range(add_count):
        A_rand = float(rng.uniform(0.01, 0.1))
        k_rand = float(rng.uniform(0.1, 20.0))
        extra.append((A_rand, k_rand))
    components.extend(extra)

    # Avoid reversing issues on this slide
    self.skip_reversing = True

    # Drive the curve and sigma 'N' together
    self.play(
        n_comp.animate.set_value(len(components)),
        rate_func=linear,
        run_time=3.0,
    )

    # Cleanup updater before ending the slide
    sigma.remove_updater(sigma_updater)

    # --- End of slide ------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
