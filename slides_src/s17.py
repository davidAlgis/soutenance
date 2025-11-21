import os

import numpy as np
import palette_colors as pc
from manim import *
from manim_slides import Slide
from slide_registry import slide

# --- Constants for Visualization ---
BLUE_GREEN_HEX = "#1F9CB9"
UCLA_GOLD_HEX = "#FFB500"
WHITE_HEX = "#FFFFFF"
DATA_DIR = "states_sph"

# --- Hardcoded Boat Geometries ---
# 1D Boat (Side view) - Local coordinates centered at bottom y=0
BOAT_1D_VERTS = np.array(
    [
        [-1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 1.0, 0.0],
        [0.5, 1.0, 0.0],
        [0.0, 1.5, 0.0],
        [-0.5, 1.0, 0.0],
        [-2.0, 1.0, 0.0],
    ]
)


# 2D Boat (Top view) - Local coordinates
def get_boat_2d_verts():
    w = 0.03
    l_stern = 0.05
    l_bow = 0.08
    return np.array(
        [
            [0.0, l_bow, 0.0],  # Tip
            [-w, 0.0, 0.0],  # Mid Left
            [-w, -l_stern, 0.0],  # Back Left
            [w, -l_stern, 0.0],  # Back Right
            [w, 0.0, 0.0],  # Mid Right
        ]
    )


