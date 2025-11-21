# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.

# flake8: noqa: F405
import os

import numpy as np
import palette_colors as pc
import slides_src  # triggers registration via decorators
from manim import *
from manim import logger
from manim_slides import Slide
from manim_tikz import Tikz
from slide_registry import all_numbers, get
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "18"


class Presentation(Slide):

    TEXT_SCALE = 0.9
    MAX_WIDTH = 12.0
    BODY_TOP_BUFF = 0.2
    BODY_LINE_BUFF = 0.15
    DEFAULT_PAD = 0.3
    BODY_FONT_SIZE = 34
    SHIFT_SCALE = 0.15

    def _top_bar(self, label: str, *, font_size: int = 48):
        """
        Create a top bar with a left-aligned title.
        Also adds a slide counter (X/Y) to the bottom left.
        """
        # --- Existing Top Bar Logic ---
        h = config.frame_height / 10.0
        w = config.frame_width

        bar = Rectangle(
            width=w,
            height=h,
            fill_color=pc.blueGreen,
            fill_opacity=1.0,
            stroke_opacity=0.0,
        )

        txt = Text(label, color=WHITE, weight=BOLD, font_size=font_size)

        inner_w = w - 2.0 * self.DEFAULT_PAD
        inner_h = h * 0.82

        if txt.width > 0 and txt.height > 0:
            scale_w = inner_w / txt.width
            scale_h = inner_h / txt.height
            scale = min(1.0, scale_w, scale_h)
            if scale < 1.0:
                txt.scale(scale)

        elements = [bar, txt]
        group = VGroup(*elements)
        group.to_edge(UP, buff=0)

        txt.align_to(bar, LEFT)
        txt.shift(RIGHT * self.DEFAULT_PAD)
        txt.set_y(bar.get_center()[1])

        # Cache for body placement
        self._current_bar = group
        self._body_last = None
        self._text_left_x = bar.get_left()[0] + self.DEFAULT_PAD

        # --- NEW CODE: Slide Counter ---
        # We check if attributes exist to avoid errors if running outside construct loop
        # Create the text, e.g., "3/41"
        counter_text = f"{self.current_slide_number}/{self.total_slides}"

        # Style the counter (Dark gray, small font)
        footer = Tex(counter_text, font_size=24, color=pc.blueGreen)

        # Position at Bottom Left (DL) with a small buffer
        footer.to_corner(DR, buff=0.3)

        # Add directly to the scene
        self.add(footer)
        # -------------------------------

        return group, footer

    def add_credit(self, credit_txt):
        credit = Tex(
            credit_txt,
            color=BLACK,
            font_size=self.BODY_FONT_SIZE - 8,
        )
        credit.to_edge(DL, buff=0.3)

        dot = Dot(color=pc.blueGreen)
        dot.next_to(credit, RIGHT, buff=0.3)
        self.play(FadeIn(credit), run_time=0.5)
        self.play(Flash(dot, color=pc.blueGreen), run_time=2.0)

    def start_body(self):
        """Initialize body placement just under the bar, with per-slide defaults."""
        # Assumes _top_bar() has been called before.
        self._body_last = None
        self._body_top_buff = self.BODY_TOP_BUFF
        self._body_font_size = self.BODY_FONT_SIZE

    def add_body_text(self, s: str, *, color=BLACK, font_size=30):
        """Add one line: first goes under the bar, then stack under previous."""
        # Assumes _top_bar() and start_body() have been called and args are not None.
        t = Tex(s, color=color, font_size=font_size)

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

    def construct(self):
        import os

        from utils import parse_selection

        self.french_template = TexTemplate()
        self.french_template.preamble = r"""
            \usepackage[french]{babel}
            \usepackage[T1]{fontenc}
            \usepackage{amsmath}
            \usepackage{amssymb}
            """
        nums = all_numbers()
        if not nums:
            return

        selection_str = os.environ.get("SLIDES", SLIDES_SELECTION)
        # We assume the "Total" is the count of all registered slides
        total_slides = len(nums)
        # Or use total_slides = max(nums) if you prefer the highest index number

        # Store total in self so _top_bar can access it
        self.total_slides = total_slides

        total_in_selection = max(nums)  # logic for the selector
        selection = parse_selection(selection_str, total_in_selection)

        for n in nums:
            if n in selection:
                # Store the current number in self before rendering
                self.current_slide_number = n
                get(n)(self)
