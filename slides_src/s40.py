import numpy as np
import palette_colors as pc
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Create, FadeIn,
                   FadeOut, Tex, TransformMatchingTex, VGroup, VMobject,
                   config)
from slide_registry import slide


@slide(40)
def slide_40(self):
    """
    Perspectives (slide 40)

    - Text on the left (intro + bullets) is left-aligned to a slide-left margin.
    - Text inside rectangles is left-aligned to each rectangle's top-left corner (with a small inset).
    - Line-by-line draw for rectangles; smooth color/text transforms; final scale keeps the "?" pinned to new top-left.
    """

    # ---------- Layout & helpers
    full_w = config.frame_width
    full_h = config.frame_height

    SLIDE_LEFT = -full_w * 0.5
    SLIDE_RIGHT = full_w * 0.5
    SLIDE_BOTTOM = -full_h * 0.5

    LEFT_MARGIN = 0.6  # slide left margin (for intro + bullets)
    TOP_PAD = 0.15  # spacing under bar
    EDGE_INSET = 0.05  # keep strokes inside the screen a bit

    TEXT_FS = 32
    LINE_BUFF = 0.35

    bar = self._top_bar("Perspectives")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]
    usable_top_y = bar_rect.get_bottom()[1] - TOP_PAD
    usable_bottom_y = SLIDE_BOTTOM + EDGE_INSET
    usable_left_x = SLIDE_LEFT + EDGE_INSET
    usable_right_x = SLIDE_RIGHT - EDGE_INSET

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

    def draw_rect_lines(x0, y0, x1, y1, color, width=6, run_time=0.25):
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
        self.play(Create(l1, run_time=run_time))
        self.play(Create(l2, run_time=run_time))
        self.play(Create(l3, run_time=run_time))
        self.play(Create(l4, run_time=run_time))
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

    # ---------- Intro
    intro = Tex(
        "Passage de la preuve de concept à l'utilisation en production :",
        color=pc.oxfordBlue,
        font_size=TEXT_FS,
    )
    left_align_to_slide(intro, usable_top_y)
    self.add(intro)

    self.next_slide()

    # ---------- Bullets (left-aligned to slide margin)
    def make_bullets(lines, base=None):
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

    self.next_slide()

    bullets_v2 = make_bullets(
        [r"2D $\rightarrow$ 3D", r"Airy $\rightarrow$ Tessendorf"]
    )
    # Lock positions for clean transform
    for b_old, b_new in zip(bullets_v1, bullets_v2):
        b_new.move_to(b_old.get_center())

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

    # ---------- Big blueGreen rectangle (fills slide under bar)
    X0, Y0 = usable_left_x, usable_bottom_y
    X1, Y1 = usable_right_x, usable_top_y
    big_rect_lines = draw_rect_lines(
        X0, Y0, X1, Y1, color=pc.blueGreen, width=6, run_time=0.2
    )

    self.next_slide()

    # ---------- "Tessendorf" label (left-aligned to big-rect top-left)
    big_label = Tex("Tessendorf", color=pc.blueGreen, font_size=TEXT_FS)
    place_label_top_left_of_rect(big_label, X0, Y0, X1, Y1)
    self.add(big_label)

    # ---------- Center small uclaGold rectangle + label "SPH"
    w_big = X1 - X0
    h_big = Y1 - Y0
    small_w = w_big * 0.55
    small_h = h_big * 0.55
    cx, cy = (X0 + X1) * 0.5, (Y0 + Y1) * 0.5
    sx0, sy0 = cx - small_w * 0.5, cy - small_h * 0.5
    sx1, sy1 = cx + small_w * 0.5, cy + small_h * 0.5

    small_rect_lines = draw_rect_lines(
        sx0, sy0, sx1, sy1, color=pc.uclaGold, width=6, run_time=0.18
    )

    small_label = Tex("SPH", color=pc.uclaGold, font_size=TEXT_FS)
    place_label_top_left_of_rect(small_label, sx0, sy0, sx1, sy1)
    self.add(small_label)

    self.next_slide()

    # ---------- Small rect: to fernGreen; "SPH" -> "LBM" (fernGreen)
    self.play(
        *[
            l.animate.set_stroke(color=pc.fernGreen, width=6)
            for l in small_rect_lines
        ],
        run_time=0.4,
    )
    lbm_label = Tex("LBM", color=pc.fernGreen, font_size=TEXT_FS)
    # start at SPH position, then snap to exact top-left (avoids drift if glyph widths differ)
    lbm_label.move_to(small_label.get_center())
    self.play(TransformMatchingTex(small_label, lbm_label), run_time=0.5)
    place_label_top_left_of_rect(lbm_label, sx0, sy0, sx1, sy1)
    small_label = lbm_label

    self.next_slide()

    # ---------- "LBM" -> "?" (jellyBean), rect -> jellyBean, scale up, keep "?" at new top-left
    SCALE = 1.25
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
            l.animate.set_stroke(color=pc.jellyBean, width=6)
            for l in small_rect_lines
        ],
        TransformMatchingTex(small_label, q_label),
        run_time=0.45,
    )
    small_label = q_label

    # scale lines about center, slide "?" to new top-left
    self.play(
        small_rect_lines.animate.scale(
            SCALE, about_point=np.array([cx, cy, 0.0])
        ),
        small_label.animate.move_to(target_tl),
        run_time=0.6,
    )
