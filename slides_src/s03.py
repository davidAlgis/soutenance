import os

import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(3)
def slide_03(self):
    """
    Objectifs (slide 3):
    - (kept) ellipse + 3 staged columns as per your latest version
    - After collapse: triangle sequence inspired by the provided figure
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
        t = Text(s, color=BLACK, font_size=COL_FS, weight=BOLD)
        t.move_to(np.array([x_center, col_top_y, 0.0]))
        t.save_state()  # final state
        t.scale(0.01)  # initial tiny
        t.move_to(ell.get_center())  # initial at ellipse center
        return t

    def build_image_under_title(
        title_saved: Mobject, img_path: str
    ) -> Mobject:
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

    revealed = []

    # -------- Column 1 --------
    col1_title = build_title_at_column("Surface", cols_x[0])
    col1_img = build_image_under_title(
        col1_title.saved_state, "Figures/goal/goal_surface.png"
    )
    col1_img.shift(DOWN * 0.35)  # only this image a bit lower

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

    # --- Final collapse + remove guides ---
    collapse_group = Group(*revealed)
    self.play(
        collapse_group.animate.scale(0).move_to(ell.get_center()),
        FadeOut(line_left),
        FadeOut(line_right),
        run_time=0.8,
    )

    # ===================== TRIANGLE SEQUENCE =====================

    # 1) Fade out the ellipse, keep the existing "Précision" text object
    self.play(FadeOut(ell, run_time=0.35))
    self.next_slide()

    # ---- Safe drawing area (inside the frame, under top bar) ----
    SAFE_PAD_X = 0.7
    SAFE_PAD_Y = 0.65
    safe_left = -full_w * 0.5 + SAFE_PAD_X
    safe_right = full_w * 0.5 - SAFE_PAD_X
    safe_bottom = y_bot + SAFE_PAD_Y
    safe_top = bar_rect.get_bottom()[1] - SAFE_PAD_Y
    safe_w = max(0.1, safe_right - safe_left)
    safe_h = max(0.1, safe_top - safe_bottom)

    # --- Reserve room for labels so lines don't overlap text ---
    TOP_LABEL_GAP = 0.55  # space above the top vertex for "Précision"
    BOT_LABEL_GAP = 0.55  # space below bottom vertices for labels
    H_USABLE = max(0.1, safe_h - (TOP_LABEL_GAP + BOT_LABEL_GAP))

    # Equilateral height h = (√3/2)*side  -> side from height
    side_from_h = (H_USABLE) * 2.0 / np.sqrt(3.0)
    side_from_w = safe_w * 0.88
    side = min(side_from_h, side_from_w)
    h = np.sqrt(3.0) * 0.5 * side

    # Place the top vertex high, bottoms low (use the reserved gaps)
    V_top_y = safe_top - TOP_LABEL_GAP
    V_bl_y = V_top_y - h
    V_br_y = V_bl_y
    tri_cx = 0.0
    V_top = np.array([tri_cx, V_top_y, 0.0])
    V_bl = np.array([tri_cx - side * 0.5, V_bl_y, 0.0])
    V_br = np.array([tri_cx + side * 0.5, V_br_y, 0.0])

    # Helper to keep any text inside the safe rect if needed
    def clamp_text(
        m: Mobject,
        left=safe_left,
        right=safe_right,
        bottom=safe_bottom,
        top=safe_top,
        pad=0.01,
    ):
        dx = 0.0
        if m.get_left()[0] < left + pad:
            dx = (left + pad) - m.get_left()[0]
        if m.get_right()[0] > right - pad:
            dx = (right - pad) - m.get_right()[0]
        if abs(dx) > 1e-6:
            m.shift(RIGHT * dx)
        dy = 0.0
        if m.get_bottom()[1] < bottom + pad:
            dy = (bottom + pad) - m.get_bottom()[1]
        if m.get_top()[1] > top - pad:
            dy = (top - pad) - m.get_top()[1]
        if abs(dy) > 1e-6:
            m.shift(UP * dy)

    # Move existing "Précision" label above the top vertex (no line overlap)
    title.move_to(V_top + np.array([0.0, 1.0, 0.0]))
    clamp_text(title)
    self.play(FadeTransformPieces(VGroup(), title), run_time=0.25)

    # Bottom labels (kept clear of edges)
    perf = Text("Performances", color=BLACK, font_size=44, weight=BOLD)
    perf.move_to(V_bl + np.array([-1.5, -1.5, 0.0]))  # left & below
    clamp_text(perf)
    self.play(FadeIn(perf, run_time=0.25))
    self.next_slide()

    echelle = Text("Échelle", color=BLACK, font_size=44, weight=BOLD)
    echelle.move_to(V_br + np.array([1.5, -1.5, 0.0]))  # right & below
    clamp_text(echelle)
    self.play(FadeIn(echelle, run_time=0.25))
    self.next_slide()

    # Triangle edges (blueGreen)
    edge1 = Line(V_top, V_br, color=pc.blueGreen, stroke_width=8)
    edge2 = Line(V_br, V_bl, color=pc.blueGreen, stroke_width=8)
    edge3 = Line(V_bl, V_top, color=pc.blueGreen, stroke_width=8)
    self.play(Create(edge1, run_time=0.30))
    self.play(Create(edge2, run_time=0.30))
    self.play(Create(edge3, run_time=0.30))
    self.next_slide()

    # JellyBean cross at centroid
    center = (V_top + V_bl + V_br) / 3.0
    cross_size = 0.25
    c1 = Line(
        center + np.array([-cross_size, -cross_size, 0.0]),
        center + np.array([cross_size, cross_size, 0.0]),
        color=pc.jellyBean,
        stroke_width=10,
    )
    c2 = Line(
        center + np.array([-cross_size, cross_size, 0.0]),
        center + np.array([cross_size, -cross_size, 0.0]),
        color=pc.jellyBean,
        stroke_width=10,
    )
    cross = VGroup(c1, c2)
    self.play(Create(c1, run_time=0.20), Create(c2, run_time=0.20))
    self.next_slide()

    # Helper: dotted, semi-opaque ellipse centered on a point
    def dotted_filled_ellipse(
        center_pt, w=1.2, h=2.0, color=pc.uclaGold, alpha=0.35
    ):
        fill = Ellipse(width=w, height=h).move_to(center_pt)
        fill.set_fill(color=color, opacity=alpha).set_stroke(opacity=0)
        dash = DashedVMobject(
            Ellipse(width=w, height=h).move_to(center_pt),
            num_dashes=24,
            dashed_ratio=0.5,
        )
        dash.set_color(BLACK).set_stroke(width=2)
        return VGroup(fill, dash)

    # Move cross toward the top-right edge (closer to "Précision")
    target1 = V_top * 0.72 + V_br * 0.28
    self.play(cross.animate.move_to(target1), run_time=0.55)
    ell_gold = dotted_filled_ellipse(
        cross.get_center(), w=1.1, h=2.1, color=pc.uclaGold, alpha=0.35
    )
    self.play(FadeIn(ell_gold, run_time=0.25))
    self.next_slide()

    # Move cross to bottom-left area
    target2 = V_bl + np.array([0.45, 0.50, 0.0])
    self.play(cross.animate.move_to(target2), run_time=0.55)
    ell_green = dotted_filled_ellipse(
        cross.get_center(), w=2.2, h=1.2, color=pc.apple, alpha=0.35
    )
    self.play(FadeIn(ell_green, run_time=0.25))
    self.next_slide()
    target3 = 0.5 * (V_bl + V_top) + np.array([0.5, 0.1, 0.0])
    target4 = 0.5 * (V_bl + V_br) + np.array([0.2, 0.5, 0.0])
    # Nudge further left
    self.play(cross.animate.move_to(target4), run_time=0.55)
    self.next_slide()

    # Nudge further down
    self.play(cross.animate.move_to(target3), run_time=0.55)

    # End slide
    self.pause()
    self.clear()
    self.next_slide()
