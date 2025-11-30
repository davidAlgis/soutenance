import numpy as np
from manim import BLACK, DOWN, UP, Create, FadeIn, ImageMobject, Tex, config
from slide_registry import slide


@slide(39)
def slide_39(self):
    """
    Merci (slide 41)

    - Top bar "Merci"
    - Text "Je vous remercie pour votre attention !" positioned below the bar.
    - Image "Figure/end_screen.jpeg" positioned below the text.
    """
    # Top bar
    bar, footer = self._top_bar("Merci")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]

    # Centered large text
    thanks = Tex(
        r"Je vous remercie pour votre attention !",
        color=BLACK,
        font_size=60,
    )
    # Place text below the bar
    thanks.next_to(bar_rect, DOWN, buff=0.5)

    # Load and position the image
    image = ImageMobject("Figures/end_screen.jpeg")
    # Place image below the text
    image.move_to([0, -0.7, 0])
    # image.next_to(thanks, DOWN, buff=0.0)
    image.scale(0.6)

    # Animate text and image
    self.play(
        FadeIn(thanks, shift=DOWN), FadeIn(image, shift=UP), run_time=1.0
    )
    self.wait(0.1)
