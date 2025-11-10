#!/usr/bin/env python3
"""
heat_diffusion.py
=================

2-D heat equation with Neumann BCs, single centered circular source,
optional exponential source fade, and optional global Newtonian cooling.

API
---
simulate_heat(
    nx=100, ny=100, lx=2.0, ly=2.0, alpha=0.01, n_steps=200, cfl=0.24,
    initial_temp=20.0,
    circle_intensity=50.0, circle_radius_frac=0.1,
    enable_circle=True, circle_steps=None, circle_decay_tau=0.0,
    enable_curve=False, curve_amplitude=8.0, curve_base=5.0, curve_thickness=2.0, curve_steps=None,
    cooling_rate=0.0
) -> np.ndarray
# Returns (n_steps+1, nx, ny)
"""

from __future__ import annotations

import argparse
import csv
import os

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


def _apply_neumann_bc(u: np.ndarray) -> None:
    """Apply zero-gradient (Neumann) boundary conditions in-place."""
    u[0, :] = u[1, :]
    u[-1, :] = u[-2, :]
    u[:, 0] = u[:, 1]
    u[:, -1] = u[:, -2]


def _build_center_circle_mask(
    nx: int, ny: int, radius: float
) -> tuple[np.ndarray, np.ndarray]:
    """Distances to center and boolean mask for a centered circle."""
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny), indexing="ij")
    cx, cy = nx // 2, ny // 2
    dist = np.sqrt((ii - cx) ** 2 + (jj - cy) ** 2)
    circle_mask = dist <= radius
    return dist, circle_mask


def _build_curve_distance(
    nx: int, ny: int, base: float, amplitude: float
) -> np.ndarray:
    """Vertical distance (in i-index) to a cosine curve of j-index."""
    j_idx = np.arange(ny)
    curve = base + amplitude * (
        1.0 - np.cos(2.0 * np.pi * (j_idx - ny / 2.0) / ny)
    )
    expected = np.tile(curve, (nx, 1))
    i_grid = np.arange(nx).reshape(nx, 1)
    return np.abs(i_grid - expected)


def simulate_heat(
    nx: int = 100,
    ny: int = 100,
    lx: float = 2.0,
    ly: float = 2.0,
    alpha: float = 0.01,
    n_steps: int = 200,
    cfl: float = 0.24,
    initial_temp: float = 20.0,
    circle_intensity: float = 50.0,
    circle_radius_frac: float = 0.1,
    enable_circle: bool = True,
    circle_steps: int | None = None,
    circle_decay_tau: float = 0.0,
    enable_curve: bool = False,
    curve_amplitude: float = 8.0,
    curve_base: float = 5.0,
    curve_thickness: float = 2.0,
    curve_steps: int | None = None,
    cooling_rate: float = 0.0,
) -> np.ndarray:
    """
    Run a 2-D heat diffusion simulation and return temperatures over time.

    - `cooling_rate` adds a global sink: du/dt -= cooling_rate * (u - initial_temp)
      (pulls field back to ambient faster).
    - `circle_decay_tau` applies exponential decay to the source amplitude per step:
        amp_t = amp_0 * exp(-t / tau)  (only while the source is active).
      Use 0 for no decay.

    Returns
    -------
    np.ndarray
        Array of shape (n_steps+1, nx, ny) (includes the t=0 field).
    """
    dx, dy = lx / (nx - 1), ly / (ny - 1)
    dt = cfl * min(dx * dx, dy * dy) / alpha

    u_time = np.empty((n_steps + 1, nx, ny), dtype=np.float64)
    u = np.full((nx, ny), float(initial_temp), dtype=np.float64)
    u_time[0] = u

    # Precompute sources
    circle_radius = circle_radius_frac * ny
    dist_circle, mask_circle = _build_center_circle_mask(nx, ny, circle_radius)

    if enable_curve:
        dist_curve = _build_curve_distance(
            nx, ny, base=curve_base, amplitude=curve_amplitude
        )

    circle_sigma2 = (circle_radius / 2.0) ** 2 if circle_radius > 0 else 1.0
    curve_sigma2 = (curve_thickness / 2.0) ** 2 if curve_thickness > 0 else 1.0

    # Time stepping
    for t in range(1, n_steps + 1):
        u_new = u.copy()
        # diffusion
        u_new[1:-1, 1:-1] = u[1:-1, 1:-1] + alpha * dt * (
            (u[2:, 1:-1] - 2.0 * u[1:-1, 1:-1] + u[:-2, 1:-1]) / (dx * dx)
            + (u[1:-1, 2:] - 2.0 * u[1:-1, 1:-1] + u[1:-1, :-2]) / (dy * dy)
        )

        # global Newton cooling toward ambient
        if cooling_rate > 0.0:
            u_new += -cooling_rate * (u - initial_temp) * dt

        # centered circular source
        if enable_circle and np.any(mask_circle):
            active = (circle_steps is None) or (t <= circle_steps)
            if active:
                # exponential decay of source amplitude (optional)
                amp = circle_intensity
                if circle_decay_tau > 0.0:
                    amp *= np.exp(-float(t) / float(circle_decay_tau))
                gaussian = np.exp(
                    -(dist_circle[mask_circle] ** 2) / (2.0 * circle_sigma2)
                )
                u_new[mask_circle] += amp * gaussian * dt

        # optional curve source
        if enable_curve:
            active = (curve_steps is None) or (t <= curve_steps)
            if active:
                curve_mask = dist_curve < curve_thickness
                if np.any(curve_mask):
                    gaussian_curve = np.exp(
                        -(dist_curve[curve_mask] ** 2) / (2.0 * curve_sigma2)
                    )
                    u_new[curve_mask] += circle_intensity * gaussian_curve * dt

        _apply_neumann_bc(u_new)
        u = u_new
        u_time[t] = u

    return u_time


