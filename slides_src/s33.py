import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(33)
def slide_33(self):
    """
    Slide 33: Forces d'Airy.

    Implements:
      - Title bar, objective line (with non-breaking spaces to avoid bad wraps).
      - Equation reveal and transform to full formula.
      - Highlight (v_i^A(t) - v_i(t)) with a drawn rectangle.
      - Dot + three arrows with labels, staged with pauses.
      - Final cleanup keeping the bar and v_i^A(t), then transform to the question.
    """
    # --- Top bar ---
    bar = self._top_bar("Forces d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Objective line ---
    self.start_body()
    objective = Tex(
        r"Objectif : faire ``tendre'' les particules SPH pour se distribuer "
        r"uniformement sur~la~surface~des~vagues~d'Airy.",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    objective.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (
        bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
    ) - objective.get_left()[0]
    objective.shift(RIGHT * dx)
    self.add(objective)
    self.wait(0.1)
    # --- Wait for input ---
    self.next_slide()

    # --- Big centered question equation ---
    eq_question = Tex(r"$F_i^A(t) = ?$", font_size=72, color=BLACK)
    eq_question.move_to([0.0, 0.0, 0.0])
    self.add(eq_question)

    # --- Wait for input ---
    self.next_slide()

    # --- Transform into full formula ---
    eq_full = Tex(
        r"$F_i^A(t) = \frac{m}{dt} \cdot \tau_i(t) \cdot (1-\phi_i(t))"
        r"\cdot \left(v_i^A(t) - v_i(t)\right)$",
        font_size=48,
        color=BLACK,
    )
    eq_full.move_to(eq_question.get_center())
    self.play(ReplacementTransform(eq_question, eq_full))

    # ======================================================================
    # Extra effects
    # ======================================================================
    self.next_slide()

    # Move the full equation a bit higher
    self.play(eq_full.animate.shift(UP * 0.8))

    # Surround ONLY the (v_i^A(t) - v_i(t)) term with a rectangle (robust selection)
    term = eq_full.get_part_by_tex(r"\left(v_i^A(t) - v_i(t)\right)")
    if term is None or term.width == 0:
        # Fallback: span from v_i^A(t) to v_i(t)
        part1 = eq_full.get_part_by_tex(r"v_i^A(t)")
        part2 = eq_full.get_part_by_tex(r"v_i(t)")
        group = VGroup(*[m for m in [part1, part2] if m is not None])
        term = group if len(group.submobjects) > 0 else eq_full
    pad = 0.08
    ul = term.get_corner(UL) + (-pad * RIGHT + pad * UP)
    ur = term.get_corner(UR) + (pad * RIGHT + pad * UP)
    lr = term.get_corner(DR) + (pad * RIGHT - pad * UP)
    ll = term.get_corner(DL) + (-pad * RIGHT - pad * UP)
    seg_top = Line(ul, ur, stroke_width=4, color=BLACK)
    seg_right = Line(ur, lr, stroke_width=4, color=BLACK)
    seg_bottom = Line(lr, ll, stroke_width=4, color=BLACK)
    seg_left = Line(ll, ul, stroke_width=4, color=BLACK)
    self.play(
        LaggedStart(
            Create(seg_top),
            Create(seg_right),
            Create(seg_bottom),
            Create(seg_left),
            lag_ratio=0.15,
        )
    )

    self.next_slide()

    # Large cornflower dot, placed lower on the slide
    dot_center = np.array([-2.0, -config.frame_height / 2 + 1.2, 0.0])
    dot = Dot(point=dot_center, radius=0.12, color=pc.cornflower)
    self.play(GrowFromCenter(dot))

    self.next_slide()

    # Arrow v_i^A : up-right from the dot
    a1_end = dot_center + np.array([2.2, 1.2, 0.0])
    arr_vA = Arrow(
        dot_center, a1_end, buff=0.0, stroke_width=6, color=pc.jellyBean
    )
    self.play(GrowArrow(arr_vA))
    # Label placed on the arrow body (midpoint), to its left
    mid_vA = (arr_vA.get_start() + arr_vA.get_end()) / 2.0
    label_vA = Tex(r"$v_i^A(t)$", font_size=36, color=BLACK)
    label_vA.move_to(mid_vA + LEFT * 0.35)

    self.add(label_vA)

    # Arrow v_i : right and slightly up, below the first one
    a2_end = dot_center + np.array([2.2, 0.5, 0.0])
    arr_v = Arrow(
        dot_center, a2_end, buff=0.0, stroke_width=6, color=pc.blueGreen
    )
    self.play(GrowArrow(arr_v))
    # Label on the arrow body (midpoint), to its right
    mid_v = (arr_v.get_start() + arr_v.get_end()) / 2.0
    label_v = Tex(r"$v_i(t)$", font_size=36, color=BLACK)
    label_v.move_to(mid_v + RIGHT * 0.35)
    self.add(label_v)

    self.next_slide()

    # Resultant arrow v_i^A - v_i : from tip of v_i to tip of v_i^A
    arr_diff = Arrow(
        arr_v.get_end(),
        arr_vA.get_end(),
        buff=0.0,
        stroke_width=6,
        color=pc.fernGreen,
    )
    self.play(GrowArrow(arr_diff))
    label_diff = Tex(r"$v_i^A(t) - v_i(t)$", font_size=36, color=BLACK)
    mid_diff = (arr_v.get_end() + arr_vA.get_end()) / 2.0
    label_diff.move_to(mid_diff + RIGHT * 0.35)
    self.add(label_diff)

    self.next_slide()

    # Clear everything except top bar and v_i^A(t) label, then transform it
    keep = VGroup(bar, label_vA)
    to_clear = VGroup(
        objective,
        eq_full,
        seg_top,
        seg_right,
        seg_bottom,
        seg_left,
        dot,
        arr_vA,
        arr_v,
        arr_diff,
        label_v,
        label_diff,
    )
    self.play(FadeOut(to_clear))

    # Transform label into centered, larger question
    question = Tex(
        r"Comment determiner $v_i^A(t)$ ?", font_size=60, color=BLACK
    )
    question.move_to(ORIGIN)
    self.play(ReplacementTransform(label_vA, question))