@slide(17)
def slide_17(self):
    """
    Action du solide sur le fluide.
    Includes 1D and 2D wave equation animations with Boat Sources.
    """
    # --- Barre de titre -------------------------------------------------------
    bar, footer = self._top_bar("Action du solide sur le fluide")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Zone utile -----------------------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    area_w = x_right - x_left

    col_width = area_w / 2
    col_1_center = x_left + col_width / 2
    col_2_center = x_left + col_width * 1.5
    y_anim_center = -0.5

    # --- Corps de texte (Tex) -------------------------------------------------
    self.start_body()

    line1 = Tex(
        "L'action du solide sur le fluide est approximée comme une simple « onde ».",
        tex_template=self.french_template,
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    line1.to_edge(LEFT, buff=1.0).set_y(y_top - 0.42)

    line2 = Tex(
        "Résolution de l'équation d'onde 2D avec la méthode des différences finies :",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    line2.next_to(line1, DOWN, buff=0.22, aligned_edge=LEFT)

    eq_pde = Tex(
        r"""
        \begin{equation*}
        \begin{cases}
            \Delta h(\mathbf{x},t)-\dfrac{1}{c^{2}}\dfrac{\partial^{2} h(\mathbf{x},t)}{\partial t^{2}}=0
            \quad \text{for} \quad \mathbf{x}\in Z\\[6pt]
            h(\mathbf{x},t)=0 \quad \text{for} \quad \mathbf{x}\in\partial Z
        \end{cases}
        \end{equation*}
        """,
        font_size=self.BODY_FONT_SIZE + 4,
        color=BLACK,
    )
    eq_pde.next_to(line2, DOWN, buff=0.32, aligned_edge=LEFT)
    if eq_pde.width > area_w * 0.90:
        eq_pde.scale_to_fit_width(area_w * 0.90)

    line3 = Tex(
        r"Où $Z$ est un domaine carré centré autour du solide.",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    line3.next_to(eq_pde, DOWN, buff=0.26, aligned_edge=LEFT)

    self.play(
        FadeIn(line1, line2, eq_pde, line3, shift=RIGHT * self.SHIFT_SCALE),
        run_time=0.5,
    )
    self.wait(0.1)
    self.next_slide()

    # --- Transition ---
    to_remove = VGroup(line1, eq_pde, line3)
    target_pos = line2.get_center()
    target_pos[1] = line1.get_y()

    self.play(
        FadeOut(to_remove, shift=LEFT),
        line2.animate.move_to(target_pos),
        run_time=0.8,
    )

    # --- ANIMATION SECTION ----------------------------------------------------

    # 1. Load Data
    try:
        d1_nd = np.load(os.path.join(DATA_DIR, "wave_1d_no_damping.npz"))
        d2_nd = np.load(os.path.join(DATA_DIR, "wave_2d_no_damping.npz"))
        d1_wd = np.load(os.path.join(DATA_DIR, "wave_1d_with_damping.npz"))
        d2_wd = np.load(os.path.join(DATA_DIR, "wave_2d_with_damping.npz"))
    except FileNotFoundError:
        print("Error: .npz files not found. Please run wave_data_gen scripts.")
        return

    # 2. Helper: Create 1D Animation Group (Boat Side View)
    def create_1d_group(data, title_str):
        H, x = data["H"], data["x"]
        L, A = float(data["L"]), float(data["A"])

        square_size = 4.5
        bg_square = Square(side_length=square_size, color=GRAY, stroke_width=2)
        bg_square.set_fill(WHITE, opacity=1)

        # --- UPDATED AXES RANGE ---
        # Reduced y_range from [-2, 2] to [-0.5, 0.5] to "zoom in" on the y-axis
        y_min, y_max = -0.5, 0.5

        axes = Axes(
            x_range=[-L, L],
            y_range=[-2.0, 8.0],
            x_length=square_size * 0.9,
            y_length=square_size * 0.8,
            axis_config={
                "color": pc.blueGreen,
                "stroke_width": 2,
                "include_ticks": False,
            },
        ).move_to(bg_square)

        # Filled area
        wave_area = VMobject(color=BLUE_GREEN_HEX, stroke_width=0)
        wave_area.set_fill(BLUE_GREEN_HEX, opacity=0.3)

        # Wave Line
        wave_line = VMobject(color=BLUE_GREEN_HEX, stroke_width=3)

        # --- Boat Visualization (Polygon) ---
        boat_points_local = BOAT_1D_VERTS.copy()
        boat_points_local[:, 1] += A

        boat_points_manim = [
            axes.c2p(pt[0], pt[1]) for pt in boat_points_local
        ]

        source_mob = Polygon(
            *boat_points_manim,
            color=UCLA_GOLD_HEX,
            fill_color=UCLA_GOLD_HEX,
            fill_opacity=1,
            stroke_width=1
        )

        label = Text(title_str, font_size=20, color=BLACK).next_to(
            bg_square, DOWN, buff=0.2
        )

        group = VGroup(
            bg_square, axes, wave_area, wave_line, source_mob, label
        )

        def update_wave(mob, dt):
            if not hasattr(mob, "frame_idx"):
                mob.frame_idx = 0

            # --- SPEED FACTOR ---
            # Increase this number to make the animation faster.
            # 1 = real time, 10 = 10x speed.
            speed_factor = 10
            mob.frame_idx = (mob.frame_idx + speed_factor) % len(H)

            y_data = H[mob.frame_idx]

            # Map coordinates
            x_coords = axes.x_axis.n2p(x)[:, 0]
            y_coords = axes.y_axis.n2p(y_data)[:, 1]
            z_coords = np.zeros_like(x_coords)

            line_points = np.stack([x_coords, y_coords, z_coords], axis=1)
            wave_line.set_points_as_corners(line_points)

            # --- UPDATED FILL LOGIC ---
            # Dynamic bottom reference: pixel y-coordinate of y_min
            # This ensures fill goes exactly to the bottom of the axis frame
            fill_base_y = axes.y_axis.n2p([y_min])[0, 1]

            bottom_left = np.array([x_coords[0], fill_base_y, 0])
            bottom_right = np.array([x_coords[-1], fill_base_y, 0])

            area_points = np.concatenate(
                ([bottom_left], line_points, [bottom_right], [bottom_left])
            )
            wave_area.set_points_as_corners(area_points)

        wave_line.add_updater(update_wave)
        return group

    # 3. Helper: Create 2D Animation Group (Boat Top View)
    def create_2d_group(data, title_str):
        H = data["H"]
        L = float(data["L"])

        bg_rgb = np.array(color_to_rgb(BLUE_GREEN_HEX))
        white_rgb = np.array(color_to_rgb(WHITE_HEX))

        square_size = 4.5
        bg_square = Square(side_length=square_size, color=GRAY, stroke_width=2)
        bg_square.set_fill(WHITE, opacity=1)

        # --- Boat Visualization (Polygon) ---
        boat_verts_local = get_boat_2d_verts()

        scale_factor = square_size / (2 * L)
        scaled_verts = boat_verts_local * scale_factor

        source_mob = Polygon(
            *scaled_verts,
            color=UCLA_GOLD_HEX,
            fill_color=UCLA_GOLD_HEX,
            fill_opacity=1,
            stroke_width=1
        )
        source_mob.move_to(bg_square.get_center())

        label = Text(title_str, font_size=20, color=BLACK).next_to(
            bg_square, DOWN, buff=0.2
        )

        vmax = 0.25

        def get_img_from_index(idx):
            arr = H[idx].T
            arr = np.flipud(arr)

            alpha = np.abs(arr) / vmax
            alpha = np.clip(alpha, 0, 1)
            alpha_ex = alpha[..., np.newaxis]

            rgb = (1.0 - alpha_ex) * white_rgb + alpha_ex * bg_rgb
            rgb_uint8 = (rgb * 255).astype("uint8")

            h, w, _ = rgb_uint8.shape
            rgba_uint8 = np.dstack(
                (rgb_uint8, np.full((h, w), 255, dtype="uint8"))
            )
            return rgba_uint8

        img_mobj = ImageMobject(get_img_from_index(0))
        img_mobj.height = square_size * 0.95
        img_mobj.width = square_size * 0.95
        img_mobj.move_to(bg_square)
        img_mobj.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])

        group = Group(bg_square, img_mobj, source_mob, label)

        def update_img(mob, dt):
            if not hasattr(mob, "frame_idx"):
                mob.frame_idx = 0
            mob.frame_idx = (mob.frame_idx + 1) % len(H)
            mob.pixel_array = get_img_from_index(mob.frame_idx)

        img_mobj.add_updater(update_img)
        return group

    # --- PHASE 1: NO DAMPING ---

    group_1d_nd = create_1d_group(d1_nd, "Vue de côté")
    group_1d_nd.move_to([col_1_center, y_anim_center, 0])

    group_2d_nd = create_2d_group(d2_nd, "Vue du dessus")
    group_2d_nd.move_to([col_2_center, y_anim_center, 0])

    self.add(group_1d_nd, group_2d_nd)

    # INCREASED WAIT TIME:
    # 1D Sim T=16s ~ 800 frames @ 60fps ~ 13.3s
    # We wait 15s to allow one full loop.
    self.next_slide(loop=True)
    self.wait(15)

    # --- PHASE 2: WITH DAMPING ---

    group_1d_wd = create_1d_group(d1_wd, "Vue de côté")
    group_1d_wd.move_to([col_1_center, y_anim_center, 0])

    group_2d_wd = create_2d_group(d2_wd, "Vue du dessus")
    group_2d_wd.move_to([col_2_center, y_anim_center, 0])

    self.remove(group_1d_nd, group_2d_nd)
    self.add(group_1d_wd, group_2d_wd)

    self.next_slide(loop=True)
    self.wait(15)

    # Finish
    self.clear()
    self.next_slide()
