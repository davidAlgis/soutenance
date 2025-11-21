import os

import numpy as np


def shift_field(field, sx, sy):
    """
    Shifts the field by (sx, sy) integers, padding with zeros.
    Implements the logic: new[i, j] = old[i - sx, j - sy]
    """
    # --- Handle X Shift (Axis 0) ---
    if sx == 0:
        tmp = field
    elif sx > 0:
        tmp = np.zeros_like(field)
        tmp[sx:, :] = field[:-sx, :]
    else:  # sx < 0
        tmp = np.zeros_like(field)
        tmp[:sx, :] = field[-sx:, :]

    # --- Handle Y Shift (Axis 1) ---
    if sy == 0:
        out = tmp
    elif sy > 0:
        out = np.zeros_like(tmp)
        out[:, sy:] = tmp[:, :-sy]
    else:
        out = np.zeros_like(tmp)
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
    Returns raw data arrays instead of plotting.
    """
    if N < 3:
        raise ValueError("N must be at least 3.")

    nx, ny = N, N
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]
    h_grid = dx

    # --- CFL & Time Step ---
    cfl_limit = 1.0 / np.sqrt(2)
    dt_sim = dt
    if c * dt / dx > cfl_limit:
        dt_sim = dx / (c * np.sqrt(2.0))

    nt_sim = int(np.ceil(T / dt_sim))
    a_coeff = (c * dt_sim / h_grid) ** 2

    # --- Arrays ---
    h_n = np.zeros((nx, ny), dtype=float)
    h_nm1 = np.zeros((nx, ny), dtype=float)

    # Storage for output: (Time, X, Y)
    nt_out = int(np.ceil(T / dt))
    H_out = np.zeros((nt_out, nx, ny), dtype=float)

    # --- Source Mask ---
    X_grid, Y_grid = np.meshgrid(x, x, indexing="ij")
    mask = (X_grid**2 + Y_grid**2) <= radius**2

    # --- Grid Translation State ---
    p_x, p_y = 0.0, 0.0
    I_x_n, I_y_n = 0, 0
    I_x_nm1, I_y_nm1 = 0, 0

    out_idx = 0
    next_out_time = 0.0

    # --- Main Loop ---
    for n in range(nt_sim):
        current_time_sim = n * dt_sim

        # 1. Calculate Next Position
        p_x_next = p_x + vel_x * dt_sim
        p_y_next = p_y + vel_y * dt_sim

        # 2. Calculate Integer Coordinates
        I_x_next = int(np.floor(p_x_next / dx))
        I_y_next = int(np.floor(p_y_next / dx))

        # 3. Calculate Shifts
        sx_n = I_x_next - I_x_n
        sy_n = I_y_next - I_y_n

        sx_nm1 = I_x_next - I_x_nm1
        sy_nm1 = I_y_next - I_y_nm1

        # 4. Shift Fields
        h_n_shifted = shift_field(h_n, sx_n, sy_n)
        h_nm1_shifted = shift_field(h_nm1, sx_nm1, sy_nm1)

        # 5. Compute Laplacian
        lap = np.zeros_like(h_n_shifted)
        lap[1:-1, 1:-1] = (
            h_n_shifted[2:, 1:-1]
            + h_n_shifted[:-2, 1:-1]
            + h_n_shifted[1:-1, 2:]
            + h_n_shifted[1:-1, :-2]
            - 4.0 * h_n_shifted[1:-1, 1:-1]
        )

        # 6. Update Step
        h_next = damping * (a_coeff * lap + 2.0 * h_n_shifted - h_nm1_shifted)

        # 7. Apply Fixed Source
        if A != 0.0:
            h_next[mask] = A

        # 8. Rotate buffers
        h_nm1 = h_n
        h_n = h_next

        I_x_nm1 = I_x_n
        I_y_nm1 = I_y_n

        I_x_n = I_x_next
        I_y_n = I_y_next

        p_x = p_x_next
        p_y = p_y_next

        # 9. Store Output
        if current_time_sim >= next_out_time and out_idx < nt_out:
            H_out[out_idx] = h_n
            out_idx += 1
            next_out_time += dt

    return H_out, x, np.arange(nt_out) * dt


def export_data_to_file(filename, H, x, t, params):
    """
    Saves 2D simulation results to .npz
    """
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Saving simulation data to {filename}...")
    # H shape is (Time, X, Y)
    np.savez_compressed(filename, H=H, x=x, t=t, **params)
    print("Done.")


if __name__ == "__main__":
    # --- Parameters ---
    L_VAL = 1.0
    C_VAL = 0.5  # Wave Speed
    A_VAL = 1.0  # Source Height
    RADIUS = 0.05
    N_VAL = 151  # Grid Size
    T_VAL = 3.0  # Duration
    DT_VAL = 0.015  # Output dt (keep relatively low to manage file size)

    # Velocity setup: Source moves Bottom -> Top
    # VEL_Y < 0 shifts the "world" down, making the source appear to move Up.
    VEL_X = 0.0
    VEL_Y = -0.8

    scenarios = [
        {"d": 1.0, "label": "no_damping"},
        {"d": 0.99, "label": "with_damping"},
    ]

    # Target directory
    DATA_DIR = "states_sph"

    for scen in scenarios:
        d_factor = scen["d"]
        label = scen["label"]

        print(f"\n--- Computing 2D Simulation: {label} (d={d_factor}) ---")

        H, x, t = simulate_wave_translated(
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

        filename = f"{DATA_DIR}/wave_2d_{label}.npz"

        params = {
            "L": L_VAL,
            "A": A_VAL,
            "radius": RADIUS,
            "vel_x": VEL_X,
            "vel_y": VEL_Y,
            "damping": d_factor,
        }

        export_data_to_file(filename, H, x, t, params)
