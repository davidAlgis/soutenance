import csv
import math
import os
import random

import matplotlib.pyplot as plt
import numpy as np

# =========================
# Parameters (tweak freely)
# =========================
N = 30
seed = 1
bounds = (0.1, 0.9)  # domain box [lo, hi] x [lo, hi]
min_distance = 0.05  # for random rejection placement
total_mass = 1.0  # uniform total mass for SPH
h_override = None  # set to a float to force smoothing length
output_csv = "states_sph/particles.csv"  # single CSV with all columns
make_plot = True  # set False to skip plotting


# =========================
# Helpers
# =========================
def ensure_dir_for_file(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def estimate_h(n, bounds=(0.1, 0.9), factor=1.2):
    """h ~ factor * spacing, spacing ~ sqrt(area/n) in 2D."""
    lo, hi = bounds
    area = (hi - lo) ** 2
    spacing = math.sqrt(area / max(1, n))
    return factor * spacing


def pairwise_distances(A, B):
    """
    Fast pairwise Euclidean distances between A (Na x 2) and B (Nb x 2).
    Returns (Na, Nb) matrix.
    """
    A2 = np.sum(A**2, axis=1, keepdims=True)  # (Na,1)
    B2 = np.sum(B**2, axis=1)[None, :]  # (1,Nb)
    cross = A @ B.T  # (Na,Nb)
    D2 = A2 - 2.0 * cross + B2
    D2 = np.maximum(D2, 0.0)
    return np.sqrt(D2)


# =========================
# Random particles (rejection with min_distance)
# =========================
def place_particles_np(
    N, seed=42, min_distance=0.05, bounds=(0.1, 0.9), max_attempts=200000
):
    rng = random.Random(seed)
    lo, hi = bounds
    pts = []

    if N <= 0:
        return np.zeros((0, 2), dtype=float)

    for _ in range(max_attempts):
        if len(pts) >= N:
            break
        x = rng.uniform(lo, hi)
        y = rng.uniform(lo, hi)
        p = np.array([x, y])
        if not pts:
            pts.append(p)
            continue
        P = np.vstack(pts)
        d = np.sqrt(np.sum((P - p) ** 2, axis=1))
        if np.all(d >= min_distance):
            pts.append(p)

    if len(pts) < N:
        print(
            f"Warning: Only placed {len(pts)} particles due to distance constraints."
        )

    return np.vstack(pts) if pts else np.zeros((0, 2), dtype=float)


# =========================
# Quincunx (staggered) grid
# =========================
def generate_quincunx_np(N, bounds=(0.1, 0.9)):
    """
    Produce >= N points in a staggered grid, then truncate to N.
    """
    lo, hi = bounds
    L = hi - lo

    rows = max(1, int(math.floor(math.sqrt(max(1, N)))))
    guard = 0

    while True:
        cols = max(1, int(math.ceil(N / rows)))

        y_vals = (
            np.linspace(lo, hi, rows)
            if rows > 1
            else np.array([(lo + hi) / 2.0])
        )
        x_base = (
            np.linspace(lo, hi, cols)
            if cols > 1
            else np.array([(lo + hi) / 2.0])
        )

        pts = []
        dx = (L / (cols - 1)) if cols > 1 else 0.0

        for r_idx, y in enumerate(y_vals):
            shift = (dx / 2.0) if (cols > 1 and (r_idx % 2 == 1)) else 0.0
            xs = x_base + shift
            mask = (xs >= lo) & (xs <= hi)
            xs = xs[mask]
            ys = np.full_like(xs, y)
            if xs.size:
                pts.append(np.stack([xs, ys], axis=1))

        P = np.vstack(pts) if pts else np.zeros((0, 2))
        if P.shape[0] >= N:
            return P[:N]

        rows += 1
        guard += 1
        if guard > 500:
            raise RuntimeError("Could not generate enough quincunx points.")


# =========================
# Greedy nearest assignment
# =========================
def greedy_match_random_to_quincunx_np(random_pts, quincunx_pts):
    """
    For each random point (in original order), pick closest unused quincunx point.
    Returns (assigned_quincunx_pts, assigned_indices_into_quincunx).
    """
    N = random_pts.shape[0]
    D = pairwise_distances(random_pts, quincunx_pts)  # (N, N)
    used = np.zeros(quincunx_pts.shape[0], dtype=bool)
    tgt = np.zeros_like(random_pts)
    idxs = np.zeros(N, dtype=int)

    for i in range(N):
        masked = np.where(used, np.inf, D[i])
        j = int(np.argmin(masked))
        used[j] = True
        tgt[i] = quincunx_pts[j]
        idxs[i] = j

    return tgt, idxs


# =========================
# SPH density (Gaussian 2D)
# =========================
def gaussian_kernel_matrix(dist_mat, h):
    """
    2D normalized Gaussian:
      W(r,h) = 1/(pi h^2) * exp( - (r/h)^2 )
    dist_mat: (N,N) pairwise distances.
    Returns W matrix (N,N).
    """
    if h <= 0:
        raise ValueError("Smoothing length h must be > 0.")
    C = 1.0 / (math.pi * h * h)
    return C * np.exp(-((dist_mat / h) ** 2))


def compute_sph_density_np(
    positions, h=None, total_mass=1.0, bounds=(0.1, 0.9)
):
    """
    ρ_i = Σ_j m_j W_ij, with uniform masses by default (sum m_j = total_mass).
    """
    N = positions.shape[0]
    if N == 0:
        return np.zeros((0,), dtype=float), (h if h is not None else 0.0)

    if h is None:
        h = estimate_h(N, bounds=bounds, factor=1.2)

    m = np.full(N, total_mass / N, dtype=float)  # uniform masses
    D = pairwise_distances(positions, positions)  # (N,N)
    W = gaussian_kernel_matrix(D, h)  # (N,N)
    rho = W @ m  # (N,)
    return rho, h


# =========================
# Color mapping (sunny→blueGreen→oxfordBlue)
# =========================
def interpolate_colors_piecewise(rho, low_rgb, mid_rgb, high_rgb):
    """
    Map each ρ to RGB using:
      min(ρ) -> low_rgb (sunny)
      median(ρ) -> mid_rgb (blueGreen)
      max(ρ) -> high_rgb (oxfordBlue)
    Piecewise linear interpolation.
    """
    rho = np.asarray(rho, dtype=float)
    rmin = float(np.min(rho)) if rho.size else 0.0
    rmed = float(np.median(rho)) if rho.size else 0.0
    rmax = float(np.max(rho)) if rho.size else 0.0

    low = np.array(low_rgb, dtype=float)
    mid = np.array(mid_rgb, dtype=float)
    high = np.array(high_rgb, dtype=float)

    colors = np.zeros((rho.size, 3), dtype=float)

    if rmax == rmin:
        colors[:] = mid
        return colors.astype(np.uint8)

    lower_mask = rho <= rmed
    if rmed > rmin:
        t = (rho[lower_mask] - rmin) / (rmed - rmin)
        colors[lower_mask] = (1 - t)[:, None] * low + t[:, None] * mid
    else:
        colors[lower_mask] = mid

    upper_mask = ~lower_mask
    if rmax > rmed:
        t = (rho[upper_mask] - rmed) / (rmax - rmed)
        colors[upper_mask] = (1 - t)[:, None] * mid + t[:, None] * high
    else:
        colors[upper_mask] = mid

    return np.clip(np.rint(colors), 0, 255).astype(np.uint8)


# =========================
# Plot
# =========================
def plot_mapping_single_figure(
    random_pts,
    quincunx_pts,
    colors_rgb,
    bounds=(0.1, 0.9),
    title="Random → Quincunx mapping",
):
    """
    One figure:
      - circles: random positions
      - squares: quincunx targets
      - arrows: random -> quincunx
      - both endpoints colored using the RGB interpolation
    """
    fig, ax = plt.subplots(figsize=(7, 7))

    # Normalize colors to [0,1] for matplotlib
    c = colors_rgb.astype(float) / 255.0

    # Plot arrows and points (same color per pair)
    for i in range(random_pts.shape[0]):
        x0, y0 = random_pts[i]
        x1, y1 = quincunx_pts[i]
        ax.arrow(
            x0,
            y0,
            x1 - x0,
            y1 - y0,
            length_includes_head=True,
            head_width=0.01,
            head_length=0.015,
            linewidth=0.8,
            color=c[i],
            alpha=0.8,
        )
        ax.scatter([x0], [y0], s=35, marker="o", edgecolors="none", c=[c[i]])
        ax.scatter([x1], [y1], s=45, marker="s", edgecolors="none", c=[c[i]])

    lo, hi = bounds
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    # draw the active domain
    rect = plt.Rectangle(
        (lo, lo), hi - lo, hi - lo, fill=False, linestyle="--"
    )
    ax.add_patch(rect)
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)
    plt.tight_layout()
    plt.show()