# ------------------------------- CLI / Demo --------------------------------- #
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Heat Diffusion (single centered source)"
    )
    parser.add_argument("--nx", type=int, default=100)
    parser.add_argument("--ny", type=int, default=100)
    parser.add_argument("--lx", type=float, default=2.0)
    parser.add_argument("--ly", type=float, default=2.0)
    parser.add_argument("--alpha", type=float, default=0.01)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--cfl", type=float, default=0.24)
    parser.add_argument("--initial_temp", type=float, default=20.0)
    parser.add_argument("--circle_intensity", type=float, default=50.0)
    parser.add_argument("--circle_radius_frac", type=float, default=0.1)
    parser.add_argument("--enable_circle", action="store_true")
    parser.add_argument(
        "--no-circle", dest="enable_circle", action="store_false"
    )
    parser.set_defaults(enable_circle=True)
    parser.add_argument(
        "--circle_steps",
        type=int,
        default=10,
        help="Apply circle source for first N steps (−1 = always)",
    )
    parser.add_argument(
        "--circle_decay_tau",
        type=float,
        default=0.0,
        help="Exponential fade time for the circle source (0 = no fade)",
    )
    parser.add_argument("--enable_curve", action="store_true")
    parser.add_argument(
        "--no-curve", dest="enable_curve", action="store_false"
    )
    parser.set_defaults(enable_curve=False)
    parser.add_argument("--curve_amplitude", type=float, default=8.0)
    parser.add_argument("--curve_base", type=float, default=5.0)
    parser.add_argument("--curve_thickness", type=float, default=2.0)
    parser.add_argument(
        "--curve_steps",
        type=int,
        default=-1,
        help="Apply curve source for first N steps (−1 = always)",
    )
    parser.add_argument(
        "--cooling_rate",
        type=float,
        default=0.0,
        help="Global Newton cooling rate k (du/dt -= k*(u-T_amb))",
    )
    parser.add_argument(
        "--animate", action="store_true", help="Show matplotlib animation"
    )
    return parser.parse_args()


