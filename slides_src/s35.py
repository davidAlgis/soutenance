import csv
import glob
import os

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(35)
def slide_35(self):
    """
    Slide 35: Facteur de modulation.

    Update:
      - Render only particles inside a world-space box to speed up rendering:
        X_CENTER = -0.5, Y_CENTER = -1.0, X_WIDTH = 3.0, Y_WIDTH = 2.0
        (filter is applied on CSV coordinates before mapping to screen).
    """
    # --- Top bar ---
    bar = self._top_bar("Facteur de modulation")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Big equation (split parts so we can surround only the modulation factor) ---
    eq = MathTex(
        r"F_i^A(t) = \frac{m}{dt} \cdot \tau_i(t) \cdot",
        r"(1-\phi_i(t))",
        r"\cdot \left(v_i^A(t) - v_i(t)\right)",
        font_size=60,
        color=BLACK,
    )
    eq.move_to(ORIGIN + DOWN * 0.2)
    self.add(eq)

    self.wait(0.1)
    self.next_slide()

    # --- Highlight (1 - phi_i(t)) with a rectangle ---
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
        r"$\phi_i(t)$ : le facteur de modulation de la i-eme particule",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    explain2 = Tex(
        r"Objectif : particules en contact d'un solide devrait moins subir la force d'Airy",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    explain1.next_to(eq, DOWN, buff=0.5)
    explain2.next_to(explain1, DOWN, buff=0.25)
    self.add(explain1, explain2)

    self.next_slide()

    # --- Keep only objective, move under bar ---
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
    # Particles from CSV (FILTERED BY WORLD-SPACE BOX BEFORE MAPPING)
    # -------------------------------------------------------------------------
    body_top = explain2.get_bottom()[1] - 0.25
    left_x = -config.frame_width / 2.0 + 0.3
    right_x = config.frame_width / 2.0 - 0.3
    bottom_y = -config.frame_height / 2.0 + 0.3

    # Box (world space, CSV coordinates)
    X_CENTER = -0.5
    Y_CENTER = -1.0
    X_WIDTH = 3.0
    Y_WIDTH = 2.0
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
                    am = int(float(row.get("airyMod", 0.0)))
                    # Filter by box BEFORE keeping
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
    else:
        # Fallback cloud (already small)
        for i in range(80):
            xv = (i % 20) * 0.1 - 1.0
            yv = (i // 20) * 0.1 - 1.0
            if (
                xv >= x_box_min
                and xv <= x_box_max
                and yv >= y_box_min
                and yv <= y_box_max
            ):
                xs_all.append(xv)
                ys_all.append(yv)
                types_all.append(0 if i % 3 else 1)
                airy_all.append(0)

    xs = np.array(xs_all, dtype=float)
    ys = np.array(ys_all, dtype=float)
    types_arr = np.array(types_all, dtype=int)
    airy_arr = np.array(airy_all, dtype=int)

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
            pos = map_pos(xs[i], ys[i])
            col = pc.blueGreen if types_arr[i] == 0 else pc.uclaGold
            d = Dot(pos, radius=0.05, color=col)
            d.set_fill(col, opacity=1.0)
            d.set_stroke(col, opacity=1.0, width=0)
            dots.append(d)

        # Appear in 5 batches (guard against tiny sets)
        batches = 5
        per = max(1, len(dots) // batches)
        for k in range(batches):
            chunk = (
                dots[k * per : (k + 1) * per]
                if k < batches - 1
                else dots[k * per :]
            )
            if chunk:
                self.play(
                    LaggedStart(
                        *[GrowFromCenter(d) for d in chunk], lag_ratio=0.05
                    )
                )

    self.next_slide()

    # --- Shrink and move particles to top-right; left label ---
    dots_group = VGroup(*dots) if dots else VGroup()
    if len(dots_group.submobjects) > 0:
        target_center = np.array(
            [
                config.frame_width / 2.0 - 1.6,
                config.frame_height / 2.0 - 2.1,
                0.0,
            ]
        )
        self.play(dots_group.animate.scale(0.45).move_to(target_center))

    left_label = Tex(
        "Phenomene de diffusion :", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    left_label.next_to(explain2, DOWN, buff=0.4)
    left_label.align_to(bar, LEFT).shift(RIGHT * self.DEFAULT_PAD)
    self.add(left_label)

    self.next_slide()

    # --- Slideshow in oxfordBlue frame on the left ---
    frame_w = 5.2
    frame_h = 3.6
    frame_center = left_label.get_center() + DOWN * 2.2
    fr_ul = frame_center + np.array([-frame_w / 2, frame_h / 2, 0.0])
    fr_ur = frame_center + np.array([frame_w / 2, frame_h / 2, 0.0])
    fr_lr = frame_center + np.array([frame_w / 2, -frame_h / 2, 0.0])
    fr_ll = frame_center + np.array([-frame_w / 2, -frame_h / 2, 0.0])

    f_top = Line(fr_ul, fr_ur, color=pc.oxfordBlue, stroke_width=5)
    f_right = Line(fr_ur, fr_lr, color=pc.oxfordBlue, stroke_width=5)
    f_bottom = Line(fr_lr, fr_ll, color=pc.oxfordBlue, stroke_width=5)
    f_left = Line(fr_ll, fr_ul, color=pc.oxfordBlue, stroke_width=5)
    self.play(
        LaggedStart(
            Create(f_top),
            Create(f_right),
            Create(f_bottom),
            Create(f_left),
            lag_ratio=0.1,
        )
    )

    imgs = sorted(
        glob.glob(os.path.join("Figures", "heat_pictures", "heat_sim_*.jpeg"))
    )
    shown = []
    for p in imgs[:20]:
        try:
            im = ImageMobject(p)
            scale = min(
                (frame_w - 0.2) / im.width, (frame_h - 0.2) / im.height
            )
            im.scale(scale)
            im.move_to(frame_center)
            self.play(FadeIn(im))
            shown.append(im)
        except Exception:
            continue

    self.next_slide()

    # Remove frame and images
    # Remove frame and images (use Group, not VGroup, because ImageMobject != VMobject)
    frame_items = [f_top, f_right, f_bottom, f_left, *shown]
    self.play(FadeOut(Group(*frame_items)))

    # --- PDE system ---
    eq_pde = Tex(
        r"$\begin{cases}"
        r"\dfrac{\partial \phi(\mathbf{p},t)}{\partial t} = D\nabla^2 \phi(\mathbf{p},t) \\ "
        r"\phi(\mathbf{p},t) = 1 \quad \forall \mathbf{p}\in \mathcal{S} \\ "
        r"\phi(\mathbf{p},t) = 0 \quad \forall \mathbf{p}\in \partial\Omega"
        r"\end{cases}$",
        font_size=44,
        color=BLACK,
    )
    eq_pde.next_to(left_label, DOWN, buff=0.6).align_to(left_label, LEFT)
    self.add(eq_pde)

    self.next_slide()

    # SPH form
    eq_sph = MathTex(
        r"\frac{d\phi_i(t)}{dt} = \sum_{j} \frac{m}{\rho_j(t)} D \big( \phi_j(t) - \phi_i(t) \big)"
        r"\frac{\mathbf{p}_{ij}(t) \cdot \nabla_i W_{ij}} {\lVert \mathbf{p}_{ij}(t) \rVert^2 + h^2}",
        font_size=44,
        color=BLACK,
    )
    eq_sph.move_to(eq_pde.get_center())
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

    self.next_slide()

    # --- Keep only bar + particles; center and scale particles to fill ---
    self.play(FadeOut(VGroup(explain2, left_label, eq_disc)))
    if len(dots) > 0:
        body_top2 = bar.submobjects[0].get_bottom()[1] - 0.25
        body_bottom2 = -config.frame_height / 2.0 + 0.3
        body_left2 = -config.frame_width / 2.0 + 0.3
        body_right2 = config.frame_width / 2.0 - 0.3
        target_center = np.array(
            [
                (body_left2 + body_right2) * 0.5,
                (body_top2 + body_bottom2) * 0.5,
                0.0,
            ]
        )
        dots_group = VGroup(*dots)
        current_w = max(1e-6, dots_group.width)
        current_h = max(1e-6, dots_group.height)
        desired_w = (body_right2 - body_left2) * 0.92
        desired_h = (body_top2 - body_bottom2) * 0.85
        scale_factor = min(desired_w / current_w, desired_h / current_h)
        self.play(
            dots_group.animate.scale(scale_factor).move_to(target_center)
        )

    self.next_slide()

    # --- Recolor type-0 particles by airyMod (0 -> jellyBean, 1 -> blueGreen) ---
    if len(dots) > 0:
        recolor_anims = []
        for i, d in enumerate(dots):
            if types_arr[i] == 0:
                recolor_anims.append(
                    d.animate.set_color(
                        pc.jellyBean if airy_arr[i] == 0 else pc.blueGreen
                    )
                )
        if recolor_anims:
            self.play(LaggedStart(*recolor_anims, lag_ratio=0.02))