# =========================
# Main
# =========================
def main():
    ensure_dir_for_file(output_csv)

    # 1) Random particles
    rnd = place_particles_np(
        N, seed=seed, min_distance=min_distance, bounds=bounds
    )

    # 2) Quincunx targets & greedy mapping (row i -> target for particle i)
    qx_all = generate_quincunx_np(N, bounds=bounds)
    qx_assigned, _ = greedy_match_random_to_quincunx_np(rnd, qx_all)

    # 3) SPH density on the *random* configuration
    h = (
        h_override
        if h_override is not None
        else estimate_h(rnd.shape[0], bounds=bounds, factor=1.2)
    )
    rho, h_used = compute_sph_density_np(
        rnd, h=h, total_mass=total_mass, bounds=bounds
    )
    print(f"SPH smoothing length h = {h_used:.6f}")

    # 4) Colors from density (sunny→blueGreen→oxfordBlue)
    SUNNY = (249, 248, 113)
    BLUE_GREEN = (31, 156, 186)
    OXFORD_BLUE = (0, 46, 69)
    colors = interpolate_colors_piecewise(
        rho, SUNNY, BLUE_GREEN, OXFORD_BLUE
    )  # (N,3) uint8

    # 5) Write single CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Particle",
                "X",
                "Y",
                "X quincunx",
                "Y quincunx",
                "rho",
                "color r",
                "color g",
                "color b",
            ]
        )
        for i in range(rnd.shape[0]):
            writer.writerow(
                [
                    i + 1,
                    f"{rnd[i,0]:.6f}",
                    f"{rnd[i,1]:.6f}",
                    f"{qx_assigned[i,0]:.6f}",
                    f"{qx_assigned[i,1]:.6f}",
                    f"{rho[i]:.8f}",
                    int(colors[i, 0]),
                    int(colors[i, 1]),
                    int(colors[i, 2]),
                ]
            )
    print(f"Wrote {rnd.shape[0]} rows to '{output_csv}'")
    print(
        "Convention: row i is random particle i; 'X quincunx','Y quincunx' are its target positions."
    )

    # 6) One plot with both positions + arrows, colored by density interpolation
    if make_plot:
        plot_mapping_single_figure(
            rnd,
            qx_assigned,
            colors,
            bounds=bounds,
            title="Random → Quincunx (colored by ρ)",
        )


if __name__ == "__main__":
    main()
