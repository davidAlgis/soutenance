import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide
from utils import make_bullet_list


@slide(32)
def slide_32(self):
    """
    Hybridation, forces d'Airy et zones.
    Implements the sequence requested for slide 32.
    """
    # ------------------------------------------------------------------ Title
    bar, footer = self._top_bar("Hybridation, forces d'Airy et zones")
    self.add(bar)
    self.add_foreground_mobject(bar)

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
    self.play(FadeIn(title_tex), run_time=0.5)

    def make_bullets(items):
        bullet_group = make_bullet_list(
            items,
            bullet_color=pc.blueGreen,
            font_size=self.BODY_FONT_SIZE,
            line_gap=self.BODY_LINE_BUFF,
            left_pad=0.25,
        )

        # Place the whole bullet group under the title, aligned with the bar padding
        bullet_group.next_to(
            title_tex,
            DOWN,
            buff=self.BODY_LINE_BUFF,
            aligned_edge=LEFT,
        )
        dx = (
            bar.submobjects[0].get_left()[0] + self.DEFAULT_PAD
        ) - bullet_group.get_left()[0]
        bullet_group.shift(RIGHT * dx)

        # Extract only the Tex objects (index 1 in each row: VGroup(bullet, txt))
        text_items = [row[1] for row in bullet_group]

        return bullet_group, text_items

    bullets_v1, texts_v1 = make_bullets(
        ["Simulation 3D", "Methode de Tessendorf", "SPH"]
    )
    self.play(FadeIn(bullets_v1), run_time=0.3)
    self.wait(0.1)
    self.next_slide()

    bullets_v2, texts_v2 = make_bullets(
        ["Simulation 2D", "Theorie des vagues d'Airy", "SPH"]
    )

    self.play(
        AnimationGroup(
            *[
                TransformMatchingTex(t1, t2)
                for t1, t2 in zip(texts_v1, texts_v2)
            ],
            lag_ratio=0.0,
            run_time=0.8,
        ),
    )
    # ------------------------------------------------------------------
    # IMPORTANT PART: after the transform, keep only ONE bullet group
    # ------------------------------------------------------------------
    for t1, t2 in zip(texts_v1, texts_v2):
        t1.become(t2)
    self.remove(bullets_v2)

    self.next_slide()

    # ----------------------------------------- Clear bullets and the subtitle
    self.play(
        FadeOut(VGroup(title_tex, bullets_v1)),
        FadeOut(bullets_v2),
        run_time=0.3,
    )

    # ---------------------------------------------------- Cosine helper maker
    def make_cosine_curve(a, k, x_min, x_max, color, samples=600):
        X = np.linspace(x_min, x_max, samples)
        pts = []
        sx = config.frame_width / (x_max - x_min)
        y0 = 0.0
        for xv in X:
            yv = a * np.cos(k * xv)
            px = (xv - (x_min + x_max) * 0.5) * sx
            py = y0 + yv * (config.frame_height * 0.25)
            pts.append([px, py, 0.0])
        path = VMobject()
        path.set_points_smoothly(pts)
        path.set_stroke(color=color, width=4)
        return path

    # ------------------------------------- First surface: 0.1*cos(0.3*x), [-10,10]
    curve1 = make_cosine_curve(
        a=0.06, k=2.5, x_min=-10.0, x_max=10.0, color=pc.blueGreen
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

    def place_on_curve(x_screen):
        return 0.1 * np.cos(1.2 * x_screen)

    def make_boat(scale=0.25):
        poly = Polygon(*boat_shape, color=pc.uclaGold, stroke_width=3)
        poly.set_fill(pc.uclaGold, opacity=1.0)
        poly.scale(scale)
        return poly

    xs = [-6.5, 0.5, 6.5]
    boats = []
    for xv in xs:
        b = make_boat()
        yv = place_on_curve(xv) * (config.frame_height * 0.25)
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

    self.next_slide()
    # ---------------------------------------------- Clear all except the top bar
    self.play(FadeOut(VGroup(curve1, *boats, jb), run_time=0.4))

    # ------------------------------ Second surface: 0.2*cos(1.2*x), [-5, 5] + boat
    curve2 = make_cosine_curve(
        a=0.2, k=1.2, x_min=-5.0, x_max=5.0, color=pc.blueGreen
    )
    self.play(Create(curve2, run_time=1.0))

    # Larger single boat (about 4x the earlier boats)
    center_boat = make_boat(scale=1.0)  # 0.25 * 4 = 1.0
    y_center = 0.2 * np.cos(1.2 * 0.0) * (config.frame_height * 0.25)
    center_boat.move_to([0.0, y_center, 0.0])
    self.add(center_boat)
    self.add_foreground_mobject(center_boat)

    self.wait(0.1)
    self.next_slide()

    # --------------------------------------- Uniform particle field (cornFlower)
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
    self.add_foreground_mobject(center_boat)
    self.wait(0.1)
    self.next_slide()

    # ---------------------------------------------------- Arrows from top line
    top_line = lines[-1]
    boat_left = center_boat.get_left()[0]
    boat_right = center_boat.get_right()[0]

    arrows = VGroup()
    for dot in top_line:
        x0, y0, _ = dot.get_center()
        if boat_left - 0.1 <= x0 <= boat_right + 0.1:
            continue
        jitter = (np.random.rand() - 0.5) * (dx * 0.25)
        y_curve = (
            0.2
            * np.cos(1.2 * (x0 / (config.frame_width / 10.0)))
            * (config.frame_height * 0.25)
        )
        # Longer and thicker arrows with larger tips
        start = np.array([x0, y0, 0.0])
        end = np.array([x0 + jitter, y_curve, 0.0])
        arr = Arrow(
            start=start,
            end=end,
            buff=0.0,
            stroke_width=15,
            color=pc.fernGreen,
            max_tip_length_to_length_ratio=0.3,
        )
        arrows.add(arr)

    self.play(
        LaggedStart(
            *[GrowArrow(a) for a in arrows], lag_ratio=0.05, run_time=1.0
        )
    )

    self.wait(0.1)
    self.next_slide()

    # --------------------------------------- Remove arrows and particles (keep boat)
    self.play(
        FadeOut(arrows, run_time=0.3), FadeOut(VGroup(*lines), run_time=0.3)
    )

    # ------------------------------------------ Nested rectangles (zone concept)
    outer_w = config.frame_width * 0.94
    outer_h = config.frame_height * 0.86
    # Lower the outer rectangle so it does not collide with the top bar
    y_offset = -config.frame_height * 0.06

    x0, y0 = -outer_w / 2.0, -outer_h / 2.0 + y_offset
    x1, y1 = outer_w / 2.0, outer_h / 2.0 + y_offset

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
    self.play(Create(l1, run_time=0.25))
    self.play(Create(l2, run_time=0.25))
    self.play(Create(l3, run_time=0.25))
    self.play(Create(l4, run_time=0.25))

    inner1 = RoundedRectangle(
        width=outer_w * 0.78,
        height=outer_h * 0.78,
        corner_radius=0.0,
        stroke_color=pc.uclaGold,
        stroke_width=6,
    )
    inner1.move_to([0.0, y_offset, 0.0])
    inner2 = RoundedRectangle(
        width=outer_w * 0.58,
        height=outer_h * 0.54,
        corner_radius=0.0,
        stroke_color=pc.blueGreen,
        stroke_width=6,
    )
    inner2.move_to([0.0, y_offset, 0.0])
    self.play(Create(inner1), run_time=0.5)
    self.play(Create(inner2), run_time=0.5)

    # End of slide
    self.pause()
    self.clear()
    self.next_slide()
