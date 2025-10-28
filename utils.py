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
