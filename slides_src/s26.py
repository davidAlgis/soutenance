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
    - Draw uclaGold guide lines in the same world frame:
        * bottom horizontal line at rectangle bottom
        * two vertical side lines cropped just under the top bar
      for the world-rectangle:
        origin=(-1.0, -0.9), size=(2.0, 5.5)
    """
    # --- Top bar ---
    bar = self._top_bar("Récapitulatif SPH")
    self.add(bar)
    self.add_foreground_mobject(bar)
    bar_rect = bar.submobjects[0]

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
    self.play(FadeIn(lead, run_time=0.25, shift=RIGHT * self.SHIFT_SCALE))
    self.wait(0.1)
    self.next_slide()

    # 1.
    l1 = Tex(
        r"1. Calculer la densité : $\rho_i=\sum_j m_j W_{ij}$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l1.next_to(lead, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    l1.shift(RIGHT * (dx + 0.6) + DOWN * 0.1)
    self.play(FadeIn(l1), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # 2.
    l2 = Tex(
        r"2. Calcul des forces de viscosité : $F^v$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l2.next_to(l1, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    self.play(FadeIn(l2), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # 3. + 4.
    l3 = Tex(
        r"3. Solveur de densité constante : $F^p_0$ pour vérifier $|\hat{\rho}-\rho_0|\rightarrow 0$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l3.next_to(l2, DOWN, buff=self.BODY_LINE_BUFF + 0.1, aligned_edge=LEFT)
    l4 = Tex(
        r"4. Solveur de « volume constante » : $F^p_1$ pour vérifier $\nabla \cdot v\rightarrow 0$",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l4.next_to(l3, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    self.play(FadeIn(l3, l4), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # 5. + centered integration formulas
    l5 = Tex(
        r"5. Intégration des forces :",
        color=BLACK,
        font_size=self.BODY_FONT_SIZE,
    )
    l5.next_to(l4, DOWN, buff=self.BODY_LINE_BUFF, aligned_edge=LEFT)
    self.play(FadeIn(l5), run_time=0.25)

    # Centered equations (keep the vertical you already set via next_to)
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
    eq1.next_to(l5, DOWN, buff=0.35)
    eq2.next_to(eq1, DOWN, buff=0.35)
    # Center horizontally while preserving current Y positions
    y1 = eq1.get_center()[1]
    y2 = eq2.get_center()[1]
    eq1.move_to(np.array([0.0, y1, 0.0]))
    eq2.move_to(np.array([0.0, y2, 0.0]))
    self.play(FadeIn(eq1, eq2), run_time=0.25)
    self.wait(0.1)
    self.next_slide()

    # --- Clear enumerate text (keep bar) ---
    self.play(
        FadeOut(VGroup(lead, l1, l2, l3, l4, l5, eq1, eq2), run_time=0.35)
    )

    # --- SPH playback (only fluid) + world-guide lines annotation ---
    # NOTE: Using your updated ROI/fit mapping exactly as provided
    roi_origin = (-2.0, -2.0)
    roi_size = (4.0, 3.0)

    # Map ROI width to ~11 units on screen and center lower for room under the bar
    fit_w = 11.0
    target_center = (0.0, -2.5)
    dot_radius = 0.06

    # Compute the SAME linear mapping as show_sph_simulation (world -> screen)
    ox, oy = roi_origin
    sx, sy = roi_size
    world_cx = ox + sx * 0.5
    world_cy = oy + sy * 0.5
    tx, ty = target_center
    s = fit_w / sx  # only width fitting

    # World rectangle specs
    rect_ox, rect_oy = -1.0, -0.9
    rect_w, rect_h = 2.0, 5.5

    # Convert to screen coords (edges)
    rect_left_x = (rect_ox - world_cx) * s + tx
    rect_right_x = (rect_ox + rect_w - world_cx) * s + tx
    rect_bottom_y = (rect_oy - world_cy) * s + ty
    rect_top_y = (rect_oy + rect_h - world_cy) * s + ty

    # Crop just under the top bar (a small margin below bar bottom)
    top_limit_y = bar_rect.get_bottom()[1] - 0.12
    vline_top_y = min(rect_top_y, top_limit_y)

    # Callback to draw the guide lines just before CSV playback starts
    def draw_world_rect(scene, dots_group: VGroup):
        stroke_w = 8

        # 1) Bottom horizontal line (exactly at rectangle bottom)
        bottom_line = Line(
            start=np.array([rect_left_x, rect_bottom_y, 0.0]),
            end=np.array([rect_right_x, rect_bottom_y, 0.0]),
            stroke_color=pc.uclaGold,
            stroke_width=stroke_w,
        )

        # 2) Left vertical line (cropped under the top bar)
        left_vline = Line(
            start=np.array([rect_left_x, rect_bottom_y, 0.0]),
            end=np.array([rect_left_x, vline_top_y, 0.0]),
            stroke_color=pc.uclaGold,
            stroke_width=stroke_w,
        )

        # 3) Right vertical line (cropped under the top bar)
        right_vline = Line(
            start=np.array([rect_right_x, rect_bottom_y, 0.0]),
            end=np.array([rect_right_x, vline_top_y, 0.0]),
            stroke_color=pc.uclaGold,
            stroke_width=stroke_w,
        )

        scene.play(
            Create(bottom_line, run_time=0.25),
            Create(left_vline, run_time=0.25),
            Create(right_vline, run_time=0.25),
        )
        scene.add_foreground_mobject(bottom_line)
        scene.add_foreground_mobject(left_vline)
        scene.add_foreground_mobject(right_vline)
        self.wait(0.1)
        self.next_slide()

    # Launch the SPH visual (note: show_sph_simulation introduces a click before playback)
    show_sph_simulation(
        self,
        "states_sph/particles_sph_all_forces.csv",
        only_fluid=True,  # type == 0
        dot_radius=dot_radius,
        manim_seconds=10,  # quick preview; adjust if you want longer
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
