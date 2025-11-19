import os

import imageio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap, Normalize


def simulate_wave_2d_dirichlet(
    L=1.0,  # half-domain size; x, y ∈ [-L, L]
    c=1.0,  # wave speed
    W=0.3,  # radius of the central circular region for the initial bell (W/2)
    A=1.0,  # amplitude of the Gaussian bell
    sigma=0.08,  # std dev of the Gaussian bell
    N=151,  # number of spatial nodes in both x and y (nx=ny=N, odd recommended)
    T=2.0,  # total simulated duration
    dt=0.005,  # user-requested output sampling step
    t0=0.0,  # time at which the truncated Gaussian is applied
):
    """
    Solve ∂²h/∂t² = c² (∂²h/∂x² + ∂²h/∂y²) on x, y ∈ [-L, L] with Dirichlet BCs h=0.
    """
    if t0 < 0:
        raise ValueError("t0 must be ≥ 0.")
    if N < 3:
        raise ValueError("N must be at least 3 for a valid grid.")

    nx = N
    ny = N

    # --- Grids
    x = np.linspace(-L, L, nx)
    y = np.linspace(-L, L, ny)
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    h = dx

    # Handle c = 0
    if c == 0.0:
        nt_out = int(np.floor(T / dt)) + 1
        t_out = np.arange(nt_out) * dt
        X, Y = np.meshgrid(x, y, indexing="ij")
        R = np.sqrt(X**2 + Y**2)
        bell = np.zeros((nx, ny), dtype=float)
        mask = R <= W / 2
        bell[mask] = A * np.exp(-0.5 * (R[mask] / sigma) ** 2)
        H_out = np.zeros((nt_out, nx, ny), dtype=float)
        if 0.0 <= t0 <= T:
            start_idx = int(round(t0 / dt))
            start_idx = min(max(start_idx, 0), nt_out - 1)
            H_out[start_idx:] = bell
        return H_out, x, y, t_out

    # --- CFL Condition
    dt_user = dt
    dt_sim = dt_user
    cfl_limit = 1.0 / np.sqrt(2)
    cfl_actual = c * dt_user / h

    if cfl_actual > cfl_limit:
        dt_sim = h / (c * np.sqrt(2.0))

    # --- Build the 2D bell
    X, Y = np.meshgrid(x, y, indexing="ij")
    R = np.sqrt(X**2 + Y**2)
    bell = np.zeros((nx, ny), dtype=float)
    mask = R <= W / 2
    bell[mask] = A * np.exp(-0.5 * (R[mask] / sigma) ** 2)

    # --- Allocate internal simulation arrays
    nt_sim = int(np.floor(T / dt_sim)) + 1
    t_sim = np.arange(nt_sim) * dt_sim
    lam2 = (c * dt_sim / h) ** 2
    H_sim = np.zeros((nt_sim, nx, ny), dtype=float)

    if t0 >= T or nt_sim < 2:
        nt_out = int(np.floor(T / dt_user)) + 1
        t_out = np.arange(nt_out) * dt_user
        H_out = np.zeros((nt_out, nx, ny), dtype=float)
        return H_out, x, y, t_out

    n0 = int(round(t0 / dt_sim))
    n0 = min(max(n0, 0), nt_sim - 1)

    # Initial conditions
    u_prev = bell.copy()
    u_prev[0, :] = 0.0
    u_prev[-1, :] = 0.0
    u_prev[:, 0] = 0.0
    u_prev[:, -1] = 0.0
    H_sim[n0] = u_prev

    # First step (Taylor)
    if n0 + 1 < nt_sim:
        u = u_prev.copy()
        lap = np.zeros((nx, ny), dtype=float)
        lap[1:-1, 1:-1] = (
            u_prev[2:, 1:-1]
            + u_prev[:-2, 1:-1]
            + u_prev[1:-1, 2:]
            + u_prev[1:-1, :-2]
            - 4.0 * u_prev[1:-1, 1:-1]
        )
        u[1:-1, 1:-1] = u_prev[1:-1, 1:-1] + 0.5 * lam2 * lap[1:-1, 1:-1]
        u[0, :] = u[-1, :] = u[:, 0] = u[:, -1] = 0.0
        H_sim[n0 + 1] = u

        # Leapfrog
        for n in range(n0 + 1, nt_sim - 1):
            u_next = np.empty((nx, ny), dtype=float)
            lap = np.zeros((nx, ny), dtype=float)
            lap[1:-1, 1:-1] = (
                u[2:, 1:-1]
                + u[:-2, 1:-1]
                + u[1:-1, 2:]
                + u[1:-1, :-2]
                - 4.0 * u[1:-1, 1:-1]
            )
            u_next[1:-1, 1:-1] = (
                2.0 * u[1:-1, 1:-1]
                - u_prev[1:-1, 1:-1]
                + lam2 * lap[1:-1, 1:-1]
            )
            u_next[0, :] = u_next[-1, :] = u_next[:, 0] = u_next[:, -1] = 0.0
            u_prev, u = u, u_next
            H_sim[n + 1] = u

    # Downsample
    nt_out = int(np.floor(T / dt_user)) + 1
    t_out = np.arange(nt_out) * dt_user
    idx_out = np.round(t_out / dt_sim).astype(int)
    idx_out = np.clip(idx_out, 0, nt_sim - 1)
    H_out = H_sim[idx_out]

    return H_out, x, y, t_out


