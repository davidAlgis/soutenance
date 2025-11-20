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
    # Use footer top if available, otherwise approximate
    footer_top = (
        footer.get_top()[1]
        if "footer" in locals()
        else -config.frame_height / 2 + 0.6
    )

    y_top = bar_rect.get_bottom()[1] - 0.2
    y_bottom = footer_top + 0.2

    area_h = y_top - y_bottom
    x_left = -config.frame_width / 2 + 0.6

    # Title
    subtitle = Tex(
        "« Généralisation » des vagues d'Airy :",
        tex_template=self.french_template,
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

    # --- Layout: 3 Rows ----------------------------------------------------
    # Calculate vertical spacing for 3 rows
    # We reserve some space for the subtitle, so we adjust area_h
    y_start_plots = subtitle.get_bottom()[1] - 0.3
    plot_space_h = y_start_plots - y_bottom

    # Height of each plot
    plot_h = min(plot_space_h / 3.2, 1.5)
    plot_w = 7.0  # Fixed width for curves

    # Y positions for the centers of the 3 rows
    y_row1 = y_start_plots - plot_h / 2
    y_row2 = y_row1 - plot_h - 0.3
    y_row3 = y_row2 - plot_h - 0.3

    plot_center_x = x_left + 1.0 + plot_w / 2.0

    # Helper: draw a smooth curve
    def make_function_curve(center, width, height, func, color=pc.blueGreen):
        x_min, x_max = -10.0, 10.0
        n = 300
        X = np.linspace(x_min, x_max, n)
        sx = width / (x_max - x_min)
        y_vis = 4.0  # Vertical clip range
        sy = (height / 2.0) / y_vis

        path = VMobject()
        pts = []
        for x in X:
            y = float(func(x))
            px = (x - x_min) * sx - width / 2.0
            py = np.clip(y, -y_vis, y_vis) * sy
            pts.append([center[0] + px, center[1] + py, 0.0])
        path.set_points_smoothly(pts)
        path.set_stroke(color=color, width=4)
        return path

    # --- Row 1: Wave 1 -----------------------------------------------------
    def func1(x):
        return 0.7 * np.cos(1.5 * x)

    curve1 = make_function_curve(
        [plot_center_x, y_row1, 0], plot_w, plot_h, func1, color=pc.blueGreen
    )

    text1 = MathTex(
        r"h_A^1(x,t)",  # Index 0
        r" = 0.7\cos(1.5\,x + \omega_1 t)",  # Index 1
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    text1[0].set_color(pc.blueGreen)
    text1.next_to(curve1, RIGHT, buff=0.5)

    # --- Row 2: Wave 2 -----------------------------------------------------
    def func2(x):
        return 0.8 * np.cos(0.9 * x)

    curve2 = make_function_curve(
        [plot_center_x, y_row2, 0], plot_w, plot_h, func2, color=pc.orange
    )

    text2 = MathTex(
        r"h_A^2(x,t)",  # Index 0
        r" = 0.8\cos(0.9\,x + \omega_2 t)",  # Index 1
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    text2[0].set_color(pc.orange)
    text2.next_to(curve2, RIGHT, buff=0.5)

    # Show Rows 1 & 2
    self.play(
        Create(curve1),
        Write(text1),
        Create(curve2),
        Write(text2),
        run_time=1.2,
    )
    self.wait(0.1)
    self.next_slide()

    # --- Row 3 Step 1: Copy Row 1 ------------------------------------------
    # Create explicit curve for Row 3 (initially identical to curve 1)
    curve3 = make_function_curve(
        [plot_center_x, y_row3, 0], plot_w, plot_h, func1, color=pc.blueGreen
    )

    text3_step1 = MathTex(
        r"h_T(x,t)",  # Index 0
        r"=",  # Index 1
        r"h_A^1(x,t)",  # Index 2
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).next_to(curve3, RIGHT, buff=0.5)

    # Apply specific colors by index
    text3_step1[0].set_color(pc.blueGreen)  # h_T
    text3_step1[2].set_color(pc.blueGreen)  # h_A^1
    # Align text3 left with text1/text2 for neatness
    text3_step1.align_to(text1, LEFT)

    # Animation: Clone curve1 and move it down
    ghost1 = curve1.copy()
    self.add(ghost1)
    self.play(
        ghost1.animate.move_to(curve3.get_center()),
        Write(text3_step1),
        run_time=0.8,
    )
    self.remove(ghost1)
    self.add(curve3)
    self.wait(0.1)
    self.next_slide()

    # --- Row 3 Step 2: Add Row 2 -------------------------------------------

    # Define the sum function
    def func_sum(x):
        return func1(x) + func2(x)

    # Target curve (Sum)
    curve3_target = make_function_curve(
        [plot_center_x, y_row3, 0],
        plot_w,
        plot_h,
        func_sum,
        color=pc.fernGreen,
    )

    text3_step2 = MathTex(
        r"h_T(x,t)",  # Index 0
        r"=",  # Index 1
        r"h_A^1(x,t)",  # Index 2
        r"+",  # Index 3
        r"h_A^2(x,t)",  # Index 4
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    ).next_to(curve3, RIGHT, buff=0.5)

    # Apply specific colors by index
    text3_step2[0].set_color(pc.fernGreen)  # h_T
    text3_step2[2].set_color(pc.blueGreen)  # h_A^1
    text3_step2[4].set_color(pc.orange)  # h_A^2 (matches your request)

    # Keep the alignment logic from the previous step
    text3_step2.align_to(text1, LEFT)

    # Animation: Clone curve2 and move it down
    ghost2 = curve2.copy()
    self.add(ghost2)

    self.play(
        ghost2.animate.move_to(curve3.get_center()).set_opacity(0),
        Transform(curve3, curve3_target),
        ReplacementTransform(text3_step1, text3_step2),
        run_time=1.0,
    )
    self.remove(ghost2)

    self.wait(0.1)
    self.next_slide()
    # --- Transition to Generalization ---------------------------------------
    self.next_slide()

    # 1. Fade out Row 1 and Row 2 (curves and text)
    # We keep curve3 and text3_step2 for a moment
    self.play(FadeOut(VGroup(curve1, text1, curve2, text2)), run_time=0.4)

    # 2. Setup dynamic objects for the main curve
    # We create an anchor at the current position of Row 3 (old position)
    # This anchor will drive the movement to the center
    sum_anchor = Dot(
        [plot_center_x, y_row3, 0], fill_opacity=0, stroke_opacity=0
    )
    self.add(sum_anchor)

    # Tracker for scaling the curve up when it moves to center
    sum_scale = ValueTracker(1.0)

    # Re-initialize components list matching the previous two rows
    components = [(0.7, 1.5), (0.8, 0.9)]
    n_comp = ValueTracker(len(components))

    # Define the summation logic
    def sum_y_up_to(m_val, x):
        s = 0.0
        # Safe integer cast
        m_int = int(np.clip(m_val, 0, len(components)))
        for i in range(m_int):
            A_i, k_i = components[i]
            s += A_i * np.cos(k_i * x)
        return s

    # Create the "Always Redraw" curve
    # We swap the static 'curve3' with this identical dynamic one attached to the anchor
    dynamic_curve = always_redraw(
        lambda: make_function_curve(
            center=sum_anchor.get_center(),
            width=plot_w * sum_scale.get_value(),
            height=plot_h * sum_scale.get_value(),
            func=lambda x: sum_y_up_to(n_comp.get_value(), x),
            color=pc.fernGreen,
        )
    )

    self.add(dynamic_curve)
    self.remove(curve3)  # Swap is invisible

    # 3. Prepare the Target Destination (CENTERED)
    # x = 0.0 is the horizontal center of the slide
    target_center_y = (
        y_top + y_bottom
    ) * 0.5 + 0.5  # Slightly higher to make room for text

    # --- Sigma label construction ---
    def build_sigma(n_val: int) -> MathTex:
        """
        Build MathTex for the sum formula.
        Colors only h_T in fernGreen, everything else BLACK.
        """
        n_txt = str(int(max(0, n_val)))
        m = MathTex(
            r"h_T(x,t)",  # Index 0
            r" = ",  # Index 1
            r"\sum",  # Index 2
            r"_{i=1}",  # Index 3
            r"^{",  # Index 4
            n_txt,  # Index 5
            r"} A_i\cos\!\left(k_i x - \omega_i t\right)",  # Index 6
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 6,
        )
        m[0].set_color(pc.fernGreen)
        return m

    # Initial Sigma text (N=2)
    sigma = build_sigma(int(n_comp.get_value()))

    # Calculate where the sigma text should end up (Centered horizontally)
    # We place it below the TARGET curve position
    sigma_target_pos = [0.0, target_center_y - 1.8, 0]
    sigma.move_to(sigma_target_pos)

    # 4. Animate Move to Center + Transform Text
    self.play(
        # Move anchor to TRUE CENTER [0, y, 0]
        sum_anchor.animate.move_to([0.0, target_center_y, 0.0]),
        # Scale up slightly
        sum_scale.animate.set_value(1.3),
        # Transform explicit sum "h = h1 + h2" to Sigma notation
        ReplacementTransform(text3_step2, sigma),
        run_time=0.8,
    )

    # 5. Setup Updater for Live Counter
    def sigma_updater(mobj: Mobject) -> None:
        # Keep the exact same center position
        pos = mobj.get_center()
        new_mobj = build_sigma(int(np.floor(n_comp.get_value())))
        new_mobj.move_to(pos)
        mobj.become(new_mobj)

    sigma.add_updater(sigma_updater)

    # 6. Generate Random Components
    rng = np.random.default_rng(42)
    extra = []
    add_count = 28
    for _ in range(add_count):
        A_rand = float(rng.uniform(0.01, 0.1))
        k_rand = float(rng.uniform(0.1, 20.0))
        extra.append((A_rand, k_rand))
    components.extend(extra)

    # Avoid reversing issues on this complex slide
    self.skip_reversing = True

    # 7. Animate the Summation (Curve gets noisy, N increases)
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
