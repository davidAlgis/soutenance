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

    Full rewrite that keeps CSV reading and enforces the staging:
    1) Show crosses only (labels).
    2) Next slide -> show particles only at CSV positions (no arrows).
    3) Next slide -> add velocity arrows.

    Other rules:
    - The right-column curve, crosses, particles and arrows share the SAME frame derived
      from the CSV ranges. The curve zero-line is aligned via the mean top-row position.
    - All texts are BLACK with uniform font size and spacing.
    - Animate TransformMatchingTex between position and velocity equations on the left.
    - Slower time animation; visuals are placed slightly lower (SCALE_Y).
    """

    # ----------------------------- imports and layout
    import csv

    import numpy as np
    from manim import (BLACK, ORIGIN, Arrow, Create, Dot, FadeOut, LaggedStart,
                       Tex, TransformMatchingTex, ValueTracker, VGroup,
                       VMobject, config)

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

    # Place visuals a bit lower in the right column
    SCALE_Y = 0.82

    def place_left_tex(mobj, above=None, buff=LINE_BUFF):
        """
        Place a Tex in the left column, left-aligned and inside the column.
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

    # ----------------------------- intro text
    intro = Tex(
        "Version lagrangienne d'Airy :", color=BLACK, font_size=TEXT_FS
    )
    intro.to_edge(LEFT, buff=0.4)
    dy_intro = top_y - intro.get_top()[1]
    intro.shift(np.array([0.0, dy_intro, 0.0]))
    self.add(intro)

    self.next_slide()

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

    # Identify top label row indices (max label_y at t0)
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

    # ----------------------------- right-column visuals: curve and crosses
    # Wave parameters for visual curve alignment
    A = 0.2
    k_val = 1.25
    omega_val = 3.51

    t_tracker = ValueTracker(T_MIN)

    def compute_y0(t):
        """
        Mean y of the top label row at time t, to align the curve midline.
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
        y(x,t) = y0(t) + A*cos(k*x - omega*t) plotted in the CSV physical x-range.
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
    self.add(wave_curve)

    # Left equation for h
    eq_h = Tex(r"$h(x,t)=A\cos(kx-\omega t)$", color=BLACK, font_size=TEXT_FS)
    place_left_tex(eq_h, above=intro, buff=LINE_BUFF * 1.2)
    self.add(eq_h)

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

    # Unique label positions at t0 for staging by rows
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
        c = make_cross(map_to_right(xn, yn), size=0.03)
        crosses.append(c)
        rid = y_to_row[round(ly, 6)]
        rows_groups.setdefault(rid, VGroup()).add(c)

    crosses_group = VGroup(*crosses)

    # Left "labels" vector
    ab_tex = Tex(
        r"$\begin{pmatrix} a \\ b \end{pmatrix}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    place_left_tex(ab_tex, above=eq_h, buff=LINE_BUFF)
    self.add(ab_tex)

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
    # Create particle dots and their updater; add after this pause so they appear alone.
    ordered_indices = sorted(rows_by_index.keys())
    particles = VGroup()
    for _ in ordered_indices:
        particles.add(Dot(point=ORIGIN, radius=0.06, color=pc.blueGreen))
    self.add(particles)
    self.add_foreground_mobject(particles)

    # Position equation on the left (animate from labels vector)
    mapping_tex = Tex(
        r"$\begin{cases} x(a,b,t) = a + \xi(a,b,t), \\ y(a,b,t) = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    place_left_tex(mapping_tex, above=eq_h, buff=LINE_BUFF)
    self.play(TransformMatchingTex(ab_tex, mapping_tex, run_time=0.8))
    ab_tex = mapping_tex

    # Updater for curve and particles
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

    # Slower animation over one period
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

    # Animate transform of left text: position -> velocity equations
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

    # Animate one more period with arrows visible
    self.play(
        t_tracker.animate.set_value(T_MIN + 2 * (T_MAX - T_MIN)),
        run_time=SLOW_RT,
    )
    t_tracker.set_value(
        ((t_tracker.get_value() - T_MIN) % (T_MAX - T_MIN)) + T_MIN
    )

    # ----------------------------- extra loop with arrows
    self.next_slide()
    self.play(
        t_tracker.animate.set_value(T_MIN + (T_MAX - T_MIN)), run_time=SLOW_RT
    )

    # ----------------------------- clear right column, keep velocity eq
    wave_curve.clear_updaters()
    particles.clear_updaters()
    arrows.clear_updaters()
    self.play(
        FadeOut(
            VGroup(wave_curve, crosses_group, particles, arrows), run_time=0.6
        ),
        FadeOut(intro, run_time=0.6),
        FadeOut(eq_h, run_time=0.6),
    )

    # Move velocity block to top-left
    vel_left_margin = -full_w * 0.5 + 0.4
    dx = vel_left_margin - ab_tex.get_left()[0]
    dy = top_y - ab_tex.get_top()[1]
    ab_tex.shift(np.array([dx, dy, 0.0]))

    self.next_slide()

    # Newton-Raphson text and equations
    missing_labels_tex = Tex(
        "Mais, on ne possede pas les labels.", color=BLACK, font_size=TEXT_FS
    )
    missing_labels_tex.next_to(
        ab_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.add(missing_labels_tex)

    self.next_slide()

    nr_title_tex = Tex(
        "On utilise la methode de Newton-Raphson :",
        color=BLACK,
        font_size=TEXT_FS,
    )
    nr_title_tex.next_to(
        missing_labels_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.add(nr_title_tex)

    nr_goal_tex = Tex(
        "A partir d'une position donnee determiner $a$ et $b$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    nr_goal_tex.next_to(
        nr_title_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.add(nr_goal_tex)

    inv_start_tex = Tex(
        r"$\begin{cases} x = a + \xi(a,b,t), \\ y = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    inv_start_tex.next_to(
        nr_goal_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.add(inv_start_tex)

    self.next_slide()

    inv_FG_tex = Tex(
        r"$\begin{cases} x = F(a) = a + \xi(a,b,t), \\ y = G(b) = b + \eta(a,b,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    inv_FG_tex.next_to(
        nr_goal_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.play(TransformMatchingTex(inv_start_tex, inv_FG_tex, run_time=1.0))
    inv_start_tex = inv_FG_tex

    self.next_slide()

    inv_final_tex = Tex(
        r"$\begin{cases} a = F^{-1}(x,y,t), \\ b = G^{-1}(x,y,t) \end{cases}$",
        color=BLACK,
        font_size=TEXT_FS,
    )
    inv_final_tex.next_to(
        nr_goal_tex,
        direction=np.array([0.0, -1.0, 0.0]),
        buff=LINE_BUFF,
        aligned_edge=LEFT,
    )
    self.play(TransformMatchingTex(inv_start_tex, inv_final_tex, run_time=1.0))

    # End
    self.pause()
    self.clear()
    self.next_slide()
