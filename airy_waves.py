#!/usr/bin/env python3
"""
airy_waves.py
=============

Python adaptation of a subset of the C++ header-only utilities for
deep-water Airy linear waves as described in the provided C++ snippet.

Coordinate convention:
- x: horizontal propagation axis
- y: vertical axis (positive upward); labels b are typically ≤ 0 (subsurface)
- z: lateral axis (no motion)

Implements:
- AiryWavesData (parameters, dispersion update)
- AiryWaves (displacements, velocities, surface height, particle state)

All functions are written for scalar inputs but are also vectorized for NumPy
arrays; pass arrays of a, b to get array outputs.
"""

from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np

ArrayLike = Union[float, np.ndarray]


@dataclass
class AiryWavesData:
    """User-defined parameters for an Airy deep-water wave model."""

    amplitude: float = 1.0  # crest amplitude [m]
    wavelength: float = 10.0  # wavelength [m]
    waterDepth: float = 50.0  # depth [m] (unused in pure deep-water approx)
    gravity: float = 9.81  # gravity [m/s^2]
    k: float = 0.0  # wavenumber [rad/m] = 2π/λ
    omega: float = 0.0  # angular frequency [rad/s] = sqrt(g k)

    def __post_init__(self) -> None:
        self.update()

    def update(self) -> None:
        """Recompute dispersion elements k and omega for deep water."""
        self.k = 2.0 * np.pi / self.wavelength
        self.omega = np.sqrt(self.gravity * self.k)
        print(self.k)
        print(self.omega)


class AiryWaves(AiryWavesData):
    """Airy wave helper with 2D and 3D APIs (z is unaffected)."""

    # --- Low-level helpers (scalar/array safe) ---
    def depth_factor(self, b: ArrayLike) -> ArrayLike:
        return np.exp(self.k * b)

    def phase(self, a: ArrayLike, t: ArrayLike) -> ArrayLike:
        return self.k * a - self.omega * t

    # --- Displacements ---
    def getHorizontalDisplacement(
        self, a: ArrayLike, b: ArrayLike, t: float
    ) -> ArrayLike:
        """
        Horizontal displacement ξ(a,b,t) = -A e^{k b} sin(θ),  θ = k a - ω t
        """
        theta = self.phase(a, t)
        AE = self.amplitude * self.depth_factor(b)
        return -AE * np.sin(theta)

    def getVerticalDisplacement(
        self, a: ArrayLike, b: ArrayLike, t: float
    ) -> ArrayLike:
        """
        Vertical displacement η(a,b,t) = A e^{k b} cos(θ - k A e^{k b} sin θ)
        Note: matches the provided C++ expression.
        """
        theta = self.phase(a, t)
        AE = self.amplitude * self.depth_factor(b)
        return AE * np.cos(theta - self.k * AE * np.sin(theta))

    # --- Surface elevation (Eulerian on x at y=0) ---
    def getWaterHeight(self, x: ArrayLike, t: float) -> ArrayLike:
        return self.amplitude * np.cos(self.phase(x, t))

    # --- Particle kinematics given 3D label (a,b,c) ---
    def getParticlePosition(
        self, a: ArrayLike, b: ArrayLike, c: ArrayLike, t: float
    ) -> Tuple[ArrayLike, ArrayLike, ArrayLike]:
        x = a + self.getHorizontalDisplacement(a, b, t)
        y = b + self.getVerticalDisplacement(a, b, t)
        z = c  # unchanged
        return x, y, z

    def getParticleVelocity(
        self, a: ArrayLike, b: ArrayLike, c: ArrayLike, t: float
    ) -> Tuple[ArrayLike, ArrayLike, ArrayLike]:
        """
        Velocity components derived from the provided C++ snippet:
          u = A e^{k b} ω cos θ
          w = A e^{k b} sin(k ξ + θ) (ω - k u)
          v_z = 0
        where ξ is the horizontal displacement.
        """
        theta = self.phase(a, t)
        AE = self.amplitude * self.depth_factor(b)
        u = AE * self.omega * np.cos(theta)

        xi = self.getHorizontalDisplacement(a, b, t)
        w = AE * np.sin(self.k * xi + theta) * (self.omega - self.k * u)

        return u, w, np.zeros_like(u)


# --------------------------- Demo & helper ---------------------------------


def sample_labels_grid(N: int, L: float, H: float):
    """
    Create uniform (a,b,c) label grid:
      a ∈ [-L, L],  b ∈ [-H, 0],  c = 0
    Returns arrays of shape (N, N) for a, b, c.
    """
    a = np.linspace(-L, L, N)
    b = np.linspace(-H, 0.0, N)
    A, B = np.meshgrid(a, b, indexing="xy")
    C = np.zeros_like(A)
    return A, B, C


