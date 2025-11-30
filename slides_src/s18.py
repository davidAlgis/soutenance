# thesis_slides.py (now supports selective rendering)
# 41 slides pour manim-slides, 1 slide = 1 méthode, aucun effet ni animation.
# Texte conservé exactement tel qu'écrit par l'utilisateur.

# flake8: noqa: F405
import os

import numpy as np
import palette_colors as pc
from manim import *
from manim import logger
from manim_slides import Slide
from manim_tikz import Tikz
from PIL import Image, ImageSequence
from slide_registry import slide
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)


@slide(18)
def slide_18(self):
    """
    Slide 19: Result of combining the three methods.
    Implements solid and dotted curved arrows with corrected placement:
    (1) Surface -> Fluide-vers-solide (ok),
    (2) Fluide-vers-solide -> Solide-vers-fluide now ends on RIGHT side of S->F,
    (3) Solide-vers-fluide -> Surface (ok),
    (4) DOTTED S->F -> F->S now inner and higher,
    (5) DOTTED S->F -> Surface inner and shifted to the right,
    (6) DOTTED F->S -> Surface inner and shifted to the left.
    Then: summary table, demo image, and final bullets.
    """
    # --- Top bar -----------------------------------------------------------
    bar, footer = self._top_bar(
        "Résultats de la combinaison des trois méthodes"
    )
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Ellipses (same spirit as slide 9) --------------------------------
    ell_w = 3.6
    ell_h = 2.8

    e_surface = Ellipse(
        width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
    )
    t_surface = Tex(
        "Simulation de surface", font_size=self.BODY_FONT_SIZE, color=BLACK
    )
    t_surface.move_to(e_surface.get_center())
    g_surface = VGroup(e_surface, t_surface).move_to([0.0, 1.3, 0.0])

    e_f2s = Ellipse(
        width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
    )
    t_f2s = Tex(
        "Solide vers fluide", font_size=self.BODY_FONT_SIZE, color=BLACK
    )
    t_f2s.move_to(e_f2s.get_center())
    g_f2s = VGroup(e_f2s, t_f2s).move_to([3.6, -1.7, 0.0])

    e_s2f = Ellipse(
        width=ell_w, height=ell_h, color=pc.blueGreen, stroke_width=7
    )
    t_s2f = Tex(
        "Fluide vers solide", font_size=self.BODY_FONT_SIZE, color=BLACK
    )
    t_s2f.move_to(e_s2f.get_center())
    g_s2f = VGroup(e_s2f, t_s2f).move_to([-3.6, -1.7, 0.0])

    self.play(Create(e_surface), FadeIn(t_surface), run_time=0.4)
    self.play(Create(e_f2s), FadeIn(t_f2s), run_time=0.4)
    self.play(Create(e_s2f), FadeIn(t_s2f), run_time=0.4)
    self.wait(0.1)

    # --- Arrow builders ----------------------------------------------------
    def _solid_curved_arrow(
        start_pt: np.ndarray, end_pt: np.ndarray, angle: float
    ) -> CurvedArrow:
        """
        Solid curved arrow between two points with a signed curvature angle.
        Positive angle is counter-clockwise, negative is clockwise.
        """
        return CurvedArrow(
            start_point=start_pt,
            end_point=end_pt,
            angle=angle,
            color=BLACK,
            stroke_width=6,
            tip_length=0.16,
        )

    def _right_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
        p = m.get_right().copy()
        p[0] += dx
        p[1] += dy
        return p

    def _left_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
        p = m.get_left().copy()
        p[0] += dx
        p[1] += dy
        return p

    def _top_of(m: Mobject, dx: float = 0.0, dy: float = 0.0) -> np.ndarray:
        p = m.get_top().copy()
        p[0] += dx
        p[1] += dy
        return p

    # ================= SOLID arrows =================
    # (1) Surface -> F->S (unchanged, correct)
    self.next_slide()
    a1 = _solid_curved_arrow(
        end_pt=_top_of(e_s2f, dx=0.10, dy=0.10),
        start_pt=_left_of(e_surface, dx=-0.10, dy=-0.10),
        angle=1.0,
    )
    self.play(Create(a1, run_time=0.6))

    # (2) F->S -> S->F : origin ok, now end on RIGHT side of S->F
    self.next_slide()
    a2 = _solid_curved_arrow(
        start_pt=_right_of(e_s2f, dx=0.0, dy=-0.6),  # moved to right side
        end_pt=_left_of(e_f2s, dx=0.0, dy=-0.6),
        angle=1.0,  # under-arc clockwise
    )
    self.play(Create(a2, run_time=0.6))

    # (3) S->F -> Surface (unchanged, correct)
    self.next_slide()
    a3 = _solid_curved_arrow(
        start_pt=_top_of(e_f2s, dx=-0.10, dy=0.10),
        end_pt=_right_of(e_surface, dx=0.10, dy=-0.10),
        angle=1.0,
    )
    self.play(Create(a3, run_time=0.6))

    self.wait(0.1)

    # --- Clear all except the bar -----------------------------------------
    self.next_slide()
    to_keep = {bar, footer}
    self.remove(*[m for m in self.mobjects if m not in to_keep])

    # --- Image Insertion (replaces table) -------------------
    img = ImageMobject("Figures/result_arc_blanc.png")

    # 1. Calculate constraints based on the bar and footer positions
    top_y = bar.get_bottom()[1]
    bottom_y = footer.get_top()[1]

    img.scale(1.1)
    # 5. Center the image vertically between bar and footer
    center_y = (top_y + bottom_y) / 2
    img.move_to([0, center_y, 0])

    # 6. Display
    self.play(FadeIn(img))
    self.wait(2.0)
    self.add_credit(r"Algis \textit{et al.}, \textit{JCGT}, 2025")

    self.next_slide()
    self.remove(*[m for m in self.mobjects if m not in to_keep])

    gif_path = "Figures/lateral_moving_boat.gif"

    # Ensure we have the bar rect (height is used for available space)
    bar_rect = bar.submobjects[0]

    pil_img = Image.open(gif_path)
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(pil_img):
        durations.append(max(0.01, frame.info.get("duration", 100) / 1000.0))
        frames.append(frame.convert("RGBA"))

    # Build ImageMobjects scaled like the still image (fit 92% area, same offset)
    mobs = []
    for fr in frames:
        arr = np.array(fr, dtype=np.uint8)
        mob = ImageMobject(arr)

        mob.scale(2.1).move_to([0.0, -0.1, 0.0])
        mobs.append(mob)

    display = mobs[0].copy()
    self.play(FadeIn(display, run_time=0.3))

    durations = np.array(durations, dtype=float)
    cum = np.cumsum(durations)
    total = float(cum[-1])
    t = ValueTracker(0.0)

    def idx_from_time(tt: float) -> int:
        if total <= 0.0:
            return 0
        x = tt % total
        i = int(np.searchsorted(cum, x, side="right"))
        return min(i, len(mobs) - 1)

    def updater(m):
        m.become(mobs[idx_from_time(t.get_value())])

    display.add_updater(updater)

    # Play one full loop of the GIF
    self.play(t.animate.set_value(total), run_time=total)
    self.next_slide()

    display.clear_updaters()
    self.play(FadeOut(display, run_time=0.25))

    self.remove(*[m for m in self.mobjects if m not in to_keep])

    # --- Bullet points (using utils.make_bullet_list) ---------------------------
    bullet_items = [
        r"La méthode de Tessendorf repose sur de très nombreuses approximations",
        r"Les méthodes de couplage se basent sur des modèles phénoménologiques",
    ]
    bullets = make_bullet_list(
        bullet_items,
        bullet_color=pc.blueGreen,
        font_size=self.BODY_FONT_SIZE,
        line_gap=0.20,
        left_pad=0.25,
    )
    bullets.next_to(
        self._current_bar, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT
    )
    dx2 = (
        -config.frame_width / 2 + 0.6 + self.DEFAULT_PAD
    ) - bullets.get_left()[0]
    bullets.shift(RIGHT * dx2)
    self.play(FadeIn(bullets, shift=RIGHT * self.SHIFT_SCALE), run_time=0.5)

    # 1. Calculate available vertical space
    # We assume 'footer' exists from your _top_bar call
    y_top = bullets.get_bottom()[1]
    y_bottom = footer.get_top()[1]
    available_h = y_top - y_bottom
    center_y = (y_top + y_bottom) / 2

    # Define center point for the triangle
    tri_center = np.array([0.0, center_y, 0.0])

    # 2. Define Geometry sizes
    # Restrict size to fit height with padding, or width constraints
    tri_size = min(config.frame_width * 0.5, available_h * 0.75)
    htri = np.sqrt(3) / 2 * tri_size

    # Calculate vertices relative to the calculated center
    # Note: We center the bounding box of the triangle, not the centroid,
    # to make it look visually centered between text and footer.
    V_top = tri_center + np.array([0.0, htri / 2, 0.0])
    V_bl = tri_center + np.array([-tri_size / 2, -htri / 2, 0.0])
    V_br = tri_center + np.array([tri_size / 2, -htri / 2, 0.0])

    tri = Polygon(V_top, V_br, V_bl, stroke_color=pc.blueGreen, stroke_width=6)

    # 3. Labels
    fs_lab = max(22, self.BODY_FONT_SIZE - 4)

    lab_top = Tex(r"Pr{\'e}c.", color=pc.blueGreen, font_size=fs_lab).next_to(
        V_top, UP, buff=0.10
    )
    lab_bl = Tex(r"Perf.", color=pc.blueGreen, font_size=fs_lab).next_to(
        V_bl, DOWN, buff=0.10
    )
    lab_br = Tex(r"{\'E}ch.", color=pc.blueGreen, font_size=fs_lab).next_to(
        V_br, DOWN, buff=0.10
    )

    tri_group = VGroup(tri, lab_top, lab_bl, lab_br)

    self.play(
        FadeIn(tri_group, run_time=0.6),
        rate_func=linear,
    )

    # Target: Midpoint of bottom edge + slight offset up/right
    # Adjusted offset slightly to be proportional to tri_size if needed,
    # but keeping your fixed offset logic which usually works well.
    target = 0.5 * (V_bl + V_br) + np.array([0.2, 0.5, 0.0])
    cross_len = tri_size * 0.06
    cross = VGroup(
        Line(
            target + np.array([-cross_len, -cross_len, 0.0]),
            target + np.array([cross_len, cross_len, 0.0]),
            stroke_color=pc.jellyBean,
            stroke_width=6,
        ),
        Line(
            target + np.array([-cross_len, cross_len, 0.0]),
            target + np.array([cross_len, -cross_len, 0.0]),
            stroke_color=pc.jellyBean,
            stroke_width=6,
        ),
    )
    self.play(Create(cross, run_time=0.35), rate_func=linear)

    # 5. Move Cross Animation
    self.wait(0.1)
    self.next_slide()

    target_again = 0.5 * (V_bl + V_top) + np.array([0.5, 0.1, 0.0])
    self.play(
        cross.animate.move_to(target_again), run_time=0.6, rate_func=linear
    )

    self.pause()
    self.clear()
    self.next_slide()