def _animate(u_time: np.ndarray, lx: float, ly: float):
    fig, ax = plt.subplots()
    vmin = float(np.min(u_time))
    vmax = float(np.max(u_time))
    if not np.isfinite(vmin):
        vmin = 0.0
    if not np.isfinite(vmax) or vmax <= vmin:
        vmax = vmin + 1e-6
    im = ax.imshow(
        u_time[0],
        cmap="hot",
        interpolation="nearest",
        extent=[0, lx, 0, ly],
        origin="lower",
        vmin=vmin,
        vmax=vmax,
    )
    fig.colorbar(im, label="Température (°C)")
    time_text = ax.text(
        0.05,
        0.95,
        "t = 0",
        transform=ax.transAxes,
        color="white",
        fontsize=12,
        verticalalignment="top",
    )

    def _frame(k):
        im.set_data(u_time[k])
        time_text.set_text(f"t-step: {k}")
        return im, time_text

    ani = animation.FuncAnimation(
        fig,
        _frame,
        frames=u_time.shape[0],
        interval=50,
        blit=False,
        repeat=False,
    )
    return fig, ani


def main() -> None:
    args = _parse_args()

    # Convert CLI inputs
    circle_steps = None if args.circle_steps < 0 else args.circle_steps
    curve_steps = None if args.curve_steps < 0 else args.curve_steps

    u_time = simulate_heat(
        nx=args.nx,
        ny=args.ny,
        lx=args.lx,
        ly=args.ly,
        alpha=args.alpha,
        n_steps=args.steps,
        cfl=args.cfl,
        initial_temp=args.initial_temp,
        circle_intensity=args.circle_intensity,
        circle_radius_frac=args.circle_radius_frac,
        enable_circle=args.enable_circle,
        circle_steps=circle_steps,
        enable_curve=args.enable_curve,
        curve_amplitude=args.curve_amplitude,
        curve_base=args.curve_base,
        curve_thickness=args.curve_thickness,
        curve_steps=curve_steps,
    )

    # Compute physical dt from args
    dx = args.lx / (args.nx - 1)
    dy = args.ly / (args.ny - 1)
    phys_dt = args.cfl * min(dx * dx, dy * dy) / args.alpha

    # NEW: save CSV with render_dt = 0.05
    save_heat_csv(u_time, phys_dt, render_dt=0.05, path="states_sph/heat.csv")

    # if args.animate:
    fig, ani = _animate(u_time, lx=args.lx, ly=args.ly)
    plt.show()


def save_heat_csv(
    u_time: np.ndarray,
    phys_dt: float,
    render_dt: float = 0.05,
    path: str = "states_sph/heat.csv",
) -> None:
    """
    Resample simulation frames based on a user-defined render_dt (not physical dt),
    then write CSV at <path>.

    CSV columns:
        time, i, j, temperature

    Parameters
    ----------
    u_time : np.ndarray
        Array of shape (n_steps+1, nx, ny), temperature history.
    phys_dt : float
        Physical dt used in simulation (returned from caller).
        (Only used to reconstruct physical time => can be ignored if desired.)
    render_dt : float
        Interval (in simulation time units) to save frames. Does NOT change simulation.
        Example: 0.05 → output every 0.05 s.
    path : str
        CSV output path
    """

    # Ensure folder exists
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    n_steps = u_time.shape[0]
    nx, ny = u_time.shape[1], u_time.shape[2]

    # Original time grid
    t_phys = np.arange(n_steps) * phys_dt
    t_end = t_phys[-1]

    # Target time grid
    t_target = np.arange(0, t_end + 1e-12, render_dt)

    # Map target times to nearest simulation step
    # (You could interpolate, but nearest is simplest and faster)
    frame_ids = np.clip(
        (t_target / phys_dt).round().astype(int), 0, n_steps - 1
    )

    # Write CSV
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "i", "j", "temperature"])
        for tidx, t in enumerate(t_target):
            k = frame_ids[tidx]
            frame = u_time[k]  # shape (nx,ny)
            for i in range(nx):
                for j in range(ny):
                    writer.writerow([f"{t:.6f}", i, j, float(frame[i, j])])

    print(f"[OK] heat.csv saved to: {path}")


if __name__ == "__main__":
    main()
