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
SLIDES_SELECTION = "25"
from slide_registry import slide

@slide(1)
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
