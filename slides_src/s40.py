import numpy as np
import palette_colors as pc
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Create, FadeIn, FadeOut,
                   Polygon, Tex, TransformMatchingTex, VGroup, VMobject,
                   config)
from slide_registry import slide


@slide(40)
def slide_40(self):
    """
    Perspectives (slide 40) — fixes:
    - Lock bullet left-edges during transform so "Airy" keeps the same X.
    - Increase outer padding for the big blueGreen rectangle.
    """

    # ---------- Layout & helpers
    full_w = config.frame_width
    full_h = config.frame_height

    SLIDE_LEFT = -full_w * 0.5
    SLIDE_RIGHT = full_w * 0.5
    SLIDE_BOTTOM = -full_h * 0.5

    LEFT_MARGIN = 0.6  # slide left margin for intro + bullets
    TOP_PAD = 0.15  # spacing under bar
    EDGE_INSET = 0.06  # tiny guard from absolute screen edges
    BIG_PAD = 0.35  # << increased padding for the big blue rectangle >>
    RECT_STROKE = 6
    TEXT_FS = 32
    LINE_BUFF = 0.35

    bar, footer = self._top_bar("Perspectives")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]
    usable_top_y = bar_rect.get_bottom()[1] - TOP_PAD
    usable_bottom_y = SLIDE_BOTTOM + EDGE_INSET

    def left_align_to_slide(mobj, y_top):
        """Left-align 'mobj' to slide margin; set its top Y to y_top."""
        target_left = SLIDE_LEFT + LEFT_MARGIN
        dx = target_left - mobj.get_left()[0]
        dy = y_top - mobj.get_top()[1]
        mobj.shift(np.array([dx, dy, 0.0]))
        return mobj

    def left_align_below(mobj, above, buff=LINE_BUFF):
        """Left-align below 'above' with same slide margin."""
        target_left = SLIDE_LEFT + LEFT_MARGIN
        mobj.next_to(above, DOWN, buff=buff, aligned_edge=LEFT)
        dx = target_left - mobj.get_left()[0]
        mobj.shift(np.array([dx, 0.0, 0.0]))
        return mobj

    def draw_rect_lines(x0, y0, x1, y1, color, width=RECT_STROKE, rt=0.22):
        """Draw a rectangle line-by-line using 4 segments."""
        l1 = (
            VMobject()
            .set_stroke(color=color, width=width)
            .set_points_as_corners([[x0, y0, 0], [x1, y0, 0]])
        )
        l2 = (
            VMobject()
            .set_stroke(color=color, width=width)
            .set_points_as_corners([[x1, y0, 0], [x1, y1, 0]])
        )
        l3 = (
            VMobject()
            .set_stroke(color=color, width=width)
            .set_points_as_corners([[x1, y1, 0], [x0, y1, 0]])
        )
        l4 = (
            VMobject()
            .set_stroke(color=color, width=width)
            .set_points_as_corners([[x0, y1, 0], [x0, y0, 0]])
        )
        self.play(Create(l1, run_time=rt))
        self.play(Create(l2, run_time=rt))
        self.play(Create(l3, run_time=rt))
        self.play(Create(l4, run_time=rt))
        return VGroup(l1, l2, l3, l4)

    def place_label_top_left_of_rect(
        label_tex, x0, y0, x1, y1, inset=(0.25, 0.22)
    ):
        """Left-align the label to the rectangle's top-left corner (x0,y1) with a small inset."""
        target_left = x0 + inset[0]
        target_top = y1 - inset[1]
        dx = target_left - label_tex.get_left()[0]
        dy = target_top - label_tex.get_top()[1]
        label_tex.shift(np.array([dx, dy, 0.0]))
        return label_tex

    # ---------- Intro (left-aligned to slide)
    intro = Tex(
        "Passage de la preuve de concept à l'utilisation en production :",
        color=pc.oxfordBlue,
        font_size=TEXT_FS,
    )
    left_align_to_slide(intro, usable_top_y)
    self.add(intro)

    self.next_slide()

    # ---------- Bullets (left-aligned to slide)
    def make_bullets(lines):
        g = VGroup()
        for i, s in enumerate(lines):
            t = Tex(
                r"\(\bullet\)\; " + s, color=pc.oxfordBlue, font_size=TEXT_FS
            )
            if i == 0:
                left_align_below(t, intro, buff=LINE_BUFF)
            else:
                left_align_below(t, g[-1], buff=LINE_BUFF)
            g.add(t)
        return g

    bullets_v1 = make_bullets(["2D", "Airy"])
    self.add(bullets_v1)
    self.wait(0.1)
    self.next_slide()

    # New bullets with arrows (note: "Airy \\leftarrow Tessendorf" per your request)
    bullets_v2 = make_bullets(
        [r"2D $\rightarrow$ 3D", r"Airy $\rightarrow$ Tessendorf"]
    )

    # --- Lock left edges before Transform so the left X doesn't move off-slide
    for b_old, b_new in zip(bullets_v1, bullets_v2):
        # Start by matching Y/center to avoid vertical pop
        b_new.move_to(b_old.get_center())
        # Then correct X so left edge matches exactly
        dx_left = b_old.get_left()[0] - b_new.get_left()[0]
        b_new.shift(np.array([dx_left, 0.0, 0.0]))

    self.play(
        *[
            TransformMatchingTex(b1, b2)
            for b1, b2 in zip(bullets_v1, bullets_v2)
        ],
        run_time=0.7,
    )
    bullets_v1 = bullets_v2

    self.next_slide()

    # ---------- Clear (keep bar)
    self.play(FadeOut(VGroup(intro, bullets_v1), run_time=0.4))

    # ---------- Big blueGreen rectangle with INCREASED padding from slide edges
    # Leave a bigger margin on all sides under the bar
    X0 = SLIDE_LEFT + BIG_PAD
    X1 = SLIDE_RIGHT - BIG_PAD
    Y1 = usable_top_y - BIG_PAD
    Y0 = usable_bottom_y + BIG_PAD

    big_rect_lines = draw_rect_lines(
        X0, Y0, X1, Y1, color=pc.blueGreen, width=RECT_STROKE, rt=0.18
    )

    # ---------- "Tessendorf" label (left-aligned to big-rect top-left)
    big_label = Tex("Tessendorf", color=pc.blueGreen, font_size=TEXT_FS)
    place_label_top_left_of_rect(big_label, X0, Y0, X1, Y1)
    self.add(big_label)

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

    self.wait(0.1)
    self.next_slide()

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
    self.add(boat)

    # ---------- Center small uclaGold rectangle + label "SPH"
    w_big = X1 - X0
    h_big = Y1 - Y0
    small_w = w_big * 0.55
    small_h = h_big * 0.55
    cx, cy = (X0 + X1) * 0.5, (Y0 + Y1) * 0.5
    sx0, sy0 = cx - small_w * 0.5, cy - small_h * 0.5
    sx1, sy1 = cx + small_w * 0.5, cy + small_h * 0.5

    small_rect_lines = draw_rect_lines(
        sx0, sy0, sx1, sy1, color=pc.uclaGold, width=RECT_STROKE, rt=0.16
    )

    small_label = Tex("SPH", color=pc.uclaGold, font_size=TEXT_FS)
    place_label_top_left_of_rect(small_label, sx0, sy0, sx1, sy1)
    self.add(small_label)

    self.wait(0.1)
    self.next_slide()

    # ---------- Small rect: to fernGreen; "SPH" -> "LBM" (fernGreen)
    self.play(
        *[
            l.animate.set_stroke(color=pc.fernGreen, width=RECT_STROKE)
            for l in small_rect_lines
        ],
        run_time=0.4,
    )
    lbm_label = Tex("LBM", color=pc.fernGreen, font_size=TEXT_FS)
    lbm_label.move_to(small_label.get_center())
    self.play(TransformMatchingTex(small_label, lbm_label), run_time=0.5)
    place_label_top_left_of_rect(lbm_label, sx0, sy0, sx1, sy1)
    small_label = lbm_label

    self.wait(0.1)
    self.next_slide()

    # ---------- "LBM" -> "?" (jellyBean), rect -> jellyBean, scale up, keep "?" at new top-left
    SCALE = 1.4
    new_w = small_w * SCALE
    new_h = small_h * SCALE
    nsx0, nsy0 = cx - new_w * 0.5, cy - new_h * 0.5
    nsx1, nsy1 = cx + new_w * 0.5, cy + new_h * 0.5

    # target top-left for label after scaling
    target_tl = np.array([nsx0 + 0.25, nsy1 - 0.22, 0.0])

    q_label = Tex("?", color=pc.jellyBean, font_size=TEXT_FS)
    q_label.move_to(small_label.get_center())

    self.play(
        *[
            l.animate.set_stroke(color=pc.jellyBean, width=RECT_STROKE)
            for l in small_rect_lines
        ],
        TransformMatchingTex(small_label, q_label),
        run_time=0.45,
    )
    small_label = q_label

    self.play(
        small_rect_lines.animate.scale(
            SCALE, about_point=np.array([cx, cy, 0.0])
        ),
        small_label.animate.move_to(target_tl),
        run_time=0.6,
    )
    self.pause()
    self.clear()
    self.next_slide()
