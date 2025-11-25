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


@slide(9)
def slide_09(self):
    """
    Slide 9: State of the art methods.
    3 Phases:
      1. Surface Simulation (Static Image)
      2. Fluid -> Solid (GIF)
      3. Solid -> Fluid (Static Image)
    """
    # --- Top bar ---------------------------------------------------------
    bar, footer = self._top_bar(
        "Trois méthodes de l'état de l'art pour la simulation d'océan"
    )
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Layout Calculations ---------------------------------------------
    bar_rect = bar.submobjects[0]
    y_top = bar_rect.get_bottom()[1] - 0.15
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6

    # Split screen: Left side for Text, Right side for Image
    mid_x = 0.0
    text_anchor_x = x_left + 0.2

    # Placeholder for Image Positioning (Right side, centered vertically in remaining space)
    y_bottom = -config.frame_height / 2 + 0.6
    img_center = np.array([x_right - 3.5, (y_top + y_bottom) / 2 - 1.0, 0])
    img_width_max = 6.0

    # Helper to create the title text
    def create_title(text_str):
        t = Tex(
            text_str,
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        # Left align to margin, Top align below bar
        t.next_to(bar_rect, DOWN, buff=0.4, aligned_edge=LEFT)
        # Correct X alignment manually if needed to match padding
        dx = text_anchor_x - t.get_left()[0]
        t.shift(RIGHT * dx)
        return t

    # Helper to create bullet lists
    def create_bullets(items):
        lst = make_bullet_list(
            items,
            bullet_color=pc.blueGreen,
            font_size=self.BODY_FONT_SIZE - 4,  # Slightly smaller to fit names
            line_gap=0.35,
            left_pad=0.22,
        )
        return lst

    # =====================================================================
    # PHASE 1: Surface Simulation
    # =====================================================================

    # 1. Title
    title_1 = create_title("État de l'art de la simulation de surface :")
    self.play(FadeIn(title_1, shift=RIGHT * self.SHIFT_SCALE))

    # 2. Bullets
    items_1 = [
        "Tessendorf, \\textit{SIGGRAPH}, 2001",
        "Dupuy et Bruneton, \\textit{SIGGRAPH Asia}, 2012",
        "Horvath, \\textit{DigiPro}, 2015",
        "Lutz \\textit{et al.}, \\textit{ACMCGIT}, 2024",
    ]
    bullets_1 = create_bullets(items_1)
    bullets_1.next_to(title_1, DOWN, buff=0.5, aligned_edge=LEFT)
    # Align bullets left edge to title left edge + indent
    bullets_1.shift(RIGHT * 0.2)

    self.play(FadeIn(bullets_1, shift=RIGHT * self.SHIFT_SCALE))

    # 3. Image (Lutz)
    img_path_1 = "Figures/lutz_ocean.jpeg"
    if os.path.exists(img_path_1):
        img_1 = ImageMobject(img_path_1)
        img_1.width = img_width_max
        img_1.move_to(img_center)
        self.play(FadeIn(img_1, shift=LEFT * self.SHIFT_SCALE))
    else:
        img_1 = VMobject()  # Placeholder if missing

    self.next_slide()

    # --- Transition 1 -> 2 ---
    self.play(FadeOut(img_1, shift=RIGHT * self.SHIFT_SCALE), run_time=0.4)

    # =====================================================================
    # PHASE 2: Fluid -> Solid (GIF)
    # =====================================================================

    # 1. Replace Title
    title_2 = create_title(
        "État de l'art de l'action du fluide sur le solide :"
    )
    # Align exactly where title_1 was for smooth replacement
    title_2.move_to(title_1.get_center())
    # Re-align left edge just in case length differs significantly centering logic
    title_2.align_to(title_1, LEFT)

    # 2. Replace Bullets
    items_2 = [
        "Yuksel, \\textit{thèse de doctorat}, 2010",
        "Kellomäki, \\textit{IJCGT}, 2014",
        "Kerner, \\textit{Game Developer}, 2016",
    ]
    bullets_2 = create_bullets(items_2)
    bullets_2.next_to(title_2, DOWN, buff=0.5, aligned_edge=LEFT)
    bullets_2.shift(RIGHT * 0.2)

    self.play(
        TransformMatchingTex(title_1, title_2),
        FadeOut(bullets_1, shift=LEFT * self.SHIFT_SCALE),
        FadeIn(bullets_2, shift=RIGHT * self.SHIFT_SCALE),
    )

    # 3. GIF Loading Logic (Kerner)
    gif_path = "Figures/kerner.gif"
    display_gif = Group()  # Empty container if fail

    pil_img = Image.open(gif_path)
    pil_frames = []
    durations = []
    for frame in ImageSequence.Iterator(pil_img):
        dur_ms = frame.info.get("duration", 100)
        durations.append(max(0.01, dur_ms / 1000.0))
        pil_frames.append(frame.convert("RGBA"))

    # No transparency needed for this specific GIF usually,
    # but using standard loading.
    frames_mobs = []
    for fr in pil_frames:
        arr = np.array(fr, dtype=np.uint8)
        mob = ImageMobject(arr)
        mob.width = img_width_max
        mob.move_to(img_center)
        frames_mobs.append(mob)

    if frames_mobs:
        # Create the display object
        display_gif = frames_mobs[0].copy()
        self.play(FadeIn(display_gif, shift=LEFT * self.SHIFT_SCALE))

        # Animation logic
        durations_np = np.array(durations, dtype=float)
        cum = np.cumsum(durations_np)
        total = float(cum[-1])
        t_track = ValueTracker(0.0)

        def idx_from_time(tt: float) -> int:
            if total <= 0.0:
                return 0
            x = tt % total
            i = int(np.searchsorted(cum, x, side="right"))
            return min(i, len(frames_mobs) - 1)

        def gif_updater(m):
            idx = idx_from_time(t_track.get_value())
            m.become(frames_mobs[idx])

        display_gif.add_updater(gif_updater)
        # Add a continuous animation to drive the tracker
        self.add(display_gif)
        # We need to advance time manually or rely on slide wait time
        # Here we attach the tracker to the scene timeline implicitly via always_redraw
        # or just let it run if we added it to scene.
        # BUT: ValueTracker doesn't auto-animate. We need a persistent animation.
        # Hack for ManimSlides: just let it sit.
        # To make it PLAY, we need an updater that uses `dt`.

        # Better updater using dt for real-time playback
        # Removing previous approach to use standard dt-based updater
        display_gif.remove_updater(gif_updater)
        display_gif.time_elapsed = 0.0

        def dt_updater(mob, dt):
            mob.time_elapsed += dt
            idx = idx_from_time(mob.time_elapsed)
            mob.become(frames_mobs[idx])

        display_gif.add_updater(dt_updater)

    self.next_slide()

    # --- Transition 2 -> 3 ---
    display_gif.clear_updaters()  # Stop GIF
    self.play(
        FadeOut(display_gif, shift=RIGHT * self.SHIFT_SCALE), run_time=0.4
    )

    # =====================================================================
    # PHASE 3: Solid -> Fluid (Static Image)
    # =====================================================================

    # 1. Replace Title
    title_3 = create_title(
        "État de l'art de l'action du solide sur le fluide :"
    )
    title_3.move_to(title_2.get_center())
    title_3.align_to(title_2, LEFT)

    # 2. Replace Bullets
    items_3 = [
        "Cords et Staadt, \\textit{Eurographics NPH}, 2009",
        "Tessendorf, \\textit{Note technique}, 2014",
        "Yuksel, \\textit{ACM Trans. Graph.}, 2007",
        "Canabal, \\textit{ACM Trans. Graph.}, 2016",
        "Jeshke, \\textit{ACM Trans. Graph.}, 2018",
        "Schreck \\textit{et al.}, \\textit{ACM Trans. Graph.}, 2019",
    ]
    bullets_3 = create_bullets(items_3)
    bullets_3.next_to(title_3, DOWN, buff=0.5, aligned_edge=LEFT)
    bullets_3.shift(RIGHT * 0.2)

    self.play(
        TransformMatchingTex(title_2, title_3),
        FadeOut(bullets_2, shift=LEFT * self.SHIFT_SCALE),
        FadeIn(bullets_3, shift=RIGHT * self.SHIFT_SCALE),
    )

    # 3. Image (Schreck)
    img_path_3 = "Figures/schreck_waves.jpeg"
    if os.path.exists(img_path_3):
        img_3 = ImageMobject(img_path_3)
        img_3.width = img_width_max
        img_3.move_to(img_center)
        self.play(FadeIn(img_3, shift=LEFT * self.SHIFT_SCALE))
    else:
        img_3 = VMobject()

    self.next_slide()

    # --- Final Clear ---
    self.play(
        FadeOut(img_3, shift=RIGHT * self.SHIFT_SCALE),
        FadeOut(bullets_3, shift=LEFT * self.SHIFT_SCALE),
        FadeOut(title_3, shift=LEFT * self.SHIFT_SCALE),
        run_time=0.5,
    )

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

    # --- Arrow builders ----------------------------------------------------
    def _solid_curved_question(
        start_pt: np.ndarray, end_pt: np.ndarray, angle: float
    ) -> VGroup:
        """
        Solid curved line between two points with a '?' at the center.
        Includes a white background behind the '?' to mask the line.
        """
        # 1. Create the curved line (Arc)
        arc = ArcBetweenPoints(
            start=start_pt,
            end=end_pt,
            angle=angle,
            color=BLACK,
            stroke_width=6,
        )

        # 2. Create the question mark
        # Using Text for a standard font, or use MathTex("?") for LaTeX font
        label = Text("?", font_size=24, color=BLACK, weight=BOLD)

        # 3. Position the label exactly at the center of the arc path
        label.move_to(arc.point_from_proportion(0.5))

        # 4. Create a small background to hide the line behind the text
        # This assumes your slide background is WHITE.
        bg = BackgroundRectangle(
            label, color=WHITE, fill_opacity=1.0, buff=0.05
        )

        # 5. Return a Group (Order matters: Arc -> Background -> Label)
        return VGroup(arc, bg, label)

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
    a1 = _solid_curved_question(
        end_pt=_top_of(e_s2f, dx=0.10, dy=0.10),
        start_pt=_left_of(e_surface, dx=-0.10, dy=-0.10),
        angle=1.0,
    )

    # (2) F->S -> S->F : origin ok, now end on RIGHT side of S->F
    a2 = _solid_curved_question(
        start_pt=_right_of(e_s2f, dx=0.0, dy=-0.6),  # moved to right side
        end_pt=_left_of(e_f2s, dx=-0.0, dy=-0.6),
        angle=1.0,  # under-arc clockwise
    )

    # (3) S->F -> Surface (unchanged, correct)
    a3 = _solid_curved_question(
        start_pt=_top_of(e_f2s, dx=-0.10, dy=0.10),
        end_pt=_right_of(e_surface, dx=0.10, dy=-0.10),
        angle=1.0,
    )
    self.play(Create(a1), Create(a2), Create(a3), run_time=0.6)

    # --- End slide --------------------------------------------------------
    self.pause()
    self.clear()
    self.next_slide()
