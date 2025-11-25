import random

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(4)
def slide_04(self):
    """
    Slide 4 : Sommaires
    - Top bar + intro
    - 'I) Couplages 3 méthodes grandes échelles'
    - Left column: miniature of slide 16 WITH animations, boxed (wave+boat stay inside)
      (colors and directions synced with your updated slide 16: buoyancy in pc.tiffanyBlue)
    - Right column: triangle + labels ('Préc.', 'Perf.', 'Éch.')
    - Then draw a jellyBean cross at center, then move it toward bottom side
      while the mini-wave is animating.
    """

    bar, footer = self._top_bar("Sommaire")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ==== Intro line ====
    intro = Tex(
        r"Pour répondre à nos objectifs :",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    intro.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (-config.frame_width / 2 + self.DEFAULT_PAD) - intro.get_left()[0]
    intro.shift(RIGHT * (dx + 0.6))
    self.play(FadeIn(intro, run_time=0.5, shift=RIGHT * self.SHIFT_SCALE))
    self.next_slide()

    # ==== Section title ====
    sec = Tex(
        r"I) Couplage 3 méthodes grandes échelles",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    sec.next_to(intro, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    sec.shift(RIGHT * (dx + 0.6))
    self.play(FadeIn(sec, run_time=0.5, shift=RIGHT * self.SHIFT_SCALE))

    # ==== Columns geometry ====
    y_bottom = -config.frame_height / 2 + 0.6
    usable_top = sec.get_bottom()[1] - 0.35
    usable_bot = y_bottom
    usable_h = max(1.0, usable_top - usable_bot)

    full_w = config.frame_width
    side_pad = 0.6
    col_gap = 0.7
    left_x = -full_w / 2 + side_pad
    right_x = full_w / 2 - side_pad
    total_w = right_x - left_x
    col_w = (total_w - col_gap) * 0.5
    left_center = np.array(
        [left_x + col_w / 2, (usable_top + usable_bot) * 0.5, 0.0]
    )
    right_center = np.array(
        [
            left_x + col_w + col_gap + col_w / 2,
            (usable_top + usable_bot) * 0.5,
            0.0,
        ]
    )

    # -------------------------------------------------------------------------
    # LEFT COLUMN: Miniature of slide 16 with animations (boxed) - synced colors
    # -------------------------------------------------------------------------
    mini_fs = self.BODY_FONT_SIZE - 6
    mini_fs_eq = mini_fs + 2

    # Forces (two columns)
    t1 = Tex(
        r"$\mathbf{F}_b$ : Poussée d'Archimède", color=BLACK, font_size=mini_fs
    )
    t1.set_color_by_tex(r"\mathbf{F}_b", pc.tiffanyBlue)
    bL1 = VGroup(t1).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

    t2 = Tex(r"$\mathbf{F}_a$ : Traînée air", color=BLACK, font_size=mini_fs)
    t2.set_color_by_tex(r"\mathbf{F}_a", pc.jellyBean)
    bL2 = VGroup(t2).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    left_forces = VGroup(bL1, bL2).arrange(DOWN, buff=0.20, aligned_edge=LEFT)

    t3 = Tex(r"$\mathbf{F}_w$ : Traînée eau", color=BLACK, font_size=mini_fs)
    t3.set_color_by_tex(r"\mathbf{F}_w", pc.heliotropeMagenta)

    bR1 = VGroup(t3).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

    t4 = Tex(r"$\mathbf{F}_g$ : Gravité", color=BLACK, font_size=mini_fs)
    t4.set_color_by_tex(r"\mathbf{F}_g", pc.apple)

    right_forces = VGroup(
        bR1, VGroup(t4).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    ).arrange(DOWN, buff=0.20, aligned_edge=LEFT)

    forces_grid = VGroup(left_forces, right_forces).arrange(
        RIGHT, buff=0.6, aligned_edge=UP
    )

    # Placeholder static wave for layout
    mini_wave_w = col_w * 0.9
    xs_static = np.linspace(-mini_wave_w / 2, mini_wave_w / 2, 200)
    amp = 0.06
    k = 1.5
    y0_base = -0.6
    ys_static = y0_base + amp * np.cos(k * xs_static)
    pts_static = np.column_stack(
        [xs_static, ys_static, np.zeros_like(xs_static)]
    )
    mini_wave_placeholder = VMobject(stroke_color=pc.blueGreen, stroke_width=3)
    mini_wave_placeholder.set_points_smoothly(
        [*map(lambda p: np.array(p), pts_static)]
    )
    y0_boat = y0_base - 0.5
    # Mini boat (stroke color synced with your new slide 16)
    boat_pts = [
        [-0.25, y0_boat + 0.12, 0.0],
        [0.25, y0_boat + 0.12, 0.0],
        [0.5, y0_boat + 0.42, 0.0],
        [0.125, y0_boat + 0.42, 0.0],
        [0.0, y0_boat + 0.70, 0.0],
        [-0.125, y0_boat + 0.42, 0.0],
        [-0.5, y0_boat + 0.42, 0.0],
    ]
    mini_boat = Polygon(
        *[np.array(p) for p in boat_pts],
        fill_color=pc.uclaGold,
        fill_opacity=1.0,
        stroke_color=pc.uclaGold,
        stroke_width=2,
    ).set_z_index(10)

    left_block = VGroup(forces_grid, mini_wave_placeholder, mini_boat).arrange(
        DOWN, buff=0.35
    )

    # Box the miniature
    box_pad = 0.25
    box = Rectangle(
        width=left_block.width + 2 * box_pad,
        height=left_block.height + 2 * box_pad,
        stroke_color=BLACK,
        stroke_width=2,
    )
    left_group = VGroup(box, left_block)

    # Fit to column and position
    max_left_w = col_w * 0.98
    max_left_h = usable_h * 0.95
    s_left = min(
        1.0,
        max_left_w / left_group.width if left_group.width > 0 else 1.0,
        max_left_h / left_group.height if left_group.height > 0 else 1.0,
    )
    if s_left < 1.0:
        left_group.scale(s_left)
    left_group.move_to(left_center)
    self.play(Create(box, run_time=0.25))

    # Anchor for animated wave and boat after layout is finalized
    wave_anchor = mini_wave_placeholder.get_center()
    # Sea baseline inside box
    y0 = wave_anchor[1]  # keep baseline at the placeholder center Y
    mini_boat.move_to([wave_anchor[0], y0 - 0.5, 0.0])

    # Animated wave (anchored inside the miniature)
    t_tracker = ValueTracker(0.0)

    def make_water():
        ys = y0_base + amp * np.cos(k * xs_static + t_tracker.get_value())
        pts = np.column_stack(
            [
                xs_static + wave_anchor[0],
                ys + wave_anchor[1],
                np.zeros_like(xs_static),
            ]
        )
        m = VMobject(stroke_color=pc.blueGreen, stroke_width=3)
        m.set_points_smoothly([*map(lambda p: np.array(p), pts)])
        m.set_z_index(1)
        return m

    mini_wave = always_redraw(make_water)
    # Replace placeholder in left_block by animated wave
    idx = left_block.submobjects.index(mini_wave_placeholder)
    left_block.submobjects[idx] = mini_wave

    # Show miniature, with its animations
    self.play(FadeIn(forces_grid, run_time=0.45))
    self.add(mini_wave)
    self.add(mini_boat)
    self.add_foreground_mobject(mini_boat)

    # Small force arrows (directions/colors synced with your new slide 16)
    boat_center = mini_boat.get_center()
    keel = mini_boat.get_bottom()
    deck = mini_boat.get_top()

    g_arrow = Arrow(
        start=[boat_center[0], boat_center[1] + 0.2, 0],
        end=[boat_center[0], boat_center[1] - 0.7, 0],
        color=pc.apple,
        stroke_width=5,
        tip_length=0.16,
    ).set_z_index(15)
    g_lbl = (
        MathTex(r"\mathbf{F}_g", color=pc.apple, font_size=mini_fs)
        .next_to(g_arrow, RIGHT, buff=0.2)
        .set_z_index(15)
    )

    b_arrow = Arrow(
        start=[boat_center[0] - 0.2, boat_center[1] - 0.4, 0],
        end=[boat_center[0] - 0.2, boat_center[1] + 0.8, 0],
        color=pc.tiffanyBlue,
        stroke_width=5,
        tip_length=0.16,
    ).set_z_index(15)
    b_lbl = (
        MathTex(r"\mathbf{F}_b", color=pc.tiffanyBlue, font_size=mini_fs)
        .next_to(b_arrow, LEFT, buff=0.1)
        .set_z_index(15)
    )

    a_arrow_end = [boat_center[0] - 0.7, boat_center[1] - 0.4, 0]
    a_arrow = Arrow(
        start=[boat_center[0] + 0.3, boat_center[1] + 0.05, 0],
        end=a_arrow_end,
        color=pc.jellyBean,
        stroke_width=5,
        tip_length=0.16,
    ).set_z_index(15)
    a_lbl = (
        MathTex(r"\mathbf{F}_a", color=pc.jellyBean, font_size=mini_fs)
        .move_to([boat_center[0] - 0.65, boat_center[1] - 0.2, 0])
        .set_z_index(15)
    )

    w_arrow_end = [boat_center[0] + 0.6, boat_center[1] + 0.6, 0]
    w_arrow = Arrow(
        start=[boat_center[0] - 0.4, boat_center[1] - 0.3, 0],
        end=w_arrow_end,
        color=pc.heliotropeMagenta,
        stroke_width=5,
        tip_length=0.16,
    ).set_z_index(15)
    w_lbl = (
        MathTex(r"\mathbf{F}_w", color=pc.heliotropeMagenta, font_size=mini_fs)
        .next_to(w_arrow_end, RIGHT, buff=-0.05)
        .set_z_index(15)
    )

    self.add_foreground_mobjects(
        g_arrow, b_arrow, a_arrow, w_arrow, g_lbl, b_lbl, a_lbl, w_lbl
    )
    self.play(
        LaggedStart(
            FadeIn(g_arrow),
            FadeIn(g_lbl),
            FadeIn(b_arrow),
            FadeIn(b_lbl),
            FadeIn(a_arrow),
            FadeIn(a_lbl),
            FadeIn(w_arrow),
            FadeIn(w_lbl),
            lag_ratio=0.12,
            run_time=0.9,
        )
    )

    self.play(
        t_tracker.animate.increment_value(8 * PI),
        run_time=6.0,
        rate_func=linear,
    )

    # -------------------------------------------------------------------------
    # RIGHT COLUMN: triangle + labels (wave keeps animating concurrently)
    # -------------------------------------------------------------------------
    tri_size = min(col_w * 0.9, usable_h * 0.9)
    htri = np.sqrt(3) / 2 * tri_size
    V_top = right_center + np.array([0.0, htri / 2, 0.0])
    V_bl = right_center + np.array([-tri_size / 2, -htri / 2, 0.0])
    V_br = right_center + np.array([tri_size / 2, -htri / 2, 0.0])

    tri = Polygon(V_top, V_br, V_bl, stroke_color=pc.blueGreen, stroke_width=6)

    fs_lab = max(22, self.BODY_FONT_SIZE - 4)
    lab_top = Tex(r"Pr{\'e}c.", color=pc.blueGreen, font_size=fs_lab).next_to(
        V_top, UP, buff=0.10
    )
    lab_bl = Tex(r"Perf.", color=pc.blueGreen, font_size=fs_lab).next_to(
        V_bl, DOWN, buff=0.10
    )
    lab_br = Tex(r"{\'E}ch.", color=pc.blueGreen, font_size=fs_lab).next_to(
        V_br, DOWN, buff=0.10
    )

    self.play(Create(tri))

    right_group = VGroup(lab_top, lab_bl, lab_br)
    self.play(
        FadeIn(right_group, run_time=0.6),
        rate_func=linear,
    )

    # ==== Cross at center ====
    self.next_slide()
    centroid = (V_top + V_bl + V_br) / 3.0
    cross_len = tri_size * 0.06
    cross = VGroup(
        Line(
            centroid + np.array([-cross_len, -cross_len, 0.0]),
            centroid + np.array([cross_len, cross_len, 0.0]),
            stroke_color=pc.jellyBean,
            stroke_width=6,
        ),
        Line(
            centroid + np.array([-cross_len, cross_len, 0.0]),
            centroid + np.array([cross_len, -cross_len, 0.0]),
            stroke_color=pc.jellyBean,
            stroke_width=6,
        ),
    )
    self.play(Create(cross, run_time=0.35), rate_func=linear)

    # ==== Move cross toward bottom side (with concurrent wave motion) ====
    self.wait(0.1)
    self.next_slide()
    target = 0.5 * (V_bl + V_br) + np.array([0.2, 0.5, 0.0])
    self.play(cross.animate.move_to(target), run_time=0.8, rate_func=linear)

    self.wait(0.1)
    self.next_slide()

    # ======================= CLEAR MINIATURE CONTENTS (keep the box) =======================
    to_clear_left = VGroup(
        forces_grid,
        mini_boat,
        g_arrow,
        b_arrow,
        a_arrow,
        w_arrow,
        g_lbl,
        b_lbl,
        a_lbl,
        w_lbl,
    )

    # Stop and remove the always_redraw water first
    if mini_wave:
        mini_wave.clear_updaters()
        self.remove(mini_wave)

    # Fade out the miniature content
    self.play(FadeOut(forces_grid, run_time=0.3))

    # IMPORTANT: also remove foreground registrations
    self.remove_foreground_mobjects(
        mini_boat,
        g_arrow,
        b_arrow,
        a_arrow,
        w_arrow,
        g_lbl,
        b_lbl,
        a_lbl,
        w_lbl,
    )

    self.remove(
        mini_boat,
        g_arrow,
        b_arrow,
        a_arrow,
        w_arrow,
        g_lbl,
        b_lbl,
        a_lbl,
        w_lbl,
    )

    # ==== Section title II) under I) ====
    sec2 = Tex(
        r"II) Hybridation SPH et champs de hauteur",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    sec2.next_to(sec, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    self.play(FadeIn(sec2, run_time=0.5, shift=RIGHT * self.SHIFT_SCALE))

    # ---------------- Miniature of slide 37 INSIDE the existing box ----------------
    inner_pad = 0.20
    inner_w = box.width - 2 * inner_pad
    inner_h = box.height - 2 * inner_pad
    inner_center = box.get_center()

    # Local miniature frame
    y_top_local = inner_h / 2 - 0.15
    y_bot_local = -inner_h / 2 + 0.15

    x_fern_local = -inner_w / 2 + 0.14 * inner_w
    x_gold_local = -inner_w / 2 + 0.80 * inner_w

    fern_line = Line(
        [inner_center[0] + x_fern_local, inner_center[1] + y_bot_local, 0],
        [inner_center[0] + x_fern_local, inner_center[1] + y_top_local, 0],
        color=pc.fernGreen,
        stroke_width=4,
    )
    gold_line = Line(
        [inner_center[0] + x_gold_local, inner_center[1] + y_bot_local, 0],
        [inner_center[0] + x_gold_local, inner_center[1] + y_top_local, 0],
        color=pc.uclaGold,
        stroke_width=4,
    )
    fern_line.save_state()
    gold_line.save_state()
    fern_line.become(
        Line(
            fern_line.get_start(),
            fern_line.get_start(),
            color=pc.fernGreen,
            stroke_width=4,
        )
    )
    gold_line.become(
        Line(
            gold_line.get_start(),
            gold_line.get_start(),
            color=pc.uclaGold,
            stroke_width=4,
        )
    )
    self.play(Transform(fern_line, fern_line.saved_state, run_time=0.25))
    self.play(Transform(gold_line, gold_line.saved_state, run_time=0.25))

    x_min_local = -inner_w / 2
    x_max_local = inner_w / 2
    y_center_local = y_bot_local + 0.75 * (y_top_local - y_bot_local)
    X = np.linspace(x_min_local, x_max_local, 350)
    Y = y_center_local + 0.22 * np.cos(0.9 * X)
    curve = VMobject().set_points_smoothly(
        np.column_stack(
            [X + inner_center[0], Y + inner_center[1], np.zeros_like(X)]
        )
    )
    curve.set_stroke(color=pc.oxfordBlue, width=3)
    self.add(curve)

    rng = random.Random(1)
    N = 30
    x_lo = x_fern_local + 0.06 * inner_w
    x_hi = x_gold_local - 0.06 * inner_w

    def mkdot(x, y, color, r=0.05):
        d = Dot([x, y, 0.0], radius=r, color=color)
        d.set_fill(color, opacity=1.0)
        d.set_stroke(color, opacity=1.0, width=0)
        return d

    dots = []
    for i in range(N):
        t = (i + 0.5) / N
        x = (
            x_lo
            + t * (x_hi - x_lo)
            + rng.uniform(-0.04 * inner_w, 0.04 * inner_w)
        )
        y_curve = y_center_local + 0.22 * np.cos(0.9 * x)
        y = y_curve + rng.uniform(y_bot_local - y_center_local, 0.18)
        y = np.clip(y, y_bot_local, y_top_local - 0.04)
        dots.append(
            mkdot(
                inner_center[0] + x, inner_center[1] + y, pc.blueGreen, r=0.05
            )
        )

    dense_dots = []
    for _ in range(8):
        x = rng.uniform(
            x_fern_local + 0.08 * inner_w, x_fern_local + 0.28 * inner_w
        )
        y_curve = y_center_local + 0.22 * np.cos(0.9 * x)
        y = y_curve - rng.uniform(0.10, 0.22)
        y = np.clip(y, y_bot_local, y_top_local - 0.04)
        dense_dots.append(
            mkdot(
                inner_center[0] + x, inner_center[1] + y, pc.blueGreen, r=0.05
            )
        )

    all_dots = dots + dense_dots
    self.play(
        LaggedStart(
            *[GrowFromCenter(d) for d in all_dots],
            lag_ratio=0.05,
            run_time=0.6,
        )
    )

    right_candidates = [
        d
        for d in dots
        if d.get_center()[0] > inner_center[0] + (x_lo + 0.6 * (x_hi - x_lo))
    ]
    hole_dots = []
    for d in right_candidates:
        if len(hole_dots) >= 6:
            break
        x, y, _ = d.get_center()
        xl = x - inner_center[0]
        yc = inner_center[1] + y_center_local + 0.22 * np.cos(0.9 * xl)
        if y < yc:
            hole_dots.append(d)
    for d in hole_dots:
        d.set_fill(opacity=0.0)
        d.set_stroke(opacity=0.0)

    above = []
    for d in all_dots:
        if d.get_fill_opacity() <= 0 and d.get_stroke_opacity() <= 0:
            continue
        x, y, _ = d.get_center()
        xl = x - inner_center[0]
        yc = inner_center[1] + y_center_local + 0.22 * np.cos(0.9 * xl)
        if y > yc:
            above.append(d)
    if above:
        self.play(
            LaggedStart(
                *[d.animate.set_color(pc.jellyBean) for d in above],
                lag_ratio=0.05,
                run_time=0.5,
            )
        )

    pops = [
        AnimationGroup(
            d.animate.scale(1.2),
            FadeOut(d, scale=0.3),
            lag_ratio=0.0,
            run_time=0.22,
        )
        for d in above
    ]
    if pops:
        self.play(LaggedStart(*pops, lag_ratio=0.05))

    if dense_dots:
        self.play(
            LaggedStart(
                *[d.animate.set_color(pc.jellyBean) for d in dense_dots],
                lag_ratio=0.05,
                run_time=0.5,
            )
        )
        pops2 = [
            AnimationGroup(
                d.animate.scale(1.2),
                FadeOut(d, scale=0.3),
                lag_ratio=0.0,
                run_time=0.22,
            )
            for d in dense_dots
        ]
        self.play(LaggedStart(*pops2, lag_ratio=0.05))

    apples = []
    for d in hole_dots:
        x, y, _ = d.get_center()
        apples.append(mkdot(x, y, pc.apple, r=0.05))
    if apples:
        self.play(
            LaggedStart(
                *[GrowFromCenter(nd) for nd in apples],
                lag_ratio=0.05,
                run_time=0.5,
            )
        )

    # ===================== Final: move the triangle cross again =====================
    self.next_slide()
    target_again = 0.5 * (V_bl + V_top) + np.array([0.5, 0.1, 0.0])
    self.play(
        cross.animate.move_to(target_again), run_time=0.6, rate_func=linear
    )

    # End slide
    self.pause()
    self.clear()
    self.next_slide()
