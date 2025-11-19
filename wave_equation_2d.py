import matplotlib

# Force 'Agg' backend to ensure GIF generation works without a display
matplotlib.use("Agg")

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap, Normalize


def shift_field(field, sx, sy):
    """
    Shifts the field by (sx, sy) integers, padding with zeros.
    Implements the logic: new[i, j] = old[i - sx, j - sy]

    If sx > 0 (Shift Right):
        new[sx:] = old[:-sx]
        new[:sx] = 0
    """
    rows, cols = field.shape
    out = np.zeros_like(field)

    # --- Handle X Shift (Axis 0) ---
    if sx == 0:
        tmp = field
    elif sx > 0:
        # Shift Right/Down (depending on axis convention, here axis 0)
        # Takes from old[i-sx]. Valid for i >= sx.
        tmp = np.zeros_like(field)
        tmp[sx:, :] = field[:-sx, :]
    else:  # sx < 0
        # Shift Left/Up
        # Takes from old[i - (-sx)] = old[i+|sx|]. Valid for i < N-|sx|
        tmp = np.zeros_like(field)
        tmp[:sx, :] = field[-sx:, :]

    # --- Handle Y Shift (Axis 1) ---
    if sy == 0:
        out = tmp
    elif sy > 0:
        out[:, sy:] = tmp[:, :-sy]
    else:
        out[:, :sy] = tmp[:, -sy:]

    return out


def simulate_wave_translated(
    L=1.0,  # half-domain size
    c=1.0,  # wave speed
    A=1.0,  # source amplitude
    radius=0.05,  # source radius
    N=151,  # grid resolution
    T=4.0,  # total time
    dt=0.01,  # output time step
    vel_x=-1.0,  # "Flow" velocity X (Grid velocity)
    vel_y=1.0,  # "Flow" velocity Y
    damping=1.0,  # Damping factor d^n
):
    """
    Solves the 2D wave equation using the Algis et al. Grid Translation scheme.
    Equation: h^{n+1} = d * ( a * Laplacian(h^n_shifted) + 2*h^n_shifted - h^{n-1}_shifted )
    """
    if N < 3:
        raise ValueError("N must be at least 3.")

    nx, ny = N, N
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]
    h_grid = dx

    # --- CFL & Time Step ---
    # Standard CFL condition for 2D
    cfl_limit = 1.0 / np.sqrt(2)
    dt_sim = dt
    if c * dt / dx > cfl_limit:
        dt_sim = dx / (c * np.sqrt(2.0))

    nt_sim = int(np.ceil(T / dt_sim))

    # Factor 'a' in the Algis equation: a = (c * dt / dx)^2
    # Note: In the standard scheme h_new = 2*h - h_old + a * Laplacian
    # The Algis equation factorizes differently:
    # h_new = a * (neighbors - 4*center) + 2*center - old
    # This is algebraically equivalent to the standard scheme.
    a_coeff = (c * dt_sim / h_grid) ** 2

    # --- Arrays ---
    # We need current (n) and previous (n-1) fields
    h_n = np.zeros((nx, ny), dtype=float)
    h_nm1 = np.zeros((nx, ny), dtype=float)  # n minus 1

    # Storage for output
    nt_out = int(np.ceil(T / dt))
    H_out = np.zeros((nt_out, nx, ny), dtype=float)

    # --- Source Mask (Fixed at Center) ---
    X, Y = np.meshgrid(x, x, indexing="ij")  # x is axis 0
    # Center is (0,0) in this coordinate system
    mask = (X**2 + Y**2) <= radius**2

    # --- Grid Translation State ---
    # Continuous position of the mesh
    p_x, p_y = 0.0, 0.0

    # Integer grid coordinates at steps n, n+1, n-1
    # Initialize at 0
    I_x_n, I_y_n = 0, 0
    I_x_nm1, I_y_nm1 = 0, 0  # n-1

    # Output index tracking
    out_idx = 0
    next_out_time = 0.0

    # --- Main Loop ---
    for n in range(nt_sim):
        current_time = n * dt_sim

        # 1. Calculate Next Position (p at t+dt)
        p_x_next = p_x + vel_x * dt_sim
        p_y_next = p_y + vel_y * dt_sim

        # 2. Calculate Integer Coordinates
        # We use floor to determine the "cell" the mesh origin resides in
        I_x_next = int(np.floor(p_x_next / dx))
        I_y_next = int(np.floor(p_y_next / dx))

        # 3. Calculate Shifts (Algis Equations 1 & 2)
        # k = i - floor(...) -> shift from n to n+1
        # Shift = I_next - I_current
        sx_n = I_x_next - I_x_n
        sy_n = I_y_next - I_y_n

        # o = i - floor(...) -> shift from n-1 to n+1
        sx_nm1 = I_x_next - I_x_nm1
        sy_nm1 = I_y_next - I_y_nm1

        # 4. Shift Fields to align with the new grid at n+1
        # h^n_{k,l} -> shifted by sx_n, sy_n
        h_n_shifted = shift_field(h_n, sx_n, sy_n)

        # h^{n-1}_{o,p} -> shifted by sx_nm1, sy_nm1
        h_nm1_shifted = shift_field(h_nm1, sx_nm1, sy_nm1)

        # 5. Compute Laplacian on the aligned n-field
        # Standard 5-point stencil
        # We can use slicing on h_n_shifted directly
        # (center is h_n_shifted)
        # h_ip1 = roll(h, -1, axis=0) (neighbor i+1)
        # h_im1 = roll(h, 1, axis=0)  (neighbor i-1)
        # Note: For speed we can use padding or assume Dirichlet 0 at boundaries
        # We'll use slicing for interior points
        lap = np.zeros_like(h_n_shifted)

        # Interior: [1:-1, 1:-1]
        # i+1: [2:, 1:-1]
        # i-1: [:-2, 1:-1]
        # j+1: [1:-1, 2:]
        # j-1: [1:-1, :-2]
        lap[1:-1, 1:-1] = (
            h_n_shifted[2:, 1:-1]
            + h_n_shifted[:-2, 1:-1]
            + h_n_shifted[1:-1, 2:]
            + h_n_shifted[1:-1, :-2]
            - 4.0 * h_n_shifted[1:-1, 1:-1]
        )

        # 6. Update Step (Algis Equation 2)
        # h^{n+1} = d * [ a * Lap + 2*h^n - h^{n-1} ]
        h_next = damping * (a_coeff * lap + 2.0 * h_n_shifted - h_nm1_shifted)

        # 7. Apply Fixed Source (Circle at center)
        # The source overrides the physics at the center
        if A != 0.0:
            h_next[mask] = A

        # 8. Rotate buffers and State
        # The calculated h_next is correctly aligned with grid I_next
        h_nm1 = h_n_shifted  # The old n becomes n-1 (but aligned!) -> Wait.
        # Careful: The recursion needs h^n and h^{n-1} valid for the *next* step.
        # Next step will shift from *this* step's grid.
        # So we just store h_next as the raw data for the grid at I_next.
        # But h_nm1 for the *next* step corresponds to h_n of *this* step.
        # Yes.
        h_nm1 = h_n  # Store the raw field at grid n
        h_n = h_next  # Store the raw field at grid n+1

        # Update positions history
        # For the NEXT iteration:
        # n becomes n-1. next becomes n.
        # So we need to store the I indices.
        I_x_nm1 = I_x_n
        I_y_nm1 = I_y_n

        I_x_n = I_x_next
        I_y_n = I_y_next

        p_x = p_x_next
        p_y = p_y_next

        # 9. Output
        if current_time >= next_out_time and out_idx < nt_out:
            H_out[out_idx] = h_n
            out_idx += 1
            next_out_time += dt

    return H_out, x, x, np.arange(nt_out) * dt


