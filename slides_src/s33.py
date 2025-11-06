from manim import *
from slide_registry import slide


@slide(33)
def slide_33(self):
    """
    Slide 33: Forces d'Airy.

    Steps:
      1) Top bar titled "Forces d'Airy".
      2) Show objective sentence (BODY_FONT_SIZE).
      3) Wait for user input (self.next_slide()).
      4) Center a large equation: "F_i^A(t) = ?".
      5) Wait for user input (self.next_slide()).
      6) Animate transform to:
         F_i^A(t) = \\frac{m}{dt} \\cdot \\tau_i(t) \\cdot (1-\\phi_i(t))
                    \\cdot \\left(v_i^A(t) - v_i(t)\\right)
    """
    # --- Top bar ---
    bar = self._top_bar("Forces d'Airy")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Objective line (use Tex, BODY_FONT_SIZE) ---
    self.start_body()
    objective = Tex(
        r'Objectif : faire "tendre" les particules SPH pour se distribuer '
        r"uniformement sur la surface des vagues d'Airy.",
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

    # --- Wait for input ---
    self.wait(0.1)
    self.next_slide()

    # --- Big centered question equation (in math mode) ---
    eq_question = Tex(r"$F_i^A(t) = ?$", font_size=72, color=BLACK)
    eq_question.move_to([0.0, 0.0, 0.0])
    self.add(eq_question)
    self.wait(0.1)
    # --- Wait for input ---
    self.next_slide()

    # --- Transform into full formula (in math mode) ---
    eq_full = Tex(
        r"$F_i^A(t) = \frac{m}{dt} \cdot \tau_i(t) \cdot (1-\phi_i(t))"
        r"\cdot \left(v_i^A(t) - v_i(t)\right)$",
        font_size=48,
        color=BLACK,
    )
    eq_full.move_to(eq_question.get_center())

    # Animate transform
    self.play(ReplacementTransform(eq_question, eq_full))
