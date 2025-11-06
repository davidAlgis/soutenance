import numpy as np
import palette_colors as pc
from manim import (BLACK, DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Arrow,
                   Create, Dot, FadeOut, GrowArrow, GrowFromCenter,
                   LaggedStart, Polygon, RoundedRectangle, Tex,
                   TransformMatchingTex, ValueTracker, VGroup, VMobject,
                   config)
from slide_registry import slide


@slide(32)
def slide_32(self):
    """
    Hybridation, forces d'Airy et zones.

    Steps implemented:
    1) Top bar, title, "Preuve de concept :" and a bullet list (3 items).
    2) Transform the bullet list content to the 2D/Airy/SPH version.
    3) Clear text, draw a cosine surface (0.1*cos(0.3*x)) on [-10, 10].
    4) Place three small boats on the curve (left, mid-right, right).
    5) Highlight right boat with a rounded "jelly bean" rectangle, then clear
       everything except the top bar.
    6) Draw a new cosine surface (0.2*cos(1.2*x)) on [-5, 5] and one boat at center.
    7) Spawn a uniform field of particles (cornFlower) from bottom up to y=0
       with line-wise grow animation; keep boat in foreground.
    8) On the top particle line, draw fernGreen arrows pointing toward the
       cosine curve with a small random horizontal component; then remove them.
    9) Draw three nested rectangles: outer fernGreen on frame border (animated
       line-by-line), inner uclaGold, innermost blueGreen.
    """
    # ------------------------------------------------------------------ Title
    bar = self._top_bar("Hybridation, forces d'Airy et zones")
    self.add(bar)
    self.add_foreground_mobject(bar)

    # ------------------------- "Preuve de concept" and bullet list (Tex only)
    self.start_body()
    title_tex = Tex(
        r"Preuve de concept :", color=BLACK, font_size=self.BODY_FONT_SIZE
    )
    title_tex.next_to(
        self._current_bar, DOWN, buff=self.BODY_TOP_BUFF, aligned_edge=LEFT
    )
    dx_title = (
        bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
    ) - title_tex.get_left()[0]
    title_tex.shift(RIGHT * dx_title)
    self.add(title_tex)

    def make_bullets(items):
        lines = VGroup()
        for i, s in enumerate(items):
            t = Tex(
                r"\(\bullet\)\; " + s,
                color=BLACK,
                font_size=self.BODY_FONT_SIZE,
            )
            if i == 0:
                t.next_to(
                    title_tex,
                    DOWN,
                    buff=self.BODY_LINE_BUFF,
                    aligned_edge=LEFT,
                )
            else:
                t.next_to(
                    lines[-1],
                    DOWN,
                    buff=self.BODY_LINE_BUFF,
                    aligned_edge=LEFT,
                )
            # Align to left padding
            dx = (
                bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
            ) - t.get_left()[0]
            t.shift(RIGHT * dx)
            lines.add(t)
        return lines

    bullets_v1 = make_bullets(
        ["Simulation 3D", "Methode de Tessendorf", "SPH"]
    )
    self.add(bullets_v1)
    self.wait(0.01)
    self.next_slide()

    bullets_v2 = make_bullets(
        ["Simulation 2D", "Theorie des vagues d'Airy", "SPH"]
    )
    self.play(
        AnimationGroup(
            *[
                TransformMatchingTex(b1, b2)
                for b1, b2 in zip(bullets_v1, bullets_v2)
            ],
            lag_ratio=0.0,
            run_time=0.8,
        )
    )

    bullets_v1 = bullets_v2

    self.next_slide()

    # ----------------------------------------- Clear bullets and the subtitle
    self.play(
        FadeOut(bullets_v1, run_time=0.3), FadeOut(title_tex, run_time=0.3)
    )

    # ---------------------------------------------------- Cosine helper maker
    def make_cosine_curve(a, k, x_min, x_max, color, samples=600):
        X = np.linspace(x_min, x_max, samples)
        pts = []
        sx = config.frame_width / (x_max - x_min)
        sy = config.frame_height * 0.25  # vertical scaling for visibility
        y0 = 0.0  # center on screen
        for xv in X:
            yv = a * np.cos(k * xv)
            px = (xv - (x_min + x_max) * 0.5) * sx
            py = y0 + yv * (config.frame_height * 0.25)  # normalized amplitude
            pts.append([px, py, 0.0])
        path = VMobject()
        path.set_points_smoothly(pts)
        path.set_stroke(color=color, width=4)
        return path

    # ------------------------------------- First surface: 0.1*cos(0.3*x), [-10,10]
    curve1 = make_cosine_curve(
        a=0.1, k=0.3, x_min=-10.0, x_max=10.0, color=pc.blueGreen
    )
    self.play(Create(curve1, run_time=1.2))

    self.next_slide()

    # ----------------------------------------------------------- Boats on curve
    boat_shape = [
        [-1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 1.0, 0.0],
        [0.5, 1.0, 0.0],
        [0.0, 1.5, 0.0],
        [-0.5, 1.0, 0.0],
        [-2.0, 1.0, 0.0],
    ]

    def place_on_curve(curve_func, x_screen):
        # Recover y on curve by sampling; curve1 lies around y=0 with amplitude set above.
        # Build the deterministic value used for our cosine.
        return 0.1 * np.cos(1.5 * x_screen)

    def make_boat(scale=0.25):
        poly = Polygon(*boat_shape, color=pc.uclaGold, stroke_width=3)
        poly.set_fill(pc.uclaGold, opacity=1.0)
        poly.scale(scale)
        return poly

    # Choose three x positions in screen space
    xs = [-6.5, 0.5, 6.5]
    boats = []
    for xv in xs:
        b = make_boat()
        yv = place_on_curve(lambda x: 0.0, xv) * (config.frame_height * 0.25)
        b.move_to([xv * (config.frame_width / 20.0), yv, 0.0])
        self.add(b)
        boats.append(b)

    self.next_slide()

    # ------------------------------------------------ Jelly-bean rectangle (right)
    right_boat = boats[-1]
    jb = RoundedRectangle(
        corner_radius=0.5,
        width=right_boat.width * 2.2,
        height=right_boat.height * 2.2,
        stroke_color=pc.uclaGold,
        stroke_width=5,
    )
    jb.move_to(right_boat.get_center())
    self.play(Create(jb, run_time=0.6))

    # ---------------------------------------------- Clear all except the top bar
    self.play(FadeOut(VGroup(curve1, *boats, jb), run_time=0.4))
    # Keep bar visible (already present)

    self.next_slide()

    # ------------------------------ Second surface: 0.2*cos(1.2*x), [-5, 5] + boat
    curve2 = make_cosine_curve(
        a=0.2, k=1.2, x_min=-5.0, x_max=5.0, color=pc.blueGreen
    )
    self.play(Create(curve2, run_time=1.0))

    center_boat = make_boat()
    y_center = 0.2 * np.cos(1.2 * 0.0) * (config.frame_height * 0.25)
    center_boat.move_to([0.0, y_center, 0.0])
    self.add(center_boat)
    self.add_foreground_mobject(center_boat)

    self.next_slide()

    # --------------------------------------- Uniform particle field (cornFlower)
    # Grid spans full width; vertically from bottom to y=0.
    x_min_px = -config.frame_width * 0.48
    x_max_px = config.frame_width * 0.48
    y_min_px = -config.frame_height * 0.48
    y_max_px = 0.0
    dx = config.frame_width / 18.0
    dy = config.frame_height / 18.0

    lines = []
    y = y_min_px
    while y <= y_max_px + 1e-6:
        row = VGroup()
        x = x_min_px
        while x <= x_max_px + 1e-6:
            d = Dot(point=[x, y, 0.0], radius=0.035, color=pc.cornflower)
            row.add(d)
            x += dx
        lines.append(row)
        y += dy

    self.play(
        LaggedStart(
            *[GrowFromCenter(row) for row in lines],
            lag_ratio=0.1,
            run_time=1.0,
        )
    )
    # Ensure boat remains above particles
    self.add_foreground_mobject(center_boat)

    self.next_slide()

    # ---------------------------------------------------- Arrows from top line
    top_line = lines[-1]
    # Compute boat horizontal extent to skip arrows behind boat
    boat_left = center_boat.get_left()[0]
    boat_right = center_boat.get_right()[0]

    arrows = VGroup()
    for dot in top_line:
        x0, y0, _ = dot.get_center()
        if boat_left - 0.1 <= x0 <= boat_right + 0.1:
            continue
        # End on the cosine curve at same x; add a tiny random horizontal component
        jitter = (np.random.rand() - 0.5) * (dx * 0.25)
        y_curve = (
            0.2
            * np.cos(1.2 * (x0 / (config.frame_width / 10.0)))
            * (config.frame_height * 0.25)
        )
        start = np.array([x0 + jitter, y0 + dy * 0.6, 0.0])
        end = np.array([x0, y_curve, 0.0])
        arr = Arrow(
            start=start,
            end=end,
            buff=0.0,
            stroke_width=3,
            color=pc.fernGreen,
            max_tip_length_to_length_ratio=0.12,
        )
        arrows.add(arr)

    self.play(
        LaggedStart(
            *[GrowArrow(a) for a in arrows], lag_ratio=0.05, run_time=1.0
        )
    )

    self.next_slide()

    # --------------------------------------- Remove arrows and particles (keep boat)
    self.play(
        FadeOut(arrows, run_time=0.3), FadeOut(VGroup(*lines), run_time=0.3)
    )

    # ------------------------------------------ Nested rectangles (zone concept)
    # Outer: border of the slide drawn line-by-line
    outer_w = config.frame_width * 0.94
    outer_h = config.frame_height * 0.86

    # Build four sides to animate sequentially
    x0, y0 = -outer_w / 2.0, -outer_h / 2.0
    x1, y1 = outer_w / 2.0, outer_h / 2.0
    # Lines as VMobjects
    l1 = (
        VMobject()
        .set_stroke(color=pc.fernGreen, width=6)
        .set_points_as_corners([[x0, y0, 0.0], [x1, y0, 0.0]])
    )
    l2 = (
        VMobject()
        .set_stroke(color=pc.fernGreen, width=6)
        .set_points_as_corners([[x1, y0, 0.0], [x1, y1, 0.0]])
    )
    l3 = (
        VMobject()
        .set_stroke(color=pc.fernGreen, width=6)
        .set_points_as_corners([[x1, y1, 0.0], [x0, y1, 0.0]])
    )
    l4 = (
        VMobject()
        .set_stroke(color=pc.fernGreen, width=6)
        .set_points_as_corners([[x0, y1, 0.0], [x0, y0, 0.0]])
    )
    frame_lines = VGroup(l1, l2, l3, l4)
    self.play(Create(l1, run_time=0.25))
    self.play(Create(l2, run_time=0.25))
    self.play(Create(l3, run_time=0.25))
    self.play(Create(l4, run_time=0.25))

    # Inner rectangles
    inner1 = RoundedRectangle(
        width=outer_w * 0.78,
        height=outer_h * 0.78,
        corner_radius=0.0,
        stroke_color=pc.uclaGold,
        stroke_width=6,
    )
    inner1.move_to(ORIGIN)
    inner2 = RoundedRectangle(
        width=outer_w * 0.58,
        height=outer_h * 0.54,
        corner_radius=0.0,
        stroke_color=pc.blueGreen,
        stroke_width=6,
    )
    inner2.move_to(ORIGIN)
    self.add(inner1, inner2)

    # End of slide
    self.pause()
    self.clear()
    self.next_slide()
