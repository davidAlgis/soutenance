import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(28)
def slide_28(self):
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Lancer de rayon et cœur RT")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ==== Intro line ====
    intro = Tex(
        r"Le lancer de rayon : une technique de rendu",
        font_size=self.BODY_FONT_SIZE,
        color=BLACK,
    )
    intro.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (-config.frame_width / 2 + self.DEFAULT_PAD) - intro.get_left()[0]
    intro.shift(RIGHT * (dx + 0.6))

    # ---------------- Camera + Circle layout -------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.20
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left
    area_h = y_top - y_bottom

    # Camera triangle (left, pointing RIGHT; aperture side on the RIGHT)
    cam_w = min(1.6, area_w * 0.18)
    cam_h = cam_w * 0.85
    cam_center = np.array(
        [x_left + cam_w * 1.1, (y_top + y_bottom) / 2.0 - 0.1, 0.0]
    )
    p_apex = cam_center + np.array([-cam_w * 0.58, 0.0, 0.0])  # rightmost
    p_bl = cam_center + np.array(
        [+cam_w * 0.58, -cam_h * 0.58, 0.0]
    )  # back bottom-left
    p_tl = cam_center + np.array(
        [+cam_w * 0.58, +cam_h * 0.58, 0.0]
    )  # back top-left

    camera_tri = Polygon(p_apex, p_bl, p_tl, color=BLACK, stroke_width=4)
    camera_label = Text(
        "Camera", color=BLACK, weight=BOLD, font_size=self.BODY_FONT_SIZE
    ).next_to(camera_tri, UP, buff=0.20)

    # Big circle (right)
    circle_r = min(area_h * 0.35, area_w * 0.25)
    circle_center = np.array([x_right - circle_r * 0.8, cam_center[1], 0.0])
    obj_circle = Circle(
        radius=circle_r, color=pc.blueGreen, stroke_width=6
    ).move_to(circle_center)

    self.play(FadeIn(intro, shift=RIGHT))
    # Draw geometry
    self.play(
        AnimationGroup(
            Create(camera_tri, run_time=0.5),
            FadeIn(camera_label, run_time=0.3),
            Create(obj_circle, run_time=0.6),
            lag_ratio=0.15,
        ),
    )

    self.wait(0.1)
    self.next_slide()

    # ---------------- Rays: start along the aperture edge ------------------
    # Define a small "aperture segment" near the apex on the right side,
    # then emit 3 rays from different points on that segment.
    edge_top = p_tl
    edge_bot = p_bl
    start_pts = [
        (1.0 - t) * edge_top + t * edge_bot for t in (0.15, 0.50, 0.85)
    ]

    # Hit points on the LEFT side of the circle (angles around pi)
    impact_angles = [np.pi * 0.92, np.pi, np.pi * 1.08]
    impact_points = [
        circle_center + circle_r * np.array([np.cos(a), np.sin(a), 0.0])
        for a in impact_angles
    ]

    def grow_and_flash(start_pt, end_pt):
        seg = VMobject().set_stroke(pc.uclaGold, width=6)
        seg.set_points_as_corners(
            np.vstack([start_pt, start_pt]).astype(float)
        )
        dot = Dot(end_pt, color=pc.uclaGold, radius=0.06)

        def _update(
            mob, alpha, s=start_pt.astype(float), e=end_pt.astype(float)
        ):
            p = s + (e - s) * alpha
            mob.set_points_as_corners(np.vstack([s, p]))

        return Succession(
            FadeIn(seg, run_time=0.01),
            UpdateFromAlphaFunc(seg, _update, run_time=0.50, rate_func=smooth),
            Flash(dot, color=pc.uclaGold, flash_radius=0.18, time_width=0.25),
            FadeOut(seg, run_time=0.25),
            FadeOut(dot, run_time=0.20),
        )

    ray_sequences = [
        grow_and_flash(s, e) for s, e in zip(start_pts, impact_points)
    ]
    self.play(LaggedStart(*ray_sequences, lag_ratio=0.22))
    self.wait(0.1)
    self.next_slide()

    # ---------------- Clear (keep bar) -------------------------------------
    for mob in [intro, camera_tri, camera_label, obj_circle]:
        if mob in self.mobjects:
            self.remove(mob)

    # ---------------- GPU title + two-column layout ------------------------
    gpu_title = Text(
        "GPU", color=BLACK, weight=BOLD, font_size=self.BODY_FONT_SIZE + 10
    )
    gpu_title.next_to(self._current_bar, DOWN, buff=0.35)
    self.play(FadeIn(gpu_title, run_time=0.3))

    # Column centers
    col_pad_x = 0.8
    left_center = np.array(
        [-config.frame_width * 0.22 - col_pad_x, -0.35, 0.0]
    )
    right_center = np.array(
        [+config.frame_width * 0.22 + col_pad_x, -0.15, 0.0]
    )

    # -------- Left column: GPU grid (many squares), smaller & lower --------
    left_title = Tex(
        r"C\oe urs généraux", font_size=self.BODY_FONT_SIZE + 5, color=BLACK
    )
    left_title.move_to([-config.frame_width * 0.22 - col_pad_x, 2.0, 0.0])

    L_rows, L_cols = 8, 10
    L_box_w, L_box_h = 0.42, 0.42  # smaller
    L_gap = 0.07
    L_total_w = L_cols * L_box_w + (L_cols - 1) * L_gap
    L_total_h = L_rows * L_box_h + (L_rows - 1) * L_gap
    L_top_left = left_center + np.array(
        [-L_total_w / 2.0, +L_total_h / 2.0, 0.0]
    )

    left_boxes = []
    for r in range(L_rows):
        for c in range(L_cols):
            x = L_top_left[0] + c * (L_box_w + L_gap) + L_box_w / 2.0
            y = L_top_left[1] - r * (L_box_h + L_gap) - L_box_h / 2.0
            rect = Rectangle(
                width=L_box_w,
                height=L_box_h,
                stroke_opacity=1.0,
                fill_opacity=0.03,
                color=pc.blueGreen,
            ).move_to([x, y, 0.0])
            left_boxes.append(rect)

    left_group = VGroup(*left_boxes)

    self.play(
        AnimationGroup(
            FadeIn(left_title, run_time=0.3),
            FadeIn(left_group, run_time=0.5),
            lag_ratio=0.1,
        )
    )

    self.next_slide()

    # -------- Right column: 3x3 RT cores grid in pc.apple ------------------
    right_title = Tex(
        r"C\oe urs RT", font_size=self.BODY_FONT_SIZE + 5, color=BLACK
    )
    right_title.move_to([+config.frame_width * 0.22 + col_pad_x, +2.0, 0.0])

    R_rows, R_cols = 3, 3
    R_box_w, R_box_h = 0.85, 0.85
    R_gap = 0.12
    R_total_w = R_cols * R_box_w + (R_cols - 1) * R_gap
    R_total_h = R_rows * R_box_h + (R_rows - 1) * R_gap
    R_top_left = right_center + np.array(
        [-R_total_w / 2.0, +R_total_h / 2.0, 0.0]
    )

    right_boxes = []
    for r in range(R_rows):
        for c in range(R_cols):
            x = R_top_left[0] + c * (R_box_w + R_gap) + R_box_w / 2.0
            y = R_top_left[1] - r * (R_box_h + R_gap) - R_box_h / 2.0
            rect = Rectangle(
                width=R_box_w,
                height=R_box_h,
                stroke_opacity=1.0,
                fill_opacity=0.10,
                color=pc.apple,
            ).move_to([x, y, 0.0])
            right_boxes.append(rect)

    right_group = VGroup(*right_boxes)

    self.play(
        AnimationGroup(
            FadeIn(right_title, run_time=0.3),
            FadeIn(right_group, run_time=0.5),
            lag_ratio=0.1,
        )
    )

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
