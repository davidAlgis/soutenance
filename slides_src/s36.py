import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(36)
def slide_36(self):
    """
    Slide 36: Decoupage du domaine en zones.

    Sequence:
      1) Top bar + intro line.
      2) Animate the curve y = 0.2*cos(1.2 x) for x in [-5, 5] (blueGreen).
      3) Place a uclaGold boat centered on the curve.
      4) FernGreen border rectangle (drawn side-by-side), label top-left.
      5) Inner blueGreen rectangle tightly surrounding the boat (drawn side-by-side), label.
      6) Intermediate uclaGold rectangle between both (drawn side-by-side), label.
    """
    # --- Top bar ---
    bar = self._top_bar("Découpage du domaine en zones")
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
    self.add(intro)

    # Pause
    self.next_slide()

    # --- Wave curve: y = 0.2 cos(1.2 x), x in [-5, 5] ---
    x_min, x_max = -5.0, 5.0
    sample_n = 800
    X = np.linspace(x_min, x_max, sample_n)
    Y = 0.2 * np.cos(1.2 * X)

    # Build a smooth path centered vertically around y=0
    pts = np.column_stack([X, Y, np.zeros_like(X)])
    wave = VMobject()
    wave.set_points_smoothly(pts)
    wave.set_stroke(color=pc.blueGreen, width=4)
    self.play(Create(wave))

    # --- Boat centered on the curve at x=0 ---
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
    y_mid = 0.2 * np.cos(0.0)  # y on the curve at x=0
    boat.move_to(np.array([0.0, y_mid, 0.0]))
    self.add_foreground_mobject(boat)
    self.add(boat)

    # Pause
    self.next_slide()

    # --- FernGreen border rectangle (near slide borders), drawn line by line ---
    margin = 0.3
    rect_outer_w = config.frame_width - 2 * margin
    rect_outer_h = config.frame_height - 2 * margin
    outer_ul = np.array([-rect_outer_w / 2, rect_outer_h / 2, 0.0])
    outer_ur = np.array([rect_outer_w / 2, rect_outer_h / 2, 0.0])
    outer_lr = np.array([rect_outer_w / 2, -rect_outer_h / 2, 0.0])
    outer_ll = np.array([-rect_outer_w / 2, -rect_outer_h / 2, 0.0])

    o_top = Line(outer_ul, outer_ur, color=pc.fernGreen, stroke_width=6)
    o_right = Line(outer_ur, outer_lr, color=pc.fernGreen, stroke_width=6)
    o_bottom = Line(outer_lr, outer_ll, color=pc.fernGreen, stroke_width=6)
    o_left = Line(outer_ll, outer_ul, color=pc.fernGreen, stroke_width=6)

    self.play(
        LaggedStart(
            Create(o_top),
            Create(o_right),
            Create(o_bottom),
            Create(o_left),
            lag_ratio=0.15,
        )
    )

    # Label "Zone statique" inside top-left
    label_static = Tex("Zone statique", color=pc.fernGreen, font_size=36)
    label_static.next_to(o_top, DOWN, buff=0.18).align_to(o_left, LEFT).shift(
        RIGHT * 0.18
    )
    self.add(label_static)

    # Pause
    self.next_slide()

    # --- BlueGreen inner rectangle surrounding the boat, drawn line by line ---
    # Get boat bounds and pad a bit
    bb_ul = boat.get_corner(UL)
    bb_ur = boat.get_corner(UR)
    bb_lr = boat.get_corner(DR)
    bb_ll = boat.get_corner(DL)
    pad = 0.25
    in_ul = np.array([bb_ul[0] - pad, bb_ul[1] + pad, 0.0])
    in_ur = np.array([bb_ur[0] + pad, bb_ur[1] + pad, 0.0])
    in_lr = np.array([bb_lr[0] + pad, bb_lr[1] - pad, 0.0])
    in_ll = np.array([bb_ll[0] - pad, bb_ll[1] - pad, 0.0])

    i_top = Line(in_ul, in_ur, color=pc.blueGreen, stroke_width=6)
    i_right = Line(in_ur, in_lr, color=pc.blueGreen, stroke_width=6)
    i_bottom = Line(in_lr, in_ll, color=pc.blueGreen, stroke_width=6)
    i_left = Line(in_ll, in_ul, color=pc.blueGreen, stroke_width=6)

    self.play(
        LaggedStart(
            Create(i_top),
            Create(i_right),
            Create(i_bottom),
            Create(i_left),
            lag_ratio=0.15,
        )
    )

    # Label "Zone SPH"
    label_sph = Tex("Zone SPH", color=pc.blueGreen, font_size=36)
    label_sph.next_to(i_top, DOWN, buff=0.14).align_to(i_left, LEFT).shift(
        RIGHT * 0.14
    )
    self.add(label_sph)

    # Pause
    self.next_slide()

    # --- UCLA Gold intermediate rectangle between the two, drawn line by line ---
    # Choose a rectangle that fits between: shrink outer slightly, expand inner
    gold_pad_outer = 0.45
    gold_pad_inner = 0.45

    # From outer (shrink)
    g_outer_ul = outer_ul + np.array([gold_pad_outer, -gold_pad_outer, 0.0])
    g_outer_ur = outer_ur + np.array([-gold_pad_outer, -gold_pad_outer, 0.0])
    g_outer_lr = outer_lr + np.array([-gold_pad_outer, gold_pad_outer, 0.0])
    g_outer_ll = outer_ll + np.array([gold_pad_outer, gold_pad_outer, 0.0])

    # From inner (expand)
    g_inner_ul = in_ul + np.array([-gold_pad_inner, gold_pad_inner, 0.0])
    g_inner_ur = in_ur + np.array([gold_pad_inner, gold_pad_inner, 0.0])
    g_inner_lr = in_lr + np.array([gold_pad_inner, -gold_pad_inner, 0.0])
    g_inner_ll = in_ll + np.array([-gold_pad_inner, -gold_pad_inner, 0.0])

    # Interpolate corners to ensure it sits between inner and outer bounds
    def mid(a, b, t=0.5):
        return (1 - t) * a + t * b

    g_ul = mid(g_inner_ul, g_outer_ul, t=0.5)
    g_ur = mid(g_inner_ur, g_outer_ur, t=0.5)
    g_lr = mid(g_inner_lr, g_outer_lr, t=0.5)
    g_ll = mid(g_inner_ll, g_outer_ll, t=0.5)

    g_top = Line(g_ul, g_ur, color=pc.uclaGold, stroke_width=6)
    g_right = Line(g_ur, g_lr, color=pc.uclaGold, stroke_width=6)
    g_bottom = Line(g_lr, g_ll, color=pc.uclaGold, stroke_width=6)
    g_left = Line(g_ll, g_ul, color=pc.uclaGold, stroke_width=6)

    self.play(
        LaggedStart(
            Create(g_top),
            Create(g_right),
            Create(g_bottom),
            Create(g_left),
            lag_ratio=0.15,
        )
    )

    # Label "Zone tampon"
    label_buffer = Tex("Zone tampon", color=pc.uclaGold, font_size=36)
    label_buffer.next_to(g_top, DOWN, buff=0.16).align_to(g_left, LEFT).shift(
        RIGHT * 0.16
    )
    self.add(label_buffer)
