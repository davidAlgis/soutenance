import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(31)
def slide_31(self):
    """
    Lancer de rayon pour la RPPV (v2):
    - Particles placed strictly below the intro line.
    - Gates further from particles and taller.
    - Same behavior as previous version (rays & collisions).
    """

    # ---------- Top bar and intro ----------
    bar = self._top_bar("Lancer de rayon pour la RPPV")
    self.add(bar)
    self.add_foreground_mobject(bar)

    self.start_body()
    intro = self.add_body_text(
        "Utiliser le lancer de rayon pour la RPPV :",
        font_size=self.BODY_FONT_SIZE,
    )

    # ---------- Layout for the body area (strictly below the intro) ----------
    bar_rect = bar.submobjects[0]
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    body_left, body_right = x_left + 0.3, x_right - 0.3
    # Keep a safe vertical gap below the intro text
    top_gap = 0.45
    body_top = intro.get_bottom()[1] - top_gap
    body_bottom2 = y_bottom + 0.35
    body_w = body_right - body_left
    body_h = body_top - body_bottom2
    if body_h < 1.0:
        # In case of tight space (e.g., small resolution), keep a minimum height
        body_top = body_bottom2 + 1.0
        body_h = 1.0

    # ---------- Load 30 points from CSV (robust column names) ----------
    def _load_pts(path: str, max_count: int = 30):
        try:
            data = np.genfromtxt(
                path, delimiter=",", names=True, dtype=None, encoding="utf-8"
            )
        except Exception:
            data = None

        if data is not None and len(data) > 0:
            for cx, cy in (
                ("X quincunx", "Y quincunx"),
                ("x", "y"),
                ("pos_x", "pos_y"),
                ("X", "Y"),
            ):
                if (
                    data is not None
                    and cx in data.dtype.names
                    and cy in data.dtype.names
                ):
                    arr = np.column_stack([data[cx], data[cy]])[:max_count]
                    xmin, ymin = np.min(arr[:, 0]), np.min(arr[:, 1])
                    xmax, ymax = np.max(arr[:, 0]), np.max(arr[:, 1])
                    if xmax > xmin and ymax > ymin:
                        nx = (arr[:, 0] - xmin) / (xmax - xmin)
                        ny = (arr[:, 1] - ymin) / (ymax - ymin)
                        px = body_left + nx * body_w
                        py = body_bottom2 + ny * body_h
                        return np.column_stack([px, py, np.zeros_like(px)])
        # Fallback grid
        cols_g, rows_g = 6, 5
        xs = np.linspace(body_left, body_right, cols_g + 2)[1:-1]
        ys = np.linspace(body_bottom2, body_top, rows_g + 2)[1:-1][::-1]
        pts = []
        for j in range(rows_g):
            for i in range(cols_g):
                pts.append([xs[i], ys[j], 0.0])
                if len(pts) >= max_count:
                    break
            if len(pts) >= max_count:
                break
        return np.array(pts, dtype=float)

    pts = _load_pts("states_sph/particles.csv", 30)
    N = len(pts)
    pr = min(body_w, body_h) / 45.0

    # ---------- Particles (grow) ----------
    dots = VGroup(*[Dot(point=p, radius=pr, color=pc.blueGreen) for p in pts])
    self.play(
        LaggedStart(
            *[GrowFromCenter(d) for d in dots], lag_ratio=0.04, run_time=0.9
        )
    )

    self.next_slide()

    # ---------- Recolor (target = 3rd) + dashed circle ----------
    target_idx = 2 if N >= 3 else 0
    for i, d in enumerate(dots):
        d.set_color(pc.jellyBean if i == target_idx else BLACK)

    target = dots[target_idx]
    dashed = DashedVMobject(
        Circle(radius=15.0 * pr, color=BLACK, stroke_width=4).move_to(
            target.get_center()
        ),
        num_dashes=48,
        dashed_ratio=0.55,
    )
    self.play(Create(dashed, run_time=0.45))

    self.next_slide()

    # ---------- Gates (further & taller) ----------
    gate_dx = 6.0 * pr  # moved further
    gate_h = 20.0 * pr  # increased height
    gates = []
    for p in pts:
        x, y, _ = p
        l1 = Line(
            [x - gate_dx, y - gate_h / 2, 0],
            [x - gate_dx, y + gate_h / 2, 0],
            color=BLACK,
            stroke_width=3,
        )
        l2 = Line(
            [x + gate_dx, y - gate_h / 2, 0],
            [x + gate_h / 2 - (gate_h / 2 - gate_dx), y + gate_h / 2, 0],
        )  # avoid accidental zero-length
        # Correct right gate definition (typo-proof)
        l2 = Line(
            [x + gate_dx, y - gate_h / 2, 0],
            [x + gate_dx, y + gate_h / 2, 0],
            color=BLACK,
            stroke_width=3,
        )
        gates.append((l1, l2))
    gates_group = VGroup(*[g for pair in gates for g in pair])
    self.play(Create(gates_group, run_time=0.45))

    self.next_slide()

    # ---------- Rays from target (NE, NW, SE, SW) ----------
    tpos = target.get_center()
    dirs = [
        np.array([+1.0, +1.0, 0.0]),
        np.array([-1.0, +1.0, 0.0]),
        np.array([+1.0, -1.0, 0.0]),
        np.array([-1.0, -1.0, 0.0]),
    ]
    dirs = [d / np.linalg.norm(d[:2]) for d in dirs]

    # Bounds (use whole frame safe area)
    xL, xR = -config.frame_width / 2 + 0.05, config.frame_width / 2 - 0.05
    yB, yT = -config.frame_height / 2 + 0.05, config.frame_height / 2 - 0.05

    def _t_to_bounds(origin, direction):
        ts = []
        if direction[0] > 0:
            ts.append((xR - origin[0]) / direction[0])
        if direction[0] < 0:
            ts.append((xL - origin[0]) / direction[0])
        if direction[1] > 0:
            ts.append((yT - origin[1]) / direction[1])
        if direction[1] < 0:
            ts.append((yB - origin[1]) / direction[1])
        ts = [t for t in ts if t > 0]
        return min(ts) if ts else 1.5

    max_dist = 15.0 * pr
    ray_events = []

    for d in dirs:
        tmax = _t_to_bounds(tpos, d)
        events = []
        for i, (p, (g1, g2)) in enumerate(zip(pts, gates)):
            if i == target_idx:
                continue
            if np.linalg.norm(p[:2] - tpos[:2]) > max_dist:
                continue
            for gx in (p[0] - gate_dx, p[0] + gate_dx):
                if abs(d[0]) < 1e-6:
                    continue
                t = (gx - tpos[0]) / d[0]
                if t <= 0 or t >= tmax:
                    continue
                y_at = tpos[1] + d[1] * t
                if (
                    (p[1] - gate_h / 2 - 1e-6)
                    <= y_at
                    <= (p[1] + gate_h / 2 + 1e-6)
                ):
                    events.append((t, i))
        events.sort(key=lambda e: e[0])
        ray_events.append((d, tmax, events))

    def anim_for_ray(direction, tmax, events):
        anims = []
        lines_created = VGroup()
        prev_t = 0.0
        speed = 1.25

        def seg(pt_a, pt_b, rt):
            line = Line(pt_a, pt_b, color=pc.uclaGold, stroke_width=6)
            lines_created.add(line)
            return Create(line, run_time=rt)

        for t_hit, idx in events:
            a = tpos + direction * prev_t
            b = tpos + direction * t_hit
            rt = max(0.08, (t_hit - prev_t) / max(tmax, 1e-6) * speed)
            anims.append(seg(a, b, rt))
            anims.append(
                dots[idx].animate.set_color(pc.blueGreen).set_stroke(width=0)
            )
            prev_t = t_hit

        a = tpos + direction * prev_t
        b = tpos + direction * tmax
        rt = max(0.12, (tmax - prev_t) / max(tmax, 1e-6) * speed)
        anims.append(seg(a, b, rt))
        anims.append(FadeOut(lines_created, run_time=0.25))
        return Succession(*anims)

    ray_anims = [anim_for_ray(d, tmax, evts) for (d, tmax, evts) in ray_events]
    self.play(AnimationGroup(*ray_anims, lag_ratio=0.05))

    self.next_slide()
