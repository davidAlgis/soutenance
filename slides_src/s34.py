import numpy as np
import palette_colors as pc
from manim import (BLACK, DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Arrow,
                   Create, Dot, FadeOut, GrowArrow, GrowFromCenter,
                   LaggedStart, Tex, TransformMatchingTex, ValueTracker,
                   VGroup, VMobject, config)
from slide_registry import slide


@slide(34)
def slide_34(self):
    """
    Vitesse d'Airy (slide 34).

    Full rewrite with a strictly consistent physical frame so that the wave curve
    and the top particle row coincide on the free surface:
    - Horizontal physical coordinate: x_phys in [-X_RANGE/2, X_RANGE/2]
    - Vertical physical coordinate:   b in [0, B_MAX]; free surface is at b = B_MAX
    - Wave: eta(x,t) = A_phys * cos(k*x - omega*t)
    - Lagrangian displacements use amp_base so that AE(b=B_MAX) == A_phys

    All texts are BLACK, same font size and spacing. Left formulas are pre-placed.
    """

    # ----------------------------- layout and common params
    full_w = config.frame_width
    full_h = config.frame_height

    left_w = full_w * 0.35
    right_w = full_w * 0.65

    left_center_x = -full_w * 0.5 + left_w * 0.5 + 0.3
    right_center_x = left_center_x + (left_w * 0.5) + (right_w * 0.5) + 0.3

    bar = self._top_bar("Vitesse d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]
    top_y = bar_rect.get_bottom()[1] - 0.2
    bottom_y = -full_h * 0.5 + 0.3

    TEXT_FS = 30
    LINE_BUFF = 0.35

    # ----------------------------- helpers
    def place_left_tex(mobj, above=None, buff=LINE_BUFF):
        """
        Place a Tex in the left column, left-aligned and clamped inside the column.
        """
        if above is None:
            mobj.to_edge(LEFT, buff=0.0)
            dx = (left_center_x - left_w * 0.5 + 0.1) - mobj.get_left()[0]
            mobj.shift(RIGHT * dx)
            dy = (top_y - 0.15) - mobj.get_top()[1]
            mobj.shift(UP * dy)
        else:
            mobj.next_to(above, DOWN, buff=buff, aligned_edge=LEFT)
            dx = (left_center_x - left_w * 0.5 + 0.1) - mobj.get_left()[0]
            mobj.shift(RIGHT * dx)
        return mobj

    def map_to_right(x_norm, y_norm):
        """
        Map normalized coords (0..1, 0..1) to the right column rectangle.
        """
        x0 = right_center_x - right_w * 0.5
        y0 = bottom_y
        return np.array(
            [x0 + x_norm * right_w, y0 + y_norm * (top_y - bottom_y), 0.0]
        )

    # --------------------------- physical frame (CONSISTENT for curve & particles)
    t_tracker = ValueTracker(0.0)

    k_val = 0.3
    omega_val = 1.0

    # Horizontal span: many periods visible
    X_PERIODS = 4.5
    X_RANGE = (
        2.0 * np.pi * X_PERIODS
    ) / k_val  # x_phys in [-X_RANGE/2, X_RANGE/2]

    # Vertical: labels b in [0, B_MAX]; free surface is at b = B_MAX
    B_MAX = 1.0

    # Choose physical free-surface amplitude
    A_phys = 0.18

    # Airy Lagrangian uses AE = amp_base * exp(k*b). To match the Eulerian wave
    # at the free surface, we set amp_base so that AE(b=B_MAX) == A_phys.
    # => amp_base = A_phys * exp(-k*B_MAX)
    amp_base = A_phys * np.exp(-k_val * B_MAX)

    # Right-column vertical placement for the free surface (screen normalized)
    y_mid = 0.62  # yn position of b = B_MAX (free surface)

    # Converters between physical and normalized
    def xn_from_xphys(x_phys):
        return (x_phys / X_RANGE) + 0.5

    def yn_from_b(b_phys):
        # b in [0..B_MAX] -> [0..y_mid]
        return (b_phys / B_MAX) * y_mid

    def yn_from_surface(b_phys_surface):
        # b_phys_surface = b + eta. For the free surface: b=B_MAX, so zero line is y_mid.
        return yn_from_b(b_phys_surface)

    # --------------------------- Airy Lagrangian displacement (physical)
    def get_horizontal_displacement(a, b, amp_base, k, omega, t_val):
        """
        xi(a,b,t) with AE(b) = amp_base * exp(k*b).
        Use phase k*a - omega*t to be consistent with Eulerian cos(k*x - omega*t).
        """
        theta = k * a - omega * t_val
        AE = amp_base * np.exp(k * b)
        return -AE * np.sin(theta)

    def get_vertical_displacement(a, b, amp_base, k, omega, t_val):
        """
        eta(a,b,t) with the standard first-order correction in the phase.
        """
        theta = k * a - omega * t_val
        AE = amp_base * np.exp(k * b)
        return AE * np.cos(theta - k * AE * np.sin(theta))

    def get_particle_position(a, b, amp_base, k, omega, t_val):
        """
        Returns (x_phys, b_phys_surface) in the SAME physical frame as the curve,
        where b_phys_surface = b + eta(a,b,t).
        """
        return (
            a + get_horizontal_displacement(a, b, amp_base, k, omega, t_val),
            b + get_vertical_displacement(a, b, amp_base, k, omega, t_val),
        )

    # ---------------------------------------------- Intro text under the bar
    intro = Tex(
        "Version lagrangienne d'Airy :", color=BLACK, font_size=TEXT_FS
    )
    intro.to_edge(LEFT, buff=0.4)
    dy_intro = top_y - intro.get_top()[1]
    intro.shift(UP * dy_intro)
    self.add(intro)

    self.next_slide()

    # ----------------------------------------------------- Eulerian wave curve on free surface
    def make_wave_curve():
        """
        Eulerian wave at the free surface:
          eta(x,t) = A_phys * cos(k*x - omega*t)
          b_surface(x,t) = B_MAX + eta(x,t)
        """
        n = 400
        pts = []
        for i in range(n):
            xn = i / (n - 1)
            x_phys = (xn - 0.5) * X_RANGE
            eta = A_phys * np.cos(
                k_val * x_phys - omega_val * t_tracker.get_value()
            )
            b_surface = B_MAX + eta
            yn = yn_from_surface(b_surface)
            pts.append(map_to_right(xn, yn))
        curve = VMobject()
        curve.set_points_smoothly(pts)
        curve.set_stroke(color=pc.oxfordBlue, width=4)
        return curve

    wave_curve = make_wave_curve()
    self.add(wave_curve)

    # Left-column equation h(x,t)
    eq_h = Tex(r"$h(x,t)=A\cos(kx-\omega t)$", color=BLACK, font_size=TEXT_FS)
    place_left_tex(eq_h, above=intro, buff=LINE_BUFF * 1.2)
    self.add(eq_h)

    # ------------------------------------------------------ Label grid (a,b) in SAME frame
    grid_nx, grid_ny = 7, 7
    labels_phys = []  # (i, j, a_phys, b_phys)
    for j in range(grid_ny):
        for i in range(grid_nx):
            a_phys = (
                (i / (grid_nx - 1)) - 0.5
            ) * X_RANGE  # [-X_RANGE/2, X_RANGE/2]
            b_phys = (j / (grid_ny - 1)) * B_MAX  # [0, B_MAX]
            labels_phys.append((i, j, a_phys, b_phys))

    def make_cross(center, size=0.03):
        dx = size
        dy = size
        p1 = center + np.array([-dx, -dy, 0.0])
        p2 = center + np.array([dx, dy, 0.0])
        p3 = center + np.array([-dx, dy, 0.0])
        p4 = center + np.array([dx, -dy, 0.0])
        l1 = (
            VMobject()
            .set_stroke(color=pc.apple, width=3)
            .set_points_as_corners([p1, p2])
        )
        l2 = (
            VMobject()
            .set_stroke(color=pc.apple, width=3)
            .set_points_as_corners([p3, p4])
        )
        return VGroup(l1, l2)

    crosses = []
    for _i, _j, a_phys, b_phys in labels_phys:
        xn = xn_from_xphys(a_phys)
        yn = yn_from_b(b_phys)  # top row (b=B_MAX) maps exactly to y_mid
        crosses.append(make_cross(map_to_right(xn, yn), size=0.03))
    crosses_group = VGroup(*crosses)

    # Left-column vector {a; b}
    ab_tex = Tex(
        r"$\begin{cases} a \\ b \end{cases}$", color=BLACK, font_size=TEXT_FS
    )
    place_left_tex(ab_tex, above=eq_h, buff=LINE_BUFF)
    self.add(ab_tex)

    # Animate crosses row-by-row
    row_groups = []
    for j in range(grid_ny):
        row = VGroup()
        for idx, (_i, jj, _a, _b) in enumerate(labels_phys):
            if jj == j:
                row.add(crosses[idx])
        row_groups.append(row)
    self.play(
        LaggedStart(
            *[Create(r) for r in row_groups], lag_ratio=0.15, run_time=1.2
        )
    )
    self.add(crosses_group)

    self.next_slide()

    # --------------------------------------- Particles at displaced positions (SAME frame)
    particles = []
    for _i, _j, a_phys, b_phys in labels_phys:
        px_phys, pb_phys = get_particle_position(
            a_phys, b_phys, amp_base, k_val, omega_val, t_tracker.get_value()
        )
        xn = xn_from_xphys(px_phys)
        yn = yn_from_surface(
            pb_phys
        )  # pb_phys is b + eta: a "surface-like" vertical position
        particles.append(
            Dot(point=map_to_right(xn, yn), radius=0.06, color=pc.blueGreen)
        )
    particles_group = VGroup(*particles)
    self.add(particles_group)

    # Replace {a;b} by mapping; pre-place destination on the left
    mapping_tex = Tex(
        r"$\begin{cases} x(a,b,t) = a + \xi(a,b,t), \\ y(a,b,t) = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    place_left_tex(mapping_tex, above=eq_h, buff=LINE_BUFF)
    self.play(TransformMatchingTex(ab_tex, mapping_tex, run_time=0.8))
    ab_tex = mapping_tex

    self.next_slide()

    # ------------------------------------------------------- Animate t (0..2pi) with updaters
    def wave_updater(mobj):
        mobj.become(make_wave_curve())

    wave_curve.add_updater(wave_updater)

    def particles_updater(group):
        for idx, (_i, _j, a_phys, b_phys) in enumerate(labels_phys):
            px_phys, pb_phys = get_particle_position(
                a_phys,
                b_phys,
                amp_base,
                k_val,
                omega_val,
                t_tracker.get_value(),
            )
            xn = xn_from_xphys(px_phys)
            yn = yn_from_surface(pb_phys)
            group[idx].move_to(map_to_right(xn, yn))

    particles_group.add_updater(particles_updater)

    self.play(t_tracker.animate.set_value(2 * np.pi), run_time=2.5)

    self.next_slide()

    self.play(t_tracker.animate.set_value(4 * np.pi), run_time=2.5)
    t_tracker.set_value(t_tracker.get_value() % (2 * np.pi))

    # ------------------------------------------------------ Velocities (arrows) in SAME frame
    def get_velocity(a, b, amp_base, k, omega, t_val):
        """
        Return (u,w) in physical units at label (a,b); AE(b)=amp_base*exp(k*b).
        """
        theta = k * a - omega * t_val
        AE = amp_base * np.exp(k * b)
        u = AE * omega * np.cos(theta)
        dep_a = get_horizontal_displacement(a, b, amp_base, k, omega, t_val)
        w = AE * np.sin(k * dep_a + theta) * (omega - k * u)
        return (u, w)

    arrows = VGroup()
    for (_i, _j, a_phys, b_phys), dot in zip(labels_phys, particles):
        px_phys, pb_phys = get_particle_position(
            a_phys, b_phys, amp_base, k_val, omega_val, t_tracker.get_value()
        )
        xn = xn_from_xphys(px_phys)
        yn = yn_from_surface(pb_phys)
        p_world = map_to_right(xn, yn)

        u, w = get_velocity(
            a_phys, b_phys, amp_base, k_val, omega_val, t_tracker.get_value()
        )
        vel_scale = 0.35
        end_world = p_world + np.array([u * vel_scale, w * vel_scale, 0.0])

        arrows.add(
            Arrow(
                start=p_world,
                end=end_world,
                buff=0.0,
                stroke_width=6,
                color=pc.uclaGold,
                max_tip_length_to_length_ratio=0.25,
            )
        )
    self.add(arrows)

    # Velocity equations; pre-place on the left before transform
    vel_tex = Tex(
        r"$\begin{cases}"
        r"v_x(a,b,t) = A \omega e^{kb} \cos(ka - \omega t), \\"
        r"v_y(a,b,t) = A e^{kb} \sin\left(ka - \omega t + k\xi(a,b,t)\right)\left(\omega - k v_x(a,b,t)\right)"
        r"\end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    place_left_tex(vel_tex, above=eq_h, buff=LINE_BUFF)
    self.play(TransformMatchingTex(ab_tex, vel_tex, run_time=0.8))
    ab_tex = vel_tex

    self.next_slide()

    def arrows_updater(arr_group):
        for idx, ((_i, _j, a_phys, b_phys), arr) in enumerate(
            zip(labels_phys, arr_group)
        ):
            px_phys, pb_phys = get_particle_position(
                a_phys,
                b_phys,
                amp_base,
                k_val,
                omega_val,
                t_tracker.get_value(),
            )
            xn = xn_from_xphys(px_phys)
            yn = yn_from_surface(pb_phys)
            p_world = map_to_right(xn, yn)

            u, w = get_velocity(
                a_phys,
                b_phys,
                amp_base,
                k_val,
                omega_val,
                t_tracker.get_value(),
            )
            vel_scale = 0.35
            end_world = p_world + np.array([u * vel_scale, w * vel_scale, 0.0])

            arr.become(
                Arrow(
                    start=p_world,
                    end=end_world,
                    buff=0.0,
                    stroke_width=6,
                    color=pc.uclaGold,
                    max_tip_length_to_length_ratio=0.25,
                )
            )

    arrows.add_updater(arrows_updater)
    self.play(
        t_tracker.animate.set_value(t_tracker.get_value() + 2 * np.pi),
        run_time=2.5,
    )

    self.next_slide()

    self.play(
        t_tracker.animate.set_value(t_tracker.get_value() + 2 * np.pi),
        run_time=2.5,
    )

    # ------------------------------------------------------- clear right column, keep velocity eq
    wave_curve.clear_updaters()
    particles_group.clear_updaters()
    arrows.clear_updaters()
    self.play(
        FadeOut(
            VGroup(wave_curve, crosses_group, particles_group, arrows),
            run_time=0.5,
        ),
        FadeOut(intro, run_time=0.5),
        FadeOut(eq_h, run_time=0.5),
    )

    # Move velocity block to top-left
    vel_left_margin = -full_w * 0.5 + 0.4
    dx = vel_left_margin - ab_tex.get_left()[0]
    dy = top_y - ab_tex.get_top()[1]
    ab_tex.shift(RIGHT * dx + UP * dy)

    self.next_slide()

    # ------------------------------------------------------- Newton–Raphson text & equations
    missing_labels_tex = Tex(
        "Mais, on ne possede pas les labels.", color=BLACK, font_size=TEXT_FS
    )
    missing_labels_tex.next_to(ab_tex, DOWN, buff=LINE_BUFF, aligned_edge=LEFT)
    self.add(missing_labels_tex)

    self.next_slide()

    nr_title_tex = Tex(
        "On utilise la methode de Newton-Raphson :",
        color=BLACK,
        font_size=TEXT_FS,
    )
    nr_title_tex.next_to(
        missing_labels_tex, DOWN, buff=LINE_BUFF, aligned_edge=LEFT
    )
    self.add(nr_title_tex)

    nr_goal_tex = Tex(
        "A partir d'une position donnee determiner $a$ et $b$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    nr_goal_tex.next_to(nr_title_tex, DOWN, buff=LINE_BUFF, aligned_edge=LEFT)
    self.add(nr_goal_tex)

    inv_start_tex = Tex(
        r"$\begin{cases} x = a + \xi(a,b,t), \\ y = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    inv_start_tex.next_to(nr_goal_tex, DOWN, buff=LINE_BUFF, aligned_edge=LEFT)
    self.add(inv_start_tex)

    self.next_slide()

    inv_FG_tex = Tex(
        r"$\begin{cases} x = F(a) = a + \xi(a,b,t), \\ y = G(b) = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    inv_FG_tex.next_to(nr_goal_tex, DOWN, buff=LINE_BUFF, aligned_edge=LEFT)
    self.play(TransformMatchingTex(inv_start_tex, inv_FG_tex, run_time=1.0))
    inv_start_tex = inv_FG_tex

    self.next_slide()

    inv_final_tex = Tex(
        r"$\begin{cases} a = F^{-1}(x,y,t), \\ b = G^{-1}(x,y,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    inv_final_tex.next_to(nr_goal_tex, DOWN, buff=LINE_BUFF, aligned_edge=LEFT)
    self.play(TransformMatchingTex(inv_start_tex, inv_final_tex, run_time=1.0))

    # End
    self.pause()
    self.clear()
    self.next_slide()
