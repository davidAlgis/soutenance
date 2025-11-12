import os

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(3)
def slide_03(self):
    """
    Objectifs (slide 3):
    - Top bar "Objectifs"
    - Ellipse with 'Précision' centered below the bar (fully visible)
    - 3 columns revealed one by one, each title emerging from the ellipse center
      (scale 0 -> 1 while translating), then image fades in while moving to place
    - Two vertical lines mark the middle column boundaries
    - Final collapse: all three columns shrink back into the ellipse center
    """
    # --- Top bar ---
    bar = self._top_bar("Objectifs")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]

    full_w = config.frame_width
    full_h = config.frame_height
    left_x = -full_w * 0.5 + 0.6
    right_x = full_w * 0.5 - 0.6
    y_bot = -full_h * 0.5 + 0.6

    # --- Central ellipse with "Précision" (keep fully visible) ---
    ellipse_w = min(10.0, full_w * 0.75)
    ellipse_h = 2.2
    # Place so ellipse TOP is just under the bar with a small gap
    top_gap = 0.20
    ellipse_center_y = bar_rect.get_bottom()[1] - (ellipse_h * 0.5) - top_gap

    ell = Ellipse(
        width=ellipse_w, height=ellipse_h, color=pc.blueGreen, stroke_width=6
    )
    ell.move_to(np.array([0.0, ellipse_center_y, 0.0]))

    title = Text("Précision", color=BLACK, font_size=48, weight=BOLD)
    # Fit inside ellipse nicely
    inner_w = ellipse_w * 0.8
    inner_h = ellipse_h * 0.65
    if title.width > 0 and title.height > 0:
        scale_w = inner_w / title.width
        scale_h = inner_h / title.height
        s = min(1.0, scale_w, scale_h)
        if s < 1.0:
            title.scale(s)
    title.move_to(ell.get_center())

    self.play(DrawBorderThenFill(ell, run_time=0.45))
    self.play(FadeIn(title, run_time=0.25))
    self.next_slide()

    # --- Columns layout (under the ellipse) ---
    cols_x = np.linspace(left_x + 2.0, right_x - 2.0, 3)
    col_span = cols_x[1] - cols_x[0]
    col_top_y = ell.get_bottom()[1] - 0.7

    COL_FS = 30  # reduced font size
    col_max_w = col_span * 0.9  # max image width per column
    col_max_h = 3.6

    # --- Middle column boundary lines ---
    mid_left_x = cols_x[1] - 0.5 * col_span
    mid_right_x = cols_x[1] + 0.5 * col_span
    line_top_y = col_top_y + 0.2  # start a bit above title zone
    line_bot_y = y_bot  # to bottom safe margin

    line_left = Line(
        np.array([mid_left_x, line_top_y, 0.0]),
        np.array([mid_left_x, line_bot_y, 0.0]),
        color=pc.oxfordBlue,
        stroke_width=3,
    )
    line_right = Line(
        np.array([mid_right_x, line_top_y, 0.0]),
        np.array([mid_right_x, line_bot_y, 0.0]),
        color=pc.oxfordBlue,
        stroke_width=3,
    )
    self.add(line_left, line_right)

    def make_column(title_str: str, img_path: str, x_center: float):
        """
        Prepare one column:
        - Title final position saved; initial state: tiny at ellipse center
        - Image's final center precomputed; initial state: at ellipse center with 0 opacity
        """
        # Title (final pose)
        t = Text(title_str, color=BLACK, font_size=COL_FS, weight=BOLD)
        t.move_to(np.array([x_center, col_top_y, 0.0]))
        t.save_state()  # final (target) state

        # Set initial "emerge" pose (scale ~ 0) at ellipse center
        t.scale(0.01)
        t.move_to(ell.get_center())

        # Image (final pose computed under title)
        if os.path.isfile(img_path):
            im = ImageMobject(img_path)
            # Scale to fit
            if im.width > 0:
                im.scale(col_max_w / im.width)
            if im.height > col_max_h:
                im.scale(col_max_h / im.height)
            im.next_to(
                t.saved_state, DOWN, buff=0.3, aligned_edge=UP
            )  # place under final title
        else:
            im = Tex(
                f"Fichier manquant : {img_path}", font_size=28, color=BLACK
            )
            im.next_to(t.saved_state, DOWN, buff=0.3, aligned_edge=UP)

        # Record final center for animation target
        im_final_center = im.get_center()

        # Initial state for image: at ellipse center, invisible
        im.move_to(ell.get_center())
        im.set_opacity(0.0)

        group = Group(t, im)  # Group accepts ImageMobject
        return group, t, im, im_final_center

    # Build the three columns
    col1_group, col1_title, col1_img, col1_img_final = make_column(
        "Surface", "Figures/goal/goal_surface.png", cols_x[0]
    )
    col2_group, col2_title, col2_img, col2_img_final = make_column(
        "Fluide vers solide", "Figures/goal/goal_coupling_f2s.png", cols_x[1]
    )
    col3_group, col3_title, col3_img, col3_img_final = make_column(
        "Solide vers fluide", "Figures/goal/goal_coupling_s2f.png", cols_x[2]
    )
    self.add(col1_group, col2_group, col3_group)

    # --- Reveal Column 1 ---
    self.play(Restore(col1_title), run_time=0.6)  # move + scale together
    self.play(
        FadeIn(col1_img, run_time=0.35),
        col1_img.animate.move_to(col1_img_final),
    )
    self.next_slide()

    # --- Reveal Column 2 ---
    self.play(Restore(col2_title), run_time=0.6)
    self.play(
        FadeIn(col2_img, run_time=0.35),
        col2_img.animate.move_to(col2_img_final),
    )
    self.next_slide()

    # --- Reveal Column 3 ---
    self.play(Restore(col3_title), run_time=0.6)
    self.play(
        FadeIn(col3_img, run_time=0.35),
        col3_img.animate.move_to(col3_img_final),
    )
    self.next_slide()

    # --- Collapse everything back into the ellipse center while shrinking ---
    all_cols = Group(col1_group, col2_group, col3_group)
    self.play(
        all_cols.animate.scale(0.3).move_to(ell.get_center()),
        run_time=0.8,
    )

    self.pause()
    self.clear()
    self.next_slide()
