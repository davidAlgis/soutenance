import re

from manim import *
from manim import logger
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

