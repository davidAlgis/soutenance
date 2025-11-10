import palette_colors as pc
from manim import BLACK, DOWN, LEFT, RIGHT, FadeIn, Text, VGroup, config
from slide_registry import slide
from utils import make_bullet_list


@slide(39)
def slide_39(self):
    """
    Conclusion (slide 39).

    - Top bar "Conclusion"
    - Title sentence under the bar, left-aligned to the slide's inner padding
    - Bullet list built with utils.make_bullet_list (blueGreen triangles)
    """
    # --- Top bar
    bar = self._top_bar("Conclusion")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Body start & left baseline (set by _top_bar)
    self.start_body()

    # Title sentence
    title = Text(
        "Cette thèse a mené aux contributions suivantes :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    # Place under bar, left-aligned to inner padding
    title.next_to(
        self._current_bar,
        direction=DOWN,
        buff=self.BODY_TOP_BUFF,
        aligned_edge=LEFT,
    )
    # Align left edge to bar's inner padding
    dx = self._text_left_x - title.get_left()[0]
    title.shift(dx * RIGHT)
    self.add(title)

    # Bullet items
    items = [
        "La bibliothèque InteropUnityCUDA",
        "Le calcul de la vitesse de l'océan en temps réel",
        "Les expressions des forces pour le couplage fluide vers solides",
        "Le masque pour l'entrée du couplage solide vers fluides",
        "Les interactions entre les trois méthodes",
        "L'utilisation de la mémoire partagée pour la RPPV",
        "L'utilisation des c\\oe ur RT pour la RPPV",
        "Un modèle théorique pour l'hybridation entre des modèles de vagues et SPH",
    ]

    bullets = make_bullet_list(
        items,
        bullet_color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
        line_gap=self.BODY_LINE_BUFF,
        left_pad=0.25,
    )
    bullets.next_to(title, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)

    # Keep bullets left-aligned to inner padding
    bdx = self._text_left_x - bullets.get_left()[0]
    bullets.shift(bdx * RIGHT)
    self.add(bullets)

    # A tiny animation to satisfy manim-slides before pausing
    self.play(FadeIn(VGroup(title, bullets), run_time=0.2))
    self.pause()
    self.clear()
    self.next_slide()
