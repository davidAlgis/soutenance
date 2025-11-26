import os
import subprocess

from pdf2image import convert_from_path

# 1. Define the LaTeX content
latex_code = r"""
\documentclass[preview,varwidth=16cm]{standalone}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{array}
\usepackage[table]{xcolor}
\usepackage{colortbl}
\usepackage{hhline} % <--- REQUIRED FOR LINES OVER COLORS

% Define the custom colors
\definecolor{blueGreen}{rgb}{0.12,0.61,0.73}
\definecolor{cornFlower}{rgb}{0.55,0.79,0.90}

\begin{document}

\setlength{\columnwidth}{15cm}
\renewcommand{\arraystretch}{1.3}

\begin{figure}
    \centering
    \begin{tabular}{|p{0.28\columnwidth}|p{0.24\columnwidth}|>{\centering\arraybackslash}p{0.14\columnwidth}|>{\centering\arraybackslash}p{0.14\columnwidth}|}
        \hline
        \rowcolor{blueGreen} & & 1 solide & 10 solides \\
        \hline
        Méthode de Tessendorf & Hauteur & 0{,}376 & 0{,}376 \\
        
        % REPLACED \cline{2-4} WITH \hhline
        % ~ means "no line in this column"
        % - means "line in this column"
        % | preserves the vertical bars
        \hhline{~|-|-|-|} 
        
        & Vitesse & 1{,}175 & 1{,}175 \\
        
        \hhline{~|-|-|-|}
        
        & \cellcolor{cornFlower}Total &\cellcolor{cornFlower} 1{,}551 & \cellcolor{cornFlower}1{,}551 \\
        \hline
        Couplage fluide-solide & Géométrie & 1{,}125 & 4{,}588 \\
        
        \hhline{~|-|-|-|}
        
        & Forces & 0{,}406 & 3{,}677 \\
        
        \hhline{~|-|-|-|}
        
        & \cellcolor{cornFlower}Total & \cellcolor{cornFlower}1{,}531 & \cellcolor{cornFlower}8{,}265 \\
        \hline
        Couplage solide-fluide & MDF & 0{,}100 & 0{,}831 \\
        
        \hhline{~|-|-|-|}
        
        & Masque & 0{,}238 & 1{,}656 \\
        
        \hhline{~|-|-|-|}
        
        & \cellcolor{cornFlower}Total & \cellcolor{cornFlower}0{,}338 & \cellcolor{cornFlower}2{,}487 \\
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
