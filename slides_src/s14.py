# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.

# flake8: noqa: F405
import os

import numpy as np
import palette_colors as pc
from manim import *
from manim import logger
from manim_slides import Slide
from manim_tikz import Tikz
from slide_registry import slide
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)


@slide(14)
def slide_14(self):
    """
    Slide 14 : Vitesse de l'océan
    """
    # --- Top bar ---------------------------------------------------------
    bar, footer = self._top_bar("Vitesse de l'océan")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ---- Usable area below the bar -------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    anchor_x = x_left + self.DEFAULT_PAD

    line1 = Tex(
        r"\mbox{La vitesse de l'eau en tout point de l'espace calculée avec le même principe de transformation}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1.next_to(self._current_bar, DOWN, aligned_edge=LEFT)
    dx = anchor_x - line1.get_left()[0]
    line1.shift(RIGHT * dx)

    line2 = Tex(
        r"d'espace de Fourier à espace réel : "
        r"$\tilde{v}(k,t,y)=E(k,y)\,\phi(k,t)$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line2.next_to(line1, DOWN, aligned_edge=LEFT)
    dx2 = anchor_x - line2.get_left()[0]
    line2.shift(RIGHT * dx2)
    self.play(
        FadeIn(line1, line2, shift=RIGHT * self.SHIFT_SCALE), run_time=0.25
    )

    # ===================== Axis & Layout =================================
    # Tweakables to nudge the axes where you want
    AXIS_RIGHT_SHIFT = 0.60  # move vertical axis further to the right
    AXIS_DOWN_SHIFT = 0.30  # move the whole axes block slightly downward

    # Left-side axes spanning from just under sentences down to bottom,
    # then apply right/down shifts.
    axis_left_x = x_left + 0.9 + AXIS_RIGHT_SHIFT
    axis_top_y = (line2.get_bottom()[1] - 0.30) - AXIS_DOWN_SHIFT
    axis_bottom_y = y_bottom + 0.35
    x_end = x_right - 0.6

    # Clamp to bounds (just in case tweaks push out of frame)
    axis_left_x = min(axis_left_x, x_right - 1.8)
    axis_top_y = min(axis_top_y, y_top - 0.2)
    axis_bottom_y = max(axis_bottom_y, y_bottom + 0.2)

    # Vertical axis: only downward from origin (no positive part)
    y_axis = Arrow(
        start=[axis_left_x, axis_top_y, 0],
        end=[axis_left_x, axis_bottom_y, 0],
        buff=0,
        stroke_width=6,
        color=BLACK,
    )

    # Horizontal axis: rightward from the same origin y
    x_axis = Arrow(
        start=[axis_left_x, axis_top_y, 0],
        end=[x_end, axis_top_y, 0],
        buff=0,
        stroke_width=6,
        color=BLACK,
    )

    axis_group = VGroup(x_axis, y_axis)
    self.add(axis_group)

    # Wave along the horizontal axis level
    wave = ParametricFunction(
        lambda t: np.array(
            [
                axis_left_x + t,
                axis_top_y - 0.30 * np.sin(1.4 * t),
                0.0,
            ]
        ),
        t_range=[0, max(0.0, x_end - axis_left_x)],
        color=pc.blueGreen,
        stroke_width=6,
    )
    self.add(wave)

    # ===================== After first reveal ===========================
    self.next_slide()

    # ===================== Depth Levels =================================
    depths = [0, 30, 80, 140]  # four lines
    y_vals = np.linspace(axis_top_y, axis_bottom_y, len(depths))

    dotted_lines = []
    labels = []

    # Fixed gap from the axis to the label's RIGHT edge
    LABEL_GAP = 0.4
    MIN_LEFT = x_left + 0.15

    for yv, d in zip(y_vals, depths):
        # dotted line from axis to right
        ln = DashedLine(
            start=[axis_left_x, yv, 0],
            end=[x_end, yv, 0],
            dash_length=0.20,
            color=BLACK,
        )
        dotted_lines.append(ln)

        # label placed so its RIGHT edge is LABEL_GAP left of the axis
        label = MathTex(
            rf"v(x, t, {d})",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        label.set_y(yv)
        right_target_x = axis_left_x - LABEL_GAP
        current_right_x = label.get_right()[0]
        label.shift(RIGHT * (right_target_x - current_right_x))

        # clamp if label would go off-slide on the left
        if label.get_left()[0] < MIN_LEFT:
            label.shift(RIGHT * (MIN_LEFT - label.get_left()[0]))

        labels.append(label)

    self.play(
        LaggedStart(
            *[Create(m) for m in (dotted_lines + labels)],
            lag_ratio=0.08,
        )
    )

    # ===================== Wait for user =================================
    self.next_slide()

    # ===================== Interpolation line ============================
    mid_y = 0.5 * (y_vals[1] + y_vals[2])
    interp_line = DashedLine(
        start=[axis_left_x, mid_y, 0],
        end=[x_end, mid_y, 0],
        dash_length=0.08,
        color=pc.blueGreen,
    )
    interp_caption = Text(
        "Interpolation Exp",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    ).next_to(interp_line, UP, buff=0.1)

    self.add(interp_line, interp_caption)
    self.play(Indicate(interp_caption, color=pc.blueGreen))

    # ===================== End slide ====================================
    self.pause()
    self.clear()
    self.next_slide()
