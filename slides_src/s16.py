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


@slide(16)
def slide_16(self):
    """
    Slide 16: Action du fluide sur le solide.
    Minimal fix: group (title, equation) pairs and stack the two pairs vertically
    in each column so that item 2 is beneath 1 (and 4 beneath 3). Remove empty
    Tex spacers to avoid arrange() quirks. All other behavior unchanged.
    """
    # --- Top bar ---
    bar = self._top_bar("Action du fluide sur le solide")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---- Usable area below the bar ----
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    x_center = 0.0
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left

    l1 = Tex(
        r"\mbox{Action du fluide sur le solide approximée par 4 forces appliquée sur le maillage }",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    local_top_buff = 0.38  # margin below the bar
    l1.next_to(self._current_bar, DOWN, buff=local_top_buff, aligned_edge=LEFT)
    l1.shift(RIGHT * ((x_left + self.DEFAULT_PAD) - l1.get_left()[0]))

    l2 = Tex(
        r"du solide :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l2.shift(RIGHT * ((x_left + self.DEFAULT_PAD) - l2.get_left()[0]))

    intro_group = VGroup(l1, l2)
    self.play(
        FadeIn(intro_group, run_time=0.35, shift=RIGHT * self.SHIFT_SCALE)
    )

    # ========= 4 forces layout (Tex only) =========
    # Left column --------------------------------------------------------------
    title1 = Tex(r"1.\; Gravité :", color=BLACK, font_size=self.BODY_FONT_SIZE)
    title1.set_color_by_tex("Gravité", pc.apple)
    eq1 = MathTex(
        r"\mathbf{F}_g = -m\,\mathbf{g}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 6,
        tex_to_color_map={r"\mathbf{F}_g": pc.apple},
    )
    left_block1 = VGroup(title1, eq1).arrange(
        DOWN, buff=0.22, center=False, aligned_edge=LEFT
    )

    title2 = Tex(
        r"2.\; Poussée d'Archimède :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    title2.set_color_by_tex("Poussée", pc.tiffanyBlue)
    eq2 = MathTex(
        r"\mathbf{F}_b = V_w\,\rho_w\,\mathbf{g}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 6,
        tex_to_color_map={r"\mathbf{F}_b": pc.tiffanyBlue},
    )
    left_block2 = VGroup(title2, eq2).arrange(
        DOWN, buff=0.22, center=False, aligned_edge=LEFT
    )

    left_col = VGroup(left_block1, left_block2).arrange(
        DOWN, buff=0.40, center=False, aligned_edge=LEFT
    )

    # Right column -------------------------------------------------------------
    title3 = Tex(
        r"3.\; Traînée eau :", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    title3.set_color_by_tex("Traînée", pc.heliotropeMagenta)
    eq3 = MathTex(
        r"\mathbf{F}_w"
        r" = -\tfrac{1}{2}\,C_d^w\,\rho_w\,A_i^{\perp}\,"
        r"\|\mathbf{v}^w_{i,\mathrm{rel}}\|\,\mathbf{v}^w_{i,\mathrm{rel}}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE - 2,
        tex_to_color_map={r"\mathbf{F}_w": pc.heliotropeMagenta},
    )
    right_block1 = VGroup(title3, eq3).arrange(
        DOWN, buff=0.22, center=False, aligned_edge=LEFT
    )

    title4 = Tex(
        r"4.\; Traînée air :", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    title4.set_color_by_tex("Traînée", pc.jellyBean)
    eq4 = MathTex(
        r"\mathbf{F}_a"
        r" = -\tfrac{1}{2}\,C_d^a\,\rho_a\,A_i^{\perp}\,"
        r"\|\mathbf{v}^a_{i,\mathrm{rel}}\|\,\mathbf{v}^a_{i,\mathrm{rel}}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE - 2,
        tex_to_color_map={r"\mathbf{F}_a": pc.jellyBean},
    )
    right_block2 = VGroup(title4, eq4).arrange(
        DOWN, buff=0.22, center=False, aligned_edge=LEFT
    )

    right_col = VGroup(right_block1, right_block2).arrange(
        DOWN, buff=0.40, center=False, aligned_edge=LEFT
    )

    # Put columns side by side and center them in the remaining area
    col_gap = 1.2
    forces_group = VGroup(left_col, right_col).arrange(
        RIGHT, buff=col_gap, aligned_edge=UP
    )

    # --- Center in the remaining space below l2 (both horizontally & vertically)
    rem_top = l2.get_bottom()[1] - 0.40
    rem_bot = y_bottom + 0.60
    rem_h = max(1.5, rem_top - rem_bot)
    rem_y_center = (rem_top + rem_bot) * 0.5

    forces_group.move_to([x_center, rem_y_center, 0.0])
    self.play(FadeIn(forces_group, run_time=0.45, shift=UP * self.SHIFT_SCALE))

    # ========= Wait, then remove 3 lines and re-center forces higher =========
    self.next_slide()
    self.play(FadeOut(intro_group, run_time=0.25))

    # Recompute the available area when the intro text is gone (use almost full body)
    new_top = y_top
    new_bot = y_bottom + 0.60
    new_center_y = (new_top + new_bot) * 0.5 + 1.0

    self.play(
        forces_group.animate.move_to([x_center, new_center_y, 0.0]),
        run_time=0.35,
    )

    # ========= Animated water + centered boat beneath the forces =========
    gap_below_forces = 0.35
    min_sea_height = 2.2
    sea_top = (
        min(left_col.get_bottom()[1], right_col.get_bottom()[1])
        - gap_below_forces
    )
    sea_bot = y_bottom
    sea_h = sea_top - sea_bot
    if sea_h < min_sea_height:
        sea_bot = sea_top - min_sea_height
        sea_h = min_sea_height

    # Choose a safe wave baseline inside the sea box
    y0 = sea_bot + 0.55 * sea_h

    t_tracker = ValueTracker(0.0)
    x_min = x_left + 0.5
    x_max = x_right - 0.5
    amp = 0.10
    k = 0.7

    def make_water():
        xs = np.linspace(x_min, x_max, 600)
        ys = y0 + amp * np.cos(k * xs + t_tracker.get_value())
        pts = np.column_stack([xs, ys, np.zeros_like(xs)])
        m = VMobject(stroke_color=pc.blueGreen, stroke_width=6)
        m.set_points_smoothly([*map(lambda p: np.array(p), pts)])
        m.set_z_index(1)  # under the boat
        return m

    water = always_redraw(make_water)
    self.add(water)
    self.play(
        t_tracker.animate.increment_value(2 * PI),
        rate_func=linear,
        run_time=2.6,
    )

    # Centered boat polygon (foreground)
    boat_local = [
        [-1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 1.0, 0.0],
        [0.5, 1.0, 0.0],
        [0.0, 1.5, 0.0],
        [-0.5, 1.0, 0.0],
        [-2.0, 1.0, 0.0],
    ]
    boat = Polygon(
        *[np.array(p) for p in boat_local],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
        stroke_width=3,
    )
    boat.scale(0.9)
    boat_center = [0.0, y0 + 0.35, 0.0]
    boat.move_to(boat_center)  # slightly above the wave baseline
    boat.set_z_index(10)
    self.add(boat)
    self.add_foreground_mobject(boat)

    self.play(
        t_tracker.animate.increment_value(2 * PI),
        rate_func=linear,
        run_time=2.6,
    )

    # ========= Force arrows (foreground), colored as requested =========
    keel = boat.get_bottom()
    deck = boat.get_top()

    g_arrow = Arrow(
        start=[boat_center[0], boat_center[1] - 0.1, 0],
        end=[boat_center[0], boat_center[1] - 2.0, 0],
        color=pc.apple,
        stroke_width=6,
        tip_length=0.18,
    ).set_z_index(15)
    g_lbl = (
        MathTex(r"\mathbf{F}_g", color=pc.apple, font_size=self.BODY_FONT_SIZE)
        .next_to(g_arrow, RIGHT, buff=0.10)
        .set_z_index(15)
    )

    b_arrow = Arrow(
        start=[boat_center[0] - 0.3, boat_center[1] - 0.6, 0],
        end=[boat_center[0] - 0.5, boat_center[1] + 1.3, 0],
        color=pc.tiffanyBlue,
        stroke_width=6,
        tip_length=0.18,
    ).set_z_index(15)
    b_lbl = (
        MathTex(
            r"\mathbf{F}_b",
            color=pc.tiffanyBlue,
            font_size=self.BODY_FONT_SIZE,
        )
        .next_to(b_arrow, LEFT, buff=0.10)
        .set_z_index(15)
    )

    a_arrow_end = [boat_center[0] - 1.7, boat_center[1] - 0.6, 0]
    a_arrow = Arrow(
        start=[boat_center[0] + 0.5, boat_center[1] + 0.1, 0],
        end=a_arrow_end,
        color=pc.jellyBean,
        stroke_width=6,
        stroke_opacity=1.0,
        tip_length=0.18,
    ).set_z_index(15)
    a_lbl = (
        MathTex(
            r"\mathbf{F}_a", color=pc.jellyBean, font_size=self.BODY_FONT_SIZE
        )
        .next_to(a_arrow_end, LEFT, buff=0.10)
        .set_z_index(15)
    )
    w_arrow_end = [boat_center[0] + 0.7, boat_center[1] + 0.7, 0]
    w_arrow = Arrow(
        start=[boat_center[0] - 0.5, boat_center[1] - 0.6, 0],
        end=w_arrow_end,
        color=pc.heliotropeMagenta,
        stroke_width=6,
        tip_length=0.18,
    ).set_z_index(15)
    w_lbl = (
        MathTex(
            r"\mathbf{F}_w",
            color=pc.heliotropeMagenta,
            font_size=self.BODY_FONT_SIZE,
        )
        .next_to(w_arrow_end, RIGHT, buff=0.10)
        .set_z_index(15)
    )

    self.add_foreground_mobjects(
        g_arrow, b_arrow, a_arrow, w_arrow, g_lbl, b_lbl, a_lbl, w_lbl
    )
    self.play(
        LaggedStart(
            FadeIn(g_arrow),
            FadeIn(g_lbl),
            FadeIn(b_arrow),
            FadeIn(b_lbl),
            FadeIn(a_arrow),
            FadeIn(a_lbl),
            FadeIn(w_arrow),
            FadeIn(w_lbl),
            lag_ratio=0.15,
            run_time=1.2,
        )
    )

    # --- End slide ---
    self.pause()
    self.clear()
    self.next_slide()
