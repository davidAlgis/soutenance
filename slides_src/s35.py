import random

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(35)
def slide_35(self):
    """
    Slide 37: Regulation de particules.

    Fix:
      - Sample particle Y relative to the water curve at each X so some points
        are below AND slightly above the curve in the same reference frame.
      - Keep earlier guards to avoid zero-duration plays.
    """
    # --- Top bar ---
    bar, footer = self._top_bar("Régulation de particules")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Subtitle (left-aligned under bar) ---
    subtitle = Tex(
        r"S'assurer que le nombre de particules est relativement constant.",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    subtitle.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (
        bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
    ) - subtitle.get_left()[0]
    subtitle.shift(RIGHT * dx)
    self.play(FadeIn(subtitle, shift=RIGHT * self.SHIFT_SCALE))

    # Layout
    frame_w = config.frame_width
    frame_h = config.frame_height
    body_top = subtitle.get_bottom()[1] - 0.5
    body_bottom = -frame_h / 2.0 + 0.2
    # Pause
    self.wait(0.1)
    self.next_slide()

    # --- Vertical lines ---
    x_fern = -frame_w / 2.0 + 0.6
    fern_line = Line(
        [x_fern, body_bottom, 0.0],
        [x_fern, body_top, 0.0],
        color=pc.fernGreen,
        stroke_width=6,
    )
    fern_line.save_state()
    fern_line.become(
        Line(
            [x_fern, body_bottom, 0.0],
            [x_fern, body_bottom, 0.0],
            color=pc.fernGreen,
            stroke_width=6,
        )
    )
    label_fern = Tex("Zone statique", color=pc.fernGreen, font_size=36)
    label_fern.next_to([x_fern, body_top, 0.0], RIGHT, buff=0.2)

    x_gold = -frame_w / 2.0 + 0.75 * frame_w
    gold_line = Line(
        [x_gold, body_bottom, 0.0],
        [x_gold, body_top, 0.0],
        color=pc.uclaGold,
        stroke_width=6,
    )
    gold_line.save_state()
    gold_line.become(
        Line(
            [x_gold, body_bottom, 0.0],
            [x_gold, body_bottom, 0.0],
            color=pc.uclaGold,
            stroke_width=6,
        )
    )
    label_gold = Tex("Zone tampon", color=pc.uclaGold, font_size=36)
    label_gold.next_to([x_gold, body_top, 0.0], RIGHT, buff=0.2)

    # --- Cosine curve across width at ~3/4 of body height ---
    x_min = -frame_w / 2.0
    x_max = frame_w / 2.0
    y_center = body_bottom + 0.75 * (body_top - body_bottom)
    X = np.linspace(x_min, x_max, 900)
    Y = y_center + 0.3 * np.cos(0.2 * X)
    curve = (
        VMobject()
        .set_points_smoothly(np.column_stack([X, Y, np.zeros_like(X)]))
        .set_stroke(color=pc.oxfordBlue, width=4)
    )

    self.play(
        Transform(fern_line, fern_line.saved_state),
        FadeIn(label_fern),
        Transform(gold_line, gold_line.saved_state),
        FadeIn(label_gold),
        Create(curve),
    )

    # --- Particles generation (Y sampled around the curve at each X) ---
    rng = random.Random(1)
    N = 50
    x_lo = x_fern + 0.15
    x_hi = x_gold - 0.15

    def mkdot(x, y, color):
        d = Dot([x, y, 0.0], radius=0.1, color=color)
        d.set_fill(color, opacity=1.0)
        d.set_stroke(color, opacity=1.0, width=0)
        return d

    dots = []
    for i in range(N):
        t = (i + 0.5) / N
        x = x_lo + t * (x_hi - x_lo) + rng.uniform(-0.15, 0.15)
        y_curve = y_center + 0.3 * np.cos(0.2 * x)
        # Jitter around the curve: mostly below, some slightly above
        y = y_curve + rng.uniform(body_bottom, 0.3)
        # Clamp to body area
        y = max(body_bottom, min(y, body_top - 0.05))
        dots.append(mkdot(x, y, pc.blueGreen))

    # Dense zone: 10 extra under-curve dots on the left
    dense_dots = []
    for _ in range(10):
        x = rng.uniform(x_fern + 0.25, x_fern + 1.0)
        y_curve = y_center + 0.3 * np.cos(0.2 * x)
        y = y_curve - rng.uniform(0.15, 0.35)
        y = max(body_bottom, min(y, body_top - 0.05))
        dense_dots.append(mkdot(x, y, pc.blueGreen))

    # --- FILTERING LOGIC MOVED HERE (Before Animation) ---

    # Identify the dots that should be holes
    right_candidates = [
        d for d in dots if d.get_center()[0] > (x_lo + 0.6 * (x_hi - x_lo))
    ]
    hole_dots = []
    for d in right_candidates:
        if len(hole_dots) >= 8:
            break
        x, y, _ = d.get_center()
        if y < (y_center + 0.3 * np.cos(0.2 * x)):
            hole_dots.append(d)

    # Combine lists, but EXCLUDE the hole_dots
    all_generated = dots + dense_dots
    visible_dots = [d for d in all_generated if d not in hole_dots]

    # --- ANIMATION ---

    # Only animate the visible ones
    self.play(
        LaggedStart(*[GrowFromCenter(d) for d in visible_dots], lag_ratio=0.05)
    )

    self.wait(0.1)
    # Pause
    self.next_slide()

    # --- Helper: visibility check ---
    def is_visible(m: Mobject) -> bool:
        try:
            return (getattr(m, "get_fill_opacity", lambda: 1.0)() > 0.0) or (
                getattr(m, "get_stroke_opacity", lambda: 1.0)() > 0.0
            )
        except Exception:
            return True

    # Recolor particles above the curve to jellyBean
    above = []
    for d in visible_dots:
        if not is_visible(d):
            continue
        x, y, _ = d.get_center()
        if y > (y_center + 0.3 * np.cos(0.2 * x)):
            above.append(d)

    if above:
        self.play(
            LaggedStart(
                *[d.animate.set_color(pc.jellyBean) for d in above],
                lag_ratio=0.05
            )
        )

    # Pause
    self.next_slide()

    # Remove jellyBean (above-curve) particles with a pop effect
    pops = [
        AnimationGroup(
            d.animate.scale(1.3),
            FadeOut(d, scale=0.3),
            lag_ratio=0.0,
            run_time=0.25,
        )
        for d in above
    ]
    if pops:
        self.play(LaggedStart(*pops, lag_ratio=0.05))

    # Pause
    self.next_slide()

    # Density estimator formula
    rho_tex = Tex(
        r"$\tilde{\rho}(\tilde{\mathbf{x}}_l) = \frac{\sum_{j} \rho_{j} W_{lj}}{\sum_{j} W_{lj}}$",
        font_size=40,
        color=BLACK,
    )
    rho_tex.next_to(VGroup(*visible_dots), UP, buff=0.3)
    self.play(FadeIn(rho_tex))

    # Pause
    self.next_slide()

    # Recolor dense-zone 10 to jellyBean
    if dense_dots:
        self.play(
            LaggedStart(
                *[d.animate.set_color(pc.jellyBean) for d in dense_dots],
                lag_ratio=0.05
            )
        )

    # Pause
    self.next_slide()

    # Remove dense-zone jellyBean particles with a pop effect
    pops2 = [
        AnimationGroup(
            d.animate.scale(1.3),
            FadeOut(d, scale=0.3),
            lag_ratio=0.0,
            run_time=0.25,
        )
        for d in dense_dots
    ]
    if pops2:
        self.play(LaggedStart(*pops2, lag_ratio=0.05))

    # Pause
    self.next_slide()

    # Reveal the 8 previously hidden (hole) particles in apple
    apples = []
    for d in hole_dots:
        x, y, _ = d.get_center()
        nd = mkdot(x, y, pc.apple)
        apples.append(nd)
    if apples:
        self.play(
            LaggedStart(*[GrowFromCenter(nd) for nd in apples], lag_ratio=0.05)
        )

    # --- End of slide ---
    self.pause()
    self.clear()
    self.next_slide()
