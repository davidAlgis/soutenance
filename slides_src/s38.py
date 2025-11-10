import os

import numpy as np
from manim import FadeIn, FadeOut, ImageMobject, Tex, ValueTracker, config
from slide_registry import slide


@slide(38)
def slide_38(self):
    """
    Resultat de l'hybridation (slide 38).

    Performance-friendly GIF playback with white made transparent:
      - Preload + scale frames once.
      - Convert each RGBA frame so near-white pixels (background) become alpha=0.
      - Drive a single ImageMobject via a ValueTracker-based updater.

    Behavior:
      - Top bar "Resultat de l'hybridation".
      - Plays Figures/hybrid.gif below the bar, scaled to fit.
    """
    # --- Top bar ---
    bar = self._top_bar("Resultat de l'hybridation")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]

    # --- Usable area below bar ---
    full_w = config.frame_width
    full_h = config.frame_height
    left_x = -full_w * 0.5 + 0.3
    right_x = full_w * 0.5 - 0.3
    bottom_y = -full_h * 0.5 + 0.3
    top_y = bar_rect.get_bottom()[1] - 0.15
    usable_w = right_x - left_x
    usable_h = top_y - bottom_y
    center_xy = np.array([0.0, (top_y + bottom_y) * 0.5, 0.0])

    # --- Load GIF frames ---
    from PIL import Image, ImageSequence

    gif_path = "Figures/hybrid.gif"
    if not os.path.isfile(gif_path):
        msg = Tex("Fichier manquant : Figures/hybrid.gif", font_size=36)
        msg.move_to(center_xy)
        self.add(msg)
        self.play(FadeIn(msg, run_time=0.2))  # ensure at least one animation
        self.next_slide()
        return

    pil_img = Image.open(gif_path)

    # Collect frames + native frame durations (sec)
    pil_frames = []
    durations = []
    for frame in ImageSequence.Iterator(pil_img):
        dur_ms = frame.info.get("duration", 100)
        durations.append(max(0.01, dur_ms / 1000.0))
        pil_frames.append(frame.convert("RGBA"))

    if not pil_frames:
        msg = Tex("Impossible de lire : Figures/hybrid.gif", font_size=36)
        msg.move_to(center_xy)
        self.add(msg)
        self.play(FadeIn(msg, run_time=0.2))
        self.next_slide()
        return

    # --- Compute target size once (preserve aspect) ---
    w0, h0 = pil_frames[0].size
    aspect = w0 / max(1, h0)
    target_w = min(usable_w, usable_h * aspect)
    target_h = target_w / aspect

    # --- Helper: key out near-white to transparent (alpha=0) ---
    def rgba_with_white_transparent(img_rgba, tol=14):
        """
        Convert PIL RGBA -> numpy RGBA and make near-white pixels transparent.
        tol: 0..255; higher = more aggressive (default 14 is mild).
        """
        arr = np.array(img_rgba, dtype=np.uint8)  # HxWx4
        rgb = arr[..., :3]
        a = arr[..., 3:4]

        # A pixel is "near white" if all three channels are above 255 - tol
        mask = (
            (rgb[..., 0] >= 255 - tol)
            & (rgb[..., 1] >= 255 - tol)
            & (rgb[..., 2] >= 255 - tol)
        )

        # Zero the alpha for those pixels
        a[mask] = 0
        arr[..., 3] = a[..., 0]
        return arr

    # --- Precreate scaled ImageMobjects with transparency applied ---
    frames_mobs = []
    for fr in pil_frames:
        # Key the white to transparent
        arr_rgba = rgba_with_white_transparent(fr, tol=14)
        mob = ImageMobject(arr_rgba)

        # Scale to fit usable area (preserve aspect)
        if mob.width > 0:
            mob.scale(target_w / mob.width)
        if mob.height > target_h:
            mob.scale(target_h / mob.height)

        mob.move_to(center_xy)
        frames_mobs.append(mob)

    # --- Single display object that swaps content via updater ---
    display = frames_mobs[0].copy()
    self.add(display)

    # Build timeline (cumulative durations)
    durations = np.array(durations, dtype=float)
    cum = np.cumsum(durations)
    total = float(cum[-1])
    t = ValueTracker(0.0)

    def frame_index_from_time(tt: float) -> int:
        if total <= 0.0:
            return 0
        x = tt % total
        idx = int(np.searchsorted(cum, x, side="right"))
        if idx >= len(frames_mobs):
            idx = len(frames_mobs) - 1
        return idx

    def display_updater(m):
        m.become(frames_mobs[frame_index_from_time(t.get_value())])

    display.add_updater(display_updater)

    # Play one full pass at native speed (ensures an animation before pause)
    self.play(t.animate.set_value(total), run_time=total)

    # Hold briefly
    self.wait(0.2)
    self.next_slide()

    # Clean exit
    display.clear_updaters()
    self.play(FadeOut(display, run_time=0.3))
    self.clear()
    self.next_slide()
