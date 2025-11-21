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


def simulate_wave_1d_translated(
    L=10.0,  # half-domain size
    c=1.0,  # wave speed
    A=1.0,  # source amplitude
    radius=0.2,  # source width
    N=401,  # grid resolution
    T=4.0,  # total time
    dt=0.01,  # output time step
    vel=-1.5,  # Grid Velocity
    damping=1.0,  # Damping factor
):
    """
    Solves 1D wave equation with Algis Grid Translation.
    Returns raw data arrays instead of plotting.
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

    # --- Source Mask ---
    mask = np.abs(x) <= radius

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

        # 6. Apply Source
        if A != 0.0:
            h_next[mask] = A

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
    This file is easily readable by Manim.
    """
    # Create directory if needed
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Saving simulation data to {filename}...")
    # We save H (wave height), x (spatial grid), t (time grid)
    # and metadata (L, A) which might be useful for setting up Manim axes.
    np.savez_compressed(filename, H=H, x=x, t=t, L=L, A=A)
    print("Done.")


if __name__ == "__main__":
    # --- Parameters ---
    L_VAL = 10.0
    C_VAL = 1.0
    A_VAL = 1.0
    RADIUS = 0.2
    N_VAL = 801
    T_VAL = 8.0
    DT_VAL = 0.02  # 50 FPS equivalent if mapped 1:1
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
            radius=RADIUS,
            N=N_VAL,
            T=T_VAL,
            dt=DT_VAL,
            vel=VEL_VAL,
            damping=d_factor,
        )

        # Export to .npz files in a 'data' folder
        filename = f"states_sph/wave_1d_{label}.npz"
        export_data_to_file(filename, H, x, t, L_VAL, A_VAL)
