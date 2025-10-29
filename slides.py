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
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "1,10"


class Presentation(Slide):
    TEXT_SCALE = 0.9
    MAX_WIDTH = 12.0
    BODY_TOP_BUFF = 0.2  # space between bar and first line
    BODY_LINE_BUFF = 0.15  # space between lines
    DEFAULT_PAD = 0.3
    BODY_FONT_SIZE = 28

    def construct(self):
        slides = [
            self.slide_01,
            self.slide_02,
            self.slide_03,
            self.slide_04,
            self.slide_05,
            self.slide_06,
            self.slide_07,
            self.slide_08,
            self.slide_09,
            self.slide_10,
            self.slide_11,
            self.slide_12,
            self.slide_13,
            self.slide_14,
            self.slide_15,
            self.slide_16,
            self.slide_17,
            self.slide_18,
            self.slide_19,
            self.slide_20,
            self.slide_21,
            self.slide_22,
            self.slide_23,
            self.slide_24,
            self.slide_25,
            self.slide_26,
            self.slide_27,
            self.slide_28,
            self.slide_29,
            self.slide_30,
            self.slide_31,
            self.slide_32,
            self.slide_33,
            self.slide_34,
            self.slide_35,
            self.slide_36,
            self.slide_37,
            self.slide_38,
            self.slide_39,
            self.slide_40,
            self.slide_41,
        ]
        selection_str = os.environ.get("SLIDES", SLIDES_SELECTION)
        selection = parse_selection(selection_str, len(slides))
        for idx, fn in enumerate(slides, start=1):
            if idx in selection:
                fn()

    # --------- Utilitaires ---------

    def _top_bar(self, label: str, *, font_size: int = 48):
        """
        Create a top bar with a left-aligned title that auto-scales to fit.
        The text is reduced in size if it would exceed the bar's inner width
        (accounting for horizontal padding) or height.
        """
        # Bar geometry
        h = config.frame_height / 10.0
        w = config.frame_width

        bar = Rectangle(
            width=w,
            height=h,
            fill_color=pc.blueGreen,
            fill_opacity=1.0,
            stroke_opacity=0.0,
        )

        # Create text at requested size
        txt = Text(label, color=WHITE, weight=BOLD, font_size=font_size)

        # Available inner space for the title
        inner_w = w - 2.0 * self.DEFAULT_PAD
        # Keep a small vertical margin so text does not touch bar edges
        inner_h = h * 0.82

        # Compute scale factors to fit width and height; only down-scale
        if txt.width > 0 and txt.height > 0:
            scale_w = inner_w / txt.width
            scale_h = inner_h / txt.height
            scale = min(1.0, scale_w, scale_h)
            if scale < 1.0:
                txt.scale(scale)

        # Assemble group and position
        elements = [bar, txt]
        group = VGroup(*elements)
        group.to_edge(UP, buff=0)

        # Left align with padding and vertically center in the bar
        txt.align_to(bar, LEFT)
        txt.shift(RIGHT * self.DEFAULT_PAD)
        txt.set_y(bar.get_center()[1])

        # Cache for body placement
        self._current_bar = group
        self._body_last = None
        self._text_left_x = bar.get_left()[0] + self.DEFAULT_PAD

        return group

    def start_body(self):
        """Initialize body placement just under the bar, with per-slide defaults."""
        # Assumes _top_bar() has been called before.
        self._body_last = None
        self._body_top_buff = self.BODY_TOP_BUFF
        self._body_font_size = self.BODY_FONT_SIZE

    def add_body_text(
        self, s: str, *, color=BLACK, font_size=30, weight=NORMAL
    ):
        """Add one line: first goes under the bar, then stack under previous."""
        # Assumes _top_bar() and start_body() have been called and args are not None.
        t = Text(s, color=color, weight=weight, font_size=font_size)

        if self._body_last is None:
            t.next_to(
                self._current_bar,
                DOWN,
                buff=self._body_top_buff,
                aligned_edge=LEFT,
            )
        else:
            t.next_to(
                self._body_last,
                DOWN,
                buff=self.BODY_LINE_BUFF,
                aligned_edge=LEFT,
            )

        dx = self._text_left_x - t.get_left()[0]
        t.shift(RIGHT * dx)

        self.add(t)
        self._body_last = t
        return t

    def _show_text(self, content):
        """Affiche uniquement le texte (str ou list[str]). Aucune pause/clear/barre."""
        sentence = "\n".join(content) if isinstance(content, list) else content
        txt = Text(sentence, color=BLACK)
        if txt.width > self.MAX_WIDTH:
            txt.scale(self.MAX_WIDTH / txt.width)
        txt.scale(self.TEXT_SCALE)
        self.add(txt)

    def default_end_slide(self, title):
        self.add(self._top_bar(title))
        self.pause()
        self.clear()
        self.next_slide()

    # --------- Slides ---------
    def slide_01(self):
        # --- Layout bounds (no top bar) ---
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_top = config.frame_height / 2 - 0.6
        y_bot = -config.frame_height / 2 + 0.6

        # ========= Title card =========
        title = (
            "Hybridation de la méthode de Tessendorf et de l'hydrodynamique "
            "des particules lissées pour la simulation d'océan en temps réel"
        )

        card_w = min((x_right - x_left) * 0.94, 13.5)
        card_h = 1.9
        card = RoundedRectangle(
            corner_radius=0.25,
            width=card_w,
            height=card_h,
            fill_color=pc.blueGreen,
            fill_opacity=1.0,
            stroke_opacity=0.0,
        ).move_to([0.0, y_top - card_h / 2.0 - 0.25, 0.0])

        t = Text(
            title, color=WHITE, font_size=self.BODY_FONT_SIZE + 8, weight=BOLD
        )
        inner_w = card_w - 0.6
        inner_h = card_h - 0.4
        if t.width and t.height:
            s = min(inner_w / t.width, inner_h / t.height, 1.0)
            if s < 1.0:
                t.scale(s)
        t.move_to(card.get_center())

        self.add(card, t)

        # ========= Author =========
        author = Text(
            "David Algis",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
            weight=BOLD,
        )
        author.next_to(card, DOWN, buff=0.35)
        self.add(author)

        # ========= Logos grid (3×2) =========
        img_paths = [
            "Figures/nyx.png",
            "Figures/aurora.jpg",
            "Figures/xlim.png",
            "Figures/up.png",
            "Figures/inria.png",
            "Figures/ensip.png",
        ]

        cols, rows = 3, 2
        hgap, vgap = 0.7, 0.6

        area_w = x_right - x_left
        grid_w = area_w * 0.94
        cell_w = (grid_w - (cols - 1) * hgap) / cols

        grid_top_y = author.get_bottom()[1] - 0.5
        max_grid_h = (grid_top_y - y_bot) * 0.92
        cell_h = min((max_grid_h - (rows - 1) * vgap) / rows, 2.2)

        grid_left_x = -grid_w / 2.0  # already centered around x=0

        imgs = []
        for i, p in enumerate(img_paths):
            r = i // cols
            c = i % cols
            cx = grid_left_x + c * (cell_w + hgap) + cell_w / 2.0
            cy = grid_top_y - r * (cell_h + vgap) - cell_h / 2.0

            im = ImageMobject(p)
            max_w = cell_w * 0.9
            max_h = cell_h * 0.9
            s = min(max_w / im.width, max_h / im.height, 1.0)
            im.scale(s)
            im.move_to([cx, cy, 0.0])
            imgs.append(im)

        # Use Group (not VGroup) because these are ImageMobjects (Mobject)
        grid_group = Group(*imgs)
        self.add(grid_group)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_02(self):
        # --- Top bar + title (kept static, on top) ---
        bar = self._top_bar("Contexte")
        self.add(bar)
        self.add_foreground_mobject(bar)  # keep the bar above everything

        # --- Body text (static) ---
        self.start_body()
        self.add_body_text(
            "Formation en réalité virtuelle : manipulation complexe sur un navire",
            font_size=self.BODY_FONT_SIZE,
        )

        # Optional background grid (behind everything else)
        # numberplane = NumberPlane(color=BLACK)
        # self.add(numberplane)

        # --- Left image (headset) - appears first (fade in) ---
        img_left = ImageMobject("Figures/man_head_set.png")
        img_left.to_edge(LEFT, buff=0.6)
        img_left.to_edge(DOWN, buff=0.1)
        img_left.scale(0.7)
        self.play(FadeIn(img_left, shift=RIGHT * 0.15, run_time=0.6))

        # --- Lines (draw from their start to end) ---
        line1 = Line([-4.5, 0, 0], [-1, -2, 0], color=pc.blueGreen)
        line2 = Line([-4.5, 0.5, 0], [-1, 2, 0], color=pc.blueGreen)
        # Draw them sequentially for clarity
        self.play(
            Create(line1, rate_func=smooth, run_time=0.9),
            Create(line2, rate_func=smooth, run_time=0.9),
        )

        # --- Right image placement (anchored to the two line endpoints) ---
        # Targets: left-lower = (-1, -2, 0), left-upper = (-1,  2, 0)
        img_boat = ImageMobject("Figures/inside_boat.jpeg")
        img_boat.set_height(4.0)  # span from y=-2 to y=+2
        img_boat.set_y(0.0)  # vertical center
        img_boat.set_x(
            -1.0 + img_boat.get_width() / 2.0
        )  # left edge at x = -1

        # Surrounding rectangle (tight fit), fade in AFTER the lines are drawn
        img_boat_box = SurroundingRectangle(
            img_boat, color=pc.blueGreen, buff=0.0, stroke_width=16
        )
        self.play(FadeIn(img_boat_box, run_time=0.5))

        # Finally, fade in the image inside the rectangle
        self.play(FadeIn(img_boat, run_time=0.6))

        # End the slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_03(self):
        # --- Top bar ---
        bar = self._top_bar("Objectifs")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Compute the area available below the bar ----
        bar_rect = bar.submobjects[0]  # the Rectangle of the top bar
        y_top = bar_rect.get_bottom()[1] - 0.15  # small gap below bar
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_center = np.array(
            [(x_left + x_right) * 0.5, (y_top + y_bottom) * 0.5, 0.0]
        )
        max_w = (x_right - x_left) * 0.95
        max_h = (y_top - y_bottom) * 0.95

        # ---- PNG image centered in the remaining area ----
        img = ImageMobject("Figures/thesis_goals.png")

        # Fit within the area while preserving aspect ratio (don't upscale beyond 1:1)
        scale_w = max_w / img.width
        scale_h = max_h / img.height
        scale_factor = min(scale_w, scale_h, 1.0)
        img.scale(scale_factor)

        img.move_to(area_center)
        self.add(img)

        # End the slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_04(self):
        self._show_text(
            [
                "Sommaire pour répondre à ses objectifs :",
                "I) Couplages 3 méthodes grandes échelles",
                "II) Hybridation SPH/Airy",
            ]
        )
        self.next_slide()
        self.pause()
        self.clear()
        self.next_slide()

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
        bar = self._top_bar("I) Introduction au calcul parallèle : CPU/GPU")
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
                    txt = Text("?", font_size=28, color=BLACK)
                else:
                    txt = Text(str(v), font_size=28, color=BLACK)
                txt.move_to(rect.get_center())
                boxes.append(rect)
                texts.append(txt)
            return VGroup(*boxes), VGroup(*texts)

        # --- Build rows: A, B, C (sequential result, initially "?") ---
        label_a = Text(
            "A", font_size=self.BODY_FONT_SIZE, color=BLACK
        ).next_to([x0 - 3.0, y_a, 0], RIGHT)
        label_b = Text(
            "B", font_size=self.BODY_FONT_SIZE, color=BLACK
        ).next_to([x0 - 3.0, y_b, 0], RIGHT)
        label_c_seq = Text(
            "C (1 thread)", font_size=self.BODY_FONT_SIZE, color=BLACK
        ).next_to([x0 - 3.5, y_c_seq, 0], RIGHT)

        boxes_a, txts_a = make_row(a_vals, y_a)
        boxes_b, txts_b = make_row(b_vals, y_b)
        boxes_c_seq, txts_c_seq = make_row(
            ["?"] * n, y_c_seq, placeholder=True
        )

        # Plus and equal signs for visual clarity
        plus1 = Text("+", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
            [x0 - 3.0, (y_a + y_b) / 2.0, 0], RIGHT
        )
        eq1 = Text("=", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
            [x0 - 3.0, (y_b + y_c_seq) / 2.0, 0], RIGHT
        )

        # --- Appear: rows and labels ---
        self.play(
            FadeIn(label_a, shift=RIGHT * 0.1, run_time=0.3),
            FadeIn(label_b, shift=RIGHT * 0.1, run_time=0.3),
            FadeIn(label_c_seq, shift=RIGHT * 0.1, run_time=0.3),
        )
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
        self.play(FadeIn(plus1, run_time=0.2), FadeIn(eq1, run_time=0.2))
        self.play(
            LaggedStart(
                *[FadeIn(mob, run_time=0.2) for mob in boxes_c_seq],
                *[FadeIn(mob, run_time=0.2) for mob in txts_c_seq],
                lag_ratio=0.05,
            )
        )

        # --- Sequential (single-thread) computation wrapped in one Succession ---
        run_time_animation_addition = 1
        steps = []
        for i in range(n):
            a_box = boxes_a[i]
            b_box = boxes_b[i]
            c_box = boxes_c_seq[i]
            c_txt_old = txts_c_seq[i]
            c_txt_new = Text(str(c_vals[i]), font_size=28, color=BLACK)
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
        label_c_par = Text(
            "C (N threads) ", font_size=self.BODY_FONT_SIZE, color=BLACK
        ).next_to([x0 - 3.5, y_c_par, 0], RIGHT)
        boxes_c_par, txts_c_par = make_row(
            ["?"] * n, y_c_par, placeholder=True
        )
        eq2 = Text("=", font_size=self.BODY_FONT_SIZE, color=BLACK).next_to(
            [x0 - 3.0, y_c_par + 1.0, 0], RIGHT
        )

        # Thread labels above each column
        thread_labels = VGroup(
            *[
                Text(f"Thread {i}", font_size=20, color=pc.oxfordBlue).next_to(
                    [x0 + i * (box_w + gap), y_c_par + 0.5, 0], UP
                )
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
            new_txt = Text(str(c_vals[i]), font_size=28, color=BLACK)
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
        bar = self._top_bar("I) Introduction au calcul parallèle : CPU/GPU")
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
                x = (
                    cpu_top_left[0]
                    + c * (cpu_box_w + cpu_gap)
                    + cpu_box_w / 2.0
                )
                y = (
                    cpu_top_left[1]
                    - r * (cpu_box_h + cpu_gap)
                    - cpu_box_h / 2.0
                )
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
                x = (
                    gpu_top_left[0]
                    + c * (gpu_box_w + gpu_gap)
                    + gpu_box_w / 2.0
                )
                y = (
                    gpu_top_left[1]
                    - r * (gpu_box_h + gpu_gap)
                    - gpu_box_h / 2.0
                )
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
        self.play(FadeIn(cpu_group, run_time=0.4))
        self.play(FadeIn(gpu_group, run_time=0.5))

        # --- End the slide ---
        self.clear()
        self.next_slide()

    def slide_06(self):
        # --- Top bar ---
        bar = self._top_bar("Unity et les compute shaders")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Usable area below the bar ----
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15  # small gap under bar
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_w = x_right - x_left
        area_h = y_top - y_bottom

        # ========= Right: Unity logo (TOP-RIGHT, reduced) =========
        logo = ImageMobject("Figures/unity_oxford_blue.png")

        # Smaller cap than before
        max_logo_w = area_w * 0.22
        max_logo_h = area_h * 0.34
        scale = min(max_logo_w / logo.width, max_logo_h / logo.height, 1.0)
        logo.scale(scale)

        right_margin = 0.35
        top_margin = 0.20
        logo_x = x_right - right_margin - logo.width * 0.5
        logo_y = y_top - top_margin - logo.height * 0.5
        logo.move_to([logo_x, logo_y, 0])
        self.add(logo)

        # ========= Left: text column =========
        # Headings + lists
        h1 = Text(
            "Unity un moteur de jeu polyvalent :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )

        bullet_items = [
            "Physique",
            "Rendu",
            "Réalité virtuelle",
            "Interface avec le GPU : les compute shaders",
            "...",
        ]
        lst = make_bullet_list(
            bullet_items,
            bullet_color=pc.blueGreen,
            font_size=self.BODY_FONT_SIZE,
            line_gap=0.18,
            left_pad=0.22,
        )
        # stack under h1
        lst.align_to(h1, LEFT)
        lst.next_to(h1, DOWN, buff=0.22, aligned_edge=LEFT)

        h2 = Text(
            "Les avantages et les inconvénients des compute shaders:",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )
        h2.align_to(h1, LEFT)
        h2.next_to(lst, DOWN, buff=0.55, aligned_edge=LEFT)

        pros = ["Multi-support"]
        cons = [
            "Ne bénéficie pas des dernières technologies",
            "Lourd à programmer",
            "Pas simple à débogger",
            "...",
        ]
        pc_list = make_pro_cons(
            pros,
            cons,
            pro_color=pc.apple,
            con_color=pc.bittersweet,
            font_size=self.BODY_FONT_SIZE,
            icon_size=self.BODY_FONT_SIZE + 2,
            col_gap=0.9,
            row_gap=0.18,
            left_pad=0.18,
        )
        pc_list.align_to(h2, LEFT)
        pc_list.next_to(h2, DOWN, buff=0.22, aligned_edge=LEFT)

        # Pack left column
        left_group = VGroup(h1, lst, h2, pc_list)

        # ---- Layout box for the left column (avoid overflow) ----
        # Reserve some spacing from the logo
        gap_to_logo = 0.6
        max_left_w = (logo.get_left()[0] - gap_to_logo) - x_left
        max_left_h = area_h * 0.92

        # Initial position (top-left anchor)
        left_group.arrange(DOWN, buff=0.18, center=False, aligned_edge=LEFT)
        left_group.move_to(
            [
                x_left + 0.2 + left_group.width * 0.5,
                y_top - 0.2 - left_group.height * 0.5,
                0,
            ]
        )

        # Auto-scale if too wide or too tall
        if left_group.width > max_left_w or left_group.height > max_left_h:
            s = min(
                max_left_w / left_group.width,
                max_left_h / left_group.height,
                1.0,
            )
            left_group.scale(s, about_point=left_group.get_top())
            # Re-anchor after scaling to keep inside bounds
            left_group.move_to(
                [
                    x_left + 0.2 + left_group.width * 0.5,
                    y_top - 0.2 - left_group.height * 0.5,
                    0,
                ]
            )

        self.add(left_group)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_07(self):
        # --- Top bar ---
        bar = self._top_bar("CUDA")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Usable area below the bar ----
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15  # small gap under bar
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_w = x_right - x_left
        area_h = y_top - y_bottom

        # ========= Right: CUDA logo (TOP-RIGHT) =========
        logo = ImageMobject("Figures/cuda_blue_green.png")
        max_logo_w = area_w * 0.22
        max_logo_h = area_h * 0.34
        scale = min(max_logo_w / logo.width, max_logo_h / logo.height, 1.0)
        logo.scale(scale)

        right_margin = 0.35
        top_margin = 0.20
        logo_x = x_right - right_margin - logo.width * 0.5
        logo_y = y_top - top_margin - logo.height * 0.5
        logo.move_to([logo_x, logo_y, 0])
        self.add(logo)

        # ========= Left: text column =========
        # Heading
        h1 = Text(
            "CUDA un langage pour programmation sur GPU :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )

        # (vspace in LaTeX → vertical gap here)
        vgap = 0.55

        # Subheading
        h2 = Text(
            "Les avantages et les inconvénients :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
            weight=BOLD,
        )

        # Pros / Cons
        pros = [
            "Intuitif à programmer",
            "Outils de débogage",
            "Performants",
            "Bénéficie des dernières technologies",
        ]
        cons = [
            "Utilisable uniquement sur carte Nvidia",
            "Pas accessible dans Unity",
        ]
        pc_list = make_pro_cons(
            pros,
            cons,
            pro_color=pc.apple,
            con_color=pc.bittersweet,
            font_size=self.BODY_FONT_SIZE,
            icon_size=self.BODY_FONT_SIZE + 2,
            col_gap=0.9,
            row_gap=0.18,
            left_pad=0.18,
        )

        # Pack left column; place under bar, left-aligned
        left_group = VGroup(h1, h2, pc_list)
        h1.set_x(x_left + 0.2)
        h1.set_y(y_top - 0.2)
        h2.align_to(h1, LEFT).next_to(h1, DOWN, buff=vgap, aligned_edge=LEFT)
        pc_list.align_to(h2, LEFT).next_to(
            h2, DOWN, buff=0.22, aligned_edge=LEFT
        )

        # ---- Avoid overlap with logo / bounds ----
        gap_to_logo = 0.6
        max_left_w = (logo.get_left()[0] - gap_to_logo) - x_left
        max_left_h = area_h * 0.92

        # Compute bounding box of left_group
        # (already positioned; now clamp size if needed)
        if left_group.width > max_left_w or left_group.height > max_left_h:
            s = min(
                max_left_w / left_group.width,
                max_left_h / left_group.height,
                1.0,
            )
            left_group.scale(s, about_point=h1.get_top())
            # Re-anchor after scaling
            dx = (x_left + 0.2) - left_group.get_left()[0]
            dy = (y_top - 0.2) - left_group[0].get_top()[
                1
            ]  # align h1 top again
            left_group.shift(RIGHT * dx + UP * dy)

        self.add(left_group)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_08(self):
        # --- Top bar ---
        bar = self._top_bar("InteropUnityCUDA (IUC)")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Usable area below the bar ----
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_w = x_right - x_left
        area_h = y_top - y_bottom
        y_center = (y_top + y_bottom) * 0.5

        # ---- Intro texts (LaTeX → manim) ----
        self.start_body()
        t1 = Text(
            "Afin d'utiliser CUDA dans Unity à la place des compute shaders : \\textbf{InteropUnityCUDA} :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        # Convert the bold part by rendering the whole line, then bold the keyword "InteropUnityCUDA"
        # (quick and robust without TeX rendering)
        t1 = Text(
            "Afin d'utiliser CUDA dans Unity à la place des compute shaders : InteropUnityCUDA :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        # Bold the keyword only
        # Find submobject index of the word to style (split into words)
        t1.set_x(x_left + 0.2)
        t1.set_y(y_top - 0.22)

        t2 = Text(
            "Un outil d'interopérabilité entre Unity et CUDA.",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        t2.align_to(t1, LEFT).next_to(t1, DOWN, buff=0.20, aligned_edge=LEFT)
        self.add(t1, t2)

        # ========= Three boxes: Unity (left), IUC (center), C++ lib (right) =========
        # Horizontal layout helpers
        cols = 3
        gap = area_w * 0.06
        cell_w = (area_w - 2 * gap) / 3.0
        cell_h = min(1.6, area_h * 0.28)

        cx_left = x_left + cell_w * 0.5
        cx_center = x_left + cell_w * 1.5 + gap
        cx_right = x_left + cell_w * 2.5 + 2 * gap
        cy = (
            y_center + 0.25
        )  # a bit above the true center to leave room for captions

        def box(label, center_x):
            r = Rectangle(
                width=cell_w,
                height=cell_h,
                stroke_color=pc.blueGreen,
                stroke_width=6,
            )
            r.move_to([center_x, cy, 0])
            txt = Text(
                label, color=BLACK, font_size=self.BODY_FONT_SIZE, weight=BOLD
            )
            txt.move_to(r.get_center())
            return VGroup(r, txt)

        box_unity = box("Unity", cx_left)
        box_iuc = box("IUC", cx_center)
        box_cpp = box("Librairie C++", cx_right)

        # We will reveal them progressively; start by adding only UNITY box
        self.add(box_unity)

        # ========= Image + caption (start under Unity) =========
        img = ImageMobject("Figures/logo_images.png")
        # size: fit under the box with some margins
        img.set_height(min(cell_h * 0.75, 1.6))
        img.move_to(
            [cx_left, box_unity.get_bottom()[1] - img.height * 0.55 - 0.25, 0]
        )

        cap1 = Text(
            "texture.unity", color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        cap1.next_to(img, DOWN, buff=0.15)

        # Show: left box + image + caption simultaneously
        self.play(
            FadeIn(img, run_time=0.4),
            FadeIn(cap1, run_time=0.4),
        )

        # ========= STEP 1 → 2 : user input then arrow to IUC, move image/caption, rename =========
        self.next_slide()

        arrow_1 = Arrow(
            start=box_unity[0].get_right(),  # rectangle's right edge
            end=box_iuc[0].get_left(),
            buff=0.08,
            stroke_color=pc.blueGreen,
            stroke_width=6,
            tip_length=0.16,
        )

        # Target positions under IUC
        img_target_pos_2 = np.array(
            [cx_center, box_iuc.get_bottom()[1] - img.height * 0.55 - 0.25, 0]
        )
        cap2 = Text(
            "conversion en texture.cuda",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        cap2.move_to(cap1)  # so Transform keeps position continuity
        cap2.next_to(
            img_target_pos_2, DOWN, buff=0.15
        )  # place relative to target img

        # Reveal IUC box + arrow, move image, change caption
        self.play(
            FadeIn(box_iuc, run_time=0.3),
            Create(arrow_1, run_time=0.6),
            img.animate.move_to(img_target_pos_2),
            Transform(cap1, cap2),
            lag_ratio=0.0,
        )

        # ========= STEP 2 → 3 : user input then arrow to C++ lib, move + rename =========
        self.next_slide()

        arrow_2 = Arrow(
            start=box_iuc[0].get_right(),
            end=box_cpp[0].get_left(),
            buff=0.08,
            stroke_color=pc.blueGreen,
            stroke_width=6,
            tip_length=0.16,
        )

        img_target_pos_3 = np.array(
            [cx_right, box_cpp.get_bottom()[1] - img.height * 0.55 - 0.25, 0]
        )
        cap3 = Text(
            "écriture dans cuda", color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        cap3.move_to(cap1)  # transform from current caption
        cap3.next_to(img_target_pos_3, DOWN, buff=0.15)

        self.play(
            FadeIn(box_cpp, run_time=0.3),
            Create(arrow_2, run_time=0.6),
            img.animate.move_to(img_target_pos_3),
            Transform(cap1, cap3),
            lag_ratio=0.0,
        )

        # ========= Bottom-right credit =========
        credit = Text(
            "Algis et al. 2025", color=BLACK, font_size=self.BODY_FONT_SIZE - 6
        )
        credit.to_edge(DOWN, buff=0.2)
        credit.to_edge(RIGHT, buff=0.3)
        self.add(credit)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_09(self):
        """
        Present three major ocean-simulation approaches with centered labels.
        Each ellipse appears after user input. Layout: one centered on top,
        two at the bottom (left and right).
        """
        # --- Top bar ---------------------------------------------------------
        bar = self._top_bar(
            "Trois méthodes de l'état de l'art pour la simulation d'océan"
        )
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Ellipse geometry (closer to circles) ----------------------------
        ell_w = 3.6
        ell_h = 2.8

        # --- First ellipse: ocean surface simulation (higher) ----------------
        e1 = Ellipse(
            width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
        )
        t1 = Paragraph(
            "Simulation de",
            "surface de l'océan",
            alignment="center",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
            line_spacing=0.6,
        )
        t1.move_to(e1.get_center())
        g1 = VGroup(e1, t1)
        g1.move_to([0.0, 0.9, 0.0])

        self.play(FadeIn(g1, run_time=0.6))
        self.next_slide()

        # --- Second ellipse: fluid -> solid ----------------------------------
        e2 = Ellipse(
            width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
        )
        t2 = Paragraph(
            "Action du fluide",
            "sur le solide",
            alignment="center",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
            line_spacing=0.6,
        )
        t2.move_to(e2.get_center())
        g2 = VGroup(e2, t2)
        g2.move_to([-3.6, -1.7, 0.0])

        self.play(FadeIn(g2, run_time=0.6))
        self.next_slide()

        # --- Third ellipse: solid -> fluid -----------------------------------
        e3 = Ellipse(
            width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
        )
        t3 = Paragraph(
            "Action du solide",
            "sur le fluide",
            alignment="center",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
            line_spacing=0.6,
        )
        t3.move_to(e3.get_center())
        g3 = VGroup(e3, t3)
        g3.move_to([3.6, -1.7, 0.0])

        self.play(FadeIn(g3, run_time=0.6))

        # --- End slide --------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()

    def slide_10(self):
        """
        Airy wave theory demonstration.
        Shows, in order: cos(x), cos(x+t), A cos(x+t), A cos(kx+t), A cos(kx+omega t).
        Keeps the intro and formulas left-aligned at a fixed anchor. Uses
        ReplacementTransform to avoid overlapping formulas. The label under the
        curve displays only parameters that have been introduced so far.
        """
        # --- Top bar --------------------------------------------------------------
        bar = self._top_bar("La théorie des vagues d'Airy")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area under the bar -------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left

        # Left anchor for intro/formulas to prevent horizontal drift
        anchor_x = x_left + 0.2

        # --- Intro line (left aligned, placed under the bar) ---------------------
        self.start_body()
        intro = Text(
            "Modèle linéaire qui simule l'océan comme une simple vague :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        intro_y = y_top - 0.35
        intro.move_to([anchor_x + intro.width / 2.0, intro_y, 0.0])
        self.add(intro)

        # --- Initial formula (left aligned under intro) --------------------------
        formula = MathTex(r"h(x,t)=\cos(x)", color=BLACK)
        formula.next_to(intro, DOWN, buff=0.25, aligned_edge=LEFT)
        dx0 = anchor_x - formula.get_left()[0]
        formula.shift(RIGHT * dx0)
        formula_y = formula.get_y()
        self.add(formula)

        # --- Axes below the formula ---------------------------------------------
        axes_top = formula.get_bottom()[1] - 0.3
        axes_bottom = y_bottom + 0.2
        axes_height = max(1.8, min(3.8, axes_top - axes_bottom))
        axes_width = area_w

        axes = Axes(
            x_range=[-2 * PI, 2 * PI, PI],
            y_range=[-2.2, 2.2, 1],
            x_length=axes_width,
            y_length=axes_height,
            axis_config={"color": GRAY, "stroke_width": 2},
            tips=False,
        )
        axes.move_to([0, axes_bottom + axes_height / 2.0, 0])
        self.add(axes)

        # --- Helper to lock any new formula to same left and y -------------------
        def _lock_left(mobj: Mobject) -> Mobject:
            dx = anchor_x - mobj.get_left()[0]
            mobj.shift(RIGHT * dx)
            mobj.set_y(formula_y)
            return mobj

        # --- Trackers ------------------------------------------------------------
        A = ValueTracker(1.0)
        k = ValueTracker(1.0)
        omega = ValueTracker(0.0)  # start with cos(x)
        t = ValueTracker(0.0)

        # --- Curve depending on trackers -----------------------------------------
        def f_y(xval: float) -> float:
            return A.get_value() * np.cos(
                k.get_value() * xval + omega.get_value() * t.get_value()
            )

        curve = always_redraw(
            lambda: axes.plot(
                lambda x: f_y(x),
                x_range=[-2 * PI, 2 * PI],
                stroke_width=4,
                color=(pc.oxfordBlue if hasattr(pc, "oxfordBlue") else BLACK),
            )
        )
        self.add(curve)

        # --- Adaptive label: show only introduced params -------------------------
        show_t = False
        show_A = False
        show_k = False
        show_omega = False

        def label_text() -> Mobject:
            parts = []
            if show_A:
                parts.append(rf"A={A.get_value():.2f}")
            if show_k:
                parts.append(rf"k={k.get_value():.2f}")
            if show_omega:
                parts.append(rf"\omega={omega.get_value():.2f}")
            if show_t:
                parts.append(rf"t={t.get_value():.2f}")

            if not parts:
                # Transparent spacer to avoid TeX on empty label
                return Rectangle(
                    width=0.1, height=0.1, stroke_opacity=0.0, fill_opacity=0.0
                )

            expr = r"\quad ".join(parts)
            return MathTex(
                expr, font_size=self.BODY_FONT_SIZE - 2, color=BLACK
            )

        value_label = always_redraw(
            lambda: label_text().next_to(axes, DOWN, buff=0.15)
        )
        self.add(value_label)

        # ===================== Step 1: h = cos(x) =================================
        self.next_slide()  # no loop here

        # ===================== Step 2: h = cos(x + t) =============================
        new_formula = MathTex(r"h(x,t)=\cos(x+t)", color=BLACK)
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()  # no loop on formula change

        omega.set_value(1.0)
        show_t = True
        self.play(t.animate.set_value(2 * PI), rate_func=linear, run_time=4.0)
        self.next_slide(loop=True)

        # ===================== Step 3: h = A cos(x + t) ===========================
        new_formula = MathTex(r"h(x,t)=A\cos(x+t)", color=BLACK)
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()  # no loop on formula change

        self.play(t.animate.set_value(0.0), run_time=0.3)
        show_A = True
        self.play(
            A.animate.set_value(2.0), rate_func=there_and_back, run_time=4.0
        )
        self.next_slide(loop=True)

        # ===================== Step 4: h = A cos(kx + t) ==========================
        new_formula = MathTex(r"h(x,t)=A\cos(kx+t)", color=BLACK)
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()  # no loop on formula change

        self.play(
            A.animate.set_value(1.0), t.animate.set_value(0.0), run_time=0.3
        )
        show_k = True
        self.play(
            k.animate.set_value(10.0), rate_func=there_and_back, run_time=5.0
        )
        self.next_slide(loop=True)

        # ===================== Step 5: h = A cos(kx + omega t) ====================
        new_formula = MathTex(r"h(x,t)=A\cos(kx+\omega t)", color=BLACK)
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()  # no loop on formula change

        self.play(
            A.animate.set_value(1.0), k.animate.set_value(1.0), run_time=0.3
        )
        show_omega = True
        self.play(
            AnimationGroup(
                omega.animate.set_value(10.0),
                t.animate.set_value(2 * PI),
                lag_ratio=0.0,
            ),
            rate_func=linear,
            run_time=5.0,
        )
        self.next_slide(loop=True)

        # --- End of slide --------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()

    def slide_11(self):
        self._show_text(
            "Présentation de la méthode de Tessendorf en 2D comme une généralisation d'Airy"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_12(self):
        self._show_text("Présentation du spectre d'océan")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_13(self):
        self._show_text("Champs de hauteur et IFFT (avec IUC)")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_14(self):
        self._show_text("Vitesse de l'océan")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_15(self):
        self._show_text(
            "Pourquoi le couplage fluide/solide ne fonctionne pas avec Tessendorf et comment on va gérer ça"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_16(self):
        self._show_text("Fluide->Solide présentation de la méthode des forces")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_17(self):
        self._show_text(
            "Solide->Fluide présentation du principe des vagues d'interactions"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_18(self):
        self._show_text("Calcul du masque")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_19(self):
        self._show_text("Résultat de la combinaison des trois méthodes")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_20(self):
        self._show_text(
            "II) Conclusion sur les trois méthodes, les faiblesses et pourquoi on veut passer à un cran supérieur. L'hybridation son prinicipe : SPH et Tessendorf"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_21(self):
        self._show_text(
            "SPH pas à pas : fluides représenté comme des particules, forces de gravité"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_22(self):
        self._show_text("SPH - Estimation en noyau pour la densité ")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_23(self):
        self._show_text("SPH - Forces de pression")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_24(self):
        self._show_text("SPH - Forces de viscosité")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_25(self):
        self._show_text("SPH - Couplage avec solides")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_26(self):
        self._show_text(
            "Optimisation avec la RPPV - explication rapide de la méthode en grille (sans parler de GPU)"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_27(self):
        self._show_text(
            "Expliquer qu'on souhaite mieux utiliser les spécificités du GPU pour la RPPV"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_28(self):
        self._show_text("Expliquer le concept de mémoire partagée")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_29(self):
        self._show_text("Expliquer la méthode x-pencil")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_30(self):
        self._show_text("Expliquer le lancer de rayon")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_31(self):
        self._show_text(
            "Expliquer nos résultats sur le lancer de rayon pour la RRPV"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_32(self):
        self._show_text(
            "Hybridation - Rentrer plus dans les détails du principe : forces d'Airy et zones"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_33(self):
        self._show_text("Définir globalement formellement la force d'Airy")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_34(self):
        self._show_text("Calcul de la vitesse d'Airy")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_35(self):
        self._show_text("Facteur de modulation")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_36(self):
        self._show_text("Expliquer les différentes zones et leurs objectifs")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_37(self):
        self._show_text("Présenter le régulateur de particules")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_38(self):
        self._show_text("Présenter les résultats de l'hybridation")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_39(self):
        self._show_text("Conclusion")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_40(self):
        self._show_text("Perspectives")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_41(self):
        self._show_text("Remerciements")
        self.pause()
        self.clear()
        self.next_slide()