def demo_quiver(
    N: int = 21,
    L: float = 10.0,
    H: float = 5.0,
    t: float = 0.0,
    amp: float = 1.0,
    wavelength: float = 10.0,
    g: float = 9.81,
) -> None:
    """
    Plot particles (Eulerian positions) and velocity arrows at time t.
    """
    import matplotlib.pyplot as plt

    wv = AiryWaves(
        amplitude=amp, wavelength=wavelength, waterDepth=100.0, gravity=g
    )
    A, B, C = sample_labels_grid(N, L, H)

    X, Y, Z = wv.getParticlePosition(A, B, C, t)
    U, W, _ = wv.getParticleVelocity(A, B, C, t)

    plt.figure()
    plt.title(f"Airy particles and velocity field (t={t:.2f}s)")
    plt.scatter(X, Y, s=10, alpha=0.7, label="particles")
    plt.quiver(
        X,
        Y,
        U,
        W,
        angles="xy",
        scale_units="xy",
        scale=1.0,
        width=0.003,
        alpha=0.8,
        label="velocity",
    )
    # Surface line (y=water height) for reference
    xs = np.linspace(-L, L, 400)
    eta = wv.getWaterHeight(xs, t)
    plt.plot(xs, eta, lw=2, label="surface y=η(x,t)")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis("equal")
    plt.xlim(-L, L)
    plt.ylim(-H - 0.25 * H, max(0.2, 1.2 * np.max(eta)))
    plt.grid(True, ls="--", alpha=0.3)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


def export_csv(
    amplitude: float, wave_length: float, dt_render: float, time_sim: float
) -> str:
    """
    Export a uniform grid of Airy particles and velocities to a semicolon-separated CSV.

    Header:
      index_p; time; label_x; label_y; pos_x; pos_y; vel_x; vel_y

    Notes
    -----
    - Grid labels are sampled uniformly on a×b ∈ [-L, L] × [-H, 0].
    - Indices go from 0..(N*N-1) row-major on the (b, a) meshgrid.
    - Writes to 'airy_particles.csv' in the current working directory.
    - Returns the absolute path to the CSV.
    """
    # Internal defaults (tweak here if needed)
    N = 10  # grid resolution per axis
    L = 2.5  # half-span in x for labels
    H = 5.0  # depth span (labels b in [-H, 0])
    gravity = 9.81
    waterDepth = 100.0
    out_path = os.path.abspath("states_sph/airy_particles.csv")

    # Build wave model
    wv = AiryWaves(
        amplitude=amplitude,
        wavelength=wave_length,
        waterDepth=waterDepth,
        gravity=gravity,
    )

    # Label grid
    A, B, C = sample_labels_grid(N, L, H)

    # Time samples
    if dt_render <= 0.0:
        raise ValueError("dt_render must be > 0.")
    if time_sim < 0.0:
        raise ValueError("time_sim must be ≥ 0.")

    # Number of steps including t=0 and t=time_sim (if divisible)
    n_steps = int(math.floor(time_sim / dt_render + 1e-12)) + 1
    times = [i * dt_render for i in range(n_steps)]
    if times[-1] < time_sim - 1e-12:
        times.append(
            time_sim
        )  # ensure final time included if not an exact multiple

    # Open CSV and write
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "index_p",
                "time",
                "label_x",
                "label_y",
                "pos_x",
                "pos_y",
                "vel_x",
                "vel_y",
            ]
        )

        # Flattened index mapping (row-major on B (rows) × A (cols))
        num = N * N
        # Precompute static label indices
        label_x = A.ravel()
        label_y = B.ravel()
        idxs = np.arange(num, dtype=np.int64)

        for t in times:
            # Positions and velocities at time t
            X, Y, _ = wv.getParticlePosition(A, B, C, t)
            U, W, _ = wv.getParticleVelocity(A, B, C, t)

            # Flatten to vectors
            pos_x = X.ravel()
            pos_y = Y.ravel()
            vel_x = U.ravel()
            vel_y = W.ravel()

            # Write rows
            for i in range(num):
                writer.writerow(
                    [
                        int(idxs[i]),
                        float(t),
                        float(label_x[i]),
                        float(label_y[i]),
                        float(pos_x[i]),
                        float(pos_y[i]),
                        float(vel_x[i]),
                        float(vel_y[i]),
                    ]
                )

    return out_path


if __name__ == "__main__":
    # --- Parameters used for both CSV export and the demo plot ---
    amp = 0.2
    wave_length = 5.0
    dt_render = 0.2
    time_sim = 6.28

    # 1) Export CSV
    path = export_csv(
        amplitude=amp,
        wave_length=wave_length,
        dt_render=dt_render,
        time_sim=time_sim,
    )
    print("CSV written to:", path)

    # 2) Show a Matplotlib quiver demo (same wave params as the CSV)
    #    Use L/H consistent with export_csv defaults for a comparable view.
    demo_quiver(
        N=21, L=5, H=5.0, t=0.0, amp=amp, wavelength=wave_length, g=9.81
    )
