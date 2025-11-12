import os

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(3)
def slide_03(self):
    """
    Objectifs (slide 3)

    - Top bar "Objectifs"
    - Center ellipse with "Précision" (large)
    - 3 columns below the ellipse:
        * each column title emerges from the ellipse center (scale 0 -> 1 + move)
        * the image below fades in
      Columns are revealed one-by-one with self.next_slide() in between.
    - Finally, all three columns collapse back into the ellipse center while shrinking.
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

    # --- Central ellipse with "Précision" ---
    ellipse_w = min(10.0, full_w * 0.75)
    ellipse_h = 2.2
    ellipse_y = bar_rect.get_bottom()[1] - 0.7  # a bit under the bar

    ell = Ellipse(
        width=ellipse_w, height=ellipse_h, color=pc.blueGreen, stroke_width=6
    )
    ell.move_to(np.array([0.0, ellipse_y, 0.0]))

    title = Text("Précision", color=BLACK, font_size=52, weight=BOLD)
    # Fit title inside ellipse
    inner_w = ellipse_w * 0.8
    inner_h = ellipse_h * 0.65
    if title.width > 0 and title.height > 0:
        scale_w = inner_w / title.width
        scale_h = inner_h / title.height
        s = min(1.0, scale_w, scale_h)
        if s < 1.0:
            title.scale(s)
    title.move_to(ell.get_center())

    # At least one animation before first pause
    self.play(DrawBorderThenFill(ell, run_time=0.45))
    self.play(FadeIn(title, run_time=0.25))
    self.next_slide()

    # --- Columns layout (under the ellipse) ---
    cols_x = np.linspace(left_x + 2.0, right_x - 2.0, 3)
    col_top_y = ell.get_bottom()[1] - 0.7
    COL_FS = 36
    col_max_w = (cols_x[1] - cols_x[0]) * 0.9
    col_max_h = 3.8

    def make_column(title_str: str, img_path: str, x_center: float):
        # Title final pose
        t = Text(title_str, color=BLACK, font_size=COL_FS, weight=BOLD)
        t.move_to(np.array([x_center, col_top_y, 0.0]))
        t.save_state()  # final (target) state
        # Prepare emerge pose: tiny at ellipse center
        t.scale(0.01)
        t.move_to(ell.get_center())

        # Image below title
        if os.path.isfile(img_path):
            im = ImageMobject(img_path)
            if im.width > 0:
                im.scale(col_max_w / im.width)
            if im.height > col_max_h:
                im.scale(col_max_h / im.height)
            im.next_to(t, DOWN, buff=0.3, aligned_edge=UP)
        else:
            im = Tex(
                f"Fichier manquant : {img_path}", font_size=28, color=BLACK
            )
            im.next_to(t, DOWN, buff=0.3, aligned_edge=UP)

        im.set_opacity(0.0)  # will fade in later

        group = Group(
            t, im
        )  # Group accepts both VMobject/Mobject (ImageMobject)
        return group, t, im

    # Build columns
    col1_group, col1_title, col1_img = make_column(
        "Surface", "Figures/goal/goal_surface.png", cols_x[0]
    )
    col2_group, col2_title, col2_img = make_column(
        "Fluide vers solide", "Figures/goal/goal_coupling_f2s.png", cols_x[1]
    )
    col3_group, col3_title, col3_img = make_column(
        "Solide vers fluide", "Figures/goal/goal_coupling_s2f.png", cols_x[2]
    )

    self.add(col1_group, col2_group, col3_group)

    # --- Reveal Column 1 ---
    self.play(Restore(col1_title), run_time=0.6)  # move + scale together
    self.play(FadeIn(col1_img, run_time=0.35))
    self.next_slide()

    # --- Reveal Column 2 ---
    self.play(Restore(col2_title), run_time=0.6)
    self.play(FadeIn(col2_img, run_time=0.35))
    self.next_slide()

    # --- Reveal Column 3 ---
    self.play(Restore(col3_title), run_time=0.6)
    self.play(FadeIn(col3_img, run_time=0.35))
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
