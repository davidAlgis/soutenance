import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide
from sph_vis import show_sph_simulation


@slide(26)
def slide_26(self):
    """
    Récapitulatif SPH (slide 26)

    - Top bar + enumerated recap with pauses
    - Centered integration equations with pause
    - Clear list, then show SPH playback (only fluid/type==0) from
      'states_sph/particles_sph_all_forces.csv'
    - Draw an uclaGold rectangle at world coords:
        origin=(-1.0, -0.9), size=(2.0, 5.5)
      using the same ROI mapping as the particles.
    """
    # --- Top bar ---
    bar = self._top_bar("Récapitulatif SPH")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # --- Body text (enumerate) ---
    self.start_body()
    lead = Tex(
        r"Pour simuler un fluide avec SPH on doit :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    lead.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx = (-config.frame_width / 2 + self.DEFAULT_PAD) - lead.get_left()[0]
    lead.shift(
        RIGHT * (dx + 0.6)
    )  # small extra pad to match your usual rhythm
    self.play(FadeIn(lead, run_time=0.25))

    # 1.
    l1 = Tex(
        r"1. Calculer la densité : $\rho_i=\sum_j m_j W_{ij}$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l1.next_to(lead, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l1.shift(RIGHT * (dx + 0.6))
    self.add(l1)
    self.next_slide()

    # 2.
    l2 = Tex(
        r"2. Calcul des forces de viscosité : $F^v$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l2.shift(RIGHT * (dx + 0.6))
    self.add(l2)
    self.next_slide()

    # 3. + 4.
    l3 = Tex(
        r"3. Solveur de densité constante : $F^p_0$ pour vérifier $|\hat{\rho}-\rho_0|\rightarrow 0$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l3.next_to(l2, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l3.shift(RIGHT * (dx + 0.6))
    l4 = Tex(
        r"4. Solveur de « volume constante » : $F^p_1$ pour vérifier $\nabla \cdot v\rightarrow 0$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l4.next_to(l3, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l4.shift(RIGHT * (dx + 0.6))
    self.add(l3, l4)
    self.next_slide()

    # 5. + centered integration formulas
    l5 = Tex(
        r"5. Intégration des forces :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l5.next_to(l4, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l5.shift(RIGHT * (dx + 0.6))
    self.add(l5)

    # Centered equations (below)
    eq1 = Tex(
        r"$v_i(t+dt) = v_i(t) + \frac{dt}{m_i}\left(F^v + F^p_0 + F^p_1 + m_i g\right)$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 2,
    )
    eq2 = Tex(
        r"$p_i(t+dt) = p_i(t) + dt\,v_i(t+dt)$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE + 2,
    )
    # Place centered in free body area
    y_anchor = (
        self._current_bar.get_bottom()[1] - 0.8
    )  # slightly lower than bar
    eq1.move_to(np.array([0.0, y_anchor - 1.2, 0.0]))
    eq2.next_to(eq1, DOWN, buff=0.35)
    self.add(eq1, eq2)
    self.next_slide()

    # --- Clear enumerate text (keep bar) ---
    self.play(
        FadeOut(VGroup(lead, l1, l2, l3, l4, l5, eq1, eq2), run_time=0.35)
    )

    # --- SPH playback (only fluid) + world-rect annotation ---
    # We choose an ROI that comfortably includes the requested rectangle:
    #   rect origin (-1.0, -0.9), size (2.0, 5.5)  -> top y = 4.6
    # Use ROI: origin (-2.0, -2.0), size (4.0, 7.0), so top = 5.0 (> 4.6)
    roi_origin = (-2.0, -2.0)
    roi_size = (4.0, 7.0)

    # Map ROI width to ~11 units on screen and center a bit lower for room under the bar
    fit_w = 11.0
    target_center = (0.0, -0.8)
    dot_radius = 0.06

    # Pre-compute the SAME linear mapping the helper uses (world -> screen)
    ox, oy = roi_origin
    sx, sy = roi_size
    world_cx = ox + sx * 0.5
    world_cy = oy + sy * 0.5
    tx, ty = target_center
    s = (
        fit_w / sx
    )  # we only fit to width here (same as show_sph_simulation when only width given)

    # Rectangle in world coords
    rect_ox, rect_oy = -1.0, -0.9
    rect_w, rect_h = 2.0, 5.5

    # Convert to screen coords (center + size)
    rect_center_world = np.array(
        [rect_ox + rect_w * 0.5, rect_oy + rect_h * 0.5]
    )
    rect_center_screen = np.array(
        [
            (rect_center_world[0] - world_cx) * s + tx,
            (rect_center_world[1] - world_cy) * s + ty,
            0.0,
        ]
    )
    rect_w_screen = rect_w * s
    rect_h_screen = rect_h * s

    # Callback to draw the rectangle just before CSV playback starts
    def draw_world_rect(scene, dots_group: VGroup):
        rect = Rectangle(
            width=rect_w_screen,
            height=rect_h_screen,
            stroke_color=pc.uclaGold,
            stroke_width=6,
        )
        rect.move_to(rect_center_screen)
        scene.play(Create(rect, run_time=0.35))
        scene.add_foreground_mobject(rect)

    # Launch the SPH visual (note: show_sph_simulation introduces a click before playback)
    show_sph_simulation(
        self,
        "states_sph/particles_sph_all_forces.csv",
        only_fluid=True,  # type == 0
        dot_radius=dot_radius,
        manim_seconds=3.5,  # quick preview; adjust if you want longer
        roi_origin=roi_origin,
        roi_size=roi_size,
        clip_outside=True,
        fit_roi_to_width=fit_w,
        fit_roi_to_height=None,
        target_center=target_center,
        cover=False,
        grow_time=0.5,
        grow_lag=0.0,
        on_after_init=draw_world_rect,  # ensures same mapping as particles
    )

    self.pause()
    self.clear()
    self.next_slide()
