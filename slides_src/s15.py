import numpy as np
import palette_colors as pc
from manim import *
from manim.utils.rate_functions import linear
from slide_registry import slide


@slide(15)
def slide_15(self):
    """
    Couplage avec des solides — scenario updated:

      1) Show a base sinus water curve A*cos(k*x + omega*t) in blue-green [Create].
         (A=0.3, k=2.0, omega=1.0)
      2) Wait (self.next_slide).
      3) Create a boat that falls through while the base water animates.
      4) Wait (self.next_slide).
      5) Remove the boat.
      6) Add a new boat that falls until it reaches the base curve height (x=0).
      7) Then make it oscillate while the base water animates.
      8) Wait (self.next_slide).
      9) Transform the base water curve into two symmetric decaying curves
         (left uses +t, right uses -t) and keep animating like before.
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
    self.play(FadeIn(subtitle, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25)

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

    # --- Time tracker (shared) ---
    t = ValueTracker(0.0)

    # =========================
    # Phase 1: base sinus water
    # =========================
    A0 = 0.1
    k0 = 0.5
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
    # Phase 2: boat falls through while base water animates
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
    boat1 = Polygon(
        *[np.array(p) for p in boat_shape],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
    ).scale(0.9)
    start_y = y_center + 2.2
    boat1.move_to([0.0, start_y, 0.0])
    boat1.set_z_index(10)
    self.add(boat1)
    self.add_foreground_mobject(boat1)

    # Animate time and falling together (constant speed)
    self.play(
        AnimationGroup(
            t.animate.set_rate_func(linear).increment_value(2.0 * np.pi),
            boat1.animate.set_rate_func(linear).move_to(
                [0.0, y_bottom - 1.5, 0.0]
            ),
            lag_ratio=0.0,
        ),
        run_time=4.0,
    )

    # =========================
    # Phase 3: remove boat1
    # =========================
    self.next_slide()
    self.play(FadeOut(boat1, run_time=0.25))

    # =========================
    # Phase 4: add a new boat that falls until it reaches base curve height
    # =========================
    boat2 = Polygon(
        *[np.array(p) for p in boat_shape],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
    ).scale(0.9)
    boat2.move_to([0.0, start_y, 0.0])
    boat2.set_z_index(10)
    self.add(boat2)
    self.add_foreground_mobject(boat2)

    # Freeze time while the boat falls to the current base curve height at x=0
    tv_now = t.get_value()
    base_y_at_x0 = plot_center[1] + sy * (
        A0 * np.cos(omega0 * tv_now)
    )  # k0*0 = 0
    self.play(
        boat2.animate.set_rate_func(linear).move_to([0.0, base_y_at_x0, 0.0]),
        t.animate.set_rate_func(linear).increment_value(1.5),
        run_time=1.2,
    )

    # Then make it oscillate following the local base wave at x=0, while base water animates
    def boat2_updater(mob: Mobject):
        tv = t.get_value()
        y = plot_center[1] + sy * (A0 * np.cos(omega0 * tv)) + 0.1
        mob.move_to([0.0, y, 0.0])

    boat2.add_updater(boat2_updater)

    self.play(
        t.animate.set_rate_func(linear).increment_value(2.0 * np.pi + 1.5),
        run_time=4.0,
    )

    # =========================
    # Phase 5: wait, then transform base curve into two symmetric decaying curves
    # =========================
    self.next_slide()

    # Decaying cosine parameters
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

    # Take a static snapshot of the current base curve to transform from
    base_static = make_water_base()
    self.add(base_static)  # layered on top of the redraw temporarily
    self.remove(water_base)  # hide the redraw version so transform is stable

    # Build static targets (left/right) at current t
    def build_static_left():
        X = np.linspace(x_min, 0.0, sample_n // 2 + 1)
        tv = t.get_value()
        pts = []
        for xv in X:
            yv = np.clip(water_left(xv, tv), -y_vis, y_vis)
            px = (xv - x_min) * sx - plot_w / 2.0
            py = yv * sy
            pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
        m = VMobject()
        m.set_points_smoothly(pts)
        m.set_stroke(color=pc.blueGreen, width=4)
        return m

    def build_static_right():
        X = np.linspace(0.0, x_max, sample_n // 2 + 1)
        tv = t.get_value()
        pts = []
        for xv in X:
            yv = np.clip(water_right(xv, tv), -y_vis, y_vis)
            px = (xv - x_min) * sx - plot_w / 2.0
            py = yv * sy
            pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
        m = VMobject()
        m.set_points_smoothly(pts)
        m.set_stroke(color=pc.blueGreen, width=4)
        return m

    left_static = build_static_left()
    right_static = build_static_right()
    target_group = VGroup(left_static, right_static)

    # Transform snapshot into the two-curve group
    self.play(ReplacementTransform(base_static, target_group), run_time=0.8)

    # Replace static targets with always_redraw animated versions
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
    self.add(water_l, water_r)
    self.remove(target_group)

    # Switch boat to follow the decaying-wave local motion at x=0
    boat2.remove_updater(boat2_updater)

    def boat2_decay_updater(mob: Mobject):
        tv = t.get_value()
        y = (
            plot_center[1] + sy * (0.03 * np.cos(omega_env * tv)) + 0.1
        )  # at x=0
        mob.move_to([0.0, y, 0.0])

    boat2.add_updater(boat2_decay_updater)

    # Animate the system (time continues linearly)
    self.play(
        t.animate.set_rate_func(linear).increment_value(4.0 * np.pi),
        run_time=8.0,
    )

    # Cleanup
    boat2.remove_updater(boat2_decay_updater)
    self.pause()
    self.clear()
    self.next_slide()
