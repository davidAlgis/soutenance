import os

import numpy as np
from manim import (FadeIn, FadeOut, ImageMobject, Tex, ValueTracker, VGroup,
                   config)
from slide_registry import slide


@slide(38)
def slide_38(self):
    """
    Résultat de l'hybridation (slide 38).

    Steps:
      1) Top bar.
      2) Show 'Figures/surface_particles_mean.jpeg' centered, scaled to fit
         within the slide with a small padding on all sides.
      3) Next slide -> remove the first figure, show 'Figures/rb_pos.jpeg'
         with the same padding rule.
      4) Next slide -> remove the second figure, then play 'Figures/hybrid.gif'
         with near-white set transparent. The GIF fills the slide horizontally:
            - no padding on left, right, and bottom,
            - a small padding below the top bar (top aligned to this line).
    """
    # --- Top bar ---
    bar = self._top_bar("Résultat de l'hybridation")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]

    # Slide geometry
    full_w = config.frame_width
    full_h = config.frame_height

    # Small generic padding for still images
    PAD_ALL = 0.3

    # For the GIF: no padding on left/right/bottom, keep a small top padding
    TOP_GIF_PAD = 0.15

    # Usable rect for still images (with padding on all sides)
    left_x_img = -full_w * 0.5 + PAD_ALL
    right_x_img = full_w * 0.5 - PAD_ALL
    bottom_y_img = -full_h * 0.5 + PAD_ALL
    top_y_img = bar_rect.get_bottom()[1] - PAD_ALL

    usable_w_img = max(0.01, right_x_img - left_x_img)
    usable_h_img = max(0.01, top_y_img - bottom_y_img)
    center_img = np.array([0.0, 0.5 * (top_y_img + bottom_y_img), 0.0])

    # Helper to load/show a still image to fit in the padded area
    def image_fit_center(path: str):
        if not os.path.isfile(path):
            msg = Tex(f"Fichier manquant : {path}", font_size=36)
            msg.move_to(center_img)
            return msg
        mob = ImageMobject(path)
        # Scale to fit within usable rect (preserve aspect)
        if mob.width > 0:
            mob.scale(usable_w_img / mob.width)
        if mob.height > usable_h_img:
            mob.scale(usable_h_img / mob.height)
        mob.move_to(center_img)
        return mob

    # --- 1) First still image
    im1_path = "Figures/surface_particles_mean.jpeg"
    im1 = image_fit_center(im1_path)
    self.play(FadeIn(im1, run_time=0.3))  # ensure at least one animation
    self.next_slide()

    # --- 2) Second still image (swap)
    im2_path = "Figures/rb_pos.jpeg"
    im2 = image_fit_center(im2_path)
    self.play(FadeOut(im1, run_time=0.25), FadeIn(im2, run_time=0.25))
    self.next_slide()

    # --- 3) GIF with white made transparent, filling the slide width (no L/R/B padding),
    #         aligned so the top sits just under the bar (keep small top padding).
    # Remove second image
    self.play(FadeOut(im2, run_time=0.25))

    # GIF usable "frame"
    left_x_gif = -full_w * 0.5
    right_x_gif = full_w * 0.5
    bottom_y_gif = -full_h * 0.5
    top_y_gif = bar_rect.get_bottom()[1] - TOP_GIF_PAD

    usable_w_gif = max(0.01, right_x_gif - left_x_gif)  # == full_w
    # Height is not constrained; we align top to top_y_gif and allow it to extend downward.

    # Load GIF frames and build transparent ImageMobjects
    from PIL import Image, ImageSequence

    gif_path = "Figures/hybrid.gif"
    if not os.path.isfile(gif_path):
        # Graceful fallback
        msg = Tex("Fichier manquant : Figures/hybrid.gif", font_size=36)
        msg.move_to(np.array([0.0, 0.5 * (top_y_gif + bottom_y_gif), 0.0]))
        self.play(FadeIn(msg, run_time=0.2))
        self.next_slide()
        return

    pil_img = Image.open(gif_path)
    pil_frames = []
    durations = []
    for frame in ImageSequence.Iterator(pil_img):
        dur_ms = frame.info.get("duration", 100)
        durations.append(max(0.01, dur_ms / 1000.0))
        pil_frames.append(frame.convert("RGBA"))

    # Key near-white to transparent
    def rgba_white_to_alpha(arr_rgba: np.ndarray, tol=14) -> np.ndarray:
        arr = arr_rgba.copy()
        rgb = arr[..., :3]
        a = arr[..., 3]
        mask = (
            (rgb[..., 0] >= 255 - tol)
            & (rgb[..., 1] >= 255 - tol)
            & (rgb[..., 2] >= 255 - tol)
        )
        a[mask] = 0
        arr[..., 3] = a
        return arr

    # Build ImageMobjects for each frame, scaled to fill FULL WIDTH.
    # Then align each frame's TOP to top_y_gif (small padding under the bar).
    frames_mobs = []
    for fr in pil_frames:
        arr = np.array(fr, dtype=np.uint8)
        arr = rgba_white_to_alpha(arr, tol=14)
        mob = ImageMobject(arr)
        if mob.width > 0:
            mob.scale(usable_w_gif / mob.width)  # force full width
        # Align top to the padded top line
        dy = top_y_gif - mob.get_top()[1]
        mob.shift(np.array([0.0, dy, 0.0]))
        frames_mobs.append(mob)

    if not frames_mobs:
        msg = Tex("Impossible de lire : Figures/hybrid.gif", font_size=36)
        msg.move_to(np.array([0.0, 0.5 * (top_y_gif + bottom_y_gif), 0.0]))
        self.play(FadeIn(msg, run_time=0.2))
        self.next_slide()
        return

    # Single display object driven by time
    display = frames_mobs[0].copy()
    self.add(display)

    durations = np.array(durations, dtype=float)
    cum = np.cumsum(durations)
    total = float(cum[-1])
    t = ValueTracker(0.0)

    def idx_from_time(tt: float) -> int:
        if total <= 0.0:
            return 0
        x = tt % total
        i = int(np.searchsorted(cum, x, side="right"))
        return min(i, len(frames_mobs) - 1)

    def updater(m):
        m.become(frames_mobs[idx_from_time(t.get_value())])

    display.add_updater(updater)

    # Play one full pass
    self.play(t.animate.set_value(total), run_time=total)
    # --- End of slide ---
    self.pause()
    self.clear()
    self.next_slide()
