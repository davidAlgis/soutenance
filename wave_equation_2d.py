import matplotlib

# Force 'Agg' backend to ensure GIF generation works without a display
# and prevents the 'NoneType' attribute error during cleanup.
matplotlib.use("Agg")

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap, Normalize


def simulate_wave_2d_dirichlet(
    L=1.0,  # half-domain size; x, y ∈ [-L, L]
    c=1.0,  # wave speed
    A=1.0,  # amplitude of the source (height of the flat circle)
    radius=0.05,  # Radius of the filled circle
    N=151,  # number of spatial nodes
    T=4.0,  # total simulated duration
    dt=0.005,  # user-requested output sampling step
    t0=0.0,  # start time
    damping=1.0,  # Damping factor (1.0 = no damping, <1.0 = decay)
    moving_source=False,
):
    """
    Solve ∂²h/∂t² = c² ∇²h
    Source is modeled as a moving Dirichlet condition (u = A inside circle).
    """
    if N < 3:
        raise ValueError("N must be at least 3.")

    nx = N
    ny = N

    # --- Grids
    x = np.linspace(-L, L, nx)
    y = np.linspace(-L, L, ny)
    dx = x[1] - x[0]
    h_grid = dx

    # Meshgrid for distance calculations
    X, Y = np.meshgrid(x, y, indexing="ij")

    # --- CFL Condition
    dt_user = dt
    dt_sim = dt_user
    cfl_limit = 1.0 / np.sqrt(2)
    cfl_actual = c * dt_user / h_grid

    if cfl_actual > cfl_limit:
        dt_sim = h_grid / (c * np.sqrt(2.0))

    # --- Allocate Arrays
    nt_sim = int(np.floor(T / dt_sim)) + 1
    t_sim = np.arange(nt_sim) * dt_sim
    lam2 = (c * dt_sim / h_grid) ** 2

    H_sim = np.zeros((nt_sim, nx, ny), dtype=float)

    # Start index
    n0 = int(round(t0 / dt_sim))
    n0 = min(max(n0, 0), nt_sim - 1)

    u_prev = np.zeros((nx, ny))
    u = np.zeros((nx, ny))

    # Trajectory definition (Top-Left to Bottom-Right)
    start_pos = np.array([-0.7 * L, 0.7 * L])
    end_pos = np.array([0.7 * L, -0.7 * L])

    # --- Main Loop ---
    for n in range(n0, nt_sim - 1):
        # 1. Laplacian
        lap = np.zeros((nx, ny), dtype=float)
        lap[1:-1, 1:-1] = (
            u[2:, 1:-1]
            + u[:-2, 1:-1]
            + u[1:-1, 2:]
            + u[1:-1, :-2]
            - 4.0 * u[1:-1, 1:-1]
        )

        # 2. Wave Update
        u_next = 2.0 * u - u_prev + lam2 * lap

        # Apply Damping
        if damping != 1.0:
            u_next *= damping

        # 3. Apply Moving Hard Source
        if A != 0.0 and moving_source:
            current_time = (n - n0) * dt_sim

            # Calculate current position
            progress = current_time / T
            if progress > 1.0:
                progress = 1.0

            curr_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
            curr_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress

            # Create Hard Mask (Filled Circle)
            dist_sq = (X - curr_x) ** 2 + (Y - curr_y) ** 2
            mask = dist_sq <= radius**2

            # Impose Dirichlet condition on the moving body
            u_next[mask] = A

        # 4. Dirichlet BCs (Walls)
        u_next[0, :] = 0.0
        u_next[-1, :] = 0.0
        u_next[:, 0] = 0.0
        u_next[:, -1] = 0.0

        # 5. Shift
        H_sim[n + 1] = u_next
        u_prev = u
        u = u_next

    # --- Downsample
    nt_out = int(np.floor(T / dt_user)) + 1
    t_out = np.arange(nt_out) * dt_user
    idx_out = np.round(t_out / dt_sim).astype(int)
    idx_out = np.clip(idx_out, 0, nt_sim - 1)
    H_out = H_sim[idx_out]

    return H_out, x, y, t_out


if __name__ == "__main__":
    # --- Parameters ---
    L_VAL = 1.0

    # Froude Number > 1 Setup (Supersonic/Supercritical)
    C_VAL = 0.5  # Wave speed
    A_VAL = 1.0  # Height of the "boat" (Displacement)
    RADIUS_VAL = 0.05  # Radius of the "boat"
    N_VAL = 201  # Higher resolution for sharper wake details
    T_VAL = 2.0  # High speed duration
    DT_VAL = 0.01  # Finer time step for smoother animation

    MOVING = True

    # Define the scenarios to run
    scenarios = [
        {"d": 1.0, "label": "no_damping"},
        {"d": 0.99, "label": "with_damping"},
    ]

    for scen in scenarios:
        d_factor = scen["d"]
        label = scen["label"]

        print(f"\n--- Running Simulation: {label} (d={d_factor}) ---")

        H, x, y, t = simulate_wave_2d_dirichlet(
            L=L_VAL,
            c=C_VAL,
            A=A_VAL,
            radius=RADIUS_VAL,
            N=N_VAL,
            T=T_VAL,
            dt=DT_VAL,
            t0=0.0,
            damping=d_factor,
            moving_source=MOVING,
        )
        print(f"Simulation complete. Frames: {H.shape[0]}")

        # --- Visualization ---
        BLUE_GREEN_LIGHT = (0.12, 0.61, 0.73)
        WHITE = (1.0, 1.0, 1.0)

        def create_symmetric_cmap(color, center):
            colors = [color, center, color]
            nodes = [0.0, 0.5, 1.0]
            return LinearSegmentedColormap.from_list(
                "SymmetricBlueGreen", list(zip(nodes, colors))
            )

        custom_cmap = create_symmetric_cmap(BLUE_GREEN_LIGHT, WHITE)

        # Visualize based on the wake amplitude
        wake_scale = 0.3
        norm = Normalize(vmin=-wake_scale, vmax=wake_scale)

        # Create figure
        fig = plt.figure(figsize=(6, 6), frameon=False)
        ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
        ax.set_axis_off()
        fig.add_axes(ax)

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

        # Create Animation (blit=False is safer for file generation)
        ani = FuncAnimation(
            fig,
            update,
            frames=range(H.shape[0]),
            interval=30,
            blit=False,
            cache_frame_data=False,  # Reduce memory usage
        )

        # GIF Export
        GIF_FILENAME = f"Figures/wave_propagation_2d_{label}.gif"
        output_dir = os.path.dirname(GIF_FILENAME)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Saving animation to GIF: {GIF_FILENAME}...")
        # Use pillow writer explicitly to avoid ImageIO warning
        ani.save(GIF_FILENAME, writer="pillow", fps=30, dpi=100)
        print("GIF export complete.")

        # Cleanup: Delete animation object before closing figure to prevent
        # 'NoneType' attribute error on event loop callback.
        del ani
        plt.close(fig)

    print("\nAll simulations done.")
