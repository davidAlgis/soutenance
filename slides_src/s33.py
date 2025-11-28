# flake8: noqa: F405
import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(33)
def slide_33(self):
    """
    Slide 33: Forces d'Airy.

    Updates:
    - Added step to surround tau_i(t) with uclaGold, then remove it smoothly.
    - Surrounds (v_i^A - v_i) with apple.
    - Vector diagrams and final question.
    """
    # --- Top bar ---
    bar, footer = self._top_bar("Forces d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    anchor_x = x_left + self.DEFAULT_PAD

    line1 = Tex(
        r"\mbox{Objectif : faire « tendre » les particules SPH pour se distribuer sous la}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    line1.shift(RIGHT * (anchor_x - line1.get_left()[0]))

    line2 = Tex(
        r"\mbox{surface de la vague d'Airy.}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line2.next_to(line1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    line2.shift(RIGHT * (anchor_x - line2.get_left()[0]))

    self.play(
        FadeIn(line1, shift=RIGHT * self.SHIFT_SCALE),
        FadeIn(line2, shift=RIGHT * self.SHIFT_SCALE),
    )

    # --- Wait for user -----------------------------------------------------
    self.next_slide()
    self.wait(0.1)
    # --- Wait for input ---
    self.next_slide()

    # --- Big centered question equation ---
    eq_question = Tex(r"$F_i^A(t) = ?$", font_size=72, color=BLACK)
    eq_question.move_to([0.0, 0.0, 0.0])
    self.play(FadeIn(eq_question), run_time=0.3)

    # --- Wait for input ---
    self.next_slide()

    # --- Transform into full formula (MathTex split into parts) ---
    eq_full = MathTex(
        r"F_i^A(t) = \frac{m}{dt} \cdot",
        r"\tau_i(t)",
        r"\cdot (1-\phi_i(t)) \cdot",
        r"\left(v_i^A(t) - v_i(t)\right)",
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

    # --- 1. Surround tau_i(t) with uclaGold ---
    term_tau = eq_full[1]
    box_tau = SurroundingRectangle(term_tau, buff=0.08)

    # Get corners for manual line creation
    ul_t = box_tau.get_corner(UL)
    ur_t = box_tau.get_corner(UR)
    lr_t = box_tau.get_corner(DR)
    ll_t = box_tau.get_corner(DL)

    # Create gold lines
    # Create gold polygon
    # Vertices order ensures drawing: Top -> Right -> Bottom -> Left
    poly_t = Polygon(ul_t, ur_t, lr_t, ll_t, color=pc.uclaGold, stroke_width=4)

    self.play(Create(poly_t), run_time=1.0)
    self.wait(0.1)
    self.next_slide()

    # --- 2. Remove Gold rectangle smoothly ---
    self.play(
        LaggedStart(
            Uncreate(poly_t),
            lag_ratio=0.15,
        )
    )

    # --- 3. Surround (v_i^A - v_i) with apple ---
    term_vel = eq_full[3]
    box_vel = SurroundingRectangle(term_vel, buff=0.08)

    ul_v = box_vel.get_corner(UL)
    ur_v = box_vel.get_corner(UR)
    lr_v = box_vel.get_corner(DR)
    ll_v = box_vel.get_corner(DL)
    # Create apple polygon
    poly_v = Polygon(ul_v, ur_v, lr_v, ll_v, color=pc.apple, stroke_width=4)

    self.play(Create(poly_v), run_time=1.0)
    self.wait(0.1)
    self.next_slide()

    # Large cornflower dot, placed lower on the slide
    dot_center = np.array([-2.0, -config.frame_height / 2 + 1.2, 0.0])
    dot = Dot(point=dot_center, radius=0.12, color=pc.cornflower)
    self.play(GrowFromCenter(dot))

    self.next_slide()

    # Arrow v_i^A : up-right from the dot
    a1_end = dot_center + np.array([1.2, 2.5, 0.0])
    arr_vA = Arrow(
        dot_center, a1_end, buff=0.0, stroke_width=6, color=pc.jellyBean
    )
    # Label on the arrow body
    mid_vA = (arr_vA.get_start() + arr_vA.get_end()) / 2.0
    label_vA = Tex(r"$v_i^A(t)$", font_size=36, color=BLACK)
    label_vA.move_to(mid_vA + LEFT * 0.7)

    # Arrow v_i : right and slightly up, below the first one
    a2_end = dot_center + np.array([3.2, 0.5, 0.0])
    arr_v = Arrow(
        dot_center, a2_end, buff=0.0, stroke_width=6, color=pc.blueGreen
    )
    # Label on the arrow body
    mid_v = (arr_v.get_start() + arr_v.get_end()) / 2.0
    label_v = Tex(r"$v_i(t)$", font_size=36, color=BLACK)
    label_v.move_to(mid_v + DOWN * 0.4)

    self.play(GrowArrow(arr_vA), GrowArrow(arr_v))
    self.play(FadeIn(label_v), FadeIn(label_vA))
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
    label_diff = Tex(r"$v_i^A(t) - v_i(t)$", font_size=36, color=pc.apple)
    mid_diff = (arr_v.get_end() + arr_vA.get_end()) / 2.0
    label_diff.move_to(mid_diff + RIGHT * 1.6)
    self.play(FadeIn(label_diff), run_time=0.3)

    self.next_slide()

    # Clear everything except top bar and v_i^A(t) label, then transform it
    to_clear = VGroup(
        line1,
        line2,
        eq_full,
        poly_v,
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
        r"Comment déterminer $v_i^A(t)$ ?", font_size=64, color=BLACK
    )
    question.move_to(ORIGIN)
    self.play(ReplacementTransform(label_vA, question))

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
