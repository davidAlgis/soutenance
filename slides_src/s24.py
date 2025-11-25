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


@slide(24)
def slide_24(self):
    """
    Slide 24: Diffusion et forces de viscosités.

    Steps:
    1) Top bar + two left-aligned lines.
    2) Wait, then split remaining area into two columns with a vertical line
       (animated bottom-to-top). Left: "Faiblement visqueux" + bullets.
       Right: "Hautement visqueux" + bullets.
    3) Wait, then clear columns and divider; show center equation.
    4) Wait, then transform the equation to the detailed SPH form.
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Diffusion et forces de viscosités")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Usable area below bar --------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    anchor_x = x_left + self.DEFAULT_PAD

    # Prefix (placed exactly like your original code using anchor_x and the top bar)
    line1_prefix = Tex(
        "Propriété de l'eau : ",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1_prefix.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    line1_prefix.shift(RIGHT * (anchor_x - line1_prefix.get_left()[0]))

    self.play(
        FadeIn(line1_prefix, shift=self.SHIFT_SCALE * RIGHT, run_time=0.3)
    )
    self.next_slide()

    # Suffix appended; keep zero horizontal gap to look like a single sentence
    line1_suffix = Tex(
        " faiblement visqueux.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line1_suffix.next_to(line1_prefix, RIGHT, buff=0.1).align_to(
        line1_prefix, DOWN
    )

    # Animate only the new part
    self.play(Write(line1_suffix, run_time=0.35))

    line2 = Tex(
        r"La viscosité représente la résistance à l'écoulement.",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    line2.next_to(
        line1_prefix, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT
    )
    line2.shift(RIGHT * (anchor_x - line2.get_left()[0]))

    self.play(FadeIn(line2, shift=self.SHIFT_SCALE * RIGHT), run_time=0.5)

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Two columns with vertical divider --------------------------------
    # Column area bounds
    content_top_y = line2.get_bottom()[1] - 0.35
    content_bottom_y = y_bottom + 0.35
    content_h = max(1.8, content_top_y - content_bottom_y)
    content_center_y = 0.5 * (content_top_y + content_bottom_y)

    # Divider x, animated bottom->top
    divider_x = 0.0
    divider = Line(
        start=[divider_x, content_bottom_y, 0.0],
        end=[divider_x, content_top_y, 0.0],
        color=BLACK,
        stroke_width=6,
    )
    self.play(Create(divider, run_time=0.7))

    # Column centers
    left_cx = x_left + 0.5 * (divider_x - x_left) - 0.2
    right_cx = x_right - 0.5 * (x_right - divider_x) + 0.2

    # Helpers to build a bullet list with Tex rows
    def make_bullets(
        labels,
        font_size,
        *,
        bullet_color=pc.blueGreen,
        line_gap=0.14,
        left_pad=0.18
    ):
        """
        Build a bullet list using utils.make_bullet_list (triangle bullets).
        `labels` can be:
          - list[str]
          - or list[tuple[str, Any]] (the extra value is ignored for compatibility).
        """
        items = [lbl if isinstance(lbl, str) else lbl[0] for lbl in labels]
        return make_bullet_list(
            items,
            bullet_color=bullet_color,
            font_size=font_size,
            line_gap=line_gap,
            left_pad=left_pad,
        )

    # Left column: title on 2 lines + bullets
    left_title = Tex(
        r"Faiblement visqueux",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 4,
    )
    left_title.move_to([left_cx, content_center_y + 2.0, 0.0])

    left_bullets = make_bullets(
        [
            (r"Cognac", BLACK),
            (r"Eau", pc.blueGreen),
            (r"Lait", BLACK),
        ],
        font_size=self.BODY_FONT_SIZE,
    )
    left_bullets.next_to(left_title, DOWN, buff=0.28, aligned_edge=LEFT)
    # Re-anchor bullets to column center x
    left_bullets.shift(LEFT * 1.5)

    # Right column: title on 2 lines + bullets
    right_title = Tex(
        r"Hautement visqueux",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 4,
    )
    right_title.move_to([right_cx, content_center_y + 2.0, 0.0])

    right_bullets = make_bullets(
        [
            (r"Huile", BLACK),
            (r"Miel", BLACK),
            (r"Mayonnaise", BLACK),
        ],
        font_size=self.BODY_FONT_SIZE,
    )
    right_bullets.next_to(right_title, DOWN, buff=0.28, aligned_edge=LEFT)
    right_bullets.shift(LEFT * 1.5)

    cols_group = VGroup(
        left_title, left_bullets, right_title, right_bullets, divider
    )
    self.play(
        LaggedStart(
            FadeIn(left_title, shift=self.SHIFT_SCALE * RIGHT),
            FadeIn(left_bullets, shift=self.SHIFT_SCALE * RIGHT),
            FadeIn(right_title, shift=self.SHIFT_SCALE * LEFT),
            FadeIn(right_bullets, shift=self.SHIFT_SCALE * LEFT),
            lag_ratio=0.12,
            run_time=0.8,
        )
    )

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Clear columns and divider ----------------------------------------
    self.play(FadeOut(cols_group, run_time=0.35))

    # --- Center equation (large) ------------------------------------------
    eq_center = MathTex(
        r"\mathbf{F}_i^v = \frac{m_i}{\rho_i}\,\mu\,\nabla^{2}\mathbf{v}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 10,
    )
    eq_center.move_to([0.0, content_center_y, 0.0])
    self.play(FadeIn(eq_center, run_time=0.4))

    # --- Wait for user -----------------------------------------------------
    self.next_slide()

    # --- Transform to SPH viscosity form ----------------------------------
    eq_sph = MathTex(
        r"\mathbf{F}_i^{v} \simeq \frac{m_i}{\rho_i}"
        r"\sum_j \frac{m_j}{\rho_j}"
        r"\frac{\mathbf{v}_{ij}\cdot\mathbf{r}_{ij}}{\lVert\mathbf{r}_{ij}\rVert^{2}}"
        r"\,\nabla W_{ij}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 6,
    )
    eq_sph.move_to(eq_center.get_center())

    self.play(ReplacementTransform(eq_center, eq_sph), run_time=0.8)

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
