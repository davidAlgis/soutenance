import numpy as np
import palette_colors as pc
from manim import *
from manim.utils.rate_functions import linear
from slide_registry import slide


@slide(42)
def slide_42(self):
    """
    Decaying wave around the boat with oscillating motion.
    Phases:
      1) Show a base sinus water curve A*cos(k*x + omega*t) (A=0.3, k=2.0, omega=1.0) in blue-green [Create].
      2) Wait for user input, then make a boat fall through while the base water animates.
      3) Wait for user input, then remove the boat and fade out the base water.
      4) Fade in the boat together with two symmetric decaying waves:
           left:  A*exp(-|x-x_c|/T)*cos(k*(x-x_c) + omega*t)
           right: A*exp(-|x-x_c|/T)*cos(k*(x-x_c) - omega*t)
         and play the animation (boat oscillates with the local wave at x=0).
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
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
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
    x_min, x_max = -10.0, 10.0
    x_span = x_max - x_min
    sample_n = 600
    y_vis = 1.0
    sx = plot_w / x_span
    sy = (plot_h / 2.0) / y_vis

    # --- Time tracker (shared by all phases) ---
    t = ValueTracker(0.0)

    # =========================
    # Phase 1: base sinus water
    # =========================
    A0 = 0.1
    k0 = 0.3
    omega0 = 1.0

    def make_water_base():
        X = np.linspace(x_min, x_max, sample_n)
        tv = t.get_value()
        pts = []
        for xv in X:
            yv = np.clip(A0 * np.cos(k0 * xv + omega0 * tv), -y_vis, y_vis)
            px = (xv - x_min) * sx - plot_w / 2.0
            py = yv * sy
            pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
        m = VMobject()
        m.set_points_smoothly(pts)
        m.set_stroke(color=pc.blueGreen, width=4)
        return m

    water_base = always_redraw(make_water_base)
    self.add(water_base)
    self.play(Create(water_base), run_time=1.0)

    # =========================
    # Phase 2: boat falls while base water animates
    # =========================
    self.next_slide()

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
    ).scale(0.9)
    start_y = y_center + 2.2
    boat.move_to([0.0, start_y, 0.0])
    boat.set_z_index(10)
    self.add(boat)
    self.add_foreground_mobject(boat)

    # Animate time and falling together
    self.play(
        AnimationGroup(
            t.animate.set_rate_func(linear).increment_value(2.0 * np.pi),
            boat.animate.set_rate_func(linear).move_to(
                [0.0, y_bottom - 1.5, 0.0]
            ),
            lag_ratio=0.0,
        ),
        run_time=4.0,
    )

    # =========================
    # Phase 3: remove boat and fade out base water
    # =========================
    self.next_slide()
    self.play(FadeOut(boat, run_time=0.1), FadeOut(water_base, run_time=0.6))

    # ==========================================================
    # Phase 4: fade in boat + two symmetric decaying-wave curves
    # ==========================================================
    # Decaying cosine parameters (center x_c = 0)
    x_c = 0.0
    A_env = 0.25
    T_env = 3.0
    k_env = 3.0
    omega_env = 3.0

    def water_left(x_val: float, t_val: float) -> float:
        x_rel = x_val - x_c
        return (
            A_env
            * np.exp(-np.abs(x_rel) / T_env)
            * np.cos(k_env * x_rel + omega_env * t_val)
        )

    def water_right(x_val: float, t_val: float) -> float:
        x_rel = x_val - x_c
        return (
            A_env
            * np.exp(-np.abs(x_rel) / T_env)
            * np.cos(k_env * x_rel - omega_env * t_val)
        )

    def make_water_curve_left():
        X = np.linspace(x_min, 0.0, sample_n // 2 + 1)
        tv = t.get_value()
        pts = []
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
        tv = t.get_value()
        pts = []
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

    # Recreate boat at gentle baseline and make it oscillate with local wave
    boat = Polygon(
        *[np.array(p) for p in boat_shape],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
    ).scale(0.9)
    base_boat_y = plot_center[1] + 0.12
    boat.move_to([0.0, base_boat_y, 0.0])
    boat.set_z_index(10)

    def boat_updater(mob: Mobject):
        tv = t.get_value()
        y_offset = 0.03 * np.cos(omega_env * tv)
        mob.move_to([0.0, base_boat_y + y_offset * sy, 0.0])

    boat.add_updater(boat_updater)

    # Fade in boat + decaying curves together
    self.add(water_l, water_r, boat)
    self.add_foreground_mobject(boat)
    self.play(FadeIn(water_l), FadeIn(water_r), FadeIn(boat), run_time=0.6)

    # Animate the system as before
    self.play(
        t.animate.increment_value(4.0 * np.pi),
        rate_func=linear,
        run_time=8.0,
    )

    # Cleanup
    boat.remove_updater(boat_updater)
    self.pause()
    self.clear()
    self.next_slide()
