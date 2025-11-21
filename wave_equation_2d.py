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


def get_boat_shape_params():
    """
    Centralized parameters for boat geometry (Top-Down View).
    """
    return {
        "W_half": 0.03,  # Half-width
        "L_stern": 0.05,  # Length of the rectangular back
        "L_bow": 0.08,  # Length of the triangular front
    }


def get_boat_mask(X, Y):
    """
    Creates a boolean mask for a boat shape (Top view).
    Shape: 'Shield' (Rectangle stern + Triangle bow).
    Orientation: Pointing towards +Y.
    """
    p = get_boat_shape_params()
    w = p["W_half"]
    l_stern = p["L_stern"]
    l_bow = p["L_bow"]

    # 1. Stern (Rectangle part): y in [-l_stern, 0], |x| <= w
    mask_stern = (Y >= -l_stern) & (Y <= 0.0) & (np.abs(X) <= w)

    # 2. Bow (Triangle part): y in [0, l_bow]
    # Width decreases linearly: x_max = w * (1 - y/l_bow)
    # Avoid division by zero if l_bow is 0 (not the case here)
    mask_bow = (Y > 0.0) & (Y <= l_bow) & (np.abs(X) <= w * (1.0 - Y / l_bow))

    return mask_stern | mask_bow


def get_boat_vertices():
    """
    Returns the polygon vertices (N, 3) for the boat to be drawn in Manim.
    Z-coordinate is 0.
    """
    p = get_boat_shape_params()
    w = p["W_half"]
    l_stern = p["L_stern"]
    l_bow = p["L_bow"]

    # Vertices in Counter-Clockwise order
    # (x, y, z)
    return np.array(
        [
            [0.0, l_bow, 0.0],  # Tip (Front)
            [-w, 0.0, 0.0],  # Mid Left
            [-w, -l_stern, 0.0],  # Back Left
            [w, -l_stern, 0.0],  # Back Right
            [w, 0.0, 0.0],  # Mid Right
            [0.0, l_bow, 0.0],  # Close loop
        ]
    )


def simulate_wave_translated(
    L=1.0,  # half-domain size
    c=1.0,  # wave speed
    A=1.0,  # source amplitude
    N=151,  # grid resolution
    T=4.0,  # total time
    dt=0.01,  # output time step
    vel_x=-1.0,  # "Flow" velocity X
    vel_y=1.0,  # "Flow" velocity Y
    damping=1.0,  # Damping factor d^n
):
    """
    Solves the 2D wave equation using the Algis et al. Grid Translation scheme.
    Source is a Boat Shape.
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

    # --- Source Mask (Boat) ---
    # X_grid corresponds to axis 0, Y_grid to axis 1
    X_grid, Y_grid = np.meshgrid(x, x, indexing="ij")

    # Create the boat mask
    mask = get_boat_mask(X_grid, Y_grid)

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

        # 7. Apply Fixed Source (Boat Hull)
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
    Includes boat_polygon for visualization.
    """
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Saving simulation data to {filename}...")

    # Get boat shape for export
    boat_poly = get_boat_vertices()

    # H shape is (Time, X, Y)
    np.savez_compressed(
        filename, H=H, x=x, t=t, boat_polygon=boat_poly, **params
    )
    print("Done.")


if __name__ == "__main__":
    # --- Parameters ---
    L_VAL = 1.0
    C_VAL = 0.5  # Wave Speed
    A_VAL = 0.5  # Source Height
    # Radius param is technically unused now, replaced by get_boat_shape_params internal logic
    N_VAL = 301  # Grid Size
    T_VAL = 8.0  # Duration
    DT_VAL = 0.007  # Output dt

    # Velocity setup: Source moves Bottom -> Top
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
            "vel_x": VEL_X,
            "vel_y": VEL_Y,
            "damping": d_factor,
        }

        export_data_to_file(filename, H, x, t, params)
