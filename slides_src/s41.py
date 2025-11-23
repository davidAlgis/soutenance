import numpy as np
from manim import BLACK, UP, Create, FadeIn, Tex, config
from slide_registry import slide


@slide(41)
def slide_41(self):
    """
    Merci (slide 41)

    - Top bar "Merci"
    - Centered (in the remaining area below the bar) large text:
      "Je vous remercie pour votre attention."
    """
    # Top bar
    bar, footer = self._top_bar("Merci")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]

    # Compute the vertical center of the usable area (below the bar)
    full_h = config.frame_height
    bottom_y = -full_h * 0.5
    top_y = bar_rect.get_bottom()[1]
    center_y = (top_y + bottom_y) * 0.5 + 0.5

    # Centered large text
    thanks = Tex(
        r"Je vous remercie pour votre attention !",
        color=BLACK,
        font_size=60,
    )
    # Place at horizontal center, and vertically centered in the remaining area
    thanks.move_to(np.array([0.0, center_y, 0.0]))

    # A gentle fade-in looks nice; remove if you prefer static add()
    self.play(FadeIn(thanks, shift=UP), run_time=1.0)
    self.wait(0.1)
