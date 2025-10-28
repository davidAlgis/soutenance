# template.py
from typing import List, Optional

from manim.utils.tex import TexTemplate


class TikzTemplate(TexTemplate):
    def __init__(
        self,
        packages: Optional[List[str]] = None,
        libraries: Optional[List[str]] = None,
        tikzset: Optional[List[str]] = None,
        preamble: Optional[str] = None,
        use_pdf: bool = False,
        **kwargs,
    ):
        # Avoid None vs list issues
        packages = packages or []
        libraries = libraries or []
        tikzset = tikzset or []

        # Manim's default LaTeX preamble (NOT self.default_preamble)
        # Option A: a fresh TexTemplate()
        base_preamble = TexTemplate().preamble
        # Option B (also fine): from the global config template
        # from manim import config
        # base_preamble = config.tex_template.preamble

        extra = []
        if packages:
            extra.append("\\usepackage{" + ",".join(packages) + "}")
        if libraries:
            extra.append("\\usetikzlibrary{" + ",".join(libraries) + "}")
        if tikzset:
            extra.append("\\tikzset{" + ",\n".join(tikzset) + "}")
        if preamble:
            extra.append(preamble)

        full_preamble = base_preamble + (
            "\n" + "\n".join(extra) if extra else ""
        )

        super().__init__(
            tex_compiler="pdflatex" if use_pdf else "latex",
            documentclass="\\documentclass[preview,tikz]{standalone}",
            output_format=".pdf" if use_pdf else ".dvi",
            preamble=full_preamble,
            **kwargs,
        )
