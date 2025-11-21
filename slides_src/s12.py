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
    - Top bar "Spectres d'océans"
    - Isometric Cube visualization (Black lines, OxfordBlue fill)
    - Input variables entering from the Left Face
    - A_i outputting from the Right Face
    - Transition to Tessendorf equations and graph
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Spectres d'océans")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Usable area below bar --------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    # Left anchor to align body content with the bar
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
    # Wait for user
    self.next_slide()

    # --- Bullet points with LaTeX symbols --------------------------------
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
    # Stack bullets under the intro, left-aligned to the same anchor
    bullets.next_to(intro, DOWN, buff=0.28, aligned_edge=LEFT)
    dx_b = anchor_x - bullets.get_left()[0]
    bullets.shift(RIGHT * dx_b)
    self.play(FadeIn(bullets, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25)

    # Wait for user
    self.next_slide()

    # --- ISOMETRIC CUBE SHAPE -----------------------------------------

    # 1. Define Vertices based on your coordinates
    sq3_2 = np.sqrt(3) / 2
    v_c = np.array([0.0, 0.0, 0.0])  # Center
    v_b = np.array([0.0, -1.0, 0.0])  # Bottom
    v_t = np.array([0.0, 1.0, 0.0])  # Top
    v_tl = np.array([-sq3_2, 0.5, 0.0])  # Top-Left
    v_tr = np.array([sq3_2, 0.5, 0.0])  # Top-Right
    v_bl = np.array([-sq3_2, -0.5, 0.0])  # Bottom-Left
    v_br = np.array([sq3_2, -0.5, 0.0])  # Bottom-Right

    # 2. Create Filled Faces (oxfordBlue)
    # We draw polygons for the faces to create the "inside" color
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

    faces = VGroup(face_left, face_right, face_top)

    # 3. Create Lines (Black) based on your specific segments
    lines = (
        VGroup(
            Line(v_b, v_br),
            Line(v_br, v_tr),
            Line(v_tr, v_t),
            Line(v_t, v_tl),
            Line(v_tl, v_bl),
            Line(v_bl, v_b),
            Line(v_b, v_c),  # Y - vertical
            Line(v_c, v_tl),  # Y - left
            Line(v_c, v_tr),  # Y - right
        )
        .set_color(BLACK)
        .set_stroke(width=4)
    )

    shape = VGroup(faces, lines)

    # Center the shape roughly in the middle of the free area, slightly lower
    cy = (y_top + y_bottom) * 0.5 - 0.5
    shape.move_to([0.0, cy, 0.0])

    shape_title = Tex(
        r"Spectre d'océan",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    shape_title.next_to(shape, UP, buff=0.2)

    self.play(FadeIn(shape), FadeIn(shape_title), run_time=0.5)

    # Wait for user
    self.next_slide()

    # --- Labels on the left: U_10, F, theta --------------------------------
    # Position them relative to the cube
    left_x = shape.get_left()[0] - 1.2
    y_span = shape.height

    # Align roughly with top/mid/bot of the left face
    y_top_lbl = cy + 0.5
    y_mid_lbl = cy
    y_bot_lbl = cy - 0.5

    lbl_u10 = MathTex(
        r"U_{10}", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
    )
    lbl_f = MathTex(r"F", color=BLACK, font_size=self.BODY_FONT_SIZE + 6)
    lbl_th = MathTex(r"\theta", color=BLACK, font_size=self.BODY_FONT_SIZE + 6)

    lbl_u10.move_to([left_x, y_mid_lbl, 0.0])
    lbl_f.move_to([left_x, y_top_lbl, 0.0])
    lbl_th.move_to([left_x, y_bot_lbl, 0.0])

    labels_left = VGroup(lbl_f, lbl_u10, lbl_th)
    self.play(FadeIn(labels_left, run_time=0.4, shift=LEFT))

    # Wait for user
    self.next_slide()

    # --- Flow into the shape (Left Face), disappear, and show A_i (Right Face) ---

    # Target: Center of the Left Face
    # The left face is bounded by B, BL, TL, C.
    # Geometric center of that face relative to shape center:
    # X = (-sqrt(3)/2 + 0)/2 ~ -0.43 relative to center
    # Y = (-0.5 + 0.5 - 1 + 0)/4 ... roughly -0.25 relative to center

    # We use coordinates relative to the shape's current position
    # Left Face Center approximation
    target_face_left = shape.get_center() + np.array([-sq3_2 * 0.6, -0.25, 0])

    self.play(
        lbl_f.animate.move_to(target_face_left),
        lbl_u10.animate.move_to(target_face_left),
        lbl_th.animate.move_to(target_face_left),
        run_time=0.8,
    )
    # Disappear as if absorbed by the shape
    self.play(FadeOut(labels_left, run_time=0.35))

    # A_i appears on the RIGHT Face and slides out
    # Right Face Center approximation
    start_face_right = shape.get_center() + np.array([sq3_2 * 0.6, -0.25, 0])

    ai = MathTex(r"A_i", color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
    ai.move_to(start_face_right)

    self.play(FadeIn(ai, run_time=0.3))
    self.play(ai.animate.shift(RIGHT * 1.5), run_time=0.4)

    self.next_slide()

    # --- Transition to Formula ------------------------------------------
    to_fade = VGroup(*[obj for obj in self.mobjects if obj not in [bar, ai]])
    self.play(FadeOut(to_fade, shift=LEFT))

    # --- Transform into full formula (MathTex split into parts) ---
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

    # --- Load Data Logic (Kept exactly as is) ---------------------------
    def load_height_data(csv_rel_path="states_sph/tessendorf_height.csv"):
        """
        Load the CSV file and return grid data.
        """
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

        # Build the height grid H[z_index, x_index]
        x_index = {float(x): i for i, x in enumerate(xs_grid)}
        z_index = {float(z): j for j, z in enumerate(zs_grid)}
        H = np.zeros((len(zs_grid), len(xs_grid)))

        for row in data_t0:
            i = x_index[float(row["x"])]
            j = z_index[float(row["z"])]
            H[j, i] = float(row["y"])

        # Take the slice z = -1 (or the closest available z)
        j_slice = int(np.argmin(np.abs(zs_grid - (-1.0))))
        xs_slice = xs_grid.copy()
        ys_slice = H[j_slice, :].copy()

        return xs_slice, ys_slice, xs_grid, zs_grid, H, t0

    # Load data from CSV
    (
        xs_slice,
        ys_slice,
        xs_grid,
        zs_grid,
        height_grid,
        self.t0,
    ) = load_height_data()

    # Draw the 2D graph y = h(x, z = -1, t0).
    y_min_axis = float(np.min(ys_slice))
    y_max_axis = float(np.max(ys_slice))
    x_min_axis = float(np.min(xs_slice))
    x_max_axis = float(np.max(xs_slice))
    if np.isclose(y_min_axis, y_max_axis):
        y_min_axis -= 1.0
        y_max_axis += 1.0
    y_margin_axis = 0.1 * (y_max_axis - y_min_axis)
    scale_4_screen = 5
    axes = Axes(
        x_range=[float(xs_slice[0]), float(xs_slice[-1]), 0.5],
        y_range=[
            y_min_axis - y_margin_axis,
            y_max_axis + y_margin_axis,
            (y_max_axis - y_min_axis) / 4.0,
        ],
        x_length=scale_4_screen * (x_max_axis - x_min_axis),
        y_length=scale_4_screen * (y_max_axis - y_min_axis),
        tips=True,
        axis_config={"stroke_width": 2},
    )
    axes.next_to(eq_tessendorf_2, DOWN, buff=2.0)

    # Build the graph from discrete points
    graph = VMobject()
    graph.set_stroke(pc.blueGreen, 3)
    points = [axes.c2p(float(x), float(y)) for x, y in zip(xs_slice, ys_slice)]
    graph.set_points_smoothly(points)

    self.play(Create(graph))
    self.next_slide()

    # New 2D vector notation equation
    eq_tessendorf_3 = MathTex(
        r"h(\mathbf x,t)=\sum_{\mathbf{k}} \tilde{h}(t, \mathbf{k}) "
        r"\exp\left( i \mathbf{k}\cdot \mathbf x\right)",
        font_size=self.BODY_FONT_SIZE + 10,
        color=BLACK,
    )
    eq_tessendorf_3.move_to(eq_tessendorf_2.get_center())

    # Second image
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

    # End slide
    self.pause()
    self.clear()
    self.next_slide()
