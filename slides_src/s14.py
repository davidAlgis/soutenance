import numpy as np
import palette_colors as pc
from manim import *
from manim.utils.rate_functions import linear
from slide_registry import slide


@slide(14)
def slide_14(self):
    """
    Couplage avec des solides — scenario updated:
      - Wave animates continuously via dt updater.
    """
    # --- Top bar ---
    bar, footer = self._top_bar("Couplage avec des solides")
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
        r"La méthode de Tessendorf ne permet pas le couplage avec des solides :",
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

    # =========================
    # Time tracker (CONTINUOUS)
    # =========================
    t = ValueTracker(0.0)

    # 1. Add t to the scene so updaters run
    self.add(t)

    # 2. Add updater: increments t by dt * speed every frame
    # Adjust '1.0' to make the wave faster or slower
    t.add_updater(lambda m, dt: m.increment_value(dt * 1.0))

    # =========================
    # Phase 1: base sinus water
    # =========================
    A0 = 0.1
    k0 = 0.5
    omega0 = 4.0

    def make_water_base():
        X = np.linspace(x_min, x_max, sample_n)
        tv = t.get_value()
        pts = []
        for xv in X:
            yv = np.clip(A0 * np.cos(k0 * xv - omega0 * tv), -y_vis, y_vis)
            px = (xv - x_min) * sx - plot_w / 2.0
            py = yv * sy
            pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
        m = VMobject()
        m.set_points_smoothly(pts)
        m.set_stroke(color=pc.blueGreen, width=4)
        return m

    water_base = always_redraw(make_water_base)
    self.play(Create(water_base), run_time=1.0)

    # =========================
    # Phase 2: boat falls through
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
    start_y = y_center + 1.9
    boat1.move_to([0.0, start_y, 0.0])
    boat1.set_z_index(10)
    self.play(FadeIn(boat1))
    self.add_foreground_mobject(boat1)

    # Because t has an updater, we just move the boat.
    # The wave animates automatically during this run_time.
    self.play(
        boat1.animate.move_to([0.0, y_bottom - 2.0, 0.0]),
        run_time=2.0,
        rate_func=linear,
    )

    # =========================
    # Phase 3: remove boat1
    # =========================
    self.next_slide()
    self.play(FadeOut(boat1, run_time=0.25))

    # =========================
    # Phase 4: boat 2
    # =========================
    boat2 = Polygon(
        *[np.array(p) for p in boat_shape],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
    ).scale(0.9)
    boat2.move_to([0.0, start_y, 0.0])
    boat2.set_z_index(10)

    f2s_title = Tex(
        r"Action du fluide sur le solide",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    f2s_title.to_edge(DOWN, buff=0.3)
    self.play(FadeIn(boat2), FadeIn(f2s_title, shift=UP))
    self.add_foreground_mobject(boat2)

    # Freeze time logic for the calculation target
    # (Note: Since t is moving, the wave will shift slightly while falling,
    # but this approximation is usually fine for visual slides).
    tv_now = t.get_value()
    base_y_at_x0 = plot_center[1] + sy * (A0 * np.cos(omega0 * tv_now)) + 0.1

    self.play(
        boat2.animate.move_to([0.0, base_y_at_x0, 0.0]),
        run_time=2.3,
    )

    # Add updater for oscillation
    # Since 't' is auto-updating, this updater will fire every frame with a new t
    def boat2_updater(mob: Mobject):
        tv = t.get_value()
        # Re-calculate Y based on current t
        y = plot_center[1] + sy * (A0 * np.cos(omega0 * tv)) + 0.1
        # Keep X and Z, update Y
        current_x = mob.get_center()[0]
        mob.move_to([current_x, y, 0.0])

    boat2.add_updater(boat2_updater)

    # Just wait to show the oscillation
    self.play(Wait(4.0))  # Wait allows updaters to run for 4 seconds

    # Cleanup updaters if you want to stop the motion before leaving the slide
    t.clear_updaters()
    boat2.clear_updaters()

    # =========================
    # Phase 5: wait, then transform base curve into two symmetric decaying curves
    # =========================
    self.next_slide()
    self.play(FadeOut(f2s_title, shift=DOWN))

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
    s2f_title = Tex(
        r"Action du solide sur la fluide",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    s2f_title.to_edge(DOWN, buff=0.3)

    # Transform snapshot into the two-curve group
    self.play(
        ReplacementTransform(base_static, target_group),
        FadeIn(s2f_title, shift=UP),
        run_time=0.8,
    )

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
            plot_center[1] + sy * (0.03 * np.cos(omega_env * tv)) + 0.2
        )  # at x=0
        mob.move_to([0.0, y, 0.0])

    boat2.add_updater(boat2_decay_updater)

    # Animate the system (time continues linearly)
    self.play(
        t.animate.set_rate_func(linear).increment_value(4.0 * np.pi),
        run_time=4.0 * np.pi,
    )

    # Cleanup
    boat2.remove_updater(boat2_decay_updater)
    self.pause()
    self.clear()
    self.next_slide()
