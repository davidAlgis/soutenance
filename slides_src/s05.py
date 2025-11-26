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


@slide(5)
def slide_05(self):
    """
    Slide 05: Introduction to parallel computing with a simple example:
    element-wise addition of two vectors. First shown as single-thread
    (sequential) work, then as multi-thread (parallel) work.

    Implementation note:
    - To avoid generating many tiny partial video files (problematic for
      manim-slides on Windows), the per-index sequential steps are wrapped
      into a single Succession so we only call self.play(...) once for the
      whole sequence. Ultra-short waits are removed.
    """
    # --- Top bar (kept above everything) ---
    bar, footer = self._top_bar("Introduction au calcul parallèle : CPU/GPU")
    self.add(bar)
    self.add_foreground_mobject(bar)
    # numberplane = NumberPlane(color=BLACK)
    # self.add(numberplane)
    # --- Data for the example ---
    a_vals = [1, 4, 2, 3, 5]
    b_vals = [3, 1, 6, 2, 4]
    n = len(a_vals)
    c_vals = [a_vals[i] + b_vals[i] for i in range(n)]

    # --- Layout parameters ---
    box_w = 1.2
    box_h = 0.8
    gap = 0.2

    # Horizontal positions for n boxes centered on screen
    total_w = n * box_w + (n - 1) * gap
    x0 = -2

    # Row y positions
    y_a = 2.5
    y_b = 0.8
    y_c_seq = -0.9
    y_c_par = -2.6

    # --- Helpers to create a row of labeled boxes ---
    def make_row(values, y, placeholder=False):
        boxes = []
        texts = []
        for i, v in enumerate(values):
            x = x0 + i * (box_w + gap)
            rect = Rectangle(
                width=box_w,
                height=box_h,
                fill_opacity=0.05,
                stroke_opacity=1.0,
                color=pc.blueGreen,
            )
            rect.move_to([x, y, 0.0])
            if placeholder:
                txt = Tex("?", font_size=28, color=BLACK)
            else:
                txt = Tex(str(v), font_size=28, color=BLACK)
            txt.move_to(rect.get_center())
            boxes.append(rect)
            texts.append(txt)
        return VGroup(*boxes), VGroup(*texts)

    # --- Build rows: A, B, C (sequential result, initially "?") ---
    label_a = Tex("A", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
        [x0 - 3.0, y_a, 0], RIGHT
    )
    label_b = Tex("B", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
        [x0 - 3.0, y_b, 0], RIGHT
    )
    label_c_seq = Tex(
        r"C (1 \textit{thread})", font_size=self.BODY_FONT_SIZE, color=BLACK
    ).next_to([x0 - 3.5, y_c_seq, 0], RIGHT)

    # Plus and equal signs for visual clarity
    plus1 = Tex("+", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
        [x0 - 3.0, (y_a + y_b) / 2.0, 0], RIGHT
    )
    eq1 = Tex("=", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
        [x0 - 3.0, (y_b + y_c_seq) / 2.0, 0], RIGHT
    )

    boxes_a, txts_a = make_row(a_vals, y_a)
    boxes_b, txts_b = make_row(b_vals, y_b)
    boxes_c_seq, txts_c_seq = make_row(["?"] * n, y_c_seq, placeholder=True)

    # --- Appear: rows and labels ---
    self.play(
        FadeIn(label_a, shift=RIGHT * self.SHIFT_SCALE, run_time=0.3),
        FadeIn(label_b, shift=RIGHT * self.SHIFT_SCALE, run_time=0.3),
        FadeIn(label_c_seq, shift=RIGHT * self.SHIFT_SCALE, run_time=0.3),
    )
    self.play(FadeIn(plus1, run_time=0.2), FadeIn(eq1, run_time=0.2))
    self.wait(0.1)
    self.next_slide()

    self.play(
        LaggedStart(
            *[FadeIn(mob, run_time=0.2) for mob in boxes_a],
            *[FadeIn(mob, run_time=0.2) for mob in txts_a],
            lag_ratio=0.05,
        )
    )
    self.play(
        LaggedStart(
            *[FadeIn(mob, run_time=0.2) for mob in boxes_b],
            *[FadeIn(mob, run_time=0.2) for mob in txts_b],
            lag_ratio=0.05,
        )
    )
    self.play(
        LaggedStart(
            *[FadeIn(mob, run_time=0.2) for mob in boxes_c_seq],
            *[FadeIn(mob, run_time=0.2) for mob in txts_c_seq],
            lag_ratio=0.05,
        )
    )
    self.next_slide()

    # --- Sequential (single-thread) computation wrapped in one Succession ---
    run_time_animation_addition = 1
    steps = []
    for i in range(n):
        a_box = boxes_a[i]
        b_box = boxes_b[i]
        c_box = boxes_c_seq[i]
        c_txt_old = txts_c_seq[i]
        c_txt_new = Tex(str(c_vals[i]), font_size=28, color=BLACK)
        c_txt_new.move_to(c_box.get_center())
        step = AnimationGroup(
            Indicate(
                a_box,
                scale_factor=1.05,
                run_time=run_time_animation_addition,
            ),
            Indicate(
                b_box,
                scale_factor=1.05,
                run_time=run_time_animation_addition,
            ),
            Transform(
                c_txt_old,
                c_txt_new,
                run_time=run_time_animation_addition / 2,
            ),
            lag_ratio=0.0,
        )
        steps.append(step)

    self.play(Succession(*steps))

    # --- Pause to discuss the sequential model ---
    self.next_slide()

    # --- Parallel (multi-thread) version: new result row with simultaneous updates ---
    label_c_par = Tex(
        r"C (N \textit{threads}) ", font_size=self.BODY_FONT_SIZE, color=BLACK
    ).next_to([x0 - 3.5, y_c_par, 0], RIGHT)
    boxes_c_par, txts_c_par = make_row(["?"] * n, y_c_par, placeholder=True)
    eq2 = Tex("=", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
        [x0 - 3.0, y_c_par + 1.0, 0], RIGHT
    )

    # Thread labels above each column
    thread_labels = VGroup(
        *[
            Tex(
                f"\\textit{{thread}} {i}",
                font_size=self.BODY_FONT_SIZE - 5,
                color=pc.oxfordBlue,
            ).next_to([x0 + i * (box_w + gap), y_c_par + 0.5, 0], UP)
            for i in range(n)
        ]
    )

    self.play(
        FadeIn(eq2, run_time=0.2),
        FadeIn(label_c_par, run_time=0.3),
        LaggedStart(
            *[FadeIn(mob, run_time=0.2) for mob in boxes_c_par],
            *[FadeIn(mob, run_time=0.2) for mob in txts_c_par],
            lag_ratio=0.05,
        ),
    )
    self.play(FadeIn(thread_labels, run_time=0.3))

    # Parallel highlight: indicate all pairs and fill results simultaneously
    indicates = []
    transforms = []
    for i in range(n):
        indicates.append(
            Indicate(
                boxes_a[i],
                scale_factor=1.03,
                run_time=4.0 * run_time_animation_addition,
            )
        )
        indicates.append(
            Indicate(
                boxes_b[i],
                scale_factor=1.03,
                run_time=4.0 * run_time_animation_addition,
            )
        )
        new_txt = Tex(str(c_vals[i]), font_size=28, color=BLACK)
        new_txt.move_to(boxes_c_par[i].get_center())
        transforms.append(
            Transform(
                txts_c_par[i],
                new_txt,
                run_time=4.0 * run_time_animation_addition / 2,
            )
        )

    # Single call to self.play to keep one robust clip
    self.play(
        AnimationGroup(
            AnimationGroup(*indicates, lag_ratio=0.0),
            AnimationGroup(*transforms, lag_ratio=0.0),
            lag_ratio=0.1,
        )
    )

    # --- Pause to discuss the parallel model ---
    self.pause()

    # --- End the slide ---
    self.clear()
    self.next_slide()
    bar, footer = self._top_bar("Introduction au calcul parallèle : CPU/GPU")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Column layout parameters ---
    col_pad_x = 1.0
    col_center_left = np.array(
        [-config.frame_width * 0.25 - col_pad_x, 0.2, 0.0]
    )
    col_center_right = np.array(
        [config.frame_width * 0.25 + col_pad_x - 0.6, 0.2, 0.0]
    )

    # --- CPU column: title + 2x4 grid with labels ---
    cpu_title = Text("CPU", font_size=46, color=BLACK)
    cpu_title.move_to(col_center_left + np.array([0.0, 2.4, 0.0]))

    cpu_rows, cpu_cols = 2, 4
    cpu_box_w, cpu_box_h = 0.9, 0.9
    cpu_gap = 0.14

    # Compute top-left position of the CPU grid
    cpu_total_w = cpu_cols * cpu_box_w + (cpu_cols - 1) * cpu_gap
    cpu_total_h = cpu_rows * cpu_box_h + (cpu_rows - 1) * cpu_gap
    cpu_top_left = col_center_left + np.array(
        [-cpu_total_w / 2.0, +cpu_total_h / 2.0, 0.0]
    )

    cpu_boxes = []
    cpu_labels = []
    for r in range(cpu_rows):
        for c in range(cpu_cols):
            x = cpu_top_left[0] + c * (cpu_box_w + cpu_gap) + cpu_box_w / 2.0
            y = cpu_top_left[1] - r * (cpu_box_h + cpu_gap) - cpu_box_h / 2.0
            rect = Rectangle(
                width=cpu_box_w,
                height=cpu_box_h,
                stroke_opacity=1.0,
                fill_opacity=0.05,
                color=pc.blueGreen,
            ).move_to([x, y, 0.0])
            lbl = Tex(r"c\oe ur", font_size=15, color=BLACK).move_to(
                rect.get_center()
            )
            cpu_boxes.append(rect)
            cpu_labels.append(lbl)

    cpu_group = VGroup(*cpu_boxes, *cpu_labels)

    # --- GPU column: title + large grid (tens of squares) ---
    gpu_title = Text("GPU", font_size=46, color=BLACK)
    gpu_title.move_to(col_center_right + np.array([-0.7, 2.4, 0.0]))

    gpu_rows, gpu_cols = 8, 10  # 80 squares (tens of them)
    gpu_box_w, gpu_box_h = 0.5, 0.5
    gpu_gap = 0.08

    gpu_total_w = gpu_cols * gpu_box_w + (gpu_cols - 1) * gpu_gap
    gpu_total_h = gpu_rows * gpu_box_h + (gpu_rows - 1) * gpu_gap
    gpu_top_left = col_center_right + np.array(
        [-gpu_total_w / 2.0, +gpu_total_h / 2.0, 0.0]
    )

    gpu_boxes = []
    for r in range(gpu_rows):
        for c in range(gpu_cols):
            x = gpu_top_left[0] + c * (gpu_box_w + gpu_gap) + gpu_box_w / 2.0
            y = gpu_top_left[1] - r * (gpu_box_h + gpu_gap) - gpu_box_h / 2.0
            rect = Rectangle(
                width=gpu_box_w,
                height=gpu_box_h,
                stroke_opacity=1.0,
                fill_opacity=0.03,
                color=pc.blueGreen,
            ).move_to([x, y, 0.0])
            gpu_boxes.append(rect)

    gpu_group = VGroup(*gpu_boxes)
    gpu_group.shift(
        LEFT * 0.6 + DOWN * 0.4
    )  # move grid left and slightly down

    # --- Add all elements with minimal animations to avoid tiny clips ---
    self.play(
        FadeIn(cpu_title, run_time=0.3),
        FadeIn(gpu_title, run_time=0.3),
    )
    # Batch grid appearances to keep rendering robust on Windows
    self.play(Create(cpu_group, run_time=1.0))
    self.play(Create(gpu_group, run_time=1.0))
    self.wait(0.1)
    # --- End the slide ---
    self.clear()
    self.next_slide()
