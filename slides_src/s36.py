import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(36)
def slide_36(self):
    """
    Slide 36: Découpage du domaine en zones.

    Fixes:
      1) Wave fills full horizontal span of the frame.
      2) fernGreen outer rectangle top stays below the intro line.
      3) Boat slightly scaled down.
      4) Add final pause/clear/next_slide.
    """
    # --- Top bar ---
    bar, footer = self._top_bar("Découpage du domaine en zones")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Intro line ---
    self.start_body()
    intro = Tex(
        r"Découpage en trois zones :",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    intro.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (
        bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
    ) - intro.get_left()[0]
    intro.shift(RIGHT * dx)
    self.play(FadeIn(intro, shift=RIGHT * self.SHIFT_SCALE))

    # Pause
    self.next_slide()

    # --- Wave curve: y = 0.2*cos(1.2 x), spanning full frame width ---
    x_min = -config.frame_width / 2.0
    x_max = config.frame_width / 2.0
    sample_n = 800
    X = np.linspace(x_min, x_max, sample_n)
    Y = 0.2 * np.cos(1.2 * X)
    pts = np.column_stack([X, Y, np.zeros_like(X)])
    wave = (
        VMobject()
        .set_points_smoothly(pts)
        .set_stroke(color=pc.blueGreen, width=4)
    )
    self.play(Create(wave))

    # --- Boat centered on the curve at x=0 (slightly scaled down) ---
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
        *[np.array(p) for p in boat_shape], color=pc.uclaGold, stroke_width=4
    )
    boat.set_fill(pc.uclaGold, opacity=1.0)
    boat.move_to(np.array([0.0, 0.2 * np.cos(0.0), 0.0]))
    boat.scale(0.4)  # fix: reduce boat size a bit
    self.add_foreground_mobject(boat)
    self.play(FadeIn(boat))
    self.wait(0.1)

    # Pause
    self.next_slide()

    # --- fernGreen border rectangle, top kept below the intro text ---
    margin_lr = 0.3
    margin_bottom = 0.3
    top_gap = 0.25  # distance below intro line
    top_y = intro.get_bottom()[1] - top_gap
    left_x = -config.frame_width / 2.0 + margin_lr
    right_x = config.frame_width / 2.0 - margin_lr
    bottom_y = -config.frame_height / 2.0 + margin_bottom + 0.5

    outer_ul = np.array([left_x, top_y, 0.0])
    outer_ur = np.array([right_x, top_y, 0.0])
    outer_lr = np.array([right_x, bottom_y, 0.0])
    outer_ll = np.array([left_x, bottom_y, 0.0])

    o_top = Line(outer_ul, outer_ur, color=pc.fernGreen, stroke_width=6)
    o_right = Line(outer_ur, outer_lr, color=pc.fernGreen, stroke_width=6)
    o_bottom = Line(outer_lr, outer_ll, color=pc.fernGreen, stroke_width=6)
    o_left = Line(outer_ll, outer_ul, color=pc.fernGreen, stroke_width=6)

    label_static = Tex("Zone statique", color=pc.fernGreen, font_size=36)
    label_static.next_to(o_top, DOWN, buff=0.18).align_to(o_left, LEFT).shift(
        RIGHT * 0.18
    )
    self.play(
        LaggedStart(
            Create(o_top),
            Create(o_right),
            Create(o_bottom),
            Create(o_left),
            lag_ratio=0.15,
        ),
        FadeIn(label_static),
    )

    # Pause
    self.next_slide()

    # --- Inner blueGreen rectangle surrounding the (now smaller) boat ---
    pad_y = 0.6
    pad_x = 1.2
    in_ul = boat.get_corner(UL) + np.array([-pad_x, pad_y, 0.0])
    in_ur = boat.get_corner(UR) + np.array([pad_x, pad_y, 0.0])
    in_lr = boat.get_corner(DR) + np.array([pad_x, -pad_y, 0.0])
    in_ll = boat.get_corner(DL) + np.array([-pad_x, -pad_y, 0.0])

    i_top = Line(in_ul, in_ur, color=pc.blueGreen, stroke_width=6)
    i_right = Line(in_ur, in_lr, color=pc.blueGreen, stroke_width=6)
    i_bottom = Line(in_lr, in_ll, color=pc.blueGreen, stroke_width=6)
    i_left = Line(in_ll, in_ul, color=pc.blueGreen, stroke_width=6)

    label_sph = Tex("Zone SPH", color=pc.blueGreen, font_size=36)
    label_sph.next_to(i_top, DOWN, buff=0.14).align_to(i_left, LEFT).shift(
        RIGHT * 0.14
    )

    self.play(
        LaggedStart(
            Create(i_top),
            Create(i_right),
            Create(i_bottom),
            Create(i_left),
            lag_ratio=0.15,
        ),
        FadeIn(label_sph),
    )

    # Pause
    self.next_slide()

    # --- Intermediate uclaGold rectangle between inner and outer ---
    # Interpolate between inner corners and outer corners so it sits between.
    def mid(a, b, t=0.5):
        return (1.0 - t) * a + t * b

    g_ul = mid(in_ul, outer_ul, t=0.5)
    g_ur = mid(in_ur, outer_ur, t=0.5)
    g_lr = mid(in_lr, outer_lr, t=0.5)
    g_ll = mid(in_ll, outer_ll, t=0.5)

    g_top = Line(g_ul, g_ur, color=pc.uclaGold, stroke_width=6)
    g_right = Line(g_ur, g_lr, color=pc.uclaGold, stroke_width=6)
    g_bottom = Line(g_lr, g_ll, color=pc.uclaGold, stroke_width=6)
    g_left = Line(g_ll, g_ul, color=pc.uclaGold, stroke_width=6)

    label_buffer = Tex("Zone tampon", color=pc.uclaGold, font_size=36)
    label_buffer.next_to(g_top, DOWN, buff=0.16).align_to(g_left, LEFT).shift(
        RIGHT * 0.16
    )

    self.play(
        LaggedStart(
            Create(g_top),
            Create(g_right),
            Create(g_bottom),
            Create(g_left),
            lag_ratio=0.15,
        ),
        FadeIn(label_buffer),
    )

    # --- End of slide ---
    self.pause()
    self.clear()
    self.next_slide()
