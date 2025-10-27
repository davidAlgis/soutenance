# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.

import os

import numpy as np
import palette_colors as pc
from manim import *
from manim import logger
from manim_slides import Slide
from utils import parse_selection

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "2"


class Presentation(Slide):
    TEXT_SCALE = 0.9
    MAX_WIDTH = 12.0
    BODY_TOP_BUFF = 0.2  # space between bar and first line
    BODY_LINE_BUFF = 0.15  # space between lines
    DEFAULT_PAD = 0.3
    BODY_FONT_SIZE = 28

    def construct(self):
        slides = [
            self.slide_01,
            self.slide_02,
            self.slide_03,
            self.slide_04,
            self.slide_05,
            self.slide_06,
            self.slide_07,
            self.slide_08,
            self.slide_09,
            self.slide_10,
            self.slide_11,
            self.slide_12,
            self.slide_13,
            self.slide_14,
            self.slide_15,
            self.slide_16,
            self.slide_17,
            self.slide_18,
            self.slide_19,
            self.slide_20,
            self.slide_21,
            self.slide_22,
            self.slide_23,
            self.slide_24,
            self.slide_25,
            self.slide_26,
            self.slide_27,
            self.slide_28,
            self.slide_29,
            self.slide_30,
            self.slide_31,
            self.slide_32,
            self.slide_33,
            self.slide_34,
            self.slide_35,
            self.slide_36,
            self.slide_37,
            self.slide_38,
            self.slide_39,
            self.slide_40,
            self.slide_41,
        ]
        selection_str = os.environ.get("SLIDES", SLIDES_SELECTION)
        selection = parse_selection(selection_str, len(slides))
        for idx, fn in enumerate(slides, start=1):
            if idx in selection:
                fn()

    # --------- Utilitaires ---------

    def _top_bar(self, label: str, *, font_size: int = 48):
        h = config.frame_height / 10
        w = config.frame_width

        bar = Rectangle(
            width=w,
            height=h,
            fill_color=pc.blueGreen,
            fill_opacity=1.0,
            stroke_opacity=0.0,
        )

        elements = [bar]

        txt = Text(label, color=WHITE, weight=BOLD, font_size=font_size)
        txt.align_to(bar, LEFT)  # temp align; final after group placement
        elements.append(txt)

        group = VGroup(*elements)
        group.to_edge(UP, buff=0)

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

    # --------- Slides ---------
    def slide_01(self):
        self._show_text(
            "Titre (Thèse CIFRE, entre Poitiers, Angoulême et Strasbourg)"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_02(self):
        # Top bar with label (unchanged position)
        bar = self._top_bar("Contexte")
        self.add(bar)
        self.add_foreground_mobject(
            bar
        )  # ensure the bar stays on top visually

        # Initialize body flow under the bar
        self.start_body()
        self.add_body_text(
            "Formation en réalité virtuelle : manipulation complexe sur un navire", font_size=self.BODY_FONT_SIZE
        )

        # Decorative lines (their right endpoints will define the left corners of the new image)
        line1 = Line([-4.5, 0, 0], [-1, -2, 0], color=pc.blueGreen)
        line2 = Line([-4.5, 0.5, 0], [-1, 2, 0], color=pc.blueGreen)
        self.add(line1, line2)

        # --- Keep the existing left image ---
        img_left_path = "Figures/man_head_set.png"
        img_left = ImageMobject(img_left_path)
        img_left.to_edge(LEFT, buff=0.6)
        img_left.to_edge(DOWN, buff=0.1)
        img_left.scale(0.7)
        self.add(img_left)

        # --- Add the new image anchored to the two line endpoints ---
        # Target corners:
        #   left-lower  = (-1, -2, 0)
        #   left-upper  = (-1,  2, 0)
        # So the image height must be 4, centered at y = 0, and its left edge at x = -1.
        img_boat = ImageMobject("Figures/inside_boat.jpeg")
        img_boat.set_height(4.0)  # span from y=-2 to y=+2
        img_boat.set_y(0.0)  # vertical center at 0
        img_boat.set_x(
            -1.0 + img_boat.get_width() / 2.0
        )  # left edge exactly at x = -1

        # Surround the image with a blueGreen rectangle (tight fit)
        img_boat_box = SurroundingRectangle(
            img_boat, color=pc.blueGreen, buff=0.0, stroke_width=4
        )

        # Add without animation
        self.add(img_boat, img_boat_box)

        # Optional background helpers (kept as in your version)
        numberplane = NumberPlane(color=BLACK)
        self.add(numberplane)

        # End the slide
        self.pause()
        self.clear()
        self.next_slide()

    def slide_03(self):
        self._show_text(
            "Objectifs : réalisme, physique (pas rendu), 60 FPS, couplage solide/fluide..."
        )
        self.default_end_slide("Objectifs")

    def slide_04(self):
        self._show_text(
            [
                "Sommaire pour répondre à ses objectifs :",
                "I) Couplages 3 méthodes grandes échelles",
                "II) Hybridation SPH/Airy",
            ]
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_05(self):
        self._show_text("I) Introduction au calcul parallèle : CPU/GPU")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_06(self):
        self._show_text(
            "Description d'un moteur de jeu : Unity et des compute shader (ses faiblesses et ses avantages)"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_07(self):
        self._show_text(
            "Présentation de CUDA (ses faiblesses et ses avantages)"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_08(self):
        self._show_text(
            "Motivation à IUC et présentation de ses principes (on verra des applications dans le reste de la présentation)"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_09(self):
        self._show_text(
            "Retour au problème de simu d'océan : présentation du principe des trois méthodes pour résoudre ça "
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_10(self):
        self._show_text("Présentation de la méthode d'Airy en 2D")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_11(self):
        self._show_text(
            "Présentation de la méthode de Tessendorf en 2D comme une généralisation d'Airy"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_12(self):
        self._show_text("Présentation du spectre d'océan")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_13(self):
        self._show_text("Champs de hauteur et IFFT (avec IUC)")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_14(self):
        self._show_text("Vitesse de l'océan")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_15(self):
        self._show_text(
            "Pourquoi le couplage fluide/solide ne fonctionne pas avec Tessendorf et comment on va gérer ça"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_16(self):
        self._show_text("Fluide->Solide présentation de la méthode des forces")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_17(self):
        self._show_text(
            "Solide->Fluide présentation du principe des vagues d'interactions"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_18(self):
        self._show_text("Calcul du masque")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_19(self):
        self._show_text("Résultat de la combinaison des trois méthodes")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_20(self):
        self._show_text(
            "II) Conclusion sur les trois méthodes, les faiblesses et pourquoi on veut passer à un cran supérieur. L'hybridation son prinicipe : SPH et Tessendorf"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_21(self):
        self._show_text(
            "SPH pas à pas : fluides représenté comme des particules, forces de gravité"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_22(self):
        self._show_text("SPH - Estimation en noyau pour la densité ")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_23(self):
        self._show_text("SPH - Forces de pression")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_24(self):
        self._show_text("SPH - Forces de viscosité")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_25(self):
        self._show_text("SPH - Couplage avec solides")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_26(self):
        self._show_text(
            "Optimisation avec la RPPV - explication rapide de la méthode en grille (sans parler de GPU)"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_27(self):
        self._show_text(
            "Expliquer qu'on souhaite mieux utiliser les spécificités du GPU pour la RPPV"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_28(self):
        self._show_text("Expliquer le concept de mémoire partagée")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_29(self):
        self._show_text("Expliquer la méthode x-pencil")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_30(self):
        self._show_text("Expliquer le lancer de rayon")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_31(self):
        self._show_text(
            "Expliquer nos résultats sur le lancer de rayon pour la RRPV"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_32(self):
        self._show_text(
            "Hybridation - Rentrer plus dans les détails du principe : forces d'Airy et zones"
        )
        self.pause()
        self.clear()
        self.next_slide()

    def slide_33(self):
        self._show_text("Définir globalement formellement la force d'Airy")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_34(self):
        self._show_text("Calcul de la vitesse d'Airy")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_35(self):
        self._show_text("Facteur de modulation")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_36(self):
        self._show_text("Expliquer les différentes zones et leurs objectifs")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_37(self):
        self._show_text("Présenter le régulateur de particules")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_38(self):
        self._show_text("Présenter les résultats de l'hybridation")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_39(self):
        self._show_text("Conclusion")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_40(self):
        self._show_text("Perspectives")
        self.pause()
        self.clear()
        self.next_slide()

    def slide_41(self):
        self._show_text("Remerciements")
        self.pause()
        self.clear()
        self.next_slide()
