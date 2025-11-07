import numpy as np
import palette_colors as pc
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Arrow,
                   Create, Dot, FadeOut, GrowArrow, GrowFromCenter,
                   LaggedStart, Tex, TransformMatchingTex, ValueTracker,
                   VGroup, VMobject, config)
from slide_registry import slide


@slide(34)
def slide_34(self):
    """
    Vitesse d'Airy (slide 34).

    Implements the requested two-column layout with the wave, labels (a,b),
    particle positions, velocities, and the Newton–Raphson derivation.
    """

    # ----------------------------------------------- columns and common params
    full_w = config.frame_width
    full_h = config.frame_height

    # Left ~35%, Right ~65%
    left_w = full_w * 0.35
    right_w = full_w * 0.65

    left_center_x = -full_w * 0.5 + left_w * 0.5 + 0.3
    right_center_x = left_center_x + (left_w * 0.5) + (right_w * 0.5) + 0.3

    # Top bar and vertical bounds
    bar = self._top_bar("Vitesse d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)

    bar_rect = bar.submobjects[0]
    top_y = bar_rect.get_bottom()[1] - 0.2
    bottom_y = -full_h * 0.5 + 0.3

    # Helpers -----------------------------------------------------------------
    def place_left_tex(mobj, above=None, buff=0.2):
        """
        Left-column placement, left aligned and clamped inside the column.
        If above is None, place under the bar; else stack below 'above'.
        """
        if above is None:
            # left align to column left
            mobj.to_edge(LEFT, buff=0.0)
            dx = (left_center_x - left_w * 0.5 + 0.1) - mobj.get_left()[0]
            mobj.shift(RIGHT * dx)
            # top clamp under the bar
            dy = (top_y - buff) - mobj.get_top()[1]
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

    # Wave parameters
    A = 0.2
    k_val = 0.3
    omega_val = 1.0
    t_tracker = ValueTracker(0.0)

    # ---------------------------------------------- Intro text under the bar
    intro_tex = Tex(
        "Version lagrangienne d'Airy :", color=pc.oxfordBlue, font_size=36
    )
    # left margin under bar
    intro_tex.to_edge(LEFT, buff=0.4)
    dy_intro = top_y - intro_tex.get_top()[1]
    intro_tex.shift(UP * dy_intro)
    self.add(intro_tex)

    self.next_slide()

    # ----------------------------------------------------- Right-column curve
    def make_wave_curve():
        """
        h(x,t) = A cos(k x + omega t), spanning the full right column width.
        """
        n = 400
        pts = []
        # vertical midline of the right column at y_norm=0.5
        y_mid = 0.5
        y_scale = (top_y - bottom_y) * 0.15
        for i in range(n):
            xn = i / (n - 1)
            x_world = xn * right_w
            y_val = A * np.cos(
                k_val * x_world + omega_val * t_tracker.get_value()
            )
            yn = y_mid + (y_val * y_scale) / (top_y - bottom_y)
            pts.append(map_to_right(xn, yn))
        curve = VMobject()
        curve.set_points_smoothly(pts)
        curve.set_stroke(color=pc.oxfordBlue, width=4)
        return curve

    wave_curve = make_wave_curve()
    self.add(wave_curve)

    # Left-column equation h(x,t)
    eq_height = Tex(
        r"$h(x,t)=A\cos(kx+\omega t)$", color=pc.oxfordBlue, font_size=32
    )
    place_left_tex(eq_height)
    self.add(eq_height)

    # ------------------------------------------------------ Label grid (a,b)
    grid_nx, grid_ny = 7, 7
    label_points = []
    for j in range(grid_ny):
        for i in range(grid_nx):
            xn = i / (grid_nx - 1)  # 0..1 across width (full spread)
            yn = (j / (grid_ny - 1)) * 0.5  # 0..0.5 vertically (bottom to mid)
            label_points.append((i, j, xn, yn))

    def make_cross(center, size=0.03):
        """
        Small diagonal cross at center in pc.apple.
        """
        dx = size
        dy = size
        p1 = center + np.array([-dx, -dy, 0.0])
        p2 = center + np.array([dx, dy, 0.0])
        p3 = center + np.array([-dx, dy, 0.0])
        p4 = center + np.array([dx, -dy, 0.0])
        l1 = VMobject().set_stroke(color=pc.apple, width=3)
        l1.set_points_as_corners([p1, p2])
        l2 = VMobject().set_stroke(color=pc.apple, width=3)
        l2.set_points_as_corners([p3, p4])
        return VGroup(l1, l2)

    crosses = [
        make_cross(map_to_right(xn, yn), size=0.03)
        for (_i, _j, xn, yn) in label_points
    ]
    crosses_group = VGroup(*crosses)

    # Left-column vector {a; b}
    ab_tex = Tex(
        r"$\begin{cases} a \\ b \end{cases}$", color=pc.apple, font_size=32
    )
    place_left_tex(ab_tex, above=eq_height, buff=0.4)

    # Animate crosses row-by-row
    row_groups = []
    for j in range(grid_ny):
        row = VGroup()
        for idx, (_i, jj, xn, yn) in enumerate(label_points):
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

    # --------------------------------------- Particles from Lagrangian mapping
    def get_horizontal_displacement(a, b, amp, k, omega, t_val):
        theta = k * a - omega * t_val
        AE = amp * np.exp(k * b)
        return -AE * np.sin(theta)

    def get_vertical_displacement(a, b, amp, k, omega, t_val):
        theta = k * a - omega * t_val
        AE = amp * np.exp(k * b)
        return AE * np.cos(theta - k * AE * np.sin(theta))

    def get_particle_position(a, b, amp, k, omega, t_val):
        return (
            a + get_horizontal_displacement(a, b, amp, k, omega, t_val),
            b + get_vertical_displacement(a, b, amp, k, omega, t_val),
        )

    particles = []
    for _i, _j, xn, yn in label_points:
        a0 = xn * right_w
        b0 = yn * (top_y - bottom_y)
        px, py = get_particle_position(
            a0, b0, A, k_val, omega_val, t_tracker.get_value()
        )
        x_norm = px / right_w
        y_norm = py / (top_y - bottom_y)
        p_world = map_to_right(x_norm, y_norm)
        particles.append(Dot(point=p_world, radius=0.04, color=pc.blueGreen))
    particles_group = VGroup(*particles)
    self.add(particles_group)

    # Replace {a;b} by mapping
    new_mapping_tex = Tex(
        r"$\begin{cases} x(a,b,t) = a + \xi(a,b,t), \\ y(a,b,t) = b + \eta(a,b,t) \end{cases}$",
        color=pc.blueGreen,
        font_size=28,
    )
    self.play(TransformMatchingTex(ab_tex, new_mapping_tex, run_time=0.8))
    place_left_tex(new_mapping_tex, above=eq_height, buff=0.4)
    ab_tex = new_mapping_tex

    self.next_slide()

    # ------------------------------------------------------- Animate t (0..2pi)
    def wave_updater(mobj):
        mobj.become(make_wave_curve())

    wave_curve.add_updater(wave_updater)

    def particles_updater(group):
        idx = 0
        for _i, _j, xn, yn in label_points:
            a0 = xn * right_w
            b0 = yn * (top_y - bottom_y)
            px, py = get_particle_position(
                a0, b0, A, k_val, omega_val, t_tracker.get_value()
            )
            x_norm = px / right_w
            y_norm = py / (top_y - bottom_y)
            group[idx].move_to(map_to_right(x_norm, y_norm))
            idx += 1

    particles_group.add_updater(particles_updater)

    self.play(t_tracker.animate.set_value(2 * np.pi), run_time=2.5)
    self.next_slide()
    self.play(t_tracker.animate.set_value(4 * np.pi), run_time=2.5)
    t_tracker.set_value(t_tracker.get_value() % (2 * np.pi))

    # ------------------------------------------------------ Velocities arrows
    def get_velocity(a, b, amp, k, omega, t_val):
        theta = k * a - omega * t_val
        AE = amp * np.exp(k * b)
        u = AE * omega * np.cos(theta)
        dep_a = get_horizontal_displacement(a, b, amp, k, omega, t_val)
        w = AE * np.sin(k * dep_a + theta) * (omega - k * u)
        return (u, w)

    arrows = VGroup()
    for (_i, _j, xn, yn), dot in zip(label_points, particles):
        a0 = xn * right_w
        b0 = yn * (top_y - bottom_y)
        px, py = get_particle_position(
            a0, b0, A, k_val, omega_val, t_tracker.get_value()
        )
        x_norm = px / right_w
        y_norm = py / (top_y - bottom_y)
        p_world = map_to_right(x_norm, y_norm)
        u, w = get_velocity(a0, b0, A, k_val, omega_val, t_tracker.get_value())
        vel_scale = 0.3
        end_world = p_world + np.array([u * vel_scale, w * vel_scale, 0.0])
        arrows.add(
            Arrow(
                start=p_world,
                end=end_world,
                buff=0.0,
                stroke_width=4,
                color=pc.uclaGold,
                max_tip_length_to_length_ratio=0.2,
            )
        )
    self.add(arrows)

    vel_tex = Tex(
        r"$\begin{cases}"
        r"v_x(a,b,t) = A \omega e^{kb} \cos(ka - \omega t), \\"
        r"v_y(a,b,t) = A e^{kb} \sin\left(ka - \omega t + k\xi(a,b,t)\right)\left(\omega - k v_x(a,b,t)\right)"
        r"\end{cases}$",
        color=pc.uclaGold,
        font_size=24,
    )
    self.play(TransformMatchingTex(ab_tex, vel_tex, run_time=0.8))
    place_left_tex(vel_tex, above=eq_height, buff=0.4)
    ab_tex = vel_tex

    self.next_slide()

    # Animate wave + particles + arrows with time again
    def arrows_updater(arr_group):
        for idx, ((_i, _j, xn, yn), arr) in enumerate(
            zip(label_points, arr_group)
        ):
            a0 = xn * right_w
            b0 = yn * (top_y - bottom_y)
            px, py = get_particle_position(
                a0, b0, A, k_val, omega_val, t_tracker.get_value()
            )
            x_norm = px / right_w
            y_norm = py / (top_y - bottom_y)
            p_world = map_to_right(x_norm, y_norm)
            u, w = get_velocity(
                a0, b0, A, k_val, omega_val, t_tracker.get_value()
            )
            vel_scale = 0.3
            end_world = p_world + np.array([u * vel_scale, w * vel_scale, 0.0])
            arr.become(
                Arrow(
                    start=p_world,
                    end=end_world,
                    buff=0.0,
                    stroke_width=4,
                    color=pc.uclaGold,
                    max_tip_length_to_length_ratio=0.2,
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

    # ------------------------------------------------------- Clear right column
    wave_curve.clear_updaters()
    particles_group.clear_updaters()
    arrows.clear_updaters()
    self.play(
        FadeOut(
            VGroup(wave_curve, crosses_group, particles_group, arrows),
            run_time=0.5,
        ),
        FadeOut(intro_tex, run_time=0.5),
        FadeOut(eq_height, run_time=0.5),
    )

    # Move velocity block to top-left (full width now)
    vel_left_margin = -full_w * 0.5 + 0.4
    dx = vel_left_margin - ab_tex.get_left()[0]
    ab_tex.shift(RIGHT * dx)
    dy = top_y - ab_tex.get_top()[1]
    ab_tex.shift(UP * dy)

    self.next_slide()

    # ------------------------------------------------------- Newton–Raphson text
    missing_labels_tex = Tex(
        "Mais, on ne possede pas les labels.",
        color=pc.oxfordBlue,
        font_size=32,
    )
    missing_labels_tex.next_to(ab_tex, DOWN, buff=0.4, aligned_edge=LEFT)
    self.add(missing_labels_tex)

    self.next_slide()

    nr_title_tex = Tex(
        "On utilise la methode de Newton-Raphson :",
        color=pc.oxfordBlue,
        font_size=32,
    )
    nr_title_tex.next_to(missing_labels_tex, DOWN, buff=0.4, aligned_edge=LEFT)
    self.add(nr_title_tex)

    nr_goal_tex = Tex(
        "A partir d'une position donnee determiner $a$ et $b$",
        color=pc.oxfordBlue,
        font_size=28,
    )
    nr_goal_tex.next_to(nr_title_tex, DOWN, buff=0.3, aligned_edge=LEFT)
    self.add(nr_goal_tex)

    inv_start_tex = Tex(
        r"$\begin{cases} x = a + \xi(a,b,t), \\ y = b + \eta(a,b,t) \end{cases}$",
        color=pc.blueGreen,
        font_size=28,
    )
    inv_start_tex.next_to(nr_goal_tex, DOWN, buff=0.4, aligned_edge=LEFT)
    self.add(inv_start_tex)

    self.next_slide()

    inv_FG_tex = Tex(
        r"$\begin{cases} x = F(a) = a + \xi(a,b,t), \\ y = G(b) = b + \eta(a,b,t) \end{cases}$",
        color=pc.blueGreen,
        font_size=28,
    )
    self.play(TransformMatchingTex(inv_start_tex, inv_FG_tex, run_time=1.0))
    # keep left alignment after transform
    dx = inv_start_tex.get_left()[0] - inv_FG_tex.get_left()[0]
    dy = inv_start_tex.get_top()[1] - inv_FG_tex.get_top()[1]
    inv_FG_tex.shift(RIGHT * dx + UP * dy)
    inv_start_tex = inv_FG_tex

    self.next_slide()

    inv_final_tex = Tex(
        r"$\begin{cases} a = F^{-1}(x,y,t), \\ b = G^{-1}(x,y,t) \end{cases}$",
        color=pc.apple,
        font_size=28,
    )
    self.play(TransformMatchingTex(inv_start_tex, inv_final_tex, run_time=1.0))
    dx = inv_start_tex.get_left()[0] - inv_final_tex.get_left()[0]
    dy = inv_start_tex.get_top()[1] - inv_final_tex.get_top()[1]
    inv_final_tex.shift(RIGHT * dx + UP * dy)

    # End
    self.pause()
    self.clear()
    self.next_slide()
