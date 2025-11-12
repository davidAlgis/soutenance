import math
import re
from typing import List, Optional

from manim import *
from manim import logger
from manim_tikz import Tikz
from PIL import Image as PILImage


def parse_selection(sel: str, max_n: int) -> set[int]:
    """Parse '1-5,8,12-14' -> {1,2,3,4,5,8,12,13,14}; 'all' -> all."""
    if not sel or sel.strip().lower() == "all":
        return set(range(1, max_n + 1))
    s: set[int] = set()
    for part in sel.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b:
                s.update(range(a, b + 1))
            else:
                s.update(range(b, a + 1))
        elif part.isdigit():
            s.add(int(part))
    return {i for i in s if 1 <= i <= max_n}


def tikz_from_file(
    file_path: str,
    packages: Optional[List[str]] = None,
    libraries: Optional[List[str]] = None,
    tikzset: Optional[List[str]] = None,
    preamble: Optional[str] = None,
    use_pdf: Optional[bool] = False,
    **kwargs,
) -> Tikz:
    """
    Create a Tikz image from a .tikz file path.

    Args:
        file_path: Path to a .tikz file, e.g. "tikz/my_tikz.tikz".
        packages, libraries, tikzset, preamble, use_pdf: same meaning as in Tikz(...).
        **kwargs: forwarded to Tikz(...) (e.g., z_index, opacity, etc.).

    Returns:
        A manim_tikz.Tikz object ready to add to the scene.
    """
    # Avoid mutable default args
    packages = packages or []
    libraries = libraries or []
    tikzset = tikzset or []

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    return Tikz(
        code=code,
        packages=packages,
        libraries=libraries,
        tikzset=tikzset,
        preamble=preamble,
        use_pdf=use_pdf,
        **kwargs,
    )


def make_triangle_bullet(color, size=0.18, rotation=-math.pi / 2):
    b = Triangle(fill_color=color, fill_opacity=1.0, stroke_width=0)
    b.set_width(size)
    b.rotate(rotation)
    return b


def make_bullet_list(
    items,
    *,
    bullet_color,  # e.g., pc.blueGreen
    font_size=32,
    line_gap=0.18,  # vertical spacing between lines
    left_pad=0.25,  # space between bullet and text
):
    rows = []
    for s in items:
        bullet = make_triangle_bullet(bullet_color)
        txt = Tex(s, color=BLACK, font_size=font_size)
        row = VGroup(bullet, txt)
        txt.next_to(bullet, RIGHT, buff=left_pad)
        rows.append(row)

    group = VGroup(*rows)
    # Stack rows vertically
    for i in range(1, len(rows)):
        rows[i].next_to(rows[i - 1], DOWN, buff=line_gap, aligned_edge=LEFT)

    # Align bullets in a column
    left_x = rows[0][0].get_left()[0]
    for r in rows:
        r[0].align_to([left_x, 0, 0], LEFT)

    return group


def make_pro_cons(
    pros,
    cons,
    *,
    pro_color,  # e.g., pc.apple
    con_color,  # e.g., pc.bittersweet
    font_size=32,
    icon_size=32,
    col_gap=1.2,
    row_gap=0.18,
    left_pad=0.20,
):
    def make_rows(items, color, icon_char):
        rows = []
        for s in items:
            icon = Text(
                icon_char, color=color, font_size=icon_size, weight=BOLD
            )
            txt = Tex(s, color=BLACK, font_size=font_size)
            row = VGroup(icon, txt)
            txt.next_to(icon, RIGHT, buff=left_pad)
            rows.append(row)
        # vertical stack
        for i in range(1, len(rows)):
            rows[i].next_to(rows[i - 1], DOWN, buff=row_gap, aligned_edge=LEFT)
        return VGroup(*rows)

    pros_col = make_rows(pros, pro_color, "✓")
    cons_col = make_rows(cons, con_color, "✗")

    # put columns side by side
    group = VGroup(pros_col, cons_col)
    cons_col.next_to(pros_col, RIGHT, buff=col_gap, aligned_edge=UP)
    return group
