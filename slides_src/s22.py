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


@slide(22)
def slide_22(self):
    """
    Slide 22 — Incompressibilité et estimation de densité
    CSV expected at states_sph/particles.csv with header: Particle,X,Y in [0,1]^2.
    """
    # ---------- Top bar ----------
    bar = self._top_bar("Incompressibilité et estimation de densité")
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

    # ---- Palette fallbacks ----
    import csv

    import numpy as np

    blueGreen = getattr(pc, "blueGreen", BLUE_D)
    jellyBean = getattr(pc, "jellyBean", RED_D)
    fernGreen = getattr(pc, "fernGreen", GREEN_D)
    oxfordBlue = getattr(pc, "oxfordBlue", BLUE_E)

    # ---------- Intro (aligned left) ----------
    intro = VGroup()
    # Display prefix, then (after next_slide) replace it by the full sentence.

    pos = [x_left + 0.01 * area_w, y_top - 0.55, 0]
    anchor_left = [x_left, 0, 0]

    # Prefix (already positioned with your existing pos/anchor_left)
    t_prefix = (
        Tex(
            "Propriété essentielle à l'eau : ",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        .move_to(pos)
        .align_to(anchor_left, LEFT)
    )

    self.play(FadeIn(t_prefix, run_time=0.3))
    self.wait(0.1)
    self.next_slide()

    # Suffix appended on the right of the existing prefix (no rewrite of the beginning)
    t_suffix = Tex(
        "~l'incompressibilité.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    t_suffix.next_to(t_prefix, RIGHT, buff=0.1).align_to(t_prefix, DOWN)

    # Animate only the new part
    self.play(Write(t_suffix, run_time=0.35))

    self.wait(0.1)
    self.next_slide()

    # --- Bullets (using utils.make_bullet_list) ---------------------------------
    bullet_items = [
        r"Densité constante : $|\hat{\rho}-\rho_0| \rightarrow 0$",
        r"La somme des volumes des particules reste constante $\nabla \cdot v = 0$",
    ]
    bullets = make_bullet_list(
        bullet_items,
        bullet_color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
        line_gap=0.28,
        left_pad=0.25,
    )
    bullets.next_to(t_prefix, DOWN, buff=0.5, aligned_edge=LEFT)
    bullets.align_to(t_prefix, LEFT)

    self.play(FadeIn(bullets), run_time=0.3)
    self.wait(0.1)
    self.next_slide()

    t2 = Tex(
        "L'estimation de la densité $\\rho$ au c\\oe ur de SPH.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    t2.next_to(bullets, DOWN, buff=1.5).align_to(t_prefix, LEFT)
    intro.add(t_prefix, t_suffix, bullets, t2)

    self.play(FadeIn(t2, shift=UP, run_time=0.35))
    self.next_slide()

    # ---------- Clear intro (keep bar) ----------
    self.play(FadeOut(intro, run_time=0.3))

    # ---------- Two columns (right larger) ----------
    sep_x = x_left + 0.42 * area_w
    separator = Line(
        [sep_x, y_bottom, 0], [sep_x, y_top, 0], color=BLACK, stroke_width=6
    )
    self.play(Create(separator), run_time=0.25)

    left_center = np.array([x_left + 0.21 * area_w, (y_top + y_bottom) / 2, 0])
    right_center = np.array(
        [x_left + 0.71 * area_w, (y_top + y_bottom) / 2, 0]
    )
    left_w, right_w = sep_x - x_left - 0.2, x_right - sep_x - 0.2
    left_h, right_h = area_h - 0.2, area_h - 0.2

    # ---------- Load 30 particles ----------
    pts01 = []
    try:
        with open(
            "states_sph/particles.csv", "r", newline="", encoding="utf-8"
        ) as f:
            reader = csv.DictReader(f)
            for row in reader:
                pts01.append((float(row["X"]), float(row["Y"])))
                if len(pts01) >= 30:
                    break
    except Exception:
        rng = np.random.default_rng(22)
        pts01 = [
            (float(rng.uniform()), float(rng.uniform())) for _ in range(30)
        ]
    if not pts01:
        pts01 = [(0.5, 0.5)] * 30

    # Map [0,1]^2 to right column
    pad = 0.1
    rc_left = right_center[0] - right_w / 2 + pad
    rc_right = right_center[0] + right_w / 2 - pad
    rc_bottom = right_center[1] - right_h / 2 + pad
    rc_top = right_center[1] + right_h / 2 - pad
    rc_w, rc_h = rc_right - rc_left, rc_top - rc_bottom

    def to_world(p01):
        return np.array(
            [rc_left + p01[0] * rc_w, rc_bottom + p01[1] * rc_h, 0.0]
        )

    Pw = [to_world(p) for p in pts01]
    r_vis = min(rc_w, rc_h) / 60.0
    dots = [
        Dot(p, radius=r_vis, color=blueGreen, fill_opacity=1.0) for p in Pw
    ]
    labels = [
        Tex(f"{i+1}", color=BLACK, font_size=self.BODY_FONT_SIZE - 10)
        .scale(0.7)
        .next_to(dots[i], UP, buff=0.02)
        for i in range(len(dots))
    ]

    self.play(
        LaggedStart(
            *[GrowFromCenter(d) for d in dots], lag_ratio=0.04, run_time=0.9
        )
    )
    self.play(
        LaggedStart(
            *[FadeIn(lb, shift=UP * 0.07) for lb in labels],
            lag_ratio=0.02,
            run_time=0.45,
        )
    )
    self.next_slide()

    # ---------- Target particle (3rd) + left equation placeholder ----------
    target_idx = min(2, len(dots) - 1)
    self.play(
        *[
            (
                dots[i].animate.set_color(jellyBean).set_fill(jellyBean, 1.0)
                if i == target_idx
                else dots[i].animate.set_color(BLACK).set_fill(BLACK, 1.0)
            )
            for i in range(len(dots))
        ],
        run_time=0.6,
    )

    eq_pos = np.array([left_center[0], left_center[1] - 0.65 * left_h / 2, 0])
    eq = MathTex(
        r"\rho_3 \;=\; ?", color=BLACK, font_size=self.BODY_FONT_SIZE + 12
    ).move_to(eq_pos)
    self.play(Write(eq), run_time=0.35)
    self.next_slide()

    # ---------- Neighborhood circle + diagonal h double-arrow ----------
    center = dots[target_idx].get_center()
    h_radius = 15.0 * r_vis
    circle = DashedVMobject(
        Circle(
            radius=h_radius, arc_center=center, color=BLACK, stroke_width=4
        ),
        num_dashes=80,
        dashed_ratio=0.55,
    )
    self.play(Create(circle), run_time=0.45)

    # diagonal ↕ arrow to top-right from center to radius
    diag = (h_radius / np.sqrt(2.0)) * np.array([1.0, 1.0, 0.0])
    h_arrow = DoubleArrow(
        center,
        center + diag,
        color=BLACK,
        stroke_width=6,
        tip_length=0.16,
        buff=0.0,
    )
    self.play(Create(h_arrow), run_time=0.25)
    # place 'h' next to (not on) the arrow
    h_tex = Tex("h", color=BLACK, font_size=self.BODY_FONT_SIZE).next_to(
        h_arrow, RIGHT, buff=0.08
    )
    self.play(Write(h_tex), run_time=0.2)

    # ---------- Four nearest neighbors (plain mass sum, break line every 2 terms) ----------
    dists = [
        (i, float(np.linalg.norm(dots[i].get_center() - center)))
        for i in range(len(dots))
        if i != target_idx
    ]
    dists.sort(key=lambda t: t[1])
    nn_indices = [i for i, _ in dists[:5]]

    def eq_simple_lines(taken):
        if not taken:
            s = r"\rho_3 \;=\; ?"
        else:
            parts = [rf"m_{{{k+1}}}" for k in taken]
            rows = [
                " + ".join(parts[i : i + 2]) for i in range(0, len(parts), 2)
            ]
            if len(rows) == 1:
                s = rf"\rho_3 \;=\; {rows[0]}"
            else:
                body = r" \\ &+ ".join(rows)
                s = rf"\begin{{aligned}} \rho_3 &= {body} \end{{aligned}}"
        return MathTex(
            s, color=BLACK, font_size=self.BODY_FONT_SIZE + 12
        ).move_to(eq_pos)

    taken = []
    for k in nn_indices:
        p = dots[k].get_center()
        L = Line(center, p, color=GRAY, stroke_width=4)
        self.play(Create(L), run_time=0.25)
        self.play(
            dots[k].animate.set_color(blueGreen).set_fill(blueGreen, 1.0),
            run_time=0.15,
        )
        taken.append(k)
        self.play(Transform(eq, eq_simple_lines(taken)), run_time=0.25)
        self.play(Uncreate(L), run_time=0.2)

    self.next_slide()

    # ---------- Reset colors & equation (smaller font) ----------
    self.play(
        *[
            (
                dots[i].animate.set_color(jellyBean).set_fill(jellyBean, 1.0)
                if i == target_idx
                else dots[i].animate.set_color(BLACK).set_fill(BLACK, 1.0)
            )
            for i in range(len(dots))
        ],
        run_time=0.5,
    )
    self.play(
        Transform(
            eq,
            MathTex(
                r"\rho_3 \;=\; ?",
                color=BLACK,
                font_size=self.BODY_FONT_SIZE + 4,
            ).move_to(eq_pos),
        ),
        run_time=0.25,
    )

    # ---------- Gaussian at top-left (axes intersect at origin, area gradient fill) ----------
    ax_center = np.array(
        [left_center[0] - 0.18 * left_w, left_center[1] + 0.18 * left_h, 0]
    )
    x_len = 0.55 * left_w
    y_len = 0.34 * left_h
    x_y_axis = 0.5 * x_len
    x_axis = Arrow(
        ax_center - np.array([0.05 * x_len, 0, 0]),
        ax_center + np.array([x_len, 0, 0]),
        stroke_width=3,
        buff=0.0,
        color=BLACK,
    )
    y_axis = Arrow(
        ax_center + np.array([x_y_axis, 0, 0]),
        ax_center + np.array([x_y_axis, y_len, 0]),
        stroke_width=3,
        buff=0.0,
        color=BLACK,
    )
    x_lbl = Tex("r", color=BLACK, font_size=self.BODY_FONT_SIZE - 6).next_to(
        x_axis, RIGHT, buff=0.05
    )
    y_lbl = Tex("W", color=BLACK, font_size=self.BODY_FONT_SIZE - 6).next_to(
        ax_center + np.array([x_y_axis, y_len, 0]), RIGHT, buff=0.05
    )

    def Wnorm(x):
        return np.exp(-(x * x) / (0.45 * 0.45))

    nS = 160
    xs = np.linspace(-1.0, 1.0, nS)
    pts_curve = [
        ax_center
        + np.array([((x + 1) / 2) * x_len, Wnorm(x) * 0.8 * y_len, 0.0])
        for x in xs
    ]
    curve = (
        VMobject(stroke_width=6)
        .set_points_smoothly(pts_curve)
        .set_color(BLACK)
    )

    # vertical-gradient-like fill under curve (via thin strips)
    strips = []
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        X0 = ax_center + np.array([((x0 + 1) / 2) * x_len, 0, 0])
        X1 = ax_center + np.array([((x1 + 1) / 2) * x_len, 0, 0])
        Y0 = ax_center + np.array(
            [((x0 + 1) / 2) * x_len, Wnorm(x0) * 0.8 * y_len, 0]
        )
        Y1 = ax_center + np.array(
            [((x1 + 1) / 2) * x_len, Wnorm(x1) * 0.8 * y_len, 0]
        )
        poly = Polygon(X0, X1, Y1, Y0, stroke_width=0)
        h_avg = 0.5 * (Wnorm(x0) + Wnorm(x1))
        poly.set_fill(
            interpolate_color(blueGreen, jellyBean, h_avg), opacity=0.75
        )
        strips.append(poly)
    fill_group = VGroup(*strips)

    kernel_label = (
        MathTex(
            r"W(r)=\frac{1}{h\pi}\exp\!\left(-\frac{r^{2}}{h^{2}}\right)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE - 6,
        )
        .next_to(y_axis, UP, buff=0.2)
        .align_to(y_axis, LEFT)
    )

    self.play(FadeIn(VGroup(x_axis, y_axis, x_lbl, y_lbl), run_time=0.25))
    self.play(FadeIn(fill_group, run_time=0.35))
    # self.play(Create(curve), run_time=0.6)
    self.play(FadeIn(kernel_label), run_time=0.25)

    # Helper: color from distance (0..h) mapped to gradient (blueGreen -> jellyBean upward)
    def color_for_r(dist, h):
        t = np.clip(dist / h, 0.0, 1.0)
        return interpolate_color(jellyBean, blueGreen, t)

    # Weighted sum with 4-NN
    def eq_weighted_lines(taken):
        if not taken:
            s = r"\rho_3 \;=\; ?"
        else:
            parts = [rf"m_{{{k+1}}}W(r_{{3,{k+1}}},h)" for k in taken]
            rows = [
                " + ".join(parts[i : i + 2]) for i in range(0, len(parts), 2)
            ]
            if len(rows) == 1:
                s = rf"\rho_3 \;=\; {rows[0]}"
            else:
                body = r" \\ &+ ".join(rows)
                s = rf"\begin{{aligned}} \rho_3 &= {body} \end{{aligned}}"
        return MathTex(s, color=BLACK, font_size=self.BODY_FONT_SIZE).move_to(
            eq_pos
        )

    taken_w = []
    x_line_len = 0.9 * x_len
    line_y_under = ax_center[1] - 0.06 * y_len
    for k in nn_indices:
        p = dots[k].get_center()
        r = float(np.linalg.norm(p - center))
        L = Line(center, p, color=oxfordBlue, stroke_width=5)
        self.play(Create(L), run_time=0.25)

        # color neighbor by kernel value
        self.play(
            dots[k]
            .animate.set_color(color_for_r(r, h_radius))
            .set_fill(color_for_r(r, h_radius), 1.0),
            run_time=0.2,
        )

        # move the line below the x-axis keeping its length
        lx = np.clip((r / h_radius) * x_line_len, 0.0, x_line_len)
        L_dest = Line(
            [ax_center[0] + x_y_axis, line_y_under, 0],
            [ax_center[0] + x_y_axis + lx, line_y_under, 0],
            color=oxfordBlue,
            stroke_width=5,
        )
        self.play(Transform(L, L_dest), run_time=0.25)

        taken_w.append(k)
        self.play(Transform(eq, eq_weighted_lines(taken_w)), run_time=0.25)
        self.play(Uncreate(L), run_time=0.2)
    self.wait(0.1)
    self.next_slide()

    # ---------- Remove right column; center the equation ----------
    right_group = VGroup(
        *dots,
        *labels,
        circle,
        h_arrow,
        h_tex,
        separator,
        x_axis,
        y_axis,
        x_lbl,
        y_lbl,
        fill_group,
        kernel_label,
    )
    self.play(FadeOut(right_group), run_time=0.45)

    eq_center = np.array([x_left + 0.5 * area_w, (y_top + y_bottom) / 2, 0])
    self.play(eq.animate.move_to(eq_center), run_time=0.4)

    # Transform to generic neighbor sum (voisins)
    eq1 = MathTex(
        r"\rho_i \;=\; \sum_{j\in\text{voisins}} m_j\, W(r_{ij},h)",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 24,
    ).move_to(eq_center)
    self.play(Transform(eq, eq1), run_time=0.55)
    self.next_slide()

    # Transform to compact notation
    eq2 = MathTex(
        r"\rho_i \;=\; \sum_{j} m_j\, W_{ij}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 24,
    ).move_to(eq_center)
    self.play(Transform(eq, eq2), run_time=0.5)
    self.next_slide()
    self.pause()
    self.clear()
