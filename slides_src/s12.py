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


@slide(12)
def slide_12(self):
    """
    Slide 12: Ocean spectra.
    - Isometric Cube (Scaled up, centered lower)
    - Inputs enter purely horizontally
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Spectres d'océans")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Usable area below bar --------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    anchor_x = x_left + self.DEFAULT_PAD

    intro = Tex(
        r"Comment calculer les $\omega_i$, $k_i$ et $A_i$ ?",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    intro.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = anchor_x - intro.get_left()[0]
    intro.shift(RIGHT * dx)
    self.play(FadeIn(intro, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25)
    self.next_slide()

    # --- Bullet points ---------------------------------------------------
    items = [
        r"$k_i$ : sont échantillonnés sur un intervalle",
        r"$\omega_i$ : sont déterminés à partir des $k_i$ avec la relation de dispersion",
        r"$A_i$ : sont définis par un spectre d'océan",
    ]
    bullets = make_bullet_list(
        items,
        bullet_color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
        line_gap=0.18,
        left_pad=0.25,
    )
    bullets.next_to(intro, DOWN, buff=0.28, aligned_edge=LEFT)
    dx_b = anchor_x - bullets.get_left()[0]
    bullets.shift(RIGHT * dx_b)
    self.play(FadeIn(bullets, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25)
    self.next_slide()

    # --- ISOMETRIC CUBE SHAPE -----------------------------------------

    # 1. Define Unit Vertices
    sq3_2 = np.sqrt(3) / 2
    v_c = np.array([0.0, 0.0, 0.0])
    v_b = np.array([0.0, -1.0, 0.0])
    v_t = np.array([0.0, 1.0, 0.0])
    v_tl = np.array([-sq3_2, 0.5, 0.0])
    v_tr = np.array([sq3_2, 0.5, 0.0])
    v_bl = np.array([-sq3_2, -0.5, 0.0])
    v_br = np.array([sq3_2, -0.5, 0.0])

    # 2. Create Faces & Lines
    face_left = Polygon(
        v_b,
        v_bl,
        v_tl,
        v_c,
        color=pc.oxfordBlue,
        fill_opacity=0.9,
        stroke_width=0,
    )
    face_right = Polygon(
        v_b,
        v_br,
        v_tr,
        v_c,
        color=pc.oxfordBlue,
        fill_opacity=0.9,
        stroke_width=0,
    )
    face_top = Polygon(
        v_c,
        v_tl,
        v_t,
        v_tr,
        color=pc.oxfordBlue,
        fill_opacity=0.9,
        stroke_width=0,
    )

    lines = (
        VGroup(
            Line(v_b, v_br),
            Line(v_br, v_tr),
            Line(v_tr, v_t),
            Line(v_t, v_tl),
            Line(v_tl, v_bl),
            Line(v_bl, v_b),
            Line(v_b, v_c),
            Line(v_c, v_tl),
            Line(v_c, v_tr),
        )
        .set_color(BLACK)
        .set_stroke(width=4)
    )

    shape = VGroup(VGroup(face_left, face_right, face_top), lines)

    # 3. Scale Up & Position Down
    # Scaling up 2.2x to ensure the left face (height ~1.0 -> ~2.2) fits 3 text items
    shape.scale(1.6)

    # Moving down significantly to center visual weight (-1.2 Y offset)
    cy = -1.8
    shape.move_to([0.0, cy, 0.0])

    shape_title = Tex(
        r"Spectre d'océan",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    shape_title.next_to(shape, UP, buff=0.3)

    self.play(FadeIn(shape), FadeIn(shape_title), run_time=0.5)
    self.wait(0.1)
    self.next_slide()

    # --- Labels on the left (F, U10, theta) --------------------------------

    # Calculate Y positions relative to the shape center
    # The left face goes from Y=-0.5 to Y=+0.5 (in unit scale).
    # After scale 2.2, it goes -1.1 to +1.1.
    # We place labels at +0.6, 0.0, -0.6 relative to center Y.
    y_offset = 0.65

    pos_top = shape.get_center() + np.array([0, y_offset, 0])
    pos_mid = shape.get_center() + np.array([0, 0, 0])
    pos_bot = shape.get_center() + np.array([0, -y_offset, 0])

    # Start X position (Left of the shape)
    start_x = shape.get_left()[0] - 1.0

    lbl_f = MathTex(r"F", color=BLACK, font_size=self.BODY_FONT_SIZE + 6)
    lbl_u10 = MathTex(
        r"U_{10}", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
    )
    lbl_th = MathTex(r"\theta", color=BLACK, font_size=self.BODY_FONT_SIZE + 6)

    lbl_f.move_to([start_x, pos_top[1], 0])
    lbl_u10.move_to([start_x, pos_mid[1], 0])
    lbl_th.move_to([start_x, pos_bot[1], 0])

    labels_left = VGroup(lbl_f, lbl_u10, lbl_th)
    self.play(FadeIn(labels_left, run_time=0.4, shift=LEFT))
    self.next_slide()

    # --- Horizontal Flow into the Shape -------------------------------------

    # Calculate Target X (Inside the left face)
    # The left face center X is roughly shape.x - (sqrt(3)/2 * scale * 0.5)
    # We manually pick an X coordinate inside the blue area
    target_x = shape.get_left()[0] - 0.5

    # We create target points using the SAME Y coordinates as start points
    # This guarantees horizontal movement.
    target_f = [target_x, pos_top[1], 0]
    target_u = [target_x, pos_mid[1], 0]
    target_th = [target_x, pos_bot[1], 0]

    self.play(
        lbl_f.animate.move_to(target_f),
        lbl_u10.animate.move_to(target_u),
        lbl_th.animate.move_to(target_th),
        run_time=0.8,
        rate_func=linear,  # Linear looks more like a mechanical flow
    )

    self.play(FadeOut(labels_left, run_time=0.4))

    # --- Output A_i -----------------------------------------------------
    # Start inside right face
    start_x_right = shape.get_right()[0] + 0.5

    ai = MathTex(r"A_i", color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
    ai.move_to([start_x_right, cy, 0.0])

    self.play(FadeIn(ai, run_time=0.4))
    self.play(ai.animate.shift(RIGHT * 0.5), run_time=0.4)

    self.next_slide()

    # --- Transition to Formula ------------------------------------------
    to_fade = VGroup(*[obj for obj in self.mobjects if obj not in [bar, ai]])
    self.play(FadeOut(to_fade, shift=LEFT))

    # Transform into full formula
    eq_tessendorf_1 = MathTex(
        r"h(x,t) = \sum_i^N A_i\cos(kx-\omega t)",
        font_size=self.BODY_FONT_SIZE + 10,
        color=BLACK,
    )
    eq_tessendorf_1.move_to(ORIGIN)

    self.play(
        ai.animate.move_to(ORIGIN),
    )
    self.play(
        TransformMatchingTex(ai, eq_tessendorf_1),
    )

    self.next_slide()

    # --- Rest of the slide (kept identical) ---
    eq_tessendorf_2 = MathTex(
        r"h(x,t)=\sum_k \tilde{h}(t, k) \exp\left(i k x\right)",
        font_size=self.BODY_FONT_SIZE + 10,
        color=BLACK,
    )
    eq_tessendorf_2.move_to(ORIGIN)

    self.play(
        ReplacementTransform(eq_tessendorf_1, eq_tessendorf_2),
    )
    self.wait(0.1)
    self.next_slide()

    self.play(eq_tessendorf_2.animate.shift(UP * 2.0), run_time=0.4)

    # (Function load_height_data omitted for brevity, assume same as before)
    def load_height_data(csv_rel_path="states_sph/tessendorf_height.csv"):
        # ... (Same loading logic) ...
        csv_path = os.path.join(csv_rel_path)
        data = np.genfromtxt(csv_path, delimiter=";", names=True)
        t_vals = data["t"]
        t0 = float(np.min(t_vals))
        mask_t0 = np.isclose(t_vals, t0)
        data_t0 = data[mask_t0]
        xs_all = data_t0["x"]
        ys_all = data_t0["y"]
        zs_all = data_t0["z"]
        xs_grid = np.unique(xs_all)
        zs_grid = np.unique(zs_all)
        xs_grid.sort()
        zs_grid.sort()
        x_index = {float(x): i for i, x in enumerate(xs_grid)}
        z_index = {float(z): j for j, z in enumerate(zs_grid)}
        H = np.zeros((len(zs_grid), len(xs_grid)))
        for row in data_t0:
            i = x_index[float(row["x"])]
            j = z_index[float(row["z"])]
            H[j, i] = float(row["y"])
        j_slice = int(np.argmin(np.abs(zs_grid - (-1.0))))
        return xs_grid.copy(), H[j_slice, :].copy(), xs_grid, zs_grid, H, t0

    (xs_slice, ys_slice, xs_grid, zs_grid, height_grid, self.t0) = (
        load_height_data()
    )

    y_min_axis = float(np.min(ys_slice))
    y_max_axis = float(np.max(ys_slice))
    x_min_axis = float(np.min(xs_slice))
    x_max_axis = float(np.max(xs_slice))
    if np.isclose(y_min_axis, y_max_axis):
        y_min_axis -= 1.0
        y_max_axis += 1.0
    y_margin_axis = 0.1 * (y_max_axis - y_min_axis)

    axes = Axes(
        x_range=[float(xs_slice[0]), float(xs_slice[-1]), 0.5],
        y_range=[
            y_min_axis - y_margin_axis,
            y_max_axis + y_margin_axis,
            (y_max_axis - y_min_axis) / 4.0,
        ],
        x_length=5 * (x_max_axis - x_min_axis),
        y_length=5 * (y_max_axis - y_min_axis),
        tips=True,
        axis_config={"stroke_width": 2},
    )
    axes.next_to(eq_tessendorf_2, DOWN, buff=2.0)

    graph = VMobject()
    graph.set_stroke(pc.blueGreen, 3)
    points = [axes.c2p(float(x), float(y)) for x, y in zip(xs_slice, ys_slice)]
    graph.set_points_smoothly(points)

    self.play(Create(graph))
    self.next_slide()

    eq_tessendorf_3 = MathTex(
        r"h(\mathbf x,t)=\sum_{\mathbf{k}} \tilde{h}(t, \mathbf{k}) \exp\left( i \mathbf{k}\cdot \mathbf x\right)",
        font_size=self.BODY_FONT_SIZE + 10,
        color=BLACK,
    )
    eq_tessendorf_3.move_to(eq_tessendorf_2.get_center())

    img2 = ImageMobject("Figures/wave_surface_rendered.jpeg")
    img2.scale(0.6)
    img2.next_to(eq_tessendorf_3, DOWN, buff=0.4)

    self.play(
        FadeOut(axes),
        FadeOut(graph),
        FadeIn(img2),
        ReplacementTransform(eq_tessendorf_2, eq_tessendorf_3),
        run_time=0.6,
    )

    self.pause()
    self.clear()
    self.next_slide()
