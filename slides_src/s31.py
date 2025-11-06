import numpy as np
import palette_colors as pc
from manim import *
from slide_registry import slide


@slide(31)
def slide_31(self):
    # ---------- Top bar & intro ----------
    bar = self._top_bar("Lancer de rayon pour la RPPV")
    self.add(bar)
    self.add_foreground_mobject(bar)
    self.start_body()
    intro = self.add_body_text(
        "Utiliser le lancer de rayon pour la RPPV :",
        font_size=self.BODY_FONT_SIZE,
    )

    # ---------- Layout under intro ----------
    x_left = -config.frame_width / 2 + 0.6
    x_right = config.frame_width / 2 - 0.6
    y_bottom = -config.frame_height / 2 + 0.6

    body_left, body_right = x_left + 0.3, x_right - 0.3
    body_top = intro.get_bottom()[1] - 0.45
    body_bottom = y_bottom + 0.35
    body_w = body_right - body_left
    body_h = max(1.0, body_top - body_bottom)

    # ---------- Load 30 points ----------
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
                if cx in data.dtype.names and cy in data.dtype.names:
                    arr = np.column_stack([data[cx], data[cy]])[:max_count]
                    xmin, ymin = np.min(arr, axis=0)
                    xmax, ymax = np.max(arr, axis=0)
                    if xmax > xmin and ymax > ymin:
                        nx = (arr[:, 0] - xmin) / (xmax - xmin)
                        ny = (arr[:, 1] - ymin) / (ymax - ymin)
                        px = body_left + nx * body_w
                        py = body_bottom + ny * body_h
                        return np.column_stack([px, py, np.zeros_like(px)])
        # Fallback small grid
        cols_g, rows_g = 6, 5
        xs = np.linspace(body_left, body_right, cols_g + 2)[1:-1]
        ys = np.linspace(body_bottom, body_top, rows_g + 2)[1:-1][::-1]
        pts = [
            [xs[i], ys[j], 0.0] for j in range(rows_g) for i in range(cols_g)
        ]
        return np.array(pts[:max_count], dtype=float)

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

    # ---------- Target color + dashed neighborhood circle ----------
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

    # ---------- Gates (dotted) ----------
    gate_dx = 6.0 * pr
    gate_h = 20.0 * pr

    # Ray setup (NE, NW, SE, SW)
    tpos = target.get_center()
    dirs = [
        np.array([+1, +1, 0.0]),
        np.array([-1, +1, 0.0]),
        np.array([+1, -1, 0.0]),
        np.array([-1, -1, 0.0]),
    ]
    dirs = [d / np.linalg.norm(d[:2]) for d in dirs]
    xL, xR = -config.frame_width / 2 + 0.05, config.frame_width / 2 - 0.05
    yB, yT = -config.frame_height / 2 + 0.05, config.frame_height / 2 - 0.05

    def _t_to_bounds(o, d):
        ts = []
        if d[0] > 0:
            ts.append((xR - o[0]) / d[0])
        if d[0] < 0:
            ts.append((xL - o[0]) / d[0])
        if d[1] > 0:
            ts.append((yT - o[1]) / d[1])
        if d[1] < 0:
            ts.append((yB - o[1]) / d[1])
        ts = [t for t in ts if t > 0]
        return min(ts) if ts else 1.5

    max_dist = 15.0 * pr

    # Collect ray events to know nearest hits
    ray_events = []
    for d in dirs:
        tmax = _t_to_bounds(tpos, d)
        events = []
        for i, p in enumerate(pts):
            if i == target_idx:
                continue
            if np.linalg.norm(p[:2] - tpos[:2]) > max_dist:  # outside 15*pr
                continue
            for gx in (p[0] - gate_dx, p[0] + gate_dx):
                if abs(d[0]) < 1e-8:
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

    nearest_hit_indices = set(e[0][1] for e in ray_events if e[2])
    # Fallback: ensure visibility if nothing was found
    if not nearest_hit_indices and N > 1:
        # choose 6 closest (excluding target)
        idxs = [i for i in range(N) if i != target_idx]
        idxs.sort(key=lambda i: np.linalg.norm(pts[i][:2] - tpos[:2]))
        nearest_hit_indices.update(idxs[: min(6, len(idxs))])

    faint_opacity = 0.35  # higher than before for readability
    strong_opacity = 1.0
    stroke_w = 5  # thicker for visibility

    gates_vm = []
    for i, p in enumerate(pts):
        if i == target_idx:
            continue
        x, y = p[0], p[1]
        L = Line(
            [x - gate_dx, y - gate_h / 2, 0], [x - gate_dx, y + gate_h / 2, 0]
        )
        R = Line(
            [x + gate_dx, y - gate_h / 2, 0], [x + gate_dx, y + gate_h / 2, 0]
        )
        Ld = DashedVMobject(
            L,
            num_dashes=22,
            dashed_ratio=0.55,
            color=BLACK,
            stroke_width=stroke_w,
        )
        Rd = DashedVMobject(
            R,
            num_dashes=22,
            dashed_ratio=0.55,
            color=BLACK,
            stroke_width=stroke_w,
        )
        opa = strong_opacity if i in nearest_hit_indices else faint_opacity
        # AFTER (0.19-compatible)
        Ld.set_stroke(color=BLACK, width=stroke_w, opacity=opa)
        Rd.set_stroke(color=BLACK, width=stroke_w, opacity=opa)

        gates_vm += [Ld, Rd]

    gates_group = VGroup(*gates_vm)
    self.play(Create(gates_group, run_time=0.45))
    self.next_slide()

    # ---------- Rays (grow-and-flash like slide 30) + color on first hit ----------
    def grow_and_flash(start_pt, end_pt):
        seg = VMobject().set_stroke(pc.uclaGold, width=6)
        seg.set_points_as_corners(
            np.vstack([start_pt, start_pt]).astype(float)
        )
        dot = Dot(end_pt, color=pc.uclaGold, radius=0.06)

        def _upd(mob, alpha, s=start_pt.astype(float), e=end_pt.astype(float)):
            p = s + (e - s) * alpha
            mob.set_points_as_corners(np.vstack([s, p]))

        return Succession(
            FadeIn(seg, run_time=0.01),
            UpdateFromAlphaFunc(seg, _upd, run_time=0.50, rate_func=smooth),
            Flash(dot, color=pc.uclaGold, flash_radius=0.18, time_width=0.25),
            FadeOut(seg, run_time=0.25),
            FadeOut(dot, run_time=0.20),
        )

    sequences = []
    for d, tmax, events in ray_events:
        end_free = tpos + d * tmax
        if events:
            t_hit, idx = events[0]
            hit_pt = tpos + d * t_hit
            sequences.append(grow_and_flash(tpos, hit_pt))
            if np.linalg.norm(pts[idx][:2] - tpos[:2]) <= max_dist + 1e-6:
                sequences.append(dots[idx].animate.set_color(pc.blueGreen))
            sequences.append(grow_and_flash(hit_pt, end_free))
        else:
            sequences.append(grow_and_flash(tpos, end_free))

    self.play(LaggedStart(*sequences, lag_ratio=0.22))
    self.next_slide()
