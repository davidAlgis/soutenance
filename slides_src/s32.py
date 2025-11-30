import numpy as np
import palette_colors as pc
from manim import (BLACK, DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Arrow,
                   Create, Dot, FadeOut, GrowArrow, GrowFromCenter,
                   LaggedStart, Tex, TransformMatchingTex, ValueTracker,
                   VGroup, VMobject, config)
from slide_registry import slide


@slide(32)
def slide_32(self):
    """
    Vitesse d'Airy (slide 34).

    CSV-driven staging:
      1) Show label crosses only.
      2) Next slide -> reveal particles ONLY (no arrows) WHILE transforming the
         left equation from labels (a,b) to positions (x,y) in a single play().
      3) Next slide -> add velocity arrows and transform the left equation to
         velocity (second velocity line split earlier to avoid overlap). During
         that first velocity animation, time advances so curve, particles and
         arrows all move.
      4) When clearing the right visuals, fade out particles and arrows too, then
         smoothly convert the velocity cases into the vector form v_i^A and move
         it under the top bar before continuing — with an explicit animated shift.
      5) The final inverse mapping cases are centered (same vertical position kept)
         and rendered with a larger font size; their transforms keep the same Y.

    All texts are BLACK with uniform base font size, unless noted.
    """
    # ----------------------------- imports and layout
    import csv

    import numpy as np
    from manim import (BLACK, LEFT, ORIGIN, Arrow, Create, Dot, FadeIn,
                       FadeOut, GrowFromCenter, LaggedStart, Tex,
                       TransformMatchingTex, ValueTracker, VGroup, VMobject,
                       config)

    full_w = config.frame_width
    full_h = config.frame_height

    left_w = full_w * 0.35
    right_w = full_w * 0.65

    left_center_x = -full_w * 0.5 + left_w * 0.5 + 0.3
    right_center_x = left_center_x + (left_w * 0.5) + (right_w * 0.5) + 0.3

    bar, footer = self._top_bar("Vitesse d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]
    top_y = bar_rect.get_bottom()[1] - 0.2
    bottom_y = -full_h * 0.5 + 0.3

    self.BODY_FONT_SIZE = self.BODY_FONT_SIZE
    LINE_BUFF = 0.35
    SCALE_Y = 0.82  # place right visuals slightly lower

    def place_left_tex(mobj, above=None, buff=LINE_BUFF):
        """
        Left-column placement helper: left align and keep within column.
        """
        if above is None:
            mobj.to_edge(LEFT, buff=0.0)
            dx = (left_center_x - left_w * 0.5 + 0.1) - mobj.get_left()[0]
            mobj.shift(np.array([dx, 0.0, 0.0]))
            dy = (top_y - 0.15) - mobj.get_top()[1]
            mobj.shift(np.array([0.0, dy, 0.0]))
        else:
            mobj.next_to(
                above,
                direction=np.array([0.0, -1.0, 0.0]),
                buff=buff,
                aligned_edge=LEFT,
            )
            dx = (left_center_x - left_w * 0.5 + 0.1) - mobj.get_left()[0]
            mobj.shift(np.array([dx, 0.0, 0.0]))
        return mobj

    def map_to_right(x_norm, y_norm):
        """
        Map normalized coords (0..1, 0..1) to the right column rectangle.
        """
        x0 = right_center_x - right_w * 0.5
        y0 = bottom_y
        return np.array(
            [
                x0 + x_norm * right_w,
                y0 + y_norm * (top_y - bottom_y) * SCALE_Y,
                0.0,
            ]
        )

    # ----------------------------- intro text (ensure at least one animation before pause)
    intro = Tex(
        r"$h(x,t)=A\cos(kx-\omega t)$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    intro.to_edge(LEFT, buff=0.4)
    dy_intro = top_y - intro.get_top()[1]
    intro.shift(np.array([0.0, dy_intro, 0.0]))
    self.play(FadeIn(intro, shift=RIGHT * self.SHIFT_SCALE), run_time=0.2)

    # ----------------------------- CSV load
    # CSV header: index_p;time;label_x;label_y;pos_x;pos_y;vel_x;vel_y
    csv_path = "states_sph/airy_particles.csv"
    times = []
    rows_by_index = {}

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            idx = int(r["index_p"])
            t = float(r["time"])
            lx = float(r["label_x"])
            ly = float(r["label_y"])
            px = float(r["pos_x"])
            py = float(r["pos_y"])
            vx = float(r["vel_x"])
            vy = float(r["vel_y"])
            if idx not in rows_by_index:
                rows_by_index[idx] = {
                    "time": [],
                    "label_x": [],
                    "label_y": [],
                    "pos_x": [],
                    "pos_y": [],
                    "vel_x": [],
                    "vel_y": [],
                }
            d = rows_by_index[idx]
            d["time"].append(t)
            d["label_x"].append(lx)
            d["label_y"].append(ly)
            d["pos_x"].append(px)
            d["pos_y"].append(py)
            d["vel_x"].append(vx)
            d["vel_y"].append(vy)
            times.append(t)

    # Sort series by time; build time bounds and physical ranges
    for idx, d in rows_by_index.items():
        order = np.argsort(np.array(d["time"]))
        for k in d.keys():
            d[k] = list(np.array(d[k])[order])

    times_all = np.unique(np.array(times))
    if len(times_all) == 0:
        return

    T_MIN = float(times_all.min())
    T_MAX = float(times_all.max())

    all_x = []
    all_y = []
    for d in rows_by_index.values():
        all_x.extend(d["label_x"])
        all_x.extend(d["pos_x"])
        all_y.extend(d["label_y"])
        all_y.extend(d["pos_y"])
    X_MIN = float(np.min(all_x))
    X_MAX = float(np.max(all_x))
    Y_MIN = float(np.min(all_y))
    Y_MAX = float(np.max(all_y))
    if X_MAX == X_MIN:
        X_MAX = X_MIN + 1.0
    if Y_MAX == Y_MIN:
        Y_MAX = Y_MIN + 1.0

    def xn_from_xphys(x_phys):
        return (x_phys - X_MIN) / (X_MAX - X_MIN)

    def yn_from_yphys(y_phys):
        return (y_phys - Y_MIN) / (Y_MAX - Y_MIN)

    def lerp_series(ts, ys, t):
        """
        Linear interpolation y(t) with times ts and samples ys.
        """
        if t <= ts[0]:
            return ys[0]
        if t >= ts[-1]:
            return ys[-1]
        i = int(np.searchsorted(ts, t))
        t1, t2 = ts[i - 1], ts[i]
        y1, y2 = ys[i - 1], ys[i]
        a = 0.0 if t2 == t1 else (t - t1) / (t2 - t1)
        return (1.0 - a) * y1 + a * y2

    # Identify indices of the top label row at t0
    t0 = float(times_all[0])
    label_y_at_t0 = []
    for idx, d in rows_by_index.items():
        label_y_at_t0.append(lerp_series(d["time"], d["label_y"], t0))
    max_label_y = float(np.max(label_y_at_t0))
    top_eps = max(1e-6, 1e-3 * max(1.0, abs(max_label_y)))
    top_indices = [
        idx
        for idx, d in rows_by_index.items()
        if abs(lerp_series(d["time"], d["label_y"], t0) - max_label_y)
        <= top_eps
    ]

    # ----------------------------- right visuals: curve and crosses
    A = 0.2
    k_val = 1.25
    omega_val = 3.51

    t_tracker = ValueTracker(T_MIN)

    def compute_y0(t):
        """
        Mean pos_y of the top label row at time t, used as wave midline.
        """
        if not top_indices:
            return 0.0
        vals = []
        for idx in top_indices:
            d = rows_by_index[idx]
            vals.append(lerp_series(d["time"], d["pos_y"], t))
        return float(np.mean(vals))

    def make_wave_curve():
        """
        y(x,t) = y0(t) + A*cos(k*x - omega*t) over [X_MIN, X_MAX].
        """
        n = 400
        pts = []
        y0 = compute_y0(t_tracker.get_value())
        for i in range(n):
            xn = i / (n - 1)
            x_phys = X_MIN + xn * (X_MAX - X_MIN)
            y_phys = y0 + A * np.cos(
                k_val * x_phys - omega_val * t_tracker.get_value()
            )
            pts.append(map_to_right(xn, yn_from_yphys(y_phys)))
        curve = VMobject()
        curve.set_points_smoothly(pts)
        curve.set_stroke(color=pc.oxfordBlue, width=4)
        return curve

    wave_curve = make_wave_curve()
    self.play(Create(wave_curve))
    self.wait(0.1)
    self.next_slide()

    # Left equation for h
    eq_h = Tex(
        r"Version lagrangienne d'Airy :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    place_left_tex(eq_h, above=intro, buff=LINE_BUFF * 1.2)
    self.play(FadeIn(eq_h, shift=RIGHT * self.SHIFT_SCALE))

    # Crosses at label positions (time-independent)
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

    labels_once = []
    for idx, d in rows_by_index.items():
        lx0 = d["label_x"][0]
        ly0 = d["label_y"][0]
        labels_once.append((idx, lx0, ly0))
    unique_ys = sorted({round(ly, 6) for (_, _, ly) in labels_once})
    y_to_row = {y: i for i, y in enumerate(unique_ys)}

    crosses = []
    rows_groups = {}
    for idx, lx, ly in labels_once:
        xn = xn_from_xphys(lx)
        yn = yn_from_yphys(ly)
        c = make_cross(map_to_right(xn, yn), size=0.07)
        crosses.append(c)
        rid = y_to_row[round(ly, 6)]
        rows_groups.setdefault(rid, VGroup()).add(c)

    crosses_group = VGroup(*crosses)

    # Left labels vector
    ab_tex = Tex(
        r"$\begin{pmatrix} a \\ b \end{pmatrix}$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    place_left_tex(ab_tex, above=eq_h, buff=LINE_BUFF)
    self.play(FadeIn(ab_tex, shift=RIGHT * self.SHIFT_SCALE))

    # Animate crosses row-by-row
    row_ids_sorted = sorted(rows_groups.keys())
    self.play(
        LaggedStart(
            *[Create(rows_groups[rid]) for rid in row_ids_sorted],
            lag_ratio=0.15,
            run_time=1.2,
        )
    )
    self.add(crosses_group)

    # ----------------------------- PAUSE 1: crosses only
    self.next_slide()

    # ----------------------------- particles only (no arrows yet)
    ordered_indices = sorted(rows_by_index.keys())
    particles = VGroup()
    for _ in ordered_indices:
        particles.add(Dot(point=ORIGIN, radius=0.06, color=pc.blueGreen))
    self.add(particles)
    self.add_foreground_mobject(particles)

    # Updaters: curve and particles
    def wave_updater(mobj):
        mobj.become(make_wave_curve())

    wave_curve.add_updater(wave_updater)

    def particles_updater(group):
        t = t_tracker.get_value()
        for i, idx in enumerate(ordered_indices):
            d = rows_by_index[idx]
            px = lerp_series(d["time"], d["pos_x"], t)
            py = lerp_series(d["time"], d["pos_y"], t)
            xn = xn_from_xphys(px)
            yn = yn_from_yphys(py)
            group[i].move_to(map_to_right(xn, yn))

    particles.add_updater(particles_updater)

    # Position equation (transform) REVEALED IN PARALLEL with particles appearance
    mapping_tex = Tex(
        r"$\begin{cases} x(a,b,t) = a + \xi(a,b,t), \\ y(a,b,t) = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    place_left_tex(mapping_tex, above=eq_h, buff=LINE_BUFF)

    # Animate both: equation transform AND particles grow, in a single play()
    self.play(
        TransformMatchingTex(ab_tex, mapping_tex),
        LaggedStart(*[GrowFromCenter(p) for p in particles], lag_ratio=0.02),
        run_time=0.9,
    )
    ab_tex = mapping_tex

    # Slower animation over one period with particles visible
    SLOW_RT = 4.0
    self.play(
        t_tracker.animate.set_value(T_MIN + (T_MAX - T_MIN)), run_time=SLOW_RT
    )

    # ----------------------------- PAUSE 2: particles are visible and animated
    self.next_slide()

    # ----------------------------- add velocity arrows now (in addition)
    # Screen-space scaling for velocity vectors
    x_scale_screen = right_w / (X_MAX - X_MIN)
    y_scale_screen = ((top_y - bottom_y) * SCALE_Y) / (Y_MAX - Y_MIN)
    VEL_GAIN = 1.2

    arrows = VGroup()
    for _ in ordered_indices:
        arrows.add(
            Arrow(
                ORIGIN,
                ORIGIN + np.array([0.4, 0.0, 0.0]),
                buff=0.0,
                stroke_width=7,
                color=pc.uclaGold,
                max_tip_length_to_length_ratio=0.3,
            )
        )
    self.add(arrows)
    self.add_foreground_mobject(arrows)

    def arrows_updater(group):
        t = t_tracker.get_value()
        for i, idx in enumerate(ordered_indices):
            d = rows_by_index[idx]
            px = lerp_series(d["time"], d["pos_x"], t)
            py = lerp_series(d["time"], d["pos_y"], t)
            vx = lerp_series(d["time"], d["vel_x"], t)
            vy = lerp_series(d["time"], d["vel_y"], t)
            p_world = map_to_right(xn_from_xphys(px), yn_from_yphys(py))
            end_world = p_world + np.array(
                [
                    vx * x_scale_screen * VEL_GAIN,
                    vy * y_scale_screen * VEL_GAIN,
                    0.0,
                ]
            )
            group[i].become(
                Arrow(
                    start=p_world,
                    end=end_world,
                    buff=0.0,
                    stroke_width=7,
                    color=pc.uclaGold,
                    max_tip_length_to_length_ratio=0.3,
                )
            )

    arrows.add_updater(arrows_updater)

    # Animate transform to velocity equations (split earlier; broken line)
    vel_cases_tex = Tex(
        r"$\begin{cases}"
        r"v_x(a,b,t) = A e^{kb} \psi(a, t), \\"
        r"v_y(a,b,t) = A e^{kb} \nu(a,t)"
        r"\end{cases}$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    place_left_tex(vel_cases_tex, above=eq_h, buff=LINE_BUFF)

    # During this first velocity reveal, advance time so curve, particles AND arrows move
    self.play(
        TransformMatchingTex(ab_tex, vel_cases_tex),
        # t_tracker.animate.set_value(T_MIN + 0.25 * (T_MAX - T_MIN)),
        run_time=0.9,
    )
    ab_tex = vel_cases_tex

    # Animate one more period with arrows visible
    # self.play(
    #     t_tracker.animate.set_value(T_MIN + 2 * (T_MAX - T_MIN)),
    #     run_time=SLOW_RT,
    # )
    t_tracker.set_value(
        ((t_tracker.get_value() - T_MIN) % (T_MAX - T_MIN)) + T_MIN
    )

    # ----------------------------- extra loop with arrows
    self.play(
        t_tracker.animate.set_value(T_MIN + (T_MAX - T_MIN)), run_time=SLOW_RT
    )
    self.wait(0.1)
    self.next_slide()
    # ----------------------------- clear right visuals; smoothly convert to vector and move under bar
    wave_curve.clear_updaters()
    particles.clear_updaters()
    arrows.clear_updaters()
    self.play(
        FadeOut(wave_curve, run_time=0.5),
        FadeOut(crosses_group, run_time=0.5),
        FadeOut(particles, run_time=0.5),
        FadeOut(arrows, run_time=0.5),
        FadeOut(intro, run_time=0.5),
        FadeOut(eq_h, run_time=0.5),
    )

    self.remove_foreground_mobject(particles)
    self.remove_foreground_mobject(arrows)

    # --- Convert velocity cases to vector form **in place** (no recentre), then animate shift to top
    vel_vector_tex = Tex(
        r"$v_i^A = \begin{pmatrix}"
        r"A e^{kb} \psi(a, t) \\ "
        r"A e^{kb} \nu(a,t)"
        r"\end{pmatrix}$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    # Position target exactly where current equation is, so TransformMatchingTex doesn't jump
    vel_vector_tex.move_to(ab_tex.get_center() + np.array([1.5, 0.0, 0.0]))
    self.play(TransformMatchingTex(ab_tex, vel_vector_tex, run_time=0.6))
    ab_tex = vel_vector_tex

    # Now compute an explicit delta to move UNDER THE BAR (top-left), and animate it clearly
    target_left_margin = -full_w * 0.5 + 0.4
    dx = target_left_margin - ab_tex.get_left()[0]
    dy = top_y - ab_tex.get_top()[1]
    # Visible move (no pre-move, no re-centre): this always animates to the top
    self.play(ab_tex.animate.shift(np.array([dx, dy, 0.0])), run_time=0.9)

    self.next_slide()

    # Newton-Raphson texts fade in smoothly
    missing_labels_tex = Tex(
        "Mais, on ne possède pas les labels.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    missing_labels_tex.next_to(
        ab_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.play(
        FadeIn(missing_labels_tex, shift=RIGHT * self.SHIFT_SCALE),
        run_time=0.3,
    )

    self.next_slide()

    nr_title_tex = Tex(
        "\mbox{Méthode de Newton-Raphson pour déterminer $a$ et $b$ à partir d'une position donnée :}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    nr_title_tex.next_to(
        missing_labels_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )

    self.play(
        FadeIn(nr_title_tex, shift=RIGHT * self.SHIFT_SCALE), run_time=0.3
    )

    # Final inverse mapping cases: BIGGER and CENTERED; keep same Y across transforms
    BIG_FS = self.BODY_FONT_SIZE + 15
    inv_y_ref = (
        nr_title_tex.get_bottom()[1] - LINE_BUFF - BIG_FS * 0.012 - 1.0
    )  # reference Y

    inv_start_tex = Tex(
        r"$\begin{cases} x = a + \xi(a,b,t), \\ y = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=BIG_FS,
    )
    inv_start_tex.move_to(np.array([0.0, inv_y_ref, 0.0]))  # center X, keep Y
    self.play(
        FadeIn(inv_start_tex, shift=RIGHT * self.SHIFT_SCALE), run_time=0.3
    )

    self.next_slide()

    inv_FG_tex = Tex(
        r"$\begin{cases} x = F(a) = a + \xi(a,b,t), \\ y = G(b) = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=BIG_FS,
    )
    inv_FG_tex.move_to(np.array([0.0, inv_start_tex.get_center()[1], 0.0]))
    self.play(TransformMatchingTex(inv_start_tex, inv_FG_tex, run_time=1.0))
    inv_start_tex = inv_FG_tex  # reuse variable for next transform

    self.next_slide()

    inv_final_tex = Tex(
        r"$\begin{cases} a = F^{-1}(x,y,t), \\ b = G^{-1}(x,y,t) \end{cases}$",
        color=BLACK,
        font_size=BIG_FS,
    )
    inv_final_tex.move_to(np.array([0.0, inv_start_tex.get_center()[1], 0.0]))
    self.play(TransformMatchingTex(inv_start_tex, inv_final_tex, run_time=1.0))

    # End
    self.wait(0.2)
    self.clear()
    self.next_slide()
