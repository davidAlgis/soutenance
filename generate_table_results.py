import os
import subprocess

from pdf2image import convert_from_path

# 1. Define the LaTeX content
latex_code = r"""
% CHANGE HERE: varwidth=16cm gives the page enough "canvas" to hold your 21cm columns
\documentclass[preview,varwidth=16cm]{standalone} 

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage{colortbl}

% Define the custom color
\definecolor{blueGreen}{rgb}{0.12,0.61,0.73}

\begin{document}

% You set this to 21cm (A4 width), so the table calculates widths based on this.
\setlength{\columnwidth}{15cm} 
\renewcommand{\arraystretch}{1.3}

\begin{figure}
    \centering
    % The sum of your columns is 0.28+0.24+0.14+0.14 = 0.8 (80% of columnwidth)
    \begin{tabular}{|p{0.28\columnwidth}|p{0.24\columnwidth}|>{\centering\arraybackslash}p{0.14\columnwidth}|>{\centering\arraybackslash}p{0.14\columnwidth}|}
        \hline
        & & 1 solides & 10 solides \\
        \hline
        Méthode de Tessendorf & Hauteur & 0{,}376 & 0{,}376 \\
        \cline{2-4}
        & Vitesse & 1{,}175 & 1{,}175 \\
        \cline{2-4}
        & Total & 1{,}551 & 1{,}551 \\
        \hline
        Couplage fluide-solide & Géométrie & 1{,}125 & 4{,}588 \\
        \cline{2-4}
        & Forces & 0{,}406 & 3{,}677 \\
        \cline{2-4}
        & Total & 1{,}531 & 8{,}265 \\
        \hline
        Couplage solide-fluide & MDF & 0{,}100 & 0{,}831 \\
        \cline{2-4}
        & Masque & 0{,}238 & 1{,}656 \\
        \cline{2-4}
        & Total & 0{,}338 & 2{,}487 \\
        \hline
        \rowcolor{blueGreen}\textbf{Total} & & \textbf{3{,}414} & \textbf{12{,}297} \\
        \hline
    \end{tabular}
\end{figure}

\end{document}
"""

filename = "result_arc_blanc"
path_image = "Figures/result_arc_blanc.png"


def compile_and_convert():
    # Step 1: Write the .tex file
    with open(f"{filename}.tex", "w", encoding="utf-8") as f:
        f.write(latex_code)
    print(f"Created {filename}.tex")

    # Step 2: Run pdflatex
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"{filename}.tex"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print("Compilation successful.")
    except subprocess.CalledProcessError:
        print("Error: LaTeX compilation failed.")
        return
    except FileNotFoundError:
        print("Error: pdflatex not found.")
        return

    # Step 3: Convert PDF to PNG
    try:
        # dpi=300 is standard print quality.
        images = convert_from_path(f"{filename}.pdf", dpi=300)
        if images:
            images[0].save(path_image, "PNG")
            print(f"Success! Image saved as {path_image}")
    except Exception as e:
        print(f"Error converting PDF to Image: {e}")

    # Cleanup
    for ext in [".aux", ".log", ".tex", ".pdf"]:
        if os.path.exists(filename + ext) and ext != ".png":
            os.remove(filename + ext)


if __name__ == "__main__":
    compile_and_convert()
