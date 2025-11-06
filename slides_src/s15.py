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
from sph_vis import show_sph_simulation
from utils import (make_bullet_list, make_pro_cons, parse_selection,
                   tikz_from_file)

config.background_color = WHITE
# --------- Sélection des slides à rendre -----------
# Mettre "all" pour tout rendre, ou une sélection type: "1-5,8,12-14"
# On peut aussi surcharger via une variable d'environnement: SLIDES="1-5,8"
SLIDES_SELECTION = "25"
from slide_registry import slide

@slide(15)
def slide_15(self):
        """
        Couplage avec des solides.
        Steps:
          1) Show animated water surface: 0.1*cos(0.7*x + t).
          2) Drop a boat polygon that falls through and exits.
          3) Drop a second boat that floats on the surface.
          4) Drop a third boat that floats while the surface shows only w(x,t).
        Boats are cleaned before the next one is spawned.
        """
        # --- Title bar ---
        bar = self._top_bar("Couplage avec des solides")
        self.add(bar)
        self.add_foreground_mobject(bar)

        # --- Layout area ---
        bar_rect = bar.submobjects[0]
        y_top = bar_rect.get_bottom()[1] - 0.15
        x_left = -config.frame_width / 2 + 0.6
        x_right = config.frame_width / 2 - 0.6
        y_bottom = -config.frame_height / 2 + 0.6
        area_w = x_right - x_left
        area_h = y_top - y_bottom
        y_center = (y_top + y_bottom) * 0.5

        # --- Subtitle ---
        self.start_body()
        subtitle = Text(
            "La méthode de Tessendorf ne permet pas le couplage avec des solides",
            color=BLACK,
            font_size=self.BODY_FONT_SIZE,
        )
        subtitle.next_to(self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT)
        dx_sub = (bar_rect.get_left()[0] + self.DEFAULT_PAD) - subtitle.get_left()[0]
        subtitle.shift(RIGHT * dx_sub)
        self.add(subtitle)

        # --- Plot area (no axes) ---
        plot_w = min(area_w * 0.88, 12.0)
        plot_h = min(area_h * 0.42, 3.2)
        plot_center = np.array([0.0, y_center, 0.0])
        x_min, x_max = -2.0 * np.pi, 2.0 * np.pi
        x_span = x_max - x_min
        sample_n = 400
        y_vis = 1.0
        sx = plot_w / x_span
        sy = (plot_h / 2.0) / y_vis

        # --- Time trackers ---
        t = ValueTracker(0.0)
        include_w = ValueTracker(0.0)

        # --- Try to load w(x,t); fallback if not available ---
        w_data = {"H": None, "x": None, "t": None, "T": None}

        def try_prepare_wave_solution():
            try:
                from wave_equation_1d import \
                    simulate_wave_1d_dirichlet  # type: ignore
                H, x_arr, t_arr = simulate_wave_1d_dirichlet(
                    L=2.0, c=1.0, W=0.6, A=0.25, sigma=0.12, nx=801, T=8.0, dt=0.005, t0=0.0
                )
                w_data["H"] = H
                w_data["x"] = x_arr
                w_data["t"] = t_arr
                w_data["T"] = float(t_arr[-1] - t_arr[0]) if len(t_arr) > 1 else 1.0
            except Exception:
                w_data["H"] = None

        try_prepare_wave_solution()

        def w_fallback(x_val: float, t_val: float) -> float:
            return 0.08 * np.cos(2.0 * x_val - 1.2 * t_val)

        def w_from_data(x_val: float, t_val: float) -> float:
            H = w_data["H"]
            x_arr = w_data["x"]
            t_arr = w_data["t"]
            Ttot = w_data["T"]
            if H is None or x_arr is None or t_arr is None or Ttot is None or Ttot <= 0:
                return w_fallback(x_val, t_val)

            t0 = t_arr[0]
            tau = (t_val - t0) % Ttot + t0
            it = int(np.clip(np.searchsorted(t_arr, tau), 1, len(t_arr) - 1))
            t1, t2 = t_arr[it - 1], t_arr[it]
            a = 0.0 if t2 == t1 else (tau - t1) / (t2 - t1)
            h1 = np.interp(x_val, x_arr, H[it - 1])
            h2 = np.interp(x_val, x_arr, H[it])
            return float((1.0 - a) * h1 + a * h2)

        # --- FIX #2: Water is ONLY cosine unless include_w == 1
        def water_y(x_val: float) -> float:
            if include_w.get_value() >= 1.0:
                return w_from_data(x_val, t.get_value())
            else:
                return 0.1 * np.cos(0.7 * x_val + t.get_value())

        def make_water_curve():
            X = np.linspace(x_min, x_max, sample_n)
            pts = []
            for xv in X:
                yv = np.clip(water_y(xv), -y_vis, y_vis)
                px = (xv - x_min) * sx - plot_w / 2.0
                py = yv * sy
                pts.append([plot_center[0] + px, plot_center[1] + py, 0.0])
            path = VMobject()
            path.set_points_smoothly(pts)
            path.set_stroke(color=pc.blueGreen, width=4)
            return path

        water_curve = always_redraw(make_water_curve)
        self.add(water_curve)

        # FIX #1 - Fully linear evolution
        self.play(
            t.animate.increment_value(2.0 * np.pi),
            rate_func=linear,
            run_time=4.0,
        )

        # --------------------------------------------------------------------------
        self.next_slide()

        # --- Boat def ---
        boat_shape = [
            [-1.0,  0.0, 0.0],
            [ 1.0,  0.0, 0.0],
            [ 2.0,  1.0, 0.0],
            [ 0.5,  1.0, 0.0],
            [ 0.0,  1.5, 0.0],
            [-0.5,  1.0, 0.0],
            [-2.0,  1.0, 0.0],
        ]

        def create_boat(y_offset: float) -> Polygon:
            poly = Polygon(*boat_shape, color=pc.uclaGold, stroke_width=4)
            poly.set_fill(pc.uclaGold, opacity=1.0)
            poly.move_to([0.0, y_offset, 0.0])
            self.add_foreground_mobject(poly)
            return poly

        def destroy_boat(poly: Mobject) -> None:
            self.play(FadeOut(poly, run_time=0.15))
            try:
                self.remove_foreground_mobject(poly)
            except Exception:
                pass
            self.remove(poly)

        # --- DROP 1 ---
        start_y = y_center + 2.2
        boat = create_boat(start_y)
        self.play(
            boat.animate.move_to([0.0, y_bottom - 1.5, 0.0]),
            rate_func=linear,
            run_time=2.5,
        )
        destroy_boat(boat)

        # --------------------------------------------------------------------------
        self.next_slide()

        # --- DROP 2 (float) ---
        boat2 = create_boat(start_y)

        def water_y_at_x0() -> float:
            return water_y(0.0)

        self.play(
            boat2.animate.move_to([0.0, water_y_at_x0(), 0.0]),
            rate_func=linear,
            run_time=0.8,
        )

        amp = 0.18
        omega_b = 1.6
        t_local = ValueTracker(0.0)

        def boat_float_updater(mob: Mobject):
            y_osc = amp * np.sin(omega_b * t_local.get_value())
            mob.move_to([0.0, y_osc, 0.0])

        boat2.add_updater(boat_float_updater)

        self.play(
            AnimationGroup(
                t.animate.increment_value(2.0 * np.pi),
                t_local.animate.increment_value(2.0 * np.pi),
                lag_ratio=0.0,
            ),
            rate_func=linear,
            run_time=4.0,
        )
        boat2.remove_updater(boat_float_updater)
        destroy_boat(boat2)

        # --------------------------------------------------------------------------
        self.next_slide()

        # --- DROP 3 (float + w(x,t) only) ---
        boat3 = create_boat(start_y)
        self.play(
            boat3.animate.move_to([0.0, water_y_at_x0(), 0.0]),
            rate_func=linear,
            run_time=0.8,
        )

        include_w.set_value(1.0)

        t_local2 = ValueTracker(0.0)

        def boat_float_updater2(mob: Mobject):
            y_osc = amp * np.sin(omega_b * t_local2.get_value())
            mob.move_to([0.0, y_osc, 0.0])

        boat3.add_updater(boat_float_updater2)

        self.play(
            AnimationGroup(
                t.animate.increment_value(2.0 * np.pi),
                t_local2.animate.increment_value(2.0 * np.pi),
                lag_ratio=0.0,
            ),
            rate_func=linear,
            run_time=4.0,
        )
        boat3.remove_updater(boat_float_updater2)
        destroy_boat(boat3)

        # --- End of slide ---
        self.pause()
        self.clear()
        self.next_slide()
