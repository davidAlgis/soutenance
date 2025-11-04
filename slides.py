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
from sph_vis import show_sph_simulation

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "21"


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
        import textwrap

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
        card_h = 2.3
        card = RoundedRectangle(
            corner_radius=0.28,
            width=card_w,
            height=card_h,
            fill_color=pc.blueGreen,
            fill_opacity=1.0,
            stroke_opacity=0.0,
        ).move_to([0.0, y_top - card_h / 2 - 0.20, 0.0])

        # ---- Helper: wrap title into <=3 lines ----
        def wrap_title(t: str, max_lines: int = 3):
            for width in (48, 44, 40, 36, 32, 28, 24):
                lines = textwrap.wrap(
                    t,
                    width=width,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                if 1 <= len(lines) <= max_lines:
                    return lines
            words = t.split()
            chunks = [[] for _ in range(max_lines)]
            for i, w in enumerate(words):
                chunks[i % max_lines].append(w)
            return [" ".join(c) for c in chunks]

        lines = wrap_title(title, max_lines=3)

        # Build Paragraph
        base_fs = self.BODY_FONT_SIZE + 18
        para = Paragraph(
            *lines,
            alignment="center",
            font_size=base_fs,
            color=WHITE,
            line_spacing=0.8,
        )

        inner_w = card_w - 0.8
        inner_h = card_h - 0.55
        if para.width and para.height:
            scale_w = inner_w / para.width
            scale_h = inner_h / para.height
            scale = min(scale_w, scale_h, 1.0)
            if scale < 1.0:
                para.scale(scale)

        para.move_to(card.get_center())
        self.add(card, para)

        # ========= Author =========
        author = Text(
            "David Algis",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
            weight=BOLD,
        )
        author.next_to(card, DOWN, buff=0.45)
        self.add(author)

        # ========= Logos grid (3×2), larger and lower =========
        img_paths = [
            "Figures/nyx.png",
            "Figures/aurora.jpg",
            "Figures/xlim.png",
            "Figures/up.png",
            "Figures/inria.png",
            "Figures/ensip.png",
        ]

        COLS, ROWS = 3, 2
        HGAP, VGAP = 0.35, 0.30
        GRID_WIDTH_RATIO = 0.96
        GRID_HEIGHT_RATIO = 0.90
        GRID_TOP_OFFSET = 1.00
        LOGO_FILL = 1.10
        MAX_UPSCALE = 2.5

        area_w = x_right - x_left
        grid_w = area_w * GRID_WIDTH_RATIO
        cell_w = (grid_w - (COLS - 1) * HGAP) / COLS

        grid_top_y = author.get_bottom()[1] - GRID_TOP_OFFSET
        max_grid_h = (grid_top_y - y_bot) * GRID_HEIGHT_RATIO
        cell_h = min((max_grid_h - (ROWS - 1) * VGAP) / ROWS, 2.20)

        grid_left_x = -grid_w / 2.0

        imgs = []
        for i, p in enumerate(img_paths):
            r = i // COLS
            c = i % COLS
            cx = grid_left_x + c * (cell_w + HGAP) + cell_w / 2.0
            cy = grid_top_y - r * (cell_h + VGAP) - cell_h / 2.0

            im = ImageMobject(p)
            max_w = cell_w * LOGO_FILL
            max_h = cell_h * LOGO_FILL
            scale_w = max_w / im.width
            scale_h = max_h / im.height
            s = min(scale_w, scale_h, MAX_UPSCALE)
            im.scale(s)
            im.move_to([cx, cy, 0.0])
            imgs.append(im)

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
        bar = self._top_bar("Introduction au calcul parallèle : CPU/GPU")
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

        # ---- Intro texts (fit to bounds, then place) ----
        self.start_body()
        self.add_body_text(
            "Afin d'utiliser CUDA dans Unity à la place des compute shaders : InteropUnityCUDA",
            font_size=self.BODY_FONT_SIZE - 4,
        )
        self.add_body_text(
            "Un outil d'interopérabilité entre Unity et CUDA.",
            font_size=self.BODY_FONT_SIZE - 4,
        )

        # ========= Bottom-right credit =========
        credit = Text(
            "Algis et al. 2025", color=BLACK, font_size=self.BODY_FONT_SIZE - 6
        )
        credit.to_edge(DOWN, buff=0.2)
        credit.to_edge(RIGHT, buff=0.3)
        self.add(credit)

        # ========= Three boxes: Unity (left), IUC (center), C++ lib (right) =========
        gap = area_w * 0.06
        cell_w = (area_w - 2 * gap) / 3.0
        cell_h = min(1.6, area_h * 0.28)

        cx_left = x_left + cell_w * 0.5
        cx_center = x_left + cell_w * 1.5 + gap
        cx_right = x_left + cell_w * 2.5 + 2 * gap
        cy = y_center + 0.25  # leave room below for image/captions

        def box(label, center_x):
            r = Rectangle(
                width=cell_w,
                height=cell_h,
                stroke_color=pc.blueGreen,
                stroke_width=6,
            ).move_to([center_x, cy, 0])
            txt = Text(
                label, color=BLACK, font_size=self.BODY_FONT_SIZE, weight=BOLD
            ).move_to(r.get_center())
            return VGroup(r, txt)

        box_unity = box("Unity", cx_left)
        box_iuc = box("IUC", cx_center)
        box_cpp = box("Librairie C++", cx_right)

        # Show only UNITY box initially
        self.add(box_unity)

        # ========= Image + caption (initial state) =========
        img = ImageMobject("Figures/logo_images.png")
        img.set_height(min(cell_h * 0.75, 1.6))

        def img_center_under(box_group):
            box_rect = box_group[0]
            return np.array(
                [
                    box_rect.get_center()[0],
                    box_rect.get_bottom()[1] - img.height * 0.55 - 0.25,
                    0.0,
                ]
            )

        # Initial placement (Unity)
        img.move_to(img_center_under(box_unity))

        cap = Text("texture.unity", color=BLACK, font_size=self.BODY_FONT_SIZE)
        cap.next_to(img, DOWN, buff=0.15)

        # Move image + caption together as a single unit
        ic_group = Group(img, cap)
        self.play(FadeIn(ic_group, run_time=0.4))

        # ========= STEP 1 → 2 =========
        self.next_slide()

        arrow_1 = Arrow(
            start=box_unity[0].get_right(),
            end=box_iuc[0].get_left(),
            buff=0.08,
            stroke_color=pc.blueGreen,
            stroke_width=6,
            tip_length=0.16,
        )
        self.play(FadeIn(box_iuc, run_time=0.3), Create(arrow_1, run_time=0.6))

        target_img_center_2 = img_center_under(box_iuc)
        shift_vec_2 = target_img_center_2 - img.get_center()
        self.play(ic_group.animate.shift(shift_vec_2), run_time=0.6)

        new_cap_2 = Text(
            "conversion en texture.cuda",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        new_cap_2.move_to(cap)  # keep position; only glyphs change
        self.play(Transform(cap, new_cap_2), run_time=0.35)

        # ========= STEP 2 → 3 =========
        self.next_slide()

        arrow_2 = Arrow(
            start=box_iuc[0].get_right(),
            end=box_cpp[0].get_left(),
            buff=0.08,
            stroke_color=pc.blueGreen,
            stroke_width=6,
            tip_length=0.16,
        )
        self.play(FadeIn(box_cpp, run_time=0.3), Create(arrow_2, run_time=0.6))

        target_img_center_3 = img_center_under(box_cpp)
        shift_vec_3 = target_img_center_3 - img.get_center()
        self.play(ic_group.animate.shift(shift_vec_3), run_time=0.6)

        new_cap_3 = Text(
            "écriture dans cuda", color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        new_cap_3.move_to(cap)
        self.play(Transform(cap, new_cap_3), run_time=0.35)

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
        g1.move_to([0.0, 1.3, 0.0])

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
        Airy wave theory demonstration with color highlights.
        Shows, in order: cos(x), cos(x+t), A cos(x+t), A cos(kx+t), A cos(kx+omega t).
        The evolving variables are colorized both in the formula and in the value label.
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

        # --- Colors for highlights ------------------------------------------------
        col_A = pc.apple
        col_k = pc.tiffanyBlue
        col_t = pc.bittersweet
        col_omega = pc.uclaGold

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

        # --- Helper: build a formula and colorize given symbols -------------------
        def make_formula(tex_expr: str, highlight: dict) -> MathTex:
            m = MathTex(
                tex_expr,
                color=BLACK,
                substrings_to_isolate=(
                    list(highlight.keys()) if highlight else None
                ),
            )
            for key, col in (highlight or {}).items():
                m.set_color_by_tex(key, col)
            return m

        # --- Initial formula (left aligned under intro) --------------------------
        formula = make_formula(r"h(x,t)=\cos(x)", highlight={})
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
        # self.add(axes)

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
                color=pc.oxfordBlue,
            )
        )
        self.add(curve)

        # --- Adaptive label: show only introduced params (colorized) -------------
        show_t = False
        show_A = False
        show_k = False
        show_omega = False

        def label_text() -> Mobject:
            parts = []
            if show_A:
                parts.append(r"A=" + f"{A.get_value():.2f}")
            if show_k:
                parts.append(r"k=" + f"{k.get_value():.2f}")
            if show_omega:
                parts.append(r"\omega=" + f"{omega.get_value():.2f}")
            if show_t:
                parts.append(r"t=" + f"{t.get_value():.2f}")

            if not parts:
                # Transparent spacer to avoid TeX on empty label
                return Rectangle(
                    width=0.1, height=0.1, stroke_opacity=0.0, fill_opacity=0.0
                )

            expr = r"\quad ".join(parts)
            tex_colors = {
                "A": col_A,
                "k": col_k,
                r"\omega": col_omega,
                "t": col_t,
            }
            return MathTex(
                expr,
                font_size=self.BODY_FONT_SIZE + 10,
                color=BLACK,
                tex_to_color_map=tex_colors,
            )

        value_label = always_redraw(
            lambda: label_text().next_to(axes, DOWN, buff=0.2)
        )
        self.add(value_label)

        # ===================== Step 1: h = cos(x) =================================
        self.next_slide()

        # ===================== Step 2: h = cos(x + t) =============================
        new_formula = make_formula(r"h(x,t)=\cos(x+t)", highlight={"t": col_t})
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        omega.set_value(1.0)
        show_t = True
        self.play(t.animate.set_value(2 * PI), rate_func=linear, run_time=4.0)
        self.next_slide()

        # ===================== Step 3: h = A cos(x + t) ===========================
        new_formula = make_formula(
            r"h(x,t)=A\cos(x+t)", highlight={"A": col_A, "t": col_t}
        )
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        self.play(t.animate.set_value(0.0), run_time=0.3)
        show_A = True
        self.play(
            A.animate.set_value(2.0), rate_func=there_and_back, run_time=4.0
        )
        self.next_slide()

        # ===================== Step 4: h = A cos(kx + t) ==========================
        new_formula = make_formula(
            r"h(x,t)=A\cos(kx+t)",
            highlight={"A": col_A, "k": col_k, "t": col_t},
        )
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

        self.play(
            A.animate.set_value(1.0), t.animate.set_value(0.0), run_time=0.3
        )
        show_k = True
        self.play(
            k.animate.set_value(10.0), rate_func=there_and_back, run_time=5.0
        )
        self.next_slide()

        # ===================== Step 5: h = A cos(kx + omega t) ====================
        new_formula = make_formula(
            r"h(x,t)=A\cos(kx+\omega t)",
            highlight={
                "A": col_A,
                "k": col_k,
                r"\omega": col_omega,
                "t": col_t,
            },
        )
        _lock_left(new_formula)
        self.play(ReplacementTransform(formula, new_formula))
        formula = new_formula
        self.wait(0.3)
        self.next_slide()

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
        self.next_slide()

        # --- End of slide --------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()

    def slide_11(self):
        """
        Methode de Tessendorf: one curve per row.

        Minimal changes:
          - Color the TOP index (N) by selecting the MathTex part that matches the
            string of N and has the highest y (superscript), avoiding the bottom i=0.
          - Move the sigma label from RIGHT to BELOW using generate_target + MoveToTarget
            to avoid any teleport/snap-back due to grouping.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Méthode de Tessendorf")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area -------------------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom

        # --- Subtitle ----------------------------------------------------------
        self.start_body()
        subtitle = Text(
            '"Généralisation" des vagues d\'Airy :',
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        subtitle.next_to(
            self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
        )
        dx_sub = (
            bar_rect.get_left()[0] + self.DEFAULT_PAD
        ) - subtitle.get_left()[0]
        subtitle.shift(RIGHT * dx_sub)
        self.add(subtitle)

        # --- Layout (two rows, no axes) ---------------------------------------
        row_gap = 0.55
        plot_w = min(area_w * 0.55, 8.8)
        plot_h = min((area_h - 1.6) * 0.35, 2.2)

        row1_y = y_top - 0.95 - plot_h / 2.0
        row2_y = row1_y - plot_h - row_gap
        plot_x = x_left + 0.9 + plot_w / 2.0

        # Helper: draw a smooth curve from sampled points (no axes)
        def make_function_curve(center, width, height, func):
            x_min, x_max = -2.0 * np.pi, 2.0 * np.pi
            n = 300
            X = np.linspace(x_min, x_max, n)
            sx = width / (x_max - x_min)
            y_vis = 4.0
            sy = (height / 2.0) / y_vis

            path = VMobject()
            pts = []
            for x in X:
                y = float(func(x))
                px = (x - x_min) * sx - width / 2.0
                py = np.clip(y, -y_vis, y_vis) * sy
                pts.append([center[0] + px, center[1] + py, 0.0])
            path.set_points_smoothly(pts)
            path.set_stroke(color=pc.blueGreen, width=4)
            return path

        # ===================== Row 1: ONE Airy wave curve ======================
        A1 = ValueTracker(0.7)
        k1 = ValueTracker(1.5)

        def airy_y(x):
            return A1.get_value() * np.cos(k1.get_value() * x)

        curve1 = always_redraw(
            lambda: make_function_curve(
                center=np.array([plot_x, row1_y, 0.0]),
                width=plot_w,
                height=plot_h,
                func=airy_y,
            )
        )

        f1_initial = MathTex(
            r"h_A(x,t) = 0.7\cos\!\left(1.5\,x + \omega t\right)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
        )
        f1_initial.next_to(curve1, RIGHT, buff=0.35, aligned_edge=UP)

        self.add(curve1, f1_initial)

        # ===================== Row 2: ONE sum curve ============================
        row2_anchor = Dot(
            [plot_x, row2_y, 0.0],
            radius=0.001,
            fill_opacity=0.0,
            stroke_opacity=0.0,
        )
        row2_scale = ValueTracker(1.0)
        self.add(row2_anchor)

        components = [(3.0, 1.5)]  # (A, k) initial

        def sum_y_up_to(m, x):
            s = 0.0
            m_int = int(max(0, min(m, len(components))))
            for i in range(m_int):
                A, k = components[i]
                s += A * np.cos(k * x)
            return s

        n_comp = ValueTracker(len(components))  # number of components included

        curve_sum = always_redraw(
            lambda: make_function_curve(
                center=row2_anchor.get_center(),
                width=plot_w * row2_scale.get_value(),
                height=plot_h * row2_scale.get_value(),
                func=lambda x: sum_y_up_to(
                    int(np.floor(n_comp.get_value())), x
                ),
            )
        )

        f2 = MathTex(
            r"h_T(x,t) = 0.7\cos\!\left(1.5\,x + \omega t\right)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
        )
        f2.next_to(curve_sum, RIGHT, buff=0.35, aligned_edge=UP)

        self.add(curve_sum, f2)

        # ----------------------------------------------------------------------
        self.next_slide()

        # Row 1: same curve, new params
        f1_new = MathTex(
            r"h_A(x,t) = 0.8\cos\!\left(0.9\,x + \omega t\right)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
        )
        f1_new.next_to(curve1, RIGHT, buff=0.35, aligned_edge=UP)

        self.play(
            A1.animate.set_value(0.8),
            k1.animate.set_value(0.9),
            ReplacementTransform(f1_initial, f1_new),
            run_time=0.7,
        )

        # ----------------------------------------------------------------------
        self.next_slide()

        # Symbolize addition: ghost flies and fades to row2
        ghost = f1_initial.copy().set_opacity(0.85)
        ghost.move_to(f1_new.get_center())
        self.add(ghost)
        self.play(
            ghost.animate.move_to(f2.get_center()).set_opacity(0.15),
            run_time=0.6,
        )

        # Two-line explicit sum to stay in bounds
        f2_sum = MathTex(
            r"h_T(x,t) = 0.7\cos\!\left(1.5\,x + \omega t\right)"
            r" \\ + 0.8\cos\!\left(0.9\,x + \omega t\right)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
        )
        f2_sum.next_to(curve_sum, RIGHT, buff=0.35, aligned_edge=UP)

        components.append((0.7, 1.5))
        n_comp.set_value(len(components))

        self.play(
            ReplacementTransform(f2, f2_sum), FadeOut(ghost), run_time=0.6
        )

        # ----------------------------------------------------------------------
        self.next_slide()

        # Remove Row 1; center and enlarge Row 2
        self.play(FadeOut(VGroup(curve1, f1_new)), run_time=0.4)

        target_center_y = (y_top + y_bottom) * 0.5 + 0.2
        self.play(
            AnimationGroup(
                row2_anchor.animate.move_to([0.0, target_center_y, 0.0]),
                row2_scale.animate.set_value(1.15),
                lag_ratio=0.0,
            ),
            run_time=0.5,
        )

        # --- Sigma label: build once, then move RIGHT -> BELOW and keep N colored ---
        def build_sigma(n_val: int) -> MathTex:
            """
            Build MathTex and color ONLY the top index 'N' (numeric) by:
              - selecting parts that match the string of N,
              - keeping the one with the highest y (superscript),
              - coloring it pc.uclaGold.
            """
            n_txt = str(int(max(0, n_val)))
            m = MathTex(
                r"h_T(x,t) = ",
                r"\sum",
                r"_{i=0}",
                r"^{",
                n_txt,
                r"} A_i\cos\!\left(k_i x - \omega t\right)",
                color=BLACK,
                font_size=self.BODY_FONT_SIZE + 6,
            )
            # m[1].set_color(pc.blueGreen)
            return m

        # Create sigma at RIGHT of the curve (replace the two-line sum)
        sigma = build_sigma(int(n_comp.get_value()))
        sigma.next_to(curve_sum, RIGHT, buff=0.35, aligned_edge=UP)
        self.play(ReplacementTransform(f2_sum, sigma), run_time=0.5)

        # Move sigma smoothly BELOW the curve (no teleport)
        sigma.generate_target()
        sigma.target.next_to(curve_sum, DOWN, buff=0.25)
        self.play(MoveToTarget(sigma), run_time=0.35)

        # Live update of N while preserving the current position
        def sigma_updater(mobj: Mobject) -> None:
            pos = mobj.get_center()
            new = build_sigma(int(np.floor(n_comp.get_value())))
            new.move_to(pos)
            mobj.become(new)

        sigma.add_updater(sigma_updater)

        # Progressive addition in one clip; curve updates via n_comp
        rng = np.random.default_rng(42)
        extra = []
        add_count = 20
        for _ in range(add_count):
            A_rand = float(rng.uniform(0.01, 0.1))
            k_rand = float(rng.uniform(0.1, 30.0))
            extra.append((A_rand, k_rand))
        components.extend(extra)

        # Avoid reversing issues on this slide
        self.skip_reversing = True

        # Drive the curve and sigma 'N' together
        self.play(
            n_comp.animate.set_value(len(components)),
            rate_func=linear,
            run_time=3.0,
        )

        # Cleanup updater before ending the slide
        sigma.remove_updater(sigma_updater)

        # --- End of slide ------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()

    def slide_12(self):
        """
        Slide 12: Ocean spectra.
        - Top bar "Spectres d'océans"
        - Intro sentence with inline LaTeX
        - Two bullet points mixing text and LaTeX
        - Then a central "bow-tie" shape
        - Then LaTeX labels on the left (U_10, F, theta)
        - Then an animation where labels move into the shape and disappear,
          while A_i appears on the right and slides a bit to the right.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Spectres d'océans")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area below bar --------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        numberplane = NumberPlane(color=BLACK)
        self.add(numberplane)
        # Left anchor to align body content with the bar
        anchor_x = x_left + self.DEFAULT_PAD

        # --- Intro sentence (Tex = text + math) -------------------------------
        self.start_body()
        intro = Tex(
            r"Comment calculer les $k_i$ et $A_i$ ?",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        intro.next_to(
            self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
        )
        dx = anchor_x - intro.get_left()[0]
        intro.shift(RIGHT * dx)
        self.add(intro)

        # --- Bullet points with LaTeX symbols --------------------------------
        # Helper to place a bullet row (dot + [math + text])
        def bullet_row(math_tex: str, tail_text: str) -> VGroup:
            dot = Dot(radius=0.05, color=pc.blueGreen)
            head = MathTex(
                math_tex, color=BLACK, font_size=self.BODY_FONT_SIZE
            )
            tail = Text(tail_text, color=BLACK, font_size=self.BODY_FONT_SIZE)
            line = VGroup(head, tail).arrange(
                RIGHT, buff=0.18, aligned_edge=DOWN
            )
            row = VGroup(dot, line).arrange(
                RIGHT, buff=0.25, aligned_edge=DOWN
            )
            return row

        b1 = bullet_row(r"k_i", "est echantillonné sur un intervalle")
        b2 = bullet_row(r"A_i", "est défini par un spectre d'océan")

        # Stack bullets under the intro, left-aligned to the same anchor
        bullets = VGroup(b1, b2).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        bullets.next_to(intro, DOWN, buff=0.28, aligned_edge=LEFT)
        dx_b = anchor_x - bullets.get_left()[0]
        bullets.shift(RIGHT * dx_b)
        self.add(bullets)

        # Wait for user
        self.next_slide()

        # --- Central "bow-tie" shape -----------------------------------------
        # Coordinates chosen to resemble the provided figure.
        left_tri = Polygon(
            [-2.0, -4, 0.0],
            [-1.0, -3.5, 0.0],
            [1.0, -3.5, 0.0],
            [2.0, -4, 0.0],
            [2.0, -2, 0.0],
            [1.0, -2.5, 0.0],
            [-1.0, -2.5, 0.0],
            [-2.0, -2, 0.0],
            fill_color=pc.blueGreen,
            fill_opacity=0.95,
            stroke_opacity=0.0,
        )
        shape = VGroup(left_tri)
        # Center the shape roughly in the middle of the free area
        cy = (y_top + y_bottom) * 0.5
        shape.move_to([0.0, cy, 0.0])
        self.play(FadeIn(shape, run_time=0.5))

        # Wait for user
        self.next_slide()

        # --- Labels on the left: U_10, F, theta --------------------------------
        left_x = shape.get_left()[0] - 1.0
        y_span = shape.height
        y_top_lbl = cy + y_span * 0.30
        y_mid_lbl = cy + y_span * 0.00
        y_bot_lbl = cy - y_span * 0.30

        lbl_u10 = MathTex(
            r"U_{10}", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
        )
        lbl_f = MathTex(r"F", color=BLACK, font_size=self.BODY_FONT_SIZE + 6)
        lbl_th = MathTex(
            r"\theta", color=BLACK, font_size=self.BODY_FONT_SIZE + 6
        )

        lbl_u10.move_to([left_x, y_mid_lbl, 0.0])
        lbl_f.move_to([left_x, y_top_lbl, 0.0])
        lbl_th.move_to([left_x, y_bot_lbl, 0.0])

        labels_left = VGroup(lbl_f, lbl_u10, lbl_th)
        self.play(FadeIn(labels_left, run_time=0.4))

        # Wait for user
        self.next_slide()

        # --- Flow into the shape, disappear, and show A_i on the right ----------
        # Target just inside the left edge of the bow-tie.
        target_x_inside = (
            left_tri.get_vertices()[0][0] - 0.4
        )  # near the center tip
        flow_targets = [
            np.array([target_x_inside, y_top_lbl, 0.0]),
            np.array([target_x_inside, y_mid_lbl, 0.0]),
            np.array([target_x_inside, y_bot_lbl, 0.0]),
        ]

        self.play(
            lbl_f.animate.move_to(flow_targets[0]),
            lbl_u10.animate.move_to(flow_targets[1]),
            lbl_th.animate.move_to(flow_targets[2]),
            run_time=0.8,
        )
        # Disappear as if absorbed by the shape
        self.play(FadeOut(labels_left, run_time=0.35))

        # A_i appears on the right and slides slightly to the right
        ai_x = shape.get_right()[0] + 0.4
        ai = MathTex(r"A_i", color=BLACK, font_size=self.BODY_FONT_SIZE + 10)
        ai.move_to([ai_x, cy, 0.0])
        self.play(FadeIn(ai, run_time=0.3))
        self.play(ai.animate.shift(RIGHT * 1.0), run_time=0.4)

        # End slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_13(self):
        """
        Transformée de Fourier rapide (IFFT) slide:
        - Top bar "Transformée de Fourier rapide"
        - Two body lines under the bar (same, larger font size; LaTeX for h_T)
        - Two-column area below:
            * LEFT  column: squared image 'Figures/fourier_space.png' with a pc.blueGreen
              square border and caption "Espace de Fourier ($h(k,t)$)"
            * Wait for user: draw arrow from RIGHT EDGE of left image toward the **left edge**
              of the right column; label above: IFFT O(N log N)
            * RIGHT column: squared image 'Figures/real_space.jpeg' with a pc.blueGreen
              square border and caption "Espace réel ($h(x,t)$)"
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Transformée de Fourier rapide")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area below the bar ----------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6

        area_w = x_right - x_left
        area_h = y_top - y_bottom
        anchor_x = x_left + self.DEFAULT_PAD

        # --- Body text (two lines, same LARGER font size; LaTeX for h_T) ------
        self.start_body()
        fs_body_big = (
            self.BODY_FONT_SIZE + 6
        )  # increased, equal for both lines

        line1 = Tex(
            r"Le calcul de la somme $h_T(x,t)$ est coûteux, donc on va",
            color=BLACK,
            font_size=fs_body_big,
        )
        line1.next_to(
            self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
        )
        dx1 = anchor_x - line1.get_left()[0]
        line1.shift(RIGHT * dx1)

        line2 = Tex(
            r"utiliser des transformée de Fourier rapide inverse (IFFT)",
            color=BLACK,
            font_size=fs_body_big,
        )
        line2.next_to(line1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        dx2 = anchor_x - line2.get_left()[0]
        line2.shift(RIGHT * dx2)

        self.add(line1, line2)

        # --- Two-column layout (below body text) ------------------------------
        content_top_y = line2.get_bottom()[1] - 0.35
        content_bottom_y = y_bottom + 0.2
        content_h = max(2.0, content_top_y - content_bottom_y)
        content_center_y = (content_top_y + content_bottom_y) * 0.5

        col_gap = area_w * 0.08
        col_w = (area_w - col_gap) * 0.5
        cx_left_col = x_left + col_w * 0.5  # LEFT column center (Fourier)
        cx_right_col = x_right - col_w * 0.5  # RIGHT column center (Real)

        caption_h = 0.35
        max_side_w = col_w * 0.82
        max_side_h = content_h * 0.82 - caption_h
        side = max(1.2, min(max_side_w, max_side_h))

        # --- LEFT column: Fourier space ---------------------------------------
        fourier_img = ImageMobject("Figures/fourier_space.png")
        scale_f = min(side / fourier_img.width, side / fourier_img.height, 1.0)
        fourier_img.scale(scale_f)
        fourier_img.move_to([cx_left_col, content_center_y + 0.10, 0.0])

        border_f = Square(side_length=side, color=pc.blueGreen, stroke_width=6)
        border_f.move_to(fourier_img.get_center())

        cap_f = Tex(
            r"Espace de Fourier ($h(k,t)$)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        cap_f.next_to(fourier_img, DOWN, buff=0.18)

        self.add(border_f, fourier_img, cap_f)

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- Arrow to the LEFT EDGE of the right image ------------------------
        # We'll end the arrow slightly before the expected left edge of the right square.
        gap_arrow_end = 0.12
        # Compute the intended left-edge x of the right square if it were centered on cx_right_col:
        intended_left_edge_x = cx_right_col - side / 2.0
        # Arrow endpoints:
        start = border_f.get_right() + np.array([0.15, 0.0, 0.0])
        end = np.array(
            [
                intended_left_edge_x - gap_arrow_end,
                fourier_img.get_center()[1],
                0.0,
            ]
        )

        arrow = Arrow(
            start=start,
            end=end,
            buff=0.0,  # we manage the gap ourselves
            stroke_color=pc.blueGreen,
            stroke_width=6,
            tip_length=0.16,
        )
        arrow_label = MathTex(
            r"IFFT~\mathcal{O}(N\log(N))",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 2,
        )
        arrow_label.next_to(arrow, UP, buff=0.18)

        self.play(Create(arrow, run_time=0.7))
        self.play(FadeIn(arrow_label, run_time=0.3))

        # --- RIGHT column: Real space -----------------------------------------
        real_img = ImageMobject("Figures/real_space.jpeg")
        scale_r = min(side / real_img.width, side / real_img.height, 1.0)
        real_img.scale(scale_r)

        # Place the real image so that its LEFT EDGE is just to the right of the arrow end.
        left_edge_x = end[0] + gap_arrow_end
        center_x = left_edge_x + side / 2.0
        real_center = np.array([center_x, fourier_img.get_center()[1], 0.0])
        real_img.move_to(real_center)

        border_r = Square(side_length=side, color=pc.blueGreen, stroke_width=6)
        border_r.move_to(real_img.get_center())

        cap_r = Tex(
            r"Espace réel ($h(x,t)$)",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        cap_r.next_to(real_img, DOWN, buff=0.18)

        self.play(FadeIn(border_r, real_img, cap_r, run_time=0.5))

        # --- End slide ---------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()

    def slide_14(self):
        """
        Slide 14 : Vitesse de l'océan
        """
        # --- Top bar ---------------------------------------------------------
        bar = self._top_bar("Vitesse de l'océan")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Usable area below the bar -------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        anchor_x = x_left + self.DEFAULT_PAD

        # ===================== Body text ====================================
        self.start_body()
        fs = self.BODY_FONT_SIZE + 3  # unified font size for both lines

        line1 = Tex(
            r"La vitesse de l'eau en tout points de l'espace est calculée avec le même principe",
            color=BLACK,
            font_size=fs,
        )
        line1.next_to(self._current_bar, DOWN, aligned_edge=LEFT)
        dx = anchor_x - line1.get_left()[0]
        line1.shift(RIGHT * dx)
        self.add(line1)

        line2 = Tex(
            r"de transformation d'espace de Fourier à espace réel : "
            r"$\tilde{v}(k,t,y)=E(k,y)\,\phi(k,t)$",
            color=BLACK,
            font_size=fs,
        )
        line2.next_to(line1, DOWN, aligned_edge=LEFT)
        dx2 = anchor_x - line2.get_left()[0]
        line2.shift(RIGHT * dx2)
        self.add(line2)

        # ===================== Axis & Layout =================================
        # Tweakables to nudge the axes where you want
        AXIS_RIGHT_SHIFT = 0.60   # move vertical axis further to the right
        AXIS_DOWN_SHIFT  = 0.30   # move the whole axes block slightly downward

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
            end=[x_end,       axis_top_y, 0],
            buff=0,
            stroke_width=6,
            color=BLACK,
        )

        axis_group = VGroup(x_axis, y_axis)
        self.add(axis_group)

        # Wave along the horizontal axis level
        wave = ParametricFunction(
            lambda t: np.array([
                axis_left_x + t,
                axis_top_y - 0.30 * np.sin(1.4 * t),
                0.0,
            ]),
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
        LABEL_GAP = 0.28
        MIN_LEFT = x_left + 0.15

        for yv, d in zip(y_vals, depths):
            # dotted line from axis to right
            ln = DashedLine(
                start=[axis_left_x, yv, 0],
                end=[x_end,       yv, 0],
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
                *[FadeIn(m) for m in (dotted_lines + labels)],
                lag_ratio=0.08,
            )
        )

        # ===================== Wait for user =================================
        self.next_slide()

        # ===================== Interpolation line ============================
        mid_y = 0.5 * (y_vals[1] + y_vals[2])
        interp_line = DashedLine(
            start=[axis_left_x, mid_y, 0],
            end=[x_end,       mid_y, 0],
            dash_length=0.08,
            color=BLACK,
        )
        interp_caption = Text(
            "Interpolation Exp",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        ).next_to(interp_line, UP, buff=0.32)

        self.add(interp_line, interp_caption)

        # Highlight the line itself (no endpoint movement)
        self.play(interp_line.animate.set_stroke(color=pc.blueGreen, width=8), run_time=0.8)
        self.play(interp_line.animate.set_stroke(color=BLACK, width=6), run_time=0.8)

        # ===================== End slide ====================================
        self.pause()
        self.clear()
        self.next_slide()

    def slide_15(self):
        """
        Couplage avec des solides.
        Steps:
          1) Show animated water surface: 0.1*cos(0.7*x + t).
          2) Drop a boat polygon that falls through and exits.
          3) Drop a second boat that floats on the surface.
          4) Drop a third boat that floats while the surface shows only w(x,t).
        Boats are cleaned before the next one is spawned.
        """
        # --- Title bar ---
        bar = self._top_bar("Couplage avec des solides")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Layout area ---
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom
        y_center = (y_top + y_bottom) * 0.5

        # --- Subtitle ---
        self.start_body()
        subtitle = Text(
            "La méthode de Tessendorf ne permet pas le couplage avec des solides",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        subtitle.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        dx_sub = (bar_rect.get_left()[0] + self.DEFAULT_PAD) - subtitle.get_left()[0]
        subtitle.shift(RIGHT * dx_sub)
        self.add(subtitle)

        # --- Plot area (no axes) ---
        plot_w = min(area_w * 0.88, 12.0)
        plot_h = min(area_h * 0.42, 3.2)
        plot_center = np.array([0.0, y_center, 0.0])
        x_min, x_max = -2.0 * np.pi, 2.0 * np.pi
        x_span = x_max - x_min
        sample_n = 400
        y_vis = 1.0
        sx = plot_w / x_span
        sy = (plot_h / 2.0) / y_vis

        # --- Time trackers ---
        t = ValueTracker(0.0)
        include_w = ValueTracker(0.0)

        # --- Try to load w(x,t); fallback if not available ---
        w_data = {"H": None, "x": None, "t": None, "T": None}

        def try_prepare_wave_solution():
            try:
                from wave_equation_1d import simulate_wave_1d_dirichlet  # type: ignore
                H, x_arr, t_arr = simulate_wave_1d_dirichlet(
                    L=2.0, c=1.0, W=0.6, A=0.25, sigma=0.12, nx=801, T=8.0, dt=0.005, t0=0.0
                )
                w_data["H"] = H
                w_data["x"] = x_arr
                w_data["t"] = t_arr
                w_data["T"] = float(t_arr[-1] - t_arr[0]) if len(t_arr) > 1 else 1.0
            except Exception:
                w_data["H"] = None

        try_prepare_wave_solution()

        def w_fallback(x_val: float, t_val: float) -> float:
            return 0.08 * np.cos(2.0 * x_val - 1.2 * t_val)

        def w_from_data(x_val: float, t_val: float) -> float:
            H = w_data["H"]
            x_arr = w_data["x"]
            t_arr = w_data["t"]
            Ttot = w_data["T"]
            if H is None or x_arr is None or t_arr is None or Ttot is None or Ttot <= 0:
                return w_fallback(x_val, t_val)

            t0 = t_arr[0]
            tau = (t_val - t0) % Ttot + t0
            it = int(np.clip(np.searchsorted(t_arr, tau), 1, len(t_arr) - 1))
            t1, t2 = t_arr[it - 1], t_arr[it]
            a = 0.0 if t2 == t1 else (tau - t1) / (t2 - t1)
            h1 = np.interp(x_val, x_arr, H[it - 1])
            h2 = np.interp(x_val, x_arr, H[it])
            return float((1.0 - a) * h1 + a * h2)

        # --- FIX #2: Water is ONLY cosine unless include_w == 1
        def water_y(x_val: float) -> float:
            if include_w.get_value() >= 1.0:
                return w_from_data(x_val, t.get_value())
            else:
                return 0.1 * np.cos(0.7 * x_val + t.get_value())

        def make_water_curve():
            X = np.linspace(x_min, x_max, sample_n)
            pts = []
            for xv in X:
                yv = np.clip(water_y(xv), -y_vis, y_vis)
                px = (xv - x_min) * sx - plot_w / 2.0
                py = yv * sy
                pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
            path = VMobject()
            path.set_points_smoothly(pts)
            path.set_stroke(color=pc.blueGreen, width=4)
            return path

        water_curve = always_redraw(make_water_curve)
        self.add(water_curve)

        # FIX #1 - Fully linear evolution
        self.play(
            t.animate.increment_value(2.0 * np.pi),
            rate_func=linear,
            run_time=4.0,
        )

        # --------------------------------------------------------------------------
        self.next_slide()

        # --- Boat def ---
        boat_shape = [
            [-1.0,  0.0, 0.0],
            [ 1.0,  0.0, 0.0],
            [ 2.0,  1.0, 0.0],
            [ 0.5,  1.0, 0.0],
            [ 0.0,  1.5, 0.0],
            [-0.5,  1.0, 0.0],
            [-2.0,  1.0, 0.0],
        ]

        def create_boat(y_offset: float) -> Polygon:
            poly = Polygon(*boat_shape, color=pc.uclaGold, stroke_width=4)
            poly.set_fill(pc.uclaGold, opacity=1.0)
            poly.move_to([0.0, y_offset, 0.0])
            self.add_foreground_mobject(poly)
            return poly

        def destroy_boat(poly: Mobject) -> None:
            self.play(FadeOut(poly, run_time=0.15))
            try:
                self.remove_foreground_mobject(poly)
            except Exception:
                pass
            self.remove(poly)

        # --- DROP 1 ---
        start_y = y_center + 2.2
        boat = create_boat(start_y)
        self.play(
            boat.animate.move_to([0.0, y_bottom - 1.5, 0.0]),
            rate_func=linear,
            run_time=2.5,
        )
        destroy_boat(boat)

        # --------------------------------------------------------------------------
        self.next_slide()

        # --- DROP 2 (float) ---
        boat2 = create_boat(start_y)

        def water_y_at_x0() -> float:
            return water_y(0.0)

        self.play(
            boat2.animate.move_to([0.0, water_y_at_x0(), 0.0]),
            rate_func=linear,
            run_time=0.8,
        )

        amp = 0.18
        omega_b = 1.6
        t_local = ValueTracker(0.0)

        def boat_float_updater(mob: Mobject):
            y_osc = amp * np.sin(omega_b * t_local.get_value())
            mob.move_to([0.0, y_osc, 0.0])

        boat2.add_updater(boat_float_updater)

        self.play(
            AnimationGroup(
                t.animate.increment_value(2.0 * np.pi),
                t_local.animate.increment_value(2.0 * np.pi),
                lag_ratio=0.0,
            ),
            rate_func=linear,
            run_time=4.0,
        )
        boat2.remove_updater(boat_float_updater)
        destroy_boat(boat2)

        # --------------------------------------------------------------------------
        self.next_slide()

        # --- DROP 3 (float + w(x,t) only) ---
        boat3 = create_boat(start_y)
        self.play(
            boat3.animate.move_to([0.0, water_y_at_x0(), 0.0]),
            rate_func=linear,
            run_time=0.8,
        )

        include_w.set_value(1.0)

        t_local2 = ValueTracker(0.0)

        def boat_float_updater2(mob: Mobject):
            y_osc = amp * np.sin(omega_b * t_local2.get_value())
            mob.move_to([0.0, y_osc, 0.0])

        boat3.add_updater(boat_float_updater2)

        self.play(
            AnimationGroup(
                t.animate.increment_value(2.0 * np.pi),
                t_local2.animate.increment_value(2.0 * np.pi),
                lag_ratio=0.0,
            ),
            rate_func=linear,
            run_time=4.0,
        )
        boat3.remove_updater(boat_float_updater2)
        destroy_boat(boat3)

        # --- End of slide ---
        self.pause()
        self.clear()
        self.next_slide()

    def slide_16(self):
        """
        Slide 16: Action du fluide sur le solide.
        Minimal fix: group (title, equation) pairs and stack the two pairs vertically
        in each column so that item 2 is beneath 1 (and 4 beneath 3). Remove empty
        Tex spacers to avoid arrange() quirks. All other behavior unchanged.
        """
        # --- Top bar ---
        bar = self._top_bar("Action du fluide sur le solide")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Usable area below the bar ----
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        x_center = 0.0
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left

        # ========= 3 intro lines (Tex) =========
        self.start_body()
        local_top_buff = 0.38  # margin below the bar
        l1 = Tex(
            r"L'action du fluide sur le solide est approximée comme",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        l1.next_to(self._current_bar, DOWN, buff=local_top_buff, aligned_edge=LEFT)
        l1.shift(RIGHT * ((x_left + self.DEFAULT_PAD) - l1.get_left()[0]))

        l2 = Tex(
            r"des forces appliquées sur le maillage du solide.",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        l2.shift(RIGHT * ((x_left + self.DEFAULT_PAD) - l2.get_left()[0]))

        l3 = Tex(
            r"Découpage en 4 forces :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        l3.next_to(l2, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        l3.shift(RIGHT * ((x_left + self.DEFAULT_PAD) - l3.get_left()[0]))

        intro_group = VGroup(l1, l2, l3)
        self.play(FadeIn(intro_group, run_time=0.35))

        # ========= 4 forces layout (Tex only) =========
        # Left column --------------------------------------------------------------
        title1 = Tex(r"1.\; Gravité :", color=BLACK, font_size=self.BODY_FONT_SIZE)
        title1.set_color_by_tex("Gravité", pc.apple)
        eq1 = MathTex(
            r"\mathbf{F}_g = -m\,\mathbf{g}",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 6,
            tex_to_color_map={r"\mathbf{F}_g": pc.apple},
        )
        left_block1 = VGroup(title1, eq1).arrange(
            DOWN, buff=0.22, center=False, aligned_edge=LEFT
        )

        title2 = Tex(r"2.\; Poussée d'Archimède :", color=BLACK, font_size=self.BODY_FONT_SIZE)
        title2.set_color_by_tex("Poussée", pc.uclaGold)
        eq2 = MathTex(
            r"\mathbf{F}_b = V_w\,\rho_w\,\mathbf{g}",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 6,
            tex_to_color_map={r"\mathbf{F}_b": pc.uclaGold},
        )
        left_block2 = VGroup(title2, eq2).arrange(
            DOWN, buff=0.22, center=False, aligned_edge=LEFT
        )

        left_col = VGroup(left_block1, left_block2).arrange(
            DOWN, buff=0.40, center=False, aligned_edge=LEFT
        )

        # Right column -------------------------------------------------------------
        title3 = Tex(r"3.\; Traînée eau :", color=BLACK, font_size=self.BODY_FONT_SIZE)
        title3.set_color_by_tex("Traînée", pc.heliotropeMagenta)
        eq3 = MathTex(
            r"\mathbf{F}_w"
            r" = -\tfrac{1}{2}\,C_d^w\,\rho_w\,A_i^{\perp}\,"
            r"\|\mathbf{v}^w_{i,\mathrm{rel}}\|\,\mathbf{v}^w_{i,\mathrm{rel}}",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE - 2,
            tex_to_color_map={r"\mathbf{F}_w": pc.heliotropeMagenta},
        )
        right_block1 = VGroup(title3, eq3).arrange(
            DOWN, buff=0.22, center=False, aligned_edge=LEFT
        )

        title4 = Tex(r"4.\; Traînée air :", color=BLACK, font_size=self.BODY_FONT_SIZE)
        title4.set_color_by_tex("Traînée", pc.jellyBean)
        eq4 = MathTex(
            r"\mathbf{F}_a"
            r" = -\tfrac{1}{2}\,C_d^a\,\rho_a\,A_i^{\perp}\,"
            r"\|\mathbf{v}^a_{i,\mathrm{rel}}\|\,\mathbf{v}^a_{i,\mathrm{rel}}",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE - 2,
            tex_to_color_map={r"\mathbf{F}_a": pc.jellyBean},
        )
        right_block2 = VGroup(title4, eq4).arrange(
            DOWN, buff=0.22, center=False, aligned_edge=LEFT
        )

        right_col = VGroup(right_block1, right_block2).arrange(
            DOWN, buff=0.40, center=False, aligned_edge=LEFT
        )

        # Put columns side by side and center them in the remaining area
        col_gap = 1.2
        forces_group = VGroup(left_col, right_col).arrange(
            RIGHT, buff=col_gap, aligned_edge=UP
        )

        # --- Center in the remaining space below l3 (both horizontally & vertically)
        rem_top = l3.get_bottom()[1] - 0.40
        rem_bot = y_bottom + 0.60
        rem_h = max(1.5, rem_top - rem_bot)
        rem_y_center = (rem_top + rem_bot) * 0.5

        forces_group.move_to([x_center, rem_y_center, 0.0])
        self.play(FadeIn(forces_group, run_time=0.45))

        # ========= Wait, then remove 3 lines and re-center forces higher =========
        self.next_slide()
        self.play(FadeOut(intro_group, run_time=0.25))

        # Recompute the available area when the intro text is gone (use almost full body)
        new_top = y_top
        new_bot = y_bottom + 0.60
        new_center_y = (new_top + new_bot) * 0.5

        self.play(forces_group.animate.move_to([x_center, new_center_y, 0.0]), run_time=0.35)

        # ========= Animated water + centered boat beneath the forces =========
        gap_below_forces = 0.35
        min_sea_height = 2.2
        sea_top = min(left_col.get_bottom()[1], right_col.get_bottom()[1]) - gap_below_forces
        sea_bot = y_bottom + 0.60
        sea_h = sea_top - sea_bot
        if sea_h < min_sea_height:
            sea_bot = sea_top - min_sea_height
            sea_h = min_sea_height

        # Choose a safe wave baseline inside the sea box
        y0 = sea_bot + 0.55 * sea_h

        t_tracker = ValueTracker(0.0)
        x_min = x_left + 0.5
        x_max = x_right - 0.5
        amp = 0.10
        k = 0.7

        def make_water():
            xs = np.linspace(x_min, x_max, 600)
            ys = y0 + amp * np.cos(k * xs + t_tracker.get_value())
            pts = np.column_stack([xs, ys, np.zeros_like(xs)])
            m = VMobject(stroke_color=pc.blueGreen, stroke_width=6)
            m.set_points_smoothly([*map(lambda p: np.array(p), pts)])
            m.set_z_index(1)  # under the boat
            return m

        water = always_redraw(make_water)
        self.add(water)
        self.play(t_tracker.animate.increment_value(2 * PI), rate_func=linear, run_time=2.6)

        # Centered boat polygon (foreground)
        boat_local = [
            [-1.0,  0.0, 0.0],
            [ 1.0,  0.0, 0.0],
            [ 2.0,  1.0, 0.0],
            [ 0.5,  1.0, 0.0],
            [ 0.0,  1.5, 0.0],
            [-0.5,  1.0, 0.0],
            [-2.0, 1.0, 0.0],
        ]
        boat = Polygon(
            *[np.array(p) for p in boat_local],
            fill_color=pc.uclaGold, fill_opacity=1.0,
            stroke_color=BLACK, stroke_width=3,
        )
        boat.scale(0.9)
        boat.move_to([0.0, y0 + 0.35, 0.0])  # slightly above the wave baseline
        boat.set_z_index(10)
        self.add(boat)
        self.add_foreground_mobject(boat)

        self.play(t_tracker.animate.increment_value(2 * PI), rate_func=linear, run_time=2.6)
        self.next_slide()

        # ========= Force arrows (foreground), colored as requested =========
        keel = boat.get_bottom()
        deck = boat.get_top()

        g_arrow = Arrow(
            start=[deck[0], deck[1] + 0.6, 0],
            end=[deck[0], deck[1] - 0.4, 0],
            color=pc.apple,
            stroke_width=6,
            tip_length=0.18,
        ).set_z_index(15)
        g_lbl = MathTex(r"\mathbf{F}_g", color=pc.apple, font_size=self.BODY_FONT_SIZE)\
            .next_to(g_arrow, UP, buff=0.10).set_z_index(15)

        b_arrow = Arrow(
            start=[keel[0], keel[1] - 0.6, 0],
            end=[keel[0], keel[1] + 0.45, 0],
            color=pc.uclaGold,
            stroke_width=6,
            tip_length=0.18,
        ).set_z_index(15)
        b_lbl = MathTex(r"\mathbf{F}_b", color=pc.uclaGold, font_size=self.BODY_FONT_SIZE)\
            .next_to(b_arrow, DOWN, buff=0.10).set_z_index(15)

        a_arrow = Arrow(
            start=[deck[0] + 1.2, deck[1] + 0.15, 0],
            end=[deck[0] - 0.3, deck[1] + 0.15, 0],
            color=pc.jellyBean,
            stroke_width=6,
            tip_length=0.18,
        ).set_z_index(15)
        a_lbl = MathTex(r"\mathbf{F}_a", color=pc.jellyBean, font_size=self.BODY_FONT_SIZE)\
            .next_to(a_arrow, UP, buff=0.10).set_z_index(15)

        w_arrow = Arrow(
            start=[keel[0] - 1.0, keel[1] - 0.15, 0],
            end=[keel[0] + 0.6, keel[1] - 0.15, 0],
            color=pc.heliotropeMagenta,
            stroke_width=6,
            tip_length=0.18,
        ).set_z_index(15)
        w_lbl = MathTex(r"\mathbf{F}_w", color=pc.heliotropeMagenta, font_size=self.BODY_FONT_SIZE)\
            .next_to(w_arrow, DOWN, buff=0.10).set_z_index(15)

        self.add_foreground_mobjects(
            g_arrow, b_arrow, a_arrow, w_arrow, g_lbl, b_lbl, a_lbl, w_lbl
        )
        self.play(
            LaggedStart(
                FadeIn(g_arrow), FadeIn(g_lbl),
                FadeIn(b_arrow), FadeIn(b_lbl),
                FadeIn(a_arrow), FadeIn(a_lbl),
                FadeIn(w_arrow), FadeIn(w_lbl),
                lag_ratio=0.15, run_time=1.2
            )
        )

        # --- End slide ---
        self.pause()
        self.clear()
        self.next_slide()



    def slide_17(self):
        """
        Action du solide sur le fluide.
        Texte d'intro, EDP 2D (equation* + cases), schéma DF,
        puis variante amortie avec d^n. Mise en page ancrée à gauche,
        espacements renforcés et largeur des équations limitée pour éviter
        tout chevauchement.
        """
        # --- Barre de titre -------------------------------------------------------
        bar = self._top_bar("Action du solide sur le fluide")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Zone utile -----------------------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        anchor_x = x_left + self.DEFAULT_PAD  # ancre gauche stable

        # Utilitaires --------------------------------------------------------------
        def _lock_left_y(mob: Mobject, y_value: float) -> Mobject:
            dx = anchor_x - mob.get_left()[0]
            mob.shift(RIGHT * dx)
            mob.set_y(y_value)
            return mob

        def _shrink_to_width_if_needed(mob: Mobject, max_w: float) -> None:
            # Ne réduit que si l'objet dépasse la largeur cible
            if mob.width > max_w:
                mob.scale_to_fit_width(max_w)

        # --- Corps de texte (Tex) -------------------------------------------------
        self.start_body()

        line1 = Tex(
            "L'action du solide sur le fluide est approximée comme",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        line1_y = y_top - 0.42
        _lock_left_y(line1, line1_y)
        self.add(line1)

        line2 = Tex(
            "une simple « onde ». Pour la déterminer on résout l'équation d'onde 2D :",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        line2.next_to(line1, DOWN, buff=0.22, aligned_edge=LEFT)
        _lock_left_y(line2, line2.get_y())
        self.add(line2)

        # Attente utilisateur ------------------------------------------------------
        self.next_slide()

        # --- EDP 2D (equation* + cases) ------------------------------------------
        eq_pde = Tex(
            r"""
            \begin{equation*}
            \begin{cases}
                \Delta h(\mathbf{x},t)-\dfrac{1}{c^{2}}\dfrac{\partial^{2} h(\mathbf{x},t)}{\partial t^{2}}=0
                \quad \text{for} \quad \mathbf{x}\in Z\\[6pt]
                h(\mathbf{x},t)=0 \quad \text{for} \quad \mathbf{x}\in\partial Z
            \end{cases}
            \end{equation*}
            """,
            font_size=self.BODY_FONT_SIZE + 4,
            color=BLACK,
        )
        eq_pde.next_to(line2, DOWN, buff=0.32, aligned_edge=LEFT)
        _lock_left_y(eq_pde, eq_pde.get_y())
        _shrink_to_width_if_needed(eq_pde, area_w * 0.90)
        self.add(eq_pde)

        line3 = Tex(
            r"Où $Z$ est un domaine carré centré autour du solide.",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        line3.next_to(eq_pde, DOWN, buff=0.26, aligned_edge=LEFT)
        _lock_left_y(line3, line3.get_y())
        self.add(line3)

        line4 = Tex(
            r"On utilise la méthode des différences finies pour la résoudre.",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        line4.next_to(line3, DOWN, buff=0.18, aligned_edge=LEFT)
        _lock_left_y(line4, line4.get_y())
        self.add(line4)

        # Forcer la 2e phrase ("est discrétisé...") à passer LIGNE SUIVANTE
        line5 = Tex(
            r"Avec $\mathbf{x}=(i\cdot dx,\,j\cdot dx)$ et $t=dt\cdot n$, $Z$",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        line5.next_to(line4, DOWN, buff=0.16, aligned_edge=LEFT)
        _lock_left_y(line5, line5.get_y())
        self.add(line5)

        line6 = Tex(
            r"est discrétisé autour du solide :",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        # Important: toujours SOUS line5 (plus de placement à droite)
        line6.next_to(line5, DOWN, buff=0.08, aligned_edge=LEFT)
        _lock_left_y(line6, line6.get_y())
        self.add(line6)

        # --- Schéma DF initial ----------------------------------------------------
        eq_fd = Tex(
            r"""
            \begin{equation*}
            \begin{cases}
                h_{i,j}^{n+1} = a\left(h_{i+1,j}^n+h_{i-1,j}^n+h_{i,j+1}^n+h_{i,j-1}^n-4h_{i,j}^n\right)
                + 2h_{i,j}^n - h_{i,j}^{n-1} \quad \text{for} \quad \mathbf{x}\in Z \\[6pt]
                h_{i,j}^n = 0 \quad \text{for} \quad \mathbf{x}\in\partial Z
            \end{cases}
            \end{equation*}
            """,
            font_size=self.BODY_FONT_SIZE + 2,
            color=BLACK,
        )
        eq_fd.next_to(line6, DOWN, buff=0.26, aligned_edge=LEFT)
        _lock_left_y(eq_fd, eq_fd.get_y())
        _shrink_to_width_if_needed(eq_fd, area_w * 0.90)
        self.add(eq_fd)

        line_a = Tex(
            r"où $a=\dfrac{c^{2}dt^{2}}{dx^{2}}$",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        line_a.next_to(eq_fd, DOWN, buff=0.22, aligned_edge=LEFT)
        _lock_left_y(line_a, line_a.get_y())
        self.add(line_a)

        # Attente utilisateur ------------------------------------------------------
        self.next_slide()

        # --- Variante amortie: facteur d^n ----------------------------------------
        eq_fd_damped = Tex(
            r"""
            \begin{equation*}
            \begin{cases}
                h_{i,j}^{n+1} = d^{n}a\left(h_{i+1,j}^n+h_{i-1,j}^n+h_{i,j+1}^n+h_{i,j-1}^n-4h_{i,j}^n\right)
                + 2h_{i,j}^n - h_{i,j}^{n-1} \quad \text{for} \quad \mathbf{x}\in Z \\[6pt]
                h_{i,j}^n = 0 \quad \text{for} \quad \mathbf{x}\in\partial Z
            \end{cases}
            \end{equation*}
            """,
            font_size=self.BODY_FONT_SIZE + 2,
            color=BLACK,
        )
        # Positionner exactement où se trouve eq_fd, puis limiter la largeur
        eq_fd_damped.move_to(eq_fd)
        _shrink_to_width_if_needed(eq_fd_damped, area_w * 0.90)

        self.play(ReplacementTransform(eq_fd, eq_fd_damped), run_time=0.6)

        # Fin de la slide ----------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()



    def slide_18(self):
        """
        Slide 18: Comment calculer l'entrée de la méthode ?
        - Top bar with title.
        - Three body lines (Tex; includes h(x,t)).
        - Wait for user.
        - Three-column gallery, each revealed step-by-step:
            1) Figures/Mask3D_theoric_view.jpeg + "Vue théorique"
            2) Figures/MaskHeightMap.jpeg       + "Vue du dessus dans le stockage"
            3) Figures/Mask3D-contrast.jpeg     + "Vue avec une mer plate"
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Comment calculer l'entrée de la méthode ?")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area below the bar ----------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom
        anchor_x = x_left + self.DEFAULT_PAD

        # --- Body text (Tex, left-aligned to anchor) --------------------------
        self.start_body()

        line1 = Tex(
            r"Lorsqu'un navire avance : une vague haute \`a l'avant et une vague basse \`a l'arri\`ere",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        line1.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        line1.shift(RIGHT * (anchor_x - line1.get_left()[0]))

        line2 = Tex(
            r"En utilisant l'intersection entre la surface de l'eau $h(x,t)$ et le solide",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        line2.next_to(line1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        line2.shift(RIGHT * (anchor_x - line2.get_left()[0]))

        line3 = Tex(
            r"nous d\`efinissons le \emph{``masque du navire''} qui met \`a jour l'onde \`a chaque pas de temps :",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        line3.next_to(line2, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        line3.shift(RIGHT * (anchor_x - line3.get_left()[0]))

        self.add(line1, line2, line3)

        # --- Wait for user before images --------------------------------------
        self.next_slide()

        # --- Columns layout ----------------------------------------------------
        content_top_y = line3.get_bottom()[1] - 0.35
        content_bottom_y = y_bottom + 0.2
        content_h = max(1.6, content_top_y - content_bottom_y)
        content_center_y = (content_top_y + content_bottom_y) * 0.5

        col_gap = area_w * 0.06
        col_w = (area_w - 2 * col_gap) / 3.0

        cx1 = x_left + col_w * 0.5
        cx2 = cx1 + col_w + col_gap
        cx3 = cx2 + col_w + col_gap

        caption_h = 0.35
        max_side_w = col_w * 0.92
        max_side_h = content_h * 0.92 - caption_h
        side_max = max(1.2, min(max_side_w, max_side_h))

        def place_image_with_caption(img_path: str, center_x: float, caption_tex: str) -> Group:
            """
            Create an ImageMobject scaled to fit within a square of side 'side_max',
            centered at (center_x, content_center_y), with a Tex caption below.
            Uses Group since ImageMobject is a Mobject (not VMobject).
            """
            img = ImageMobject(img_path)
            scale = min(side_max / img.width, side_max / img.height, 1.0)
            img.scale(scale)
            img.move_to([center_x, content_center_y + 0.10, 0.0])

            cap = Tex(caption_tex, color=BLACK, font_size=self.BODY_FONT_SIZE)
            cap.next_to(img, DOWN, buff=0.18)
            return Group(img, cap)

        # --- Column 1 ----------------------------------------------------------
        col1 = place_image_with_caption(
            "Figures/Mask3D_theoric_view.jpeg",
            cx1,
            r"Vue th\'eorique",
        )
        self.play(FadeIn(col1, run_time=0.4))

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- Column 2 ----------------------------------------------------------
        col2 = place_image_with_caption(
            "Figures/MaskHeightMap.jpeg",
            cx2,
            r"Vue du dessus dans le stockage",
        )
        self.play(FadeIn(col2, run_time=0.4))

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- Column 3 ----------------------------------------------------------
        col3 = place_image_with_caption(
            "Figures/Mask3D-contrast.jpeg",
            cx3,
            r"Vue avec une mer plate",
        )
        self.play(FadeIn(col3, run_time=0.4))

        # --- End slide ---------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()

    def slide_19(self):
        """
        Slide 19: Result of combining the three methods.
        Implements solid and dotted curved arrows with corrected placement:
        (1) Surface -> Fluide-vers-solide (ok),
        (2) Fluide-vers-solide -> Solide-vers-fluide now ends on RIGHT side of S->F,
        (3) Solide-vers-fluide -> Surface (ok),
        (4) DOTTED S->F -> F->S now inner and higher,
        (5) DOTTED S->F -> Surface inner and shifted to the right,
        (6) DOTTED F->S -> Surface inner and shifted to the left.
        Then: summary table, demo image, and final bullets.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Résultat de la combinaison des trois méthodes")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Ellipses (same spirit as slide 9) --------------------------------
        ell_w = 3.6
        ell_h = 2.8

        e_surface = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
        t_surface = Tex("Simulation de surface", font_size=self.BODY_FONT_SIZE, color=BLACK)
        t_surface.move_to(e_surface.get_center())
        g_surface = VGroup(e_surface, t_surface).move_to([0.0, 1.3, 0.0])

        e_f2s = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
        t_f2s = Tex("Fluide vers solide", font_size=self.BODY_FONT_SIZE, color=BLACK)
        t_f2s.move_to(e_f2s.get_center())
        g_f2s = VGroup(e_f2s, t_f2s).move_to([3.6, -1.7, 0.0])

        e_s2f = Ellipse(width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7)
        t_s2f = Tex("Solide vers fluide", font_size=self.BODY_FONT_SIZE, color=BLACK)
        t_s2f.move_to(e_s2f.get_center())
        g_s2f = VGroup(e_s2f, t_s2f).move_to([-3.6, -1.7, 0.0])

        self.play(FadeIn(g_surface, run_time=0.4))
        self.play(FadeIn(g_f2s, run_time=0.4))
        self.play(FadeIn(g_s2f, run_time=0.4))

        # --- Arrow builders ----------------------------------------------------
        def _solid_curved_arrow(start_pt: np.ndarray, end_pt: np.ndarray, angle: float) -> CurvedArrow:
            """
            Solid curved arrow between two points with a signed curvature angle.
            Positive angle is counter-clockwise, negative is clockwise.
            """
            return CurvedArrow(
                start_point=start_pt,
                end_point=end_pt,
                angle=angle,
                color=BLACK,
                stroke_width=6,
                tip_length=0.16,
            )

        def _dotted_curved_arrow(start_pt: np.ndarray, end_pt: np.ndarray, angle: float, num_dashes = 60, dashed_ratio=0.5) -> VGroup:
            """
            Dotted curved arrow for Manim 0.19: dashed arc + triangular tip aligned
            to the end tangent. Uses num_dashes/dashed_ratio (no dash_length).
            """
            arc = ArcBetweenPoints(start_pt, end_pt, angle=angle, color=BLACK, stroke_width=6)
            dashed = DashedVMobject(arc, num_dashes, dashed_ratio)
            pts = arc.get_points()
            p_end = pts[-1]
            p_prev = pts[-2]
            v = p_end - p_prev
            theta = np.arctan2(v[1], v[0])
            tip = Triangle().scale(0.10).set_fill(BLACK, opacity=1.0).set_stroke(opacity=0.0)
            tip.move_to(p_end).rotate(theta)
            return VGroup(dashed, tip)

        def _right_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
            p = m.get_right().copy(); p[0] += dx; p[1] += dy; return p

        def _left_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
            p = m.get_left().copy(); p[0] += dx; p[1] += dy; return p

        def _top_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
            p = m.get_top().copy(); p[0] += dx; p[1] += dy; return p

        # ================= SOLID arrows =================
        # (1) Surface -> F->S (unchanged, correct)
        self.next_slide()
        a1 = _solid_curved_arrow(
            start_pt=_right_of(e_surface, dx=0.10, dy=-0.10),
            end_pt=_top_of(e_f2s, dx=-0.10, dy=0.10),
            angle=-1.0,
        )
        self.play(Create(a1, run_time=0.6))

        # (2) F->S -> S->F : origin ok, now end on RIGHT side of S->F
        self.next_slide()
        a2 = _solid_curved_arrow(
            start_pt=_left_of(e_f2s, dx=-0.10, dy=0.05),
            end_pt=_right_of(e_s2f, dx=0.15, dy=0.05),  # moved to right side
            angle=-1.0,  # under-arc clockwise
        )
        self.play(Create(a2, run_time=0.6))

        # (3) S->F -> Surface (unchanged, correct)
        self.next_slide()
        a3 = _solid_curved_arrow(
            start_pt=_top_of(e_s2f, dx=0.10, dy=0.10),
            end_pt=_left_of(e_surface, dx=-0.10, dy=-0.10),
            angle=-1.0,
        )
        self.play(Create(a3, run_time=0.6))

        # ================= DOTTED arrows =================
        # (4) S->F -> F->S : inner arc, higher
        self.next_slide()
        d1 = _dotted_curved_arrow(
            start_pt=_right_of(e_s2f, dx=0.10, dy=0.4),      # higher start
            end_pt=_left_of(e_f2s, dx=-0.10, dy=0.4),       # higher end
            angle=-0.8,                                     # inner bulge
        )
        self.play(FadeIn(d1, run_time=0.6))

        # (5) S->F -> Surface : inner, shifted right at both ends
        self.next_slide()
        d2 = _dotted_curved_arrow(
            start_pt=_top_of(e_s2f, dx=1.4, dy=-0.35),    # more to the right
            end_pt=_left_of(e_surface, dx=0.30, dy=-1.05), # more to the right
            angle=+0.6, 
            num_dashes=20,                                    
        )
        self.play(FadeIn(d2, run_time=0.6))

        # (6) F->S -> Surface : inner, shifted left
        self.next_slide()
        d3 = _dotted_curved_arrow(
            start_pt=_top_of(e_f2s, dx=-1.30, dy=-0.3),    # more to the left
            end_pt=_right_of(e_surface, dx=-0.30, dy=-1.05), # more to the left
            angle=-0.6,  
            num_dashes=20,                                   
        )
        self.play(FadeIn(d3, run_time=0.6))

        # --- Clear all except the bar -----------------------------------------
        self.next_slide()
        to_keep = {bar}
        self.remove(*[m for m in self.mobjects if m not in to_keep])

        # --- Summary table (BLACK text, pass-through for Tex) -------------------
        def _tx(s: str) -> Tex:
            return Tex(s, color=BLACK)

        headers = [
            _tx(""),
            _tx(""),
            _tx(r"\emph{un solide}"),
            _tx(r"\emph{dix solides}"),
        ]
        body = [
            [_tx("M\\'ethode de Tessendorf"), _tx("Hauteur"), _tx("0.4"), _tx("0.4")],
            [_tx(""), _tx("Vitesse"), _tx("1.1"), _tx("1.1")],
            [_tx(""), _tx("Total"), _tx("1.5"), _tx("1.5")],
            [_tx("Fluide-vers-Solide"), _tx("G\\'eom\\'etrie"), _tx("1.1"), _tx("4.6")],
            [_tx(""), _tx("Forces"), _tx("0.4"), _tx("3.6")],
            [_tx(""), _tx("Total"), _tx("1.5"), _tx("8.2")],
            [_tx("Solide-vers-Fluide"), _tx("MDF"), _tx("0.1"), _tx("0.8")],
            [_tx(""), _tx("Masque"), _tx("0.2"), _tx("1.6")],
            [_tx(""), _tx("Total"), _tx("0.3"), _tx("2.4")],
            [_tx(r"\textbf{Total}"), _tx(""), _tx(r"\textbf{3.4 ms}"), _tx(r"\textbf{12.2 ms}")],
        ]

        tbl = Table(
            body,
            col_labels=headers,
            include_outer_lines=True,
            line_config={"stroke_width": 2},
            h_buff=0.7,
            v_buff=0.35,
            element_to_mobject=lambda x: x,   # <- crucial: keep Tex as-is
        )
        tbl.set_color(BLACK)

        for line in tbl.get_horizontal_lines() + tbl.get_vertical_lines():
            line.set_stroke(width=2)

        last_row = len(body)
        for c in range(1, 5):
            tbl.get_cell((last_row, c)).set_fill(pc.blueGreen, opacity=0.15)

        max_w = config.frame_width * 0.92
        max_h = (config.frame_height * 0.92) - bar.height
        if tbl.width > max_w:
            tbl.scale_to_fit_width(max_w)
        if tbl.height > max_h:
            tbl.scale_to_fit_height(max_h)
        tbl.move_to([0.0, -0.1, 0.0])

        self.play(FadeIn(tbl, run_time=0.6))
        self.next_slide()
        self.remove(*[m for m in self.mobjects if m not in to_keep])

        # --- Demo image ---------------------------------------------------------
        img = ImageMobject("Figures/demo_arc_blanc.jpeg")
        s = min((config.frame_width * 0.92) / img.width,
                ((config.frame_height * 0.92) - bar.height - 0.2) / img.height,
                1.0)
        img.scale(s).move_to([0.0, -0.1, 0.0])
        self.play(FadeIn(img, run_time=0.6))

        self.next_slide()
        self.remove(*[m for m in self.mobjects if m not in to_keep])

        # --- Final bullets ------------------------------------------------------
        self.start_body()
        line = Tex("Néanmoins :", font_size=self.BODY_FONT_SIZE, color=BLACK)
        line.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        dx = (-config.frame_width / 2 + 0.6 + self.DEFAULT_PAD) - line.get_left()[0]
        line.shift(RIGHT * dx)
        self.add(line)

        bullet_items = [
            r"La méthode de Tessendorf repose sur de très nombreuses approximations",
            r"Les méthodes de couplage se basent sur des modéles phénoménologiques",
        ]
        rows = []
        for s in bullet_items:
            dot = Dot(radius=0.06, color=pc.blueGreen)
            txt = Tex(s, font_size=self.BODY_FONT_SIZE, color=BLACK)
            rows.append(VGroup(dot, txt).arrange(RIGHT, buff=0.25, aligned_edge=DOWN))
        bullets = VGroup(*rows).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        bullets.next_to(line, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        dx2 = (-config.frame_width / 2 + 0.6 + self.DEFAULT_PAD) - bullets.get_left()[0]
        bullets.shift(RIGHT * dx2)
        self.play(FadeIn(bullets, run_time=0.5))

        self.pause()
        self.clear()
        self.next_slide()

    def slide_20(self):
        """
        Slide 20: Principe de l'hybridation
        - Top bar + 3 body lines (Tex).
        - Wait for user.
        - Draw a pc.blueGreen rectangle filling most of remaining space.
        - Title inside rectangle (top-left): "Océan - Méthode de Tessendorf" in pc.blueGreen.
        - Two very small top-view boats (given polygon coords), placed apart with border gap.
        - Wait for user.
        - Draw two pc.uclaGold squares around each boat and add "SPH" label in their top-left.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Principe de l'hybridation")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area below the bar ----------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom
        anchor_x = x_left + self.DEFAULT_PAD

        # --- Body text (Tex) ---------------------------------------------------
        self.start_body()
        l1 = Tex(
            r"On conserve la m\'ethode de Tessendorf pour les grandes \'etendues et pour la couplage avec les solides",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        l1.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        l1.shift(RIGHT * (anchor_x - l1.get_left()[0]))

        l2 = Tex(
            r"et pour la couplage avec les solides on utilise la m\'ethode ",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        l2.shift(RIGHT * (anchor_x - l2.get_left()[0]))

        l3 = Tex(
            r"\textit{smoothed particles hydrodynamics} (SPH)",
            color=BLACK, font_size=self.BODY_FONT_SIZE
        )
        l3.next_to(l2, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
        l3.shift(RIGHT * (anchor_x - l3.get_left()[0]))

        self.add(l1, l2, l3)

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- Big blueGreen rectangle (most of remaining space) -----------------
        content_top_y = l3.get_bottom()[1] - 0.35
        content_bottom_y = y_bottom + 0.2
        rect_h = max(2.0, content_top_y - content_bottom_y)
        rect_w = area_w * 0.96
        rect_margin_x = area_w * 0.02

        ocean_rect = Rectangle(
            width=rect_w, height=rect_h,
            stroke_color=pc.blueGreen, stroke_width=6,
            fill_opacity=0.0
        )
        rect_center = np.array([ (x_left + x_right) * 0.5, (content_top_y + content_bottom_y) * 0.5, 0.0 ])
        ocean_rect.move_to(rect_center)
        self.add(ocean_rect)

        # Label inside rectangle (top-left, with small padding)
        pad_x = 0.25
        pad_y = 0.20
        ocean_label = Tex(
            r"Oc\'ean - M\'ethode de Tessendorf",
            color=pc.blueGreen, font_size=self.BODY_FONT_SIZE
        )
        # Place near top-left inside the rectangle
        tl = ocean_rect.get_corner(UL)
        ocean_label.move_to([tl[0] + pad_x + ocean_label.width * 0.5, tl[1] - pad_y - ocean_label.height * 0.5, 0.0])
        self.add(ocean_label)

        # --- Boats (very small, top view) --------------------------------------
        boat_coords = [
            [ 0.0, -1.0, 0.0],
            [ 1.0,  0.0, 0.0],
            [ 1.0,  4.0, 0.0],
            [ 0.0,  5.0, 0.0],
            [-1.0,  4.0, 0.0],
            [-1.0,  0.0, 0.0],
        ]

        def make_boat(scale_factor: float = 0.20) -> Polygon:
            pts = [np.array(p) for p in boat_coords]
            poly = Polygon(*pts, color=pc.oxfordBlue, stroke_width=4)
            poly.set_fill(pc.oxfordBlue, opacity=1.0)
            poly.scale(scale_factor)
            return poly

        # Compute inner placement bounds with a gap
        gap_x = max(0.5, rect_w * 0.05)
        gap_y = max(0.4, rect_h * 0.06)
        inner_left = ocean_rect.get_left()[0] + gap_x
        inner_right = ocean_rect.get_right()[0] - gap_x
        inner_top = ocean_rect.get_top()[1] - gap_y
        inner_bottom = ocean_rect.get_bottom()[1] + gap_y

        # Target positions: left and right halves
        left_center = np.array([ (inner_left + (inner_left + inner_right) * 0.5) * 0.5, (inner_top + inner_bottom) * 0.5, 0.0 ])
        right_center = np.array([ (inner_right + (inner_left + inner_right) * 0.5) * 0.5, (inner_top + inner_bottom) * 0.5, 0.0 ])

        boat1 = make_boat()
        boat2 = make_boat()
        boat1.move_to(left_center + np.array([-0.2, 0.1, 0.0]))
        boat2.move_to(right_center + np.array([0.2, -0.1, 0.0]))

        self.add(boat1, boat2)

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- SPH squares around each boat + "SPH" labels -----------------------
        def surround_with_sph(mob: Mobject) -> Group:
            # Padding around boat
            pad = 0.6
            w = mob.width + 2 * pad
            h = mob.height + 2 * pad
            side = max(w, h)  # make it square
            sq = Rectangle(width=side, height=side, stroke_color=pc.uclaGold, stroke_width=6)
            sq.move_to(mob.get_center())

            # "SPH" label inside square, top-left with a small inner offset
            lbl = Tex("SPH", color=pc.uclaGold, font_size=self.BODY_FONT_SIZE)
            tl = sq.get_corner(UL)
            lbl.move_to([tl[0] + 0.18 + lbl.width * 0.5, tl[1] - 0.14 - lbl.height * 0.5, 0.0])

            return Group(sq, lbl)

        sph1 = surround_with_sph(boat1)
        sph2 = surround_with_sph(boat2)

        self.play(FadeIn(sph1, run_time=0.3), FadeIn(sph2, run_time=0.3))

        # --- End slide
        # ---------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()


    def slide_21(self):
        # --- Top bar ---
        bar = self._top_bar("SPH pas à pas")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Intro line ---
        self.start_body()
        intro = Tex(
            r"SPH est une m{\'e}thode qui simule le fluide comme des particules :",
            font_size=self.BODY_FONT_SIZE,
            color=BLACK,
        )
        intro.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        dx = (-config.frame_width / 2 + 0.6 + self.DEFAULT_PAD) - intro.get_left()[0]
        intro.shift(RIGHT * dx)
        self.play(FadeIn(intro, run_time=0.3))

        # --- SPH animation (fluids only) with ROI crop ---
        show_sph_simulation(
            self,
            "states_sph/sph_gravity.csv",
            only_fluid=True,
            dot_radius=0.08,
            manim_seconds=3.0,            # Manim playback duration
            roi_origin=(-1.5, -3.0),
            roi_size=(3.0, 5.0),
            clip_outside=True,
            # NEW mapping: fit ROI height to 7 units and center it slightly below mid
            fit_roi_to_height=None,
            fit_roi_to_width=11.0,        # or set both and choose cover=True/False
            target_center=(0.0, -1.0),
            cover=False,
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
        """
        Slide 26 : Recherche du plus proche voisin (RPPV)

        CSV expected format (first 20 rows used):
            Particle,X,Y
            1,0.2075,0.7779
            2,0.7110,0.3041
            3,0.4963,0.4596
        with positions normalized in [0,1]x[0,1].
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Recherche du plus proche voisin (RPPV)")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # ---- Usable area below the bar ---------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom

        # Colors
        col_blue = getattr(pc, "blueGreen", BLUE_D)
        col_target = getattr(pc, "jellyBean", RED_D)
        col_far = getattr(pc, "fernGreen", GREEN_D)

        # --- Load positions from CSV ------------------------------------------
        import csv
        pts = []
        try:
            with open(
                "states_sph/particles.csv", "r", newline="", encoding="utf-8"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "X" in row and "Y" in row:
                        x = float(row["X"])
                        y = float(row["Y"])
                        pts.append((x, y))
                    if len(pts) >= 20:
                        break
        except Exception:
            # Fallback: deterministic 20 points in [0,1]^2
            rng = np.random.default_rng(7)
            for _ in range(20):
                pts.append((float(rng.uniform()), float(rng.uniform())))

        if not pts:
            pts = [(0.5, 0.5)]

        # --- Map [0,1]^2 to slide body ----------------------------------------
        pad_x = 0.6
        pad_y = 0.55
        tgt_left = x_left + pad_x
        tgt_right = x_right - pad_x
        tgt_bottom = y_bottom + pad_y
        tgt_top = y_top - pad_y
        tgt_w = max(0.1, tgt_right - tgt_left)
        tgt_h = max(0.1, tgt_top - tgt_bottom)

        def to_world(p01):
            return np.array(
                [
                    tgt_left + p01[0] * tgt_w,
                    tgt_bottom + p01[1] * tgt_h,
                    0.0,
                ]
            )

        Pw = [to_world(p) for p in pts]

        # Visual particle radius
        r_vis = min(tgt_w, tgt_h) / 60.0

        # --- Create particle dots ----------------------------------------------
        particles = []
        for (x, y, z) in Pw:
            particles.append(
                Dot(
                    point=[x, y, z],
                    radius=r_vis,
                    color=col_blue,
                    fill_opacity=1.0,
                )
            )
        particles_group = VGroup(*particles)
        self.add(particles_group)

        # Step: just the points
        self.next_slide()

        # --- Select target (3rd) and recolor others black ----------------------
        target_idx = min(2, len(particles) - 1)  # third in file
        for i, p in enumerate(particles):
            if i == target_idx:
                p.set_color(col_target)
                p.set_fill(col_target, opacity=1.0)
            else:
                p.set_color(BLACK)
                p.set_fill(BLACK, opacity=1.0)

        self.next_slide()

        # --- Dotted circle and "h" arrow ---------------------------------------
        center = particles[target_idx].get_center()
        h_radius = 20.0 * r_vis

        circle = DashedVMobject(
            Circle(
                radius=h_radius, arc_center=center, color=BLACK, stroke_width=4
            ),
            num_dashes=60,
            dashed_ratio=0.55,
        )
        self.add(circle)

        h_arrow = DoubleArrow(
            start=center,
            end=center + np.array([0.0, h_radius, 0.0]),
            stroke_width=6,
            color=BLACK,
            tip_length=0.16,
            buff=0.0,
        )
        h_text = Tex("h", color=BLACK, font_size=self.BODY_FONT_SIZE).next_to(
            h_arrow, RIGHT, buff=0.06
        )
        self.add(h_arrow, h_text)

        # --- Five probe lines to random particles -------------------------------
        rng = np.random.default_rng(42)
        probe_pool = [i for i in range(len(particles)) if i != target_idx]
        for _ in range(min(5, len(probe_pool))):
            j = int(rng.choice(probe_pool))
            probe_pool.remove(j)
            pj = particles[j].get_center()
            L = Line(center, pj, color=GRAY, stroke_width=4)
            self.add(L)
            d = float(np.linalg.norm(pj - center))
            if d <= h_radius:
                particles[j].set_color(col_blue).set_fill(col_blue, opacity=1.0)
            else:
                particles[j].set_color(col_far).set_fill(col_far, opacity=1.0)

        self.next_slide()

        # --- Color all in/out + show O(20^2) then O(N^2) -----------------------
        for i, p in enumerate(particles):
            if i == target_idx:
                continue
            d = float(np.linalg.norm(p.get_center() - center))
            if d <= h_radius:
                p.set_color(col_blue).set_fill(col_blue, opacity=1.0)
            else:
                p.set_color(col_far).set_fill(col_far, opacity=1.0)

        complex_pos = np.array(
            [x_right - 2.4, (y_top + y_bottom) * 0.5 + 0.2, 0.0]
        )
        t_20 = MathTex(
            r"\mathcal{O}(20^{2})",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 10,
        ).move_to(complex_pos)
        self.add(t_20)
        self.next_slide()

        t_n2 = MathTex(
            r"\mathcal{O}(N^{2})",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 10,
        ).move_to(complex_pos)
        self.play(ReplacementTransform(t_20, t_n2))
        self.next_slide()

        self.play(FadeOut(t_n2))
        for i, p in enumerate(particles):
            if i != target_idx:
                p.set_color(BLACK).set_fill(BLACK, opacity=1.0)
        self.next_slide()

        # --- Draw a 4x4 background grid behind particles -----------------------
        grid_w = tgt_w
        grid_h = tgt_h
        grid_rect = Rectangle(
            width=grid_w, height=grid_h, color=BLACK, stroke_width=6
        )
        grid_rect.move_to(
            [(tgt_left + tgt_right) * 0.5, (tgt_bottom + tgt_top) * 0.5, 0.0]
        )

        grid_lines = []
        for i in range(1, 4):
            # verticals
            x = grid_rect.get_left()[0] + i * (grid_w / 4.0)
            grid_lines.append(
                Line(
                    [x, grid_rect.get_bottom()[1], 0],
                    [x, grid_rect.get_top()[1], 0],
                    color=BLACK,
                    stroke_width=6,
                )
            )
            # horizontals
            y = grid_rect.get_bottom()[1] + i * (grid_h / 4.0)
            grid_lines.append(
                Line(
                    [grid_rect.get_left()[0], y, 0],
                    [grid_rect.get_right()[0], y, 0],
                    color=BLACK,
                    stroke_width=6,
                )
            )

        grid_group = VGroup(grid_rect, *grid_lines)
        grid_group.set_z_index(-10)  # ensure it stays behind dots
        self.add(grid_group)
        self.next_slide()

        # --- Recolor by in/out with some transparency --------------------------
        for i, p in enumerate(particles):
            if i == target_idx:
                continue
            d = float(np.linalg.norm(p.get_center() - center))
            if d <= h_radius:
                p.set_color(col_blue).set_fill(col_blue, opacity=0.85)
            else:
                p.set_color(col_far).set_fill(col_far, opacity=0.65)

        self.next_slide()

        # --- Show O(1) (re-create O(N^2) at same place then transform) ----------
        t_n2_new = MathTex(
            r"\mathcal{O}(N^{2})",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE + 10,
        ).move_to(complex_pos)
        self.add(t_n2_new)
        t_o1 = MathTex(
            r"\mathcal{O}(1)", color=BLACK, font_size=self.BODY_FONT_SIZE + 10
        ).move_to(complex_pos)
        self.play(ReplacementTransform(t_n2_new, t_o1))
        self.next_slide()

        # --- End ----------------------------------------------------------------
        self.pause()
        self.clear()
        self.next_slide()


    def slide_27(self):
        self._show_text(
            "TODO REMOVE Expliquer qu'on souhaite mieux utiliser les spécificités du GPU pour la RPPV"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_28(self):
        """
        Slide 28 : Mémoire partagée (shared memory)
        Fixes requested:
          1) From "Mémoire globale" draw ONE vertical line down to mid-height,
             then two horizontal arrows from that point to each grid.
          2) Move the two "Mémoire partagée" rectangles so their centers are
             vertically halfway between the top rectangle and the grids.
        """
        # --- Top bar -----------------------------------------------------------
        bar = self._top_bar("Mémoire partagée")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Usable area -------------------------------------------------------
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom
        mid_x = 0.0

        # Helper: 4x4 grid
        def make_grid(center, w, h, stroke=6):
            outer = Rectangle(width=w, height=h, color=BLACK, stroke_width=stroke).move_to(center)
            lines = []
            for i in range(1, 4):
                x = outer.get_left()[0] + i * (w / 4.0)
                lines.append(Line([x, outer.get_bottom()[1], 0], [x, outer.get_top()[1], 0], color=BLACK, stroke_width=stroke))
            for i in range(1, 4):
                y = outer.get_bottom()[1] + i * (h / 4.0)
                lines.append(Line([outer.get_left()[0], y, 0], [outer.get_right()[0], y, 0], color=BLACK, stroke_width=stroke))
            return VGroup(outer, *lines)

        # --- Top: large "Mémoire globale" rectangle ----------------------------
        top_rect_w = area_w * 0.55
        top_rect_h = area_h * 0.14
        top_rect_y = y_top - top_rect_h * 0.5 - 0.10
        global_rect = RoundedRectangle(
            width=top_rect_w, height=top_rect_h, corner_radius=0.18,
            stroke_color=BLACK, stroke_width=6, fill_opacity=0.0
        ).move_to([mid_x, top_rect_y, 0.0])
        global_label = Tex(r"M\'emoire globale", color=BLACK, font_size=self.BODY_FONT_SIZE + 6).move_to(global_rect.get_center())
        self.add(global_rect, global_label)

        # --- Grids (left and right) -------------------------------------------
        grid_w = min(5.2, area_w * 0.34)
        grid_h = min(3.8, area_h * 0.30)
        grids_y = y_bottom + grid_h * 0.5 + 0.60
        gap_lr = area_w * 0.10
        left_center = np.array([mid_x - (grid_w + gap_lr) * 0.6, grids_y, 0.0])
        right_center = np.array([mid_x + (grid_w + gap_lr) * 0.6, grids_y, 0.0])

        grid_left = make_grid(left_center, grid_w, grid_h)
        grid_right = make_grid(right_center, grid_w, grid_h)
        self.add(grid_left, grid_right)

        # --- Central vertical line + horizontal arrows (lent/large) ------------
        # Vertical line from bottom of global_rect to mid-height between rect and grids
        grid_top_y = grid_left[0].get_top()[1]
        y_mid = 0.5 * (global_rect.get_bottom()[1] + grid_top_y)

        central_line = Line(
            [mid_x, global_rect.get_bottom()[1], 0.0],
            [mid_x, grids_y, 0.0],
            color=BLACK, stroke_width=6
        )

        # Horizontal arrows from the end of the vertical line to each grid center (x)
        arrow_left = Arrow(
            start=[mid_x, grids_y, 0.0],
            end=[left_center[0]+0.5*grid_w, grids_y, 0.0],
            color=BLACK, stroke_width=6, buff=0.0
        )
        arrow_right = Arrow(
            start=[mid_x, grids_y, 0.0],
            end=[right_center[0]-0.5*grid_w, grids_y, 0.0],
            color=BLACK, stroke_width=6, buff=0.0
        )

        lbl_slow_l = Tex(r"D\'ebit lent\\Stockage large", color=BLACK, font_size=self.BODY_FONT_SIZE)\
            .next_to(central_line, RIGHT, buff=0.12)
        # lbl_slow_r = Tex(r"D\'ebit lent\\Stockage large", color=BLACK, font_size=self.BODY_FONT_SIZE)\
            # .next_to(central_line, LEFT, buff=0.12)

        self.add(central_line, arrow_left, arrow_right, lbl_slow_l)

        # --- Wait for user -----------------------------------------------------
        self.next_slide()

        # --- "Mémoire partagée" rectangles centered vertically between top+grids
        small_w = grid_w * 0.55
        small_h = grid_h * 0.28

        shared_y = y_mid  # centered vertically as requested

        shared_left = RoundedRectangle(
            width=small_w, height=small_h, corner_radius=0.18,
            stroke_color=BLACK, stroke_width=6, fill_opacity=0.0
        ).move_to([left_center[0], shared_y, 0.0])

        shared_right = RoundedRectangle(
            width=small_w, height=small_h, corner_radius=0.18,
            stroke_color=BLACK, stroke_width=6, fill_opacity=0.0
        ).move_to([right_center[0], shared_y, 0.0])

        txt_shared_l = Tex(r"M\'emoire partag\'ee", color=BLACK, font_size=self.BODY_FONT_SIZE).move_to(shared_left.get_center())
        txt_shared_r = Tex(r"M\'emoire partag\'ee", color=BLACK, font_size=self.BODY_FONT_SIZE).move_to(shared_right.get_center())

        self.add(shared_left, shared_right, txt_shared_l, txt_shared_r)

        # --- Fast/small arrows from shared boxes down to grids -----------------
        fast_arrow_l = Arrow(
            start=[left_center[0], shared_left.get_bottom()[1] - 0.02, 0.0],
            end=[left_center[0], grid_left[0].get_top()[1] + 0.02, 0.0],
            stroke_width=6, color=BLACK, buff=0.0
        )
        fast_arrow_r = Arrow(
            start=[right_center[0], shared_right.get_bottom()[1] - 0.02, 0.0],
            end=[right_center[0], grid_right[0].get_top()[1] + 0.02, 0.0],
            stroke_width=6, color=BLACK, buff=0.0
        )

        lbl_fast_l = Tex(r"D\'ebit rapide\\Stockage l\'eger", color=BLACK, font_size=self.BODY_FONT_SIZE)\
            .next_to(fast_arrow_l, LEFT, buff=0.18)
        lbl_fast_r = Tex(r"D\'ebit rapide\\Stockage l\'eger", color=BLACK, font_size=self.BODY_FONT_SIZE)\
            .next_to(fast_arrow_r, RIGHT, buff=0.18)

        self.add(fast_arrow_l, fast_arrow_r, lbl_fast_l, lbl_fast_r)

        # --- End slide ---------------------------------------------------------
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
