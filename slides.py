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
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "30"
import slides_src  # triggers registration via decorators
from slide_registry import all_numbers, get


class Presentation(Slide):

    TEXT_SCALE = 0.9
    MAX_WIDTH = 12.0
    BODY_TOP_BUFF = 0.2
    BODY_LINE_BUFF = 0.15
    DEFAULT_PAD = 0.3
    BODY_FONT_SIZE = 28

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

    def construct(self):
        import os

        from utils import parse_selection

        nums = all_numbers()
        if not nums:
            return
        selection_str = os.environ.get("SLIDES", SLIDES_SELECTION)
        total = max(nums)
        selection = parse_selection(selection_str, total)
        for n in nums:
            if n in selection:
                get(n)(self)
