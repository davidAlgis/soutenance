import csv
import glob
import os
import re

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(35)
def slide_35(self):
    """
    Slide 35: Facteur de modulation.

    Updates in this revision:
    - Heat frames: strictly load existing 'heat_sim_*.jpeg' with numeric suffix <= 1000,
      no frames/rectangles/placeholders -> only the images are shown.
    - AiryMod recolor: continuous interpolation between pc.jellyBean and pc.blueGreen,
      applied only to fluid particles (type==0), fast run_time.
    """
    # --- Top bar ---
    bar = self._top_bar("Facteur de modulation")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Big equation, split to frame only (1 - phi_i) ---
    eq = MathTex(
        r"F_i^A(t) = \frac{m}{dt} \cdot \tau_i(t) \cdot",
        r"(1-\phi_i(t))",
        r"\cdot \left(v_i^A(t) - v_i(t)\right)",
        font_size=60,
        color=BLACK,
    )
    eq.move_to(ORIGIN + DOWN * 0.2)
    self.play(FadeIn(eq))

    self.wait(0.1)
    self.next_slide()

    # --- Surround only the modulation factor (1 - phi_i) ---
    target = eq[1]
    pad = 0.08
    ul = target.get_corner(UL) + (-pad * RIGHT + pad * UP)
    ur = target.get_corner(UR) + (pad * RIGHT + pad * UP)
    lr = target.get_corner(DR) + (pad * RIGHT - pad * UP)
    ll = target.get_corner(DL) + (-pad * RIGHT - pad * UP)
    seg_top = Line(ul, ur, color=BLACK, stroke_width=4)
    seg_right = Line(ur, lr, color=BLACK, stroke_width=4)
    seg_bottom = Line(lr, ll, color=BLACK, stroke_width=4)
    seg_left = Line(ll, ul, color=BLACK, stroke_width=4)
    self.play(
        LaggedStart(
            Create(seg_top),
            Create(seg_right),
            Create(seg_bottom),
            Create(seg_left),
            lag_ratio=0.15,
        )
    )

    # --- Sentences ---
    explain1 = Tex(
        r"$\phi_i(t)$ : le facteur de modulation de la i-ème particule",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    explain2 = Tex(
        r"\mbox{Objectif : les particules en contact d'un solide devrait moins subir la force d'Airy}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    explain1.next_to(eq, DOWN, buff=0.5)
    explain2.next_to(explain1, DOWN, buff=0.25)
    self.play(FadeIn(explain1, explain2))
    self.wait(0.1)
    self.next_slide()

    # --- Keep only objective; move it under the bar, left-aligned with padding ---
    self.play(
        FadeOut(eq),
        FadeOut(seg_top),
        FadeOut(seg_right),
        FadeOut(seg_bottom),
        FadeOut(seg_left),
        FadeOut(explain1),
    )
    explain2.generate_target()
    explain2.target.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (
        bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
    ) - explain2.target.get_left()[0]
    explain2.target.shift(RIGHT * dx)
    self.play(MoveToTarget(explain2))

    # -------------------------------------------------------------------------
    # Particles from CSV (filtered to box to speed up)
    # -------------------------------------------------------------------------
    body_top = explain2.get_bottom()[1] - 0.25
    left_x = -config.frame_width / 2.0 + 0.3
    right_x = config.frame_width / 2.0 - 0.3
    bottom_y = -config.frame_height / 2.0 + 0.3

    # Filter box in world space (CSV coords)
    X_CENTER, Y_CENTER = -0.5, -1.0
    X_WIDTH, Y_WIDTH = 3.0, 2.0
    x_box_min = X_CENTER - X_WIDTH * 0.5
    x_box_max = X_CENTER + X_WIDTH * 0.5
    y_box_min = Y_CENTER - Y_WIDTH * 0.5
    y_box_max = Y_CENTER + Y_WIDTH * 0.5

    csv_path = "states_sph/hybrid_step_0_sph_hybrid.csv"
    xs_all, ys_all, types_all, airy_all = [], [], [], []
    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    xv = float(row["x"])
                    yv = float(row["y"])
                    tv = int(row["type"])
                    am = float(row.get("airyMod", 0.0))
                    if (
                        xv >= x_box_min
                        and xv <= x_box_max
                        and yv >= y_box_min
                        and yv <= y_box_max
                    ):
                        xs_all.append(xv)
                        ys_all.append(yv)
                        types_all.append(tv)
                        airy_all.append(am)
                except Exception:
                    continue

    xs = np.asarray(xs_all, dtype=float)
    ys = np.asarray(ys_all, dtype=float)
    types_arr = np.asarray(types_all, dtype=int)
    airy_arr = np.asarray(airy_all, dtype=float)

    dots = []
    if len(xs) > 0:
        # Map filtered CSV coords to body rectangle
        min_x, max_x = float(xs.min()), float(xs.max())
        min_y, max_y = float(ys.min()), float(ys.max())
        span_x = max(1e-6, max_x - min_x)
        span_y = max(1e-6, max_y - min_y)
        pad_x, pad_y = 0.05, 0.05
        avail_w = (right_x - left_x) * (1.0 - 2 * pad_x)
        avail_h = (body_top - bottom_y) * (1.0 - 2 * pad_y)

        def map_pos(xv, yv):
            x_m = (
                left_x
                + (pad_x * (right_x - left_x))
                + ((xv - min_x) / span_x) * avail_w
            )
            y_m = (
                bottom_y
                + (pad_y * (body_top - bottom_y))
                + ((yv - min_y) / span_y) * avail_h
            )
            return np.array([x_m, y_m, 0.0])

        for i in range(len(xs)):
            tv = types_arr[i]
            # Draw fluids (type==0) in blueGreen, negative types in uclaGold; skip positive non-zero types
            if tv == 0:
                col = pc.blueGreen
            elif tv < 0:
                col = pc.uclaGold
            else:
                continue
            pos = map_pos(xs[i], ys[i])
            d = Dot(pos, radius=0.05, color=col)
            d.set_fill(col, opacity=1.0)
            d.set_stroke(col, opacity=1.0, width=0)
            dots.append(d)

        # All particles appear together quickly (0.5s total)
        self.play(
            AnimationGroup(
                *[GrowFromCenter(d) for d in dots], lag_ratio=0.0, run_time=0.5
            )
        )

    self.next_slide()

    # --- Move particles block to top-right but lower to avoid overlapping the objective
    dots_group = VGroup(*dots) if dots else VGroup()
    if len(dots_group.submobjects) > 0:
        safe_top_y = explain2.get_bottom()[1] - 0.8
        target_center = np.array(
            [config.frame_width / 2.0 - 1.6, safe_top_y, 0.0]
        )
        self.play(dots_group.animate.scale(0.3).move_to(target_center))

    # Left label
    left_label = Tex(
        "Phénomène de diffusion :", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    left_label.next_to(explain2, DOWN, buff=0.4)
    left_label.align_to(bar, LEFT).shift(RIGHT * self.DEFAULT_PAD)
    self.add(left_label)

    self.next_slide()

    # --- Heat simulation on the left (NO border), shift right so fully visible
    max_w, max_h = 5.2, 3.6
    safe_left = -config.frame_width / 2.0 + 1.2  # padding from left edge
    img_center = np.array(
        [safe_left + max_w * 0.5, left_label.get_center()[1] - 2.2, 0.0]
    )

    # Strictly gather existing files heat_sim_*.jpeg with numeric suffix <= 1000
    frame_pat = re.compile(r".*[/\\]heat_sim_(\d+)\.jpeg$", re.IGNORECASE)
    all_candidates = glob.glob(
        os.path.join("Figures", "heat_pictures", "heat_sim_*.jpeg")
    )
    pairs = []
    for p in all_candidates:
        m = frame_pat.match(p)
        if not m:
            continue
        idx = int(m.group(1))
        if idx <= 1000 and os.path.isfile(p):
            pairs.append((idx, p))
    pairs.sort(key=lambda t: t[0])

    shown_imgs = []
    for _, p in pairs[:20]:
        im = ImageMobject(p)
        scale = min(max_w / im.width, max_h / im.height)
        im.scale(scale).move_to(img_center)
        # Show only the image (no extra shapes), then keep for cleanup
        self.play(FadeIn(im))
        shown_imgs.append(im)

    # Remove only the images (no rectangle exists)
    if shown_imgs:
        self.play(FadeOut(Group(*shown_imgs)))

    self.next_slide()

    # --- PDE system (ensure fully in-frame)
    eq_pde = Tex(
        r"$\begin{cases}"
        r"\dfrac{\partial \phi(\mathbf{p},t)}{\partial t} = D\nabla^2 \phi(\mathbf{p},t) \\ "
        r"\phi(\mathbf{p},t) = 1 \quad \forall \mathbf{p}\in \mathcal{S} \\ "
        r"\phi(\mathbf{p},t) = 0 \quad \forall \mathbf{p}\in \partial\Omega"
        r"\end{cases}$",
        font_size=44,
        color=BLACK,
    )
    eq_pde.next_to(left_label, DOWN, buff=0.6)
    safe_left_equ = -config.frame_width / 2.0 + 1.0
    eq_pde.shift(RIGHT * (safe_left_equ - eq_pde.get_left()[0]))
    self.play(FadeIn(eq_pde))

    self.next_slide()

    # SPH form
    eq_sph = MathTex(
        r"\frac{d\phi_i(t)}{dt} = \sum_{j} \frac{m}{\rho_j(t)} D \big( \phi_j(t) - \phi_i(t) \big)"
        r"\frac{\mathbf{p}_{ij}(t) \cdot \nabla_i W_{ij}} {\lVert \mathbf{p}_{ij}(t) \rVert^2 + h^2}",
        font_size=44,
        color=BLACK,
    )
    eq_sph.move_to(eq_pde.get_center())
    eq_sph.shift(
        RIGHT * (safe_left_equ - eq_sph.get_left()[0])
    )  # keep inside slide
    self.play(TransformMatchingTex(eq_pde, eq_sph))

    self.next_slide()

    # Discrete update
    eq_disc = MathTex(
        r"\phi_i(t+dt) = (1-\tilde{s_i})\phi_i(t) + \frac{\tilde{s_i}}{s_i}dt\sum_{j}\xi_{ij}\phi_j(t)",
        font_size=44,
        color=BLACK,
    )
    eq_disc.move_to(eq_sph.get_center())
    self.play(TransformMatchingTex(eq_sph, eq_disc))
    eq_disc.shift(
        RIGHT * (safe_left_equ - eq_disc.get_left()[0])
    )  # keep inside slide

    self.next_slide()

    # --- Keep only bar + particles; center and scale particles to fill body for airyMod coloring ---
    self.play(FadeOut(VGroup(explain2, left_label, eq_disc)))

    if len(dots) > 0:
        body_top2 = bar.submobjects[0].get_bottom()[1] - 0.25
        body_bottom2 = -config.frame_height / 2.0 + 0.3
        body_left2 = -config.frame_width / 2.0 + 0.3
        body_right2 = config.frame_width / 2.0 - 0.3
        target_center2 = np.array(
            [
                (body_left2 + body_right2) * 0.5,
                (body_top2 + body_bottom2) * 0.5,
                0.0,
            ]
        )

        dots_group2 = VGroup(*dots)
        current_w = max(1e-6, dots_group2.width)
        current_h = max(1e-6, dots_group2.height)
        desired_w = (body_right2 - body_left2) * 0.92
        desired_h = (body_top2 - body_bottom2) * 0.85
        scale_factor = min(desired_w / current_w, desired_h / current_h)
        self.play(
            dots_group2.animate.scale(scale_factor).move_to(target_center2)
        )

    if len(dots) > 0:
        # Precompute start and target colors for each dot
        start_colors = []
        target_colors = []

        for i, d in enumerate(dots):
            # Safety guards in case arrays are shorter than dots
            if i >= len(types_arr) or i >= len(airy_arr):
                start_colors.append(None)
                target_colors.append(None)
                continue

            if types_arr[i] != 0:
                start_colors.append(None)
                target_colors.append(None)
                continue

            a = float(airy_arr[i])
            if a < 0.0:
                a = 0.0
            elif a > 1.0:
                a = 1.0

            target_col = interpolate_color(pc.jellyBean, pc.blueGreen, a)
            start_col = d.get_fill_color()

            # If there is no actual change, skip interpolation for this dot
            if start_col == target_col:
                start_colors.append(None)
                target_colors.append(None)
            else:
                start_colors.append(start_col)
                target_colors.append(target_col)

        # Check if there is at least one dot to animate
        if any(c is not None for c in target_colors):
            alpha_tracker = ValueTracker(0.0)
            dot_group = VGroup(*dots)

            def update_colors(mob):
                alpha = alpha_tracker.get_value()
                for i, d in enumerate(dots):
                    sc = start_colors[i]
                    tc = target_colors[i]
                    if sc is None or tc is None:
                        continue
                    col = interpolate_color(sc, tc, alpha)
                    d.set_fill(col, opacity=1.0)
                    d.set_stroke(col, width=0, opacity=1.0)

            dot_group.add_updater(update_colors)
            self.add(dot_group)

            # One single animation for all particles at once
            self.play(
                alpha_tracker.animate.set_value(1.0),
                run_time=2.0,  # keep this reasonably long to avoid tiny clips
            )

            dot_group.remove_updater(update_colors)

    # --- End of slide ---
    self.pause()
    self.clear()
    self.next_slide()
