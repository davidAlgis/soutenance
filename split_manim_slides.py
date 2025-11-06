#!/usr/bin/env python3
"""
Split a monolithic manim slides.py into:
- slides_src/sXX.py (one file per slide_XX(self))
- slides_src/__init__.py  (imports all sXX so they register)
- slide_registry.py       (decorator + registry)
- slides.py               (entry point with helpers, SLIDES_SELECTION kept)

Usage:
    python split_manim_slides.py

Assumptions:
- Your current file is named 'slides.py' and contains:
    * imports (manim, manim_slides.Slide, etc.)
    * global config + SLIDES_SELECTION
    * class Presentation(Slide) with methods:
        - helpers (e.g., _top_bar, start_body, add_body_text, _show_text, default_end_slide)
        - construct(self) that sequences slide_XX methods
        - slide_01(self) ... slide_41(self) (any subset)
- We preserve all non-slide methods (helpers) inside the new slides.py.
- We replace construct() to call registry-registered functions from slides_src.

This script is idempotent on fresh source; it overwrites generated files.
"""

import ast
import os
import re
import shutil
import textwrap

ENTRY_FILE = "slides.py"
BACKUP_FILE = "slides_legacy.py"
SRC_DIR = "slides_src"
REGISTRY_FILE = "slide_registry.py"


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def extract_import_block(src: str) -> str:
    """
    Grab the leading import/config block to reuse in generated files.
    We stop when we hit the first 'class ' or 'def ' at column 0.
    """
    lines = src.splitlines()
    out = []
    for i, line in enumerate(lines):
        if re.match(r"^(class|def)\s", line):
            break
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def find_presentation_class(module: ast.Module):
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "Presentation":
            return node
    return None


def is_slide_method(func: ast.FunctionDef) -> bool:
    return bool(re.match(r"slide_(\d+)$", func.name))


def get_source_segment(src: str, node: ast.AST) -> str:
    return ast.get_source_segment(src, node)


def dedent_to_top_level(code: str) -> str:
    return textwrap.dedent(code)


def collect_non_slide_methods_and_constants(src: str, klass: ast.ClassDef):
    """
    Return (constants_block, helper_methods_block) as code strings.
    - constants: class-level assignments (e.g., TEXT_SCALE = 0.9)
    - helper methods: any def in class that is NOT slide_XX and NOT construct
    """
    constants = []
    helpers = []
    for node in klass.body:
        if isinstance(node, ast.Assign):  # class constants
            constants.append(get_source_segment(src, node))
        elif isinstance(node, ast.AnnAssign):  # annotated assignments, just in case
            constants.append(get_source_segment(src, node))
        elif isinstance(node, ast.FunctionDef):
            if node.name not in ("construct",) and not is_slide_method(node):
                helpers.append(get_source_segment(src, node))

    constants_block = "\n".join(constants).strip()
    helpers_block = "\n\n".join(helpers).strip()
    return constants_block, helpers_block


def collect_slide_methods(src: str, klass: ast.ClassDef):
    """
    Return list of (slide_number:int, code:str) where code is a top-level function
    decorated with @slide(n) and same body as original method.
    """
    out = []
    for node in klass.body:
        if isinstance(node, ast.FunctionDef) and is_slide_method(node):
            m = re.match(r"slide_(\d+)$", node.name)
            n = int(m.group(1))
            method_src = get_source_segment(src, node)
            # dedent to top-level
            top_src = dedent_to_top_level(method_src)
            # keep the same signature; we'll just decorate it in the per-file module
            out.append((n, top_src))
    out.sort(key=lambda t: t[0])
    return out


def extract_global_vars(src: str):
    """
    Pull out SLIDES_SELECTION and config.background_color assignment if present,
    to keep them in the new slides.py.
    """
    slides_sel = None
    bg_line = None

    for line in src.splitlines():
        # SLIDES_SELECTION = "..."
        if re.match(r"^\s*SLIDES_SELECTION\s*=\s*.+", line):
            slides_sel = line.strip()
        # config.background_color = ...
        if re.match(r"^\s*config\.background_color\s*=\s*.+", line):
            bg_line = line.strip()

    return slides_sel, bg_line


def build_registry_py() -> str:
    return textwrap.dedent(
        """\
        # slide_registry.py
        from typing import Callable, Dict, List

        SlideFunc = Callable[[object], None]
        _registry: Dict[int, SlideFunc] = {}

        def slide(number: int):
            \"\"\"Decorator to register a slide function under a numeric index.\"\"\"
            def _wrap(fn: SlideFunc) -> SlideFunc:
                if number in _registry:
                    raise ValueError(f"Slide #{number} already registered by {_registry[number].__name__}")
                _registry[number] = fn
                return fn
            return _wrap

        def all_numbers() -> List[int]:
            return sorted(_registry.keys())

        def get(number: int) -> SlideFunc:
            return _registry[number]
        """
    )


