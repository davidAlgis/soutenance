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
    - Smaller ellipse (fully visible) with 'Précision'
    - 3 columns revealed one by one:
        * titles grow+translate from ellipse center (scale 0 -> 1 + move)
        * images simply FadeIn at their final place under the title
    - Two vertical guide lines mark the middle column
    - Final collapse: only revealed elements collapse back to ellipse
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

    # --- Ellipse (smaller, fully visible) ---
    ellipse_w = min(8.5, full_w * 0.58)
    ellipse_h = 1.35
    top_gap = 0.22
    ellipse_center_y = bar_rect.get_bottom()[1] - (ellipse_h * 0.5) - top_gap

    ell = Ellipse(
        width=ellipse_w, height=ellipse_h, color=pc.blueGreen, stroke_width=6
    )
    ell.move_to(np.array([0.0, ellipse_center_y, 0.0]))

    title = Text("Précision", color=BLACK, font_size=44, weight=BOLD)
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

    # --- Columns layout under the ellipse ---
    cols_x = np.linspace(left_x + 2.0, right_x - 2.0, 3)
    col_span = cols_x[1] - cols_x[0]
    col_top_y = ell.get_bottom()[1] - 0.7

    COL_FS = 30
    col_max_w = col_span * 0.9
    col_max_h = 3.6

    # --- Middle column guide lines ---
    mid_left_x = cols_x[1] - 0.5 * col_span
    mid_right_x = cols_x[1] + 0.5 * col_span
    line_top_y = col_top_y + 0.2
    line_bot_y = y_bot

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

    def build_title_at_column(s: str, x_center: float) -> Text:
        """Create a title with saved final state; initial tiny at ellipse center."""
        t = Text(s, color=BLACK, font_size=COL_FS, weight=BOLD)
        t.move_to(np.array([x_center, col_top_y, 0.0]))
        t.save_state()  # final state
        t.scale(0.01)  # initial tiny
        t.move_to(ell.get_center())  # initial position (ellipse center)
        return t

    def build_image_under_title(
        title_saved: Mobject, img_path: str
    ) -> Mobject:
        """Create the image positioned under the saved (final) title."""
        if os.path.isfile(img_path):
            im = ImageMobject(img_path)
            if im.width > 0:
                im.scale(col_max_w / im.width)
            if im.height > col_max_h:
                im.scale(col_max_h / im.height)
        else:
            im = Tex(
                f"Fichier manquant : {img_path}", font_size=28, color=BLACK
            )
        im.next_to(title_saved, DOWN, buff=0.3, aligned_edge=UP)
        return im

    revealed = []  # collect revealed mobjects for the final collapse

    # -------- Column 1 --------
    col1_title = build_title_at_column("Surface", cols_x[0])
    col1_img = build_image_under_title(
        col1_title.saved_state, "Figures/goal/goal_surface.png"
    )
    col1_img.shift(DOWN * 0.35)

    self.add(col1_title)
    self.play(Restore(col1_title), run_time=0.6)
    self.play(FadeIn(col1_img, run_time=0.35))
    revealed += [col1_title, col1_img]
    self.next_slide()

    # -------- Column 2 --------
    col2_title = build_title_at_column("Fluide vers solide", cols_x[1])
    col2_img = build_image_under_title(
        col2_title.saved_state, "Figures/goal/goal_coupling_f2s.png"
    )

    self.add(col2_title)
    self.play(Restore(col2_title), run_time=0.6)
    self.play(FadeIn(col2_img, run_time=0.35))
    revealed += [col2_title, col2_img]
    self.next_slide()

    # -------- Column 3 --------
    col3_title = build_title_at_column("Solide vers fluide", cols_x[2])
    col3_img = build_image_under_title(
        col3_title.saved_state, "Figures/goal/goal_coupling_s2f.png"
    )

    self.add(col3_title)
    self.play(Restore(col3_title), run_time=0.6)
    self.play(FadeIn(col3_img, run_time=0.35))
    revealed += [col3_title, col3_img]
    self.next_slide()

    # --- Final collapse (only revealed elements) ---
    collapse_group = Group(*revealed)
    self.play(
        collapse_group.animate.scale(0).move_to(ell.get_center()),
        FadeOut(line_left),
        FadeOut(line_right),
        run_time=0.8,
    )

    self.pause()
    self.clear()
    self.next_slide()