if __name__ == "__main__":
    # --- 1. Simulation Parameters ---
    L_VAL = 1.0
    C_VAL = 1.0
    W_VAL = 0.5
    A_VAL = 1.0
    SIGMA_VAL = 0.1
    N_VAL = 151
    T_VAL = 3.0
    DT_VAL = 0.02
    T0_VAL = 0.0

    print("Running 2D wave simulation...")
    H, x, y, t = simulate_wave_2d_dirichlet(
        L=L_VAL,
        c=C_VAL,
        W=W_VAL,
        A=A_VAL,
        sigma=SIGMA_VAL,
        N=N_VAL,
        T=T_VAL,
        dt=DT_VAL,
        t0=T0_VAL,
    )
    print(f"Simulation complete. Total frames: {H.shape[0]}")

    # --- 2. Custom Colormap Setup (More Intense Blue-Green Only) ---

    # Max positive displacement color (your desired blue-green)
    BLUE_GREEN_LIGHT = (0.12, 0.61, 0.73)
    # Zero displacement color
    WHITE = (1.0, 1.0, 1.0)
    # Max negative displacement color (a more saturated/darker blue-green)
    # Example: slightly darker blue-green (values decreased by ~20%)
    BLUE_GREEN_DARK = (0.08, 0.40, 0.48)

    # Create a divergent map: Dark BlueGreen (Min) -> White (Zero) -> Light BlueGreen (Max)
    def create_divergent_cmap(min_color, center_color, max_color):
        colors = [min_color, center_color, max_color]
        nodes = [0.0, 0.5, 1.0]
        return LinearSegmentedColormap.from_list(
            "IntenseBlueGreen", list(zip(nodes, colors))
        )

    custom_cmap = create_divergent_cmap(
        BLUE_GREEN_LIGHT, WHITE, BLUE_GREEN_LIGHT
    )

    # Determine absolute max for symmetric scaling
    abs_max = np.max(np.abs(H))
    if abs_max == 0.0:
        abs_max = 1.0
    norm = Normalize(vmin=-abs_max, vmax=abs_max)

    # --- 3. Live Animation Setup ---
    print("Starting Live Animation Window...")

    fig = plt.figure(figsize=(6, 6), frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)

    # Initial Plot
    img = ax.imshow(
        H[0].T,
        cmap=custom_cmap,
        norm=norm,
        origin="lower",
        extent=[-L_VAL, L_VAL, -L_VAL, L_VAL],
        interpolation="bilinear",
    )

    def update(frame):
        img.set_data(H[frame].T)
        return [img]

    # Create Animation
    ani = FuncAnimation(
        fig,
        update,
        frames=range(H.shape[0]),
        interval=30,  # ~30ms per frame
        blit=True,
    )

    # --- 4. GIF Export Setup ---
    GIF_FILENAME = "Figures/wave_propagation_2d.gif"

    # Create directory if it doesn't exist
    output_dir = os.path.dirname(GIF_FILENAME)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    print(f"Saving animation to GIF: {GIF_FILENAME}...")
    # This uses the same FuncAnimation object to save the frames
    # The fps argument controls the animation speed in the GIF
    ani.save(
        GIF_FILENAME, writer="imageio", fps=1000 / 30, dpi=100
    )  # fps = 1000/interval
    print("GIF export complete.")

    # Display the live animation after saving the GIF
    plt.show()
