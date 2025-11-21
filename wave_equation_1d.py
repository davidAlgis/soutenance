import os

import numpy as np


def shift_array_1d(arr, shift):
    """
    Shifts a 1D array by integer 'shift'.
    new[i] = old[i - shift]
    """
    out = np.zeros_like(arr)

    if shift == 0:
        return arr
    elif shift > 0:
        # Shift Right
        out[shift:] = arr[:-shift]
    else:
        # Shift Left
        out[:shift] = arr[-shift:]

    return out


def get_boat_bottom_profile(x_grid, offset_y):
    """
    Computes the hull displacement profile for the simulation.
    Based on the boat vertices:
      - Flat bottom between x = -1 and 1 (y_local = 0)
      - Rises linearly to y_local = 1 at x = 2 and x = -2
    """
    # Initialize grid with default value (e.g., 0 or the offset)
    h_hull = np.zeros_like(x_grid)

    # The boat exists between x = -2.0 and x = 2.0
    mask = (x_grid >= -2.0) & (x_grid <= 2.0)

    if not np.any(mask):
        return h_hull, mask

    x_active = x_grid[mask]

    # Formula derived from vertices:
    # y_local = 0 for |x| <= 1
    # y_local = |x| - 1 for 1 < |x| <= 2
    # Combined: max(0, |x| - 1)
    y_local = np.maximum(0, np.abs(x_active) - 1.0)

    # Add vertical offset (A) to position the boat height relative to water rest level (0)
    h_hull[mask] = y_local + offset_y

    return h_hull, mask


def simulate_wave_1d_translated(
    L=10.0,  # half-domain size
    c=1.0,  # wave speed
    A=0.5,  # Vertical offset of the boat bottom (Draft/Waterline)
    N=401,  # grid resolution
    T=4.0,  # total time
    dt=0.01,  # output time step
    vel=-1.5,  # Grid Velocity
    damping=1.0,  # Damping factor
):
    """
    Solves 1D wave equation with Algis Grid Translation.
    Uses a boat-shaped source.
    """
    nx = N
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]

    # --- CFL Condition ---
    cfl_limit = 1.0
    dt_sim = dt
    if c * dt / dx > cfl_limit:
        dt_sim = dx / c

    nt_sim = int(np.ceil(T / dt_sim))
    lambda_sq = (c * dt_sim / dx) ** 2

    # --- Arrays ---
    h_n = np.zeros(nx, dtype=float)
    h_nm1 = np.zeros(nx, dtype=float)

    # Output storage
    nt_out = int(np.ceil(T / dt))
    H_out = np.zeros((nt_out, nx), dtype=float)

    # --- Source Profile ---
    # We pre-calculate the shape of the boat hull on the fixed grid x
    # This acts as a Dirichlet boundary condition wherever the boat is present.
    source_h, source_mask = get_boat_bottom_profile(x, A)

    # --- Grid Translation State ---
    p = 0.0
    I_n = 0
    I_nm1 = 0

    out_idx = 0
    next_out_time = 0.0

    # --- Main Loop ---
    for n in range(nt_sim):
        current_time_sim = n * dt_sim

        # 1. Calculate Position & Integer Index
        p_next = p + vel * dt_sim
        I_next = int(np.floor(p_next / dx))

        # 2. Calculate Shifts
        s_n = I_next - I_n
        s_nm1 = I_next - I_nm1

        # 3. Shift Fields
        h_n_shifted = shift_array_1d(h_n, s_n)
        h_nm1_shifted = shift_array_1d(h_nm1, s_nm1)

        # 4. Laplacian
        lap = np.zeros_like(h_n_shifted)
        lap[1:-1] = (
            h_n_shifted[2:] - 2.0 * h_n_shifted[1:-1] + h_n_shifted[:-2]
        )

        # 5. Update Scheme
        h_next = damping * (
            lambda_sq * lap + 2.0 * h_n_shifted - h_nm1_shifted
        )

        # 6. Apply Boat Source
        # Dirichlet BC: Force water height to match boat hull
        if np.any(source_mask):
            h_next[source_mask] = source_h[source_mask]

        # 7. Rotate & Update State
        h_nm1 = h_n
        h_n = h_next

        I_nm1 = I_n
        I_n = I_next
        p = p_next

        # 8. Store Output
        if current_time_sim >= next_out_time and out_idx < nt_out:
            H_out[out_idx] = h_n
            out_idx += 1
            next_out_time += dt

    return H_out, x, np.arange(nt_out) * dt


def export_data_to_file(filename, H, x, t, L, A):
    """
    Saves the simulation results to a compressed numpy format (.npz).
    Includes the boat polygon vertices for Manim visualization.
    """
    # Create directory if needed
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define the Boat Polygon (Local Coords)
    boat_polygon = np.array(
        [
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [0.5, 1.0, 0.0],
            [0.0, 1.5, 0.0],
            [-0.5, 1.0, 0.0],
            [-2.0, 1.0, 0.0],
        ]
    )

    # We shift the polygon so it matches the simulation offset A
    # The bottom points (y=0) should align with A
    boat_polygon[:, 1] += A

    print(f"Saving simulation data to {filename}...")
    np.savez_compressed(
        filename, H=H, x=x, t=t, L=L, A=A, boat_polygon=boat_polygon
    )
    print("Done.")


if __name__ == "__main__":
    # --- Parameters ---
    L_VAL = 10.0
    C_VAL = 1.0

    # A_VAL is now the vertical offset (height of the flat bottom relative to rest water)
    # Setting it to 0.0 puts the bottom at water level.
    # Setting it to 0.5 lifts it slightly (hovercraft style).
    # Setting it to -0.5 would submerge it.
    A_VAL = 0.1

    N_VAL = 801
    T_VAL = 16.0
    DT_VAL = 0.02
    VEL_VAL = -1.5

    scenarios = [
        {"d": 1.0, "label": "no_damping"},
        {"d": 0.995, "label": "with_damping"},
    ]

    for scen in scenarios:
        d_factor = scen["d"]
        label = scen["label"]

        print(f"\n--- Computing: {label} (d={d_factor}) ---")

        H, x, t = simulate_wave_1d_translated(
            L=L_VAL,
            c=C_VAL,
            A=A_VAL,
            N=N_VAL,
            T=T_VAL,
            dt=DT_VAL,
            vel=VEL_VAL,
            damping=d_factor,
        )

        filename = f"states_sph/wave_1d_{label}.npz"
        export_data_to_file(filename, H, x, t, L_VAL, A_VAL)
