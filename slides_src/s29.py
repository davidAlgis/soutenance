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


@slide(29)
def slide_29(self):
    """
    Slide 29: Methode X-Pencil.
    Minimal changes requested by user:
    - Extra vertical padding between top bar and the two rectangles.
    - Keep only the right-side 6 blueGreen cells; remove the 6 left ones.
    - Remove the 4 cornflower cells on the left; surround only on the right side.
    - Put the brace at the right of the whole grid.
    - Lower the 'Mémoire partagée' rectangle in the second part.
    - Lower the 30 particles.
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar("Méthode X-Pencil")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Layout bounds -----------------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6
    area_w = x_right - x_left

    # --- Two rectangles (top left / top right) ----------------------------
    rect_w = min(3.8, area_w * 0.28)
    rect_h = 0.9
    # Added vertical padding below the top bar
    TOP_RECT_VPAD = 0.55
    top_y = y_top - TOP_RECT_VPAD

    left_rect = Rectangle(
        width=rect_w, height=rect_h, color=BLACK, stroke_width=3
    )
    left_rect.move_to([x_left + rect_w * 0.5 + 0.2, top_y, 0.0])
    left_lbl = Tex(
        r"M\'emoire globale", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    left_lbl.move_to(left_rect.get_center())

    right_rect = Rectangle(
        width=rect_w, height=rect_h, color=BLACK, stroke_width=3
    )
    right_rect.move_to([x_right - rect_w * 0.5 - 0.2, top_y, 0.0])
    right_lbl = Tex(
        r"M\'emoire partag\'ee", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    right_lbl.move_to(right_rect.get_center())

    self.play(
        Create(left_rect),
        Create(right_rect),
        FadeIn(left_lbl),
        FadeIn(right_lbl),
    )
    # --- 7x7 grid ----------------------------------------------------------
    grid_top = top_y - rect_h * 0.95
    grid_bottom = y_bottom + 0.5
    grid_h = max(2.8, grid_top - grid_bottom)
    grid_w = min(area_w * 0.70, 9.0)
    grid_center_x = 0.0

    rows, cols = 7, 7
    gap = 0.02
    cell_w = (grid_w - (cols - 1) * gap) / cols
    cell_h = (grid_h - (rows - 1) * gap) / rows
    top_left_x = grid_center_x - (grid_w / 2.0) + cell_w / 2.0
    top_left_y = grid_top - cell_h / 2.0

    cell_matrix = []
    row_groups = []
    for r in range(rows):
        row = []
        for c in range(cols):
            cx = top_left_x + c * (cell_w + gap)
            cy = top_left_y - r * (cell_h + gap)
            rect = Rectangle(
                width=cell_w,
                height=cell_h,
                stroke_width=2,
                stroke_color=BLACK,
                fill_opacity=1.0,
                fill_color=pc.gainsboro,
            ).move_to([cx, cy, 0.0])
            row.append(rect)
        cell_matrix.append(row)
        row_groups.append(VGroup(*row))

    # Draw rows in one clip
    self.play(
        LaggedStart(
            *[FadeIn(g, run_time=0.18) for g in row_groups], lag_ratio=0.08
        ),
    )

    # --- Color the cells: keep only the RIGHT-side 6 on rows 4-5 -----------
    # Previously first 6 columns; now last 6 columns (0-based: 1..6)
    block_rows = [3, 4]  # rows 4 and 5 (0-based)
    block_cols = list(range(4, 7))  # keep the 6 on the RIGHT side only
    blue_set = {(r, c) for r in block_rows for c in block_cols}

    # Surrounding cells ONLY on/right of the block (no left-of-block padding)
    surround_set = set()
    min_r = max(min(block_rows) - 1, 0)
    max_r = min(max(block_rows) + 1, rows - 1)
    min_c = min(block_cols)  # do not include cc < min_c
    max_c = min(max(block_cols) + 1, cols - 1)

    for rr in range(min_r, max_r + 1):
        for cc in range(min_c, max_c + 1):
            if (rr, cc) in blue_set:
                continue
            if (
                (rr in block_rows and cc in (min_c, max(block_cols) + 1))
                or (
                    cc in block_cols
                    and rr in (min(block_rows) - 1, max(block_rows) + 1)
                )
                or (
                    (rr in (min(block_rows) - 1, max(block_rows) + 1))
                    and (cc in (min_c, max(block_cols) + 1))
                )
            ):
                surround_set.add((rr, cc))
    surround_set.add((2, 3))
    surround_set.add((3, 3))
    surround_set.add((4, 3))
    surround_set.add((5, 3))
    blue_cells = [cell_matrix[r][c] for (r, c) in sorted(blue_set)]
    corn_cells = [cell_matrix[r][c] for (r, c) in sorted(surround_set)]

    self.play(
        *[m.animate.set_fill(pc.blueGreen, 1.0) for m in blue_cells],
        run_time=0.30
    )
    self.play(
        *[m.animate.set_fill(pc.cornflower, 1.0) for m in corn_cells],
        run_time=0.30
    )

    # --- Wait ---------------------------------------------------------------
    self.next_slide()

    # --- Brace at the RIGHT of the WHOLE GRID ------------------------------
    grid_right_x = max(
        cell_matrix[r][c].get_right()[0]
        for r in range(rows)
        for c in range(cols)
    )
    grid_top_y = max(cell_matrix[2][c].get_top()[1] for c in range(cols))
    grid_bottom_y = min(cell_matrix[5][c].get_bottom()[1] for c in range(cols))

    brace_anchor = Line(
        [grid_right_x + 0.02, grid_bottom_y, 0.0],
        [grid_right_x + 0.02, grid_top_y, 0.0],
    )
    brace = Brace(brace_anchor, direction=RIGHT, color=BLACK)

    brace_center = brace.get_center()
    mid_above = 0.5 * (left_rect.get_right() + right_rect.get_left())
    mid_above[1] = top_y + 0.05
    curve = CubicBezier(
        brace_center + np.array([0.25, 0.0, 0.0]),
        brace_center + np.array([5.0, 0.9, 0.0]),
        mid_above - np.array([0.9, 0.9, 0.0]),
        mid_above - np.array([0.1, 0.0, 0.0]),
        stroke_color=pc.blueGreen,
        stroke_width=5,
    )

    copy_arrow = Arrow(
        start=left_rect.get_right(),
        end=right_rect.get_left(),
        buff=0.08,
        stroke_width=5,
        color=pc.blueGreen,
    )
    copy_lbl = Tex(r"Copie", color=BLACK, font_size=self.BODY_FONT_SIZE)
    copy_lbl.next_to(copy_arrow, UP, buff=0.10)

    self.play(
        AnimationGroup(
            Create(brace, run_time=0.4),
            AnimationGroup(Create(curve, run_time=0.5)),
            AnimationGroup(
                Create(copy_arrow, run_time=0.5),
                FadeIn(copy_lbl, run_time=0.2),
            ),
            lag_ratio=0.10,
        )
    )

    # --- Wait ---------------------------------------------------------------
    self.next_slide()

    # --- Keep only bar + right rectangle; fade others ----------------------
    keep = VGroup(bar, right_rect, right_lbl)
    to_fade = Group(*[m for m in self.mobjects if m not in keep])
    self.play(FadeOut(to_fade, run_time=0.35))

    # Lower the shared-memory rectangle in the second part
    SECOND_TOP_VPAD = TOP_RECT_VPAD + 0.20  # slightly lower than before
    right_rect.move_to([0.0, y_top - SECOND_TOP_VPAD, 0.0])
    right_lbl.move_to(right_rect.get_center())
    self.add_foreground_mobject(right_rect)
    self.add_foreground_mobject(right_lbl)

    # --- Particles from CSV (lowered area) ---------------------------------
    # Lower the particle field by reducing the body_top
    body_top = y_top - (SECOND_TOP_VPAD + 0.85)
    body_bottom = y_bottom + 0.4
    body_left = x_left + 0.4
    body_right = x_right - 0.4
    body_w = body_right - body_left
    body_h = max(1.2, body_top - body_bottom)

    def _load_pts(path: str, max_count: int = 30):
        try:
            data = np.genfromtxt(
                path, delimiter=",", names=True, dtype=None, encoding="utf-8"
            )
        except Exception:
            data = None
        if data is not None and len(data) > 0:
            for cx, cy in (
                ("X quincunx", "Y quincunx"),
                ("x", "y"),
                ("pos_x", "pos_y"),
                ("X", "Y"),
            ):
                if cx in data.dtype.names and cy in data.dtype.names:
                    arr = np.column_stack([data[cx], data[cy]])[:max_count]
                    xmin, ymin = np.min(arr[:, 0]), np.min(arr[:, 1])
                    xmax, ymax = np.max(arr[:, 0]), np.max(arr[:, 1])
                    if xmax > xmin and ymax > ymin:
                        nx = (arr[:, 0] - xmin) / (xmax - xmin)
                        ny = (arr[:, 1] - ymin) / (ymax - ymin)
                        px = body_left + nx * body_w
                        py = body_bottom + ny * body_h
                        return np.column_stack([px, py, np.zeros_like(px)])
        # Fallback grid (6x5)
        cols_g, rows_g = 6, 5
        xs = np.linspace(body_left, body_right, cols_g + 2)[1:-1]
        ys = np.linspace(body_bottom, body_top, rows_g + 2)[1:-1][::-1]
        pts = []
        for j in range(rows_g):
            for i in range(cols_g):
                pts.append([xs[i], ys[j], 0.0])
                if len(pts) >= max_count:
                    break
            if len(pts) >= max_count:
                break
        return np.array(pts)

    pts = _load_pts("states_sph/particles.csv", 30)
    pr = min(body_w, body_h) / 45.0
    particles = VGroup(
        *[Dot(point=p, radius=pr, color=pc.blueGreen) for p in pts]
    )
    self.play(
        LaggedStart(
            *[GrowFromCenter(p) for p in particles],
            lag_ratio=0.04,
            run_time=0.9
        )
    )

    # --- Wait ---------------------------------------------------------------
    self.next_slide()

    # --- Recolor: 3rd = jellyBean, others = black; dashed circle -----------
    target_idx = 2 if len(particles) >= 3 else 0
    for i, p in enumerate(particles):
        p.set_color(pc.jellyBean if i == target_idx else BLACK)

    from manim import DashedVMobject

    target = particles[target_idx]
    circle = DashedVMobject(
        Circle(radius=15.0 * pr, color=BLACK, stroke_width=4).move_to(
            target.get_center()
        ),
        num_dashes=40,
        dashed_ratio=0.55,
    )
    self.play(Create(circle, run_time=0.5))

    # --- Four neighbor demos (batched per neighbor) ------------------------
    centers = np.array([p.get_center() for p in particles])
    tgt = centers[target_idx]
    dists = np.linalg.norm(centers - tgt, axis=1)
    order = [idx for idx in np.argsort(dists) if idx != target_idx][:8]

    used = set()
    for _ in range(4):
        nbr = next((i for i in order if i not in used), None)
        if nbr is None:
            break
        used.add(nbr)
        start_pt = target.get_center()
        end_pt = particles[nbr].get_center()
        line = Line(
            start=start_pt, end=end_pt, stroke_width=5, color=pc.blueGreen
        )
        label = Tex(
            r"Mem. partag\'ee", color=BLACK, font_size=self.BODY_FONT_SIZE - 6
        )
        label.move_to(start_pt - np.array([0.0, 0.3, 0.0]))

        self.play(
            Succession(
                Create(line, run_time=0.35),
                AnimationGroup(
                    particles[nbr].animate.set_color(pc.blueGreen),
                    FadeIn(label, run_time=0.15),
                    lag_ratio=0.0,
                ),
                AnimationGroup(
                    Uncreate(line, run_time=0.25),
                    FadeOut(label, run_time=0.15),
                ),
            )
        )

    credit = Tex(
        r"Algis \textit{et al.} (2024), \textit{Efficient GPU...}",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE - 6,
    )
    credit.to_edge(DOWN, buff=0.5)
    credit.to_edge(RIGHT, buff=0.5)

    dot = Dot(color=pc.blueGreen)
    dot.next_to(credit, LEFT, buff=0.3)
    self.play(FadeIn(credit), run_time=0.5)
    self.play(Flash(dot, color=pc.blueGreen), run_time=2.0)

    # --- End slide ---------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