def build_new_slides_py(import_block: str,
                        slides_selection_line: str | None,
                        bg_line: str | None,
                        class_constants_block: str,
                        helper_methods_block: str) -> str:
    """
    New entry file:
    - keeps imports (plus slide_registry + slides_src import)
    - keeps SLIDES_SELECTION (or sets default)
    - keeps background_color line
    - defines Presentation(Slide) with constants + helper methods
    - defines construct() that calls registered slide functions by selection
    """
    extra_imports = "\nfrom slide_registry import all_numbers, get\nimport slides_src  # triggers registration via decorators\n"
    # ensure parse_selection import stays available; rely on user’s original import block
    header = import_block.rstrip() + extra_imports

    slides_sel = slides_selection_line or 'SLIDES_SELECTION = "all"'
    bg = (bg_line or "").strip()
    if bg and not bg.endswith("\n"):
        bg += "\n"

    class_header = "class Presentation(Slide):\n"

    constants = (textwrap.indent(class_constants_block, "    ") + "\n") if class_constants_block else ""
    helpers = (textwrap.indent(helper_methods_block, "    ") + "\n") if helper_methods_block else ""

    construct_fn = textwrap.dedent(
        """\
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
        """
    )
    construct_indented = textwrap.indent(construct_fn, "    ")

    return "\n".join([
        header,
        "",
        bg,
        slides_sel,
        "",
        class_header,
        constants or "    pass  # (constants will be added below)\n",
        helpers,
        construct_indented,
        "",
    ])


def build_slide_module(import_block: str, slide_number: int, method_src: str) -> str:
    """
    Per-file module: reuse top import block + add decorator import.
    We keep the method body identical, just top-level and add @slide(n).
    """
    # Keep the user's imports (manim, colors, tikz, etc.) in each file for safety.
    # Add the registry decorator import.
    hdr = import_block.rstrip() + "\nfrom slide_registry import slide\n"
    decorated = f"@slide({slide_number})\n{method_src.strip()}\n"
    return f"{hdr}\n{decorated}"


def build_init_py(slide_numbers):
    lines = [f"from .s{n:02d} import *" for n in sorted(slide_numbers)]
    return "\n".join(lines) + ("\n" if lines else "")


def main():
    if not os.path.isfile(ENTRY_FILE):
        raise SystemExit(f"Cannot find {ENTRY_FILE} in current directory.")

    src = read_text(ENTRY_FILE)
    try:
        mod = ast.parse(src)
    except SyntaxError as e:
        raise SystemExit(f"Syntax error while parsing {ENTRY_FILE}: {e}")

    klass = find_presentation_class(mod)
    if not klass:
        raise SystemExit("Could not find class Presentation(Slide) in slides.py.")

    # Backup original
    if not os.path.exists(BACKUP_FILE):
        shutil.copyfile(ENTRY_FILE, BACKUP_FILE)

    import_block = extract_import_block(src)
    slides_selection_line, bg_line = extract_global_vars(src)
    class_constants_block, helper_methods_block = collect_non_slide_methods_and_constants(src, klass)
    slides = collect_slide_methods(src, klass)

    if not slides:
        raise SystemExit("No slide_XX methods found in Presentation. Nothing to split.")

    # 1) Write registry
    write_text(REGISTRY_FILE, build_registry_py())

    # 2) Write slide files
    os.makedirs(SRC_DIR, exist_ok=True)
    written = []
    for n, method_src in slides:
        out_path = os.path.join(SRC_DIR, f"s{n:02d}.py")
        write_text(out_path, build_slide_module(import_block, n, method_src))
        written.append(n)

    # 3) __init__.py importing all slides (ensures registration)
    write_text(os.path.join(SRC_DIR, "__init__.py"), build_init_py(written))

    # 4) New slides.py (entry point)
    new_slides_py = build_new_slides_py(
        import_block=import_block,
        slides_selection_line=slides_selection_line,
        bg_line=bg_line,
        class_constants_block=class_constants_block,
        helper_methods_block=helper_methods_block,
    )
    write_text(ENTRY_FILE, new_slides_py)

    print(f"Done. Backed up original to {BACKUP_FILE}.")
    print(f"Generated: {REGISTRY_FILE}, {SRC_DIR}/__init__.py and {len(written)} slide file(s).")
    print("Your build systems that call 'slides.py Presentation' remain valid.")


if __name__ == "__main__":
    main()
