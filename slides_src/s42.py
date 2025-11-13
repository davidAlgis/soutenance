# slide_42.py
# Decaying wave on both sides with a centered oscillating boat.
# Two curves:
#   - for x < 0 uses +t in cos
#   - for x > 0 uses -t in cos
# Boat oscillates vertically with same phase as local water motion.

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(42)
def slide_42(self):
    """
    Decaying wave around the boat with oscillating motion.
    Two decaying wave curves symmetric around x=0:
      - left side:  A * exp(-|x - x_c| / T) * cos(k * (x - x_c) + t)
      - right side: A * exp(-|x - x_c| / T) * cos(k * (x - x_c) - t)
    Boat oscillates vertically in phase with the local wave at x = 0.
    """
    # --- Top bar ---
    bar = self._top_bar("Couplage avec des solides")
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
    y_center = 0.5 * (y_top + y_bottom)

    # --- Subtitle (Tex) ---
    self.start_body()
    subtitle = Tex(
        r"La m\'ethode de Tessendorf ne permet pas le couplage avec des solides :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    subtitle.next_to(
        self._current_bar,
        DOWN,
        buff=self.BODY_TOP_BUFF,
        aligned_edge=LEFT,
    )
    dx_sub = (bar_rect.get_left()[0] + self.DEFAULT_PAD) - subtitle.get_left()[
        0
    ]
    subtitle.shift(RIGHT * dx_sub)
    self.play(FadeIn(subtitle), run_time=0.25)

    # --- Plot mapping (no axes) ---
    plot_w = min(area_w * 0.88, 12.0)
    plot_h = min(area_h * 0.48, 3.6)
    plot_center = np.array([0.0, y_center, 0.0])
    x_min, x_max = -10, 10
    x_span = x_max - x_min
    sample_n = 600
    y_vis = 1.0
    sx = plot_w / x_span
    sy = (plot_h / 2.0) / y_vis

    # --- Time tracker ---
    t = ValueTracker(0.0)

    # --- Decaying cosine parameters ---
    x_c = 0.0
    A_env = 0.25
    T_env = 3.0
    k_env = 3.0
    omega_env = 3.0

    def water_left(x_val: float, t_val: float) -> float:
        """Left side (x < 0): A * exp(-|x - x_c| / T) * cos(k * (x - x_c) + t)."""
        x_rel = x_val - x_c
        return (
            A_env
            * np.exp(-np.abs(x_rel) / T_env)
            * np.cos(k_env * x_rel + omega_env * t_val)
        )

    def water_right(x_val: float, t_val: float) -> float:
        """Right side (x > 0): A * exp(-|x - x_c| / T) * cos(k * (x - x_c) - t)."""
        x_rel = x_val - x_c
        return (
            A_env
            * np.exp(-np.abs(x_rel) / T_env)
            * np.cos(k_env * x_rel - omega_env * t_val)
        )

    # --- Water curves ---
    def make_water_curve_left():
        X = np.linspace(x_min, 0.0, sample_n // 2 + 1)
        pts = []
        tv = t.get_value()
        for xv in X:
            yv = np.clip(water_left(xv, tv), -y_vis, y_vis)
            px = (xv - x_min) * sx - plot_w / 2.0
            py = yv * sy
            pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
        path = VMobject()
        path.set_points_smoothly(pts)
        path.set_stroke(color=pc.blueGreen, width=4)
        return path

    def make_water_curve_right():
        X = np.linspace(0.0, x_max, sample_n // 2 + 1)
        pts = []
        tv = t.get_value()
        for xv in X:
            yv = np.clip(water_right(xv, tv), -y_vis, y_vis)
            px = (xv - x_min) * sx - plot_w / 2.0
            py = yv * sy
            pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
        path = VMobject()
        path.set_points_smoothly(pts)
        path.set_stroke(color=pc.blueGreen, width=4)
        return path

    water_l = always_redraw(make_water_curve_left)
    water_r = always_redraw(make_water_curve_right)
    self.add(water_l, water_r)

    # --- Boat polygon (foreground) ---
    boat_shape = [
        [-1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 1.0, 0.0],
        [0.5, 1.0, 0.0],
        [0.0, 1.5, 0.0],
        [-0.5, 1.0, 0.0],
        [-2.0, 1.0, 0.0],
    ]
    boat = Polygon(
        *[np.array(p) for p in boat_shape],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
    )
    boat.scale(0.9)
    boat_center = [0.0, plot_center[1] + 0.12, 0.0]
    boat.move_to(boat_center)
    boat.set_z_index(10)
    self.add(boat)
    self.add_foreground_mobject(boat)

    # --- Boat oscillation in phase with local wave ---
    def boat_updater(mob: Mobject):
        """Make the boat follow the vertical motion of the wave at x=0."""
        tv = t.get_value()
        y_offset = 0.03 * np.cos(omega_env * tv)
        mob.move_to([0.0, plot_center[1] + 0.15 + y_offset * sy, 0.0])

    boat.add_updater(boat_updater)

    # --- Animate the system ---
    self.play(
        t.animate.increment_value(4.0 * np.pi),
        rate_func=linear,
        run_time=8.0,
    )

    # --- Cleanup and end slide ---
    boat.remove_updater(boat_updater)
    self.pause()
    self.clear()
    self.next_slide()
