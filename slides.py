# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.

import os

from manim import *
from manim_slides import Slide
from utils import parse_selection

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "1-3"


class Presentation(Slide):
    TEXT_SCALE = 0.9
    MAX_WIDTH = 12.0

    def construct(self):
        # Liste ordonnée des méthodes de slides (indexées à partir de 1)
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
        # Priorité à la variable d'env SLIDES si définie
        selection_str = os.environ.get("SLIDES", SLIDES_SELECTION)
        selection = parse_selection(selection_str, len(slides))

        for idx, fn in enumerate(slides, start=1):
            if idx in selection:
                fn()

    # --------- Utilitaires ---------
    def _show_text(self, content):
        """Affiche exactement le texte donné (str ou list[str]), sans animation."""
        if isinstance(content, list):
            sentence = "\n".join(content)
        else:
            sentence = content
        txt = Text(sentence, color=BLACK)
        if txt.width > self.MAX_WIDTH:
            txt.scale(self.MAX_WIDTH / txt.width)
        txt.scale(self.TEXT_SCALE)
        self.add(txt)
        self.pause()
        self.clear()

    # --------- Slides ---------
    def slide_01(self):
        self._show_text(
            "Titre (Thèse CIFRE, entre Poitiers, Angoulême et Strasbourg)"
        )
        self.next_slide()

    def slide_02(self):
        self._show_text(
            "Contexte : un besoin dans l'industrie navale avec de la formation à des maneuvres complexes."
        )
        self.next_slide()

    def slide_03(self):
        self._show_text(
            "Objectifs : réalisme, physique (pas rendu), 60 FPS, couplage solide/fluide..."
        )

    def slide_04(self):
        self._show_text(
            [
                "Sommaire pour répondre à ses objectifs :",
                "I) Couplages 3 méthodes grandes échelles",
                "II) Hybridation SPH/Airy",
            ]
        )
        self.next_slide()

    def slide_05(self):
        self._show_text("I) Introduction au calcul parallèle : CPU/GPU")
        self.next_slide()

    def slide_06(self):
        self._show_text(
            "Description d'un moteur de jeu : Unity et des compute shader (ses faiblesses et ses avantages)"
        )
        self.next_slide()

    def slide_07(self):
        self._show_text(
            "Présentation de CUDA (ses faiblesses et ses avantages)"
        )
        self.next_slide()

    def slide_08(self):
        self._show_text(
            "Motivation à IUC et présentation de ses principes (on verra des applications dans le reste de la présentation)"
        )
        self.next_slide()

    def slide_09(self):
        self._show_text(
            "Retour au problème de simu d'océan : présentation du principe des trois méthodes pour résoudre ça "
        )
        self.next_slide()

    def slide_10(self):
        self._show_text("Présentation de la méthode d'Airy en 2D")
        self.next_slide()

    def slide_11(self):
        self._show_text(
            "Présentation de la méthode de Tessendorf en 2D comme une généralisation d'Airy"
        )
        self.next_slide()

    def slide_12(self):
        self._show_text("Présentation du spectre d'océan")
        self.next_slide()

    def slide_13(self):
        self._show_text("Champs de hauteur et IFFT (avec IUC)")
        self.next_slide()

    def slide_14(self):
        self._show_text("Vitesse de l'océan")
        self.next_slide()

    def slide_15(self):
        self._show_text(
            "Pourquoi le couplage fluide/solide ne fonctionne pas avec Tessendorf et comment on va gérer ça"
        )
        self.next_slide()

    def slide_16(self):
        self._show_text("Fluide->Solide présentation de la méthode des forces")
        self.next_slide()

    def slide_17(self):
        self._show_text(
            "Solide->Fluide présentation du principe des vagues d'interactions"
        )
        self.next_slide()

    def slide_18(self):
        self._show_text("Calcul du masque")
        self.next_slide()

    def slide_19(self):
        self._show_text("Résultat de la combinaison des trois méthodes")
        self.next_slide()

    def slide_20(self):
        self._show_text(
            "II) Conclusion sur les trois méthodes, les faiblesses et pourquoi on veut passer à un cran supérieur. L'hybridation son prinicipe : SPH et Tessendorf"
        )
        self.next_slide()

    def slide_21(self):
        self._show_text(
            "SPH pas à pas : fluides représenté comme des particules, forces de gravité"
        )
        self.next_slide()

    def slide_22(self):
        self._show_text("SPH - Estimation en noyau pour la densité ")
        self.next_slide()

    def slide_23(self):
        self._show_text("SPH - Forces de pression")
        self.next_slide()

    def slide_24(self):
        self._show_text("SPH - Forces de viscosité")
        self.next_slide()

    def slide_25(self):
        self._show_text("SPH - Couplage avec solides")
        self.next_slide()

    def slide_26(self):
        self._show_text(
            "Optimisation avec la RPPV - explication rapide de la méthode en grille (sans parler de GPU)"
        )
        self.next_slide()

    def slide_27(self):
        self._show_text(
            "Expliquer qu'on souhaite mieux utiliser les spécificités du GPU pour la RPPV"
        )
        self.next_slide()

    def slide_28(self):
        self._show_text("Expliquer le concept de mémoire partagée")
        self.next_slide()

    def slide_29(self):
        self._show_text("Expliquer la méthode x-pencil")
        self.next_slide()

    def slide_30(self):
        self._show_text("Expliquer le lancer de rayon")
        self.next_slide()

    def slide_31(self):
        self._show_text(
            "Expliquer nos résultats sur le lancer de rayon pour la RRPV"
        )
        self.next_slide()

    def slide_32(self):
        self._show_text(
            "Hybridation - Rentrer plus dans les détails du principe : forces d'Airy et zones"
        )
        self.next_slide()

    def slide_33(self):
        self._show_text("Définir globalement formellement la force d'Airy")
        self.next_slide()

    def slide_34(self):
        self._show_text("Calcul de la vitesse d'Airy")
        self.next_slide()

    def slide_35(self):
        self._show_text("Facteur de modulation")
        self.next_slide()

    def slide_36(self):
        self._show_text("Expliquer les différentes zones et leurs objectifs")
        self.next_slide()

    def slide_37(self):
        self._show_text("Présenter le régulateur de particules")
        self.next_slide()

    def slide_38(self):
        self._show_text("Présenter les résultats de l'hybridation")
        self.next_slide()

    def slide_39(self):
        self._show_text("Conclusion")
        self.next_slide()

    def slide_40(self):
        self._show_text("Perspectives")
        self.next_slide()

    def slide_41(self):
        self._show_text("Remerciements")
        self.next_slide()