if __name__ == "__main__":
    # --- Parameters ---
    L_VAL = 1.0
    C_VAL = 0.5  # Wave Speed
    A_VAL = 1.0  # Source Height
    RADIUS = 0.05
    N_VAL = 151  # Grid Size
    T_VAL = 3.0  # Duration
    DT_VAL = 0.015  # Output dt

    # Velocity setup to visualize wake
    # Simulating flow (-0.8, 0.8) implies boat moves (0.8, -0.8)
    VEL_X = -0.8
    VEL_Y = 0.8

    scenarios = [
        {"d": 1.0, "label": "no_damping"},
        {"d": 0.95, "label": "with_damping"},
    ]

    for scen in scenarios:
        d_factor = scen["d"]
        label = scen["label"]

        print(
            f"\n--- Running Algis Translation Scheme: {label} (d={d_factor}) ---"
        )

        H, x, y, t = simulate_wave_translated(
            L=L_VAL,
            c=C_VAL,
            A=A_VAL,
            radius=RADIUS,
            N=N_VAL,
            T=T_VAL,
            dt=DT_VAL,
            vel_x=VEL_X,
            vel_y=VEL_Y,
            damping=d_factor,
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

        # Tighter norm to see the wake
        wake_scale = 0.3
        norm = Normalize(vmin=-wake_scale, vmax=wake_scale)

        fig = plt.figure(figsize=(6, 6), frameon=False)
        ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
        ax.set_axis_off()
        fig.add_axes(ax)

        # Plot centered (local coordinates)
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

        ani = FuncAnimation(
            fig,
            update,
            frames=range(H.shape[0]),
            interval=30,
            blit=False,
            cache_frame_data=False,
        )

        GIF_FILENAME = f"Figures/wave_propagation_2d_{label}.gif"
        output_dir = os.path.dirname(GIF_FILENAME)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Saving animation to GIF: {GIF_FILENAME}...")
        ani.save(GIF_FILENAME, writer="pillow", fps=30, dpi=100)

        del ani
        plt.close(fig)

    print("\nAll simulations done.")
