import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(33)
def slide_33(self):
    """
    Slide 33: Forces d'Airy.

    Minimal fixes:
    - Use MathTex with parts so we can surround only (v_i^A(t) - v_i(t)).
    - Use pc.cornflower.
    - Lower the dot and arrows.
    - Place labels along arrow bodies.
    - Center and enlarge the final question text.
    """
    # --- Top bar ---
    bar = self._top_bar("Forces d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Objective line ---
    self.start_body()
    objective = Tex(
        r"\mbox{Objectif : faire « tendre » les particules SPH pour se distribuer uniformement sur la surface des vagues}",
        # r"~d'Airy.",
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
    self.play(FadeIn(eq_question), un_time=0.3)

    # --- Wait for input ---
    self.next_slide()

    # --- Transform into full formula (MathTex split into parts) ---
    eq_full = MathTex(
        r"F_i^A(t) = \frac{m}{dt} \cdot \tau_i(t) \cdot (1-\phi_i(t)) \cdot",
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

    # Surround ONLY the (v_i^A(t) - v_i(t)) term with a rectangle
    term = eq_full[1]  # thanks to MathTex parts
    surround_box = SurroundingRectangle(term, buff=0.08)
    ul = surround_box.get_corner(UL)
    ur = surround_box.get_corner(UR)
    lr = surround_box.get_corner(DR)
    ll = surround_box.get_corner(DL)

    seg_top = Line(ul, ur, stroke_width=4, color=pc.apple)
    seg_right = Line(ur, lr, stroke_width=4, color=pc.apple)
    seg_bottom = Line(lr, ll, stroke_width=4, color=pc.apple)
    seg_left = Line(ll, ul, stroke_width=4, color=pc.apple)

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
        r"Comment déterminer $v_i^A(t)$ ?", font_size=64, color=BLACK
    )
    question.move_to(ORIGIN)
    self.play(ReplacementTransform(label_vA, question))

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
