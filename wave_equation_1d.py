import os

import numpy as np


def shift_array_1d(arr, shift):
    """
    Shifts a 1D array by integer 'shift'.
    """
    out = np.zeros_like(arr)
    if shift == 0:
        return arr
    elif shift > 0:
        out[shift:] = arr[:-shift]
    else:
        out[:shift] = arr[-shift:]
    return out


def get_boat_bottom_profile(x_grid, A):
    """
    Computes the source profile using the 'Old Script' logic:
    A hard 'Top Hat' source that forces displacement ONLY under the boat.

    This avoids the 'sharp peaks' caused by the previous script trying to
    smoothly force the water to 0.0 at the edges of the mask.
    """
    h_hull = np.zeros_like(x_grid)

    # The boat polygon in the export function is defined from x = -1.0 to x = 1.0
    radius = 1.0

    # Create a mask exactly where the boat bottom is
    mask = np.abs(x_grid) <= radius

    # Force height A inside the mask (Piston/Displacement model)
    if np.any(mask):
        h_hull[mask] = A

    return h_hull, mask


def simulate_wave_1d_translated(
    L=10.0, c=1.0, A=0.5, N=401, T=4.0, dt=0.01, vel=-1.5, damping=1.0
):
    """Solves 1D wave equation with Algis Grid Translation."""
    nx = N
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]

    # CFL condition
    cfl_limit = 1.0
    dt_sim = dt
    if c * dt / dx > cfl_limit:
        dt_sim = dx / c

    nt_sim = int(np.ceil(T / dt_sim))
    lambda_sq = (c * dt_sim / dx) ** 2

    h_n = np.zeros(nx, dtype=float)
    h_nm1 = np.zeros(nx, dtype=float)

    nt_out = int(np.ceil(T / dt))
    H_out = np.zeros((nt_out, nx), dtype=float)

    # Generate the profile (Behaving like the Old Script's logic)
    source_h, source_mask = get_boat_bottom_profile(x, A)

    p = 0.0
    I_n = 0
    I_nm1 = 0
    out_idx = 0
    next_out_time = 0.0

    for n in range(nt_sim):
        current_time_sim = n * dt_sim

        p_next = p + vel * dt_sim
        I_next = int(np.floor(p_next / dx))

        s_n = I_next - I_n
        s_nm1 = I_next - I_nm1

        h_n_shifted = shift_array_1d(h_n, s_n)
        h_nm1_shifted = shift_array_1d(h_nm1, s_nm1)

        # Laplacian
        lap = np.zeros_like(h_n_shifted)
        lap[1:-1] = (
            h_n_shifted[2:] - 2.0 * h_n_shifted[1:-1] + h_n_shifted[:-2]
        )

        # Update Step
        h_next = damping * (
            lambda_sq * lap + 2.0 * h_n_shifted - h_nm1_shifted
        )

        # --- Source Application (The Fix) ---
        # Like the old script, we perform a HARD overwrite inside the mask.
        # We do NOT force values outside the mask (allowing the wave to detach).
        if np.any(source_mask):
            h_next[source_mask] = source_h[source_mask]

        # Rotate buffers
        h_nm1 = h_n
        h_n = h_next
        I_nm1 = I_n
        I_n = I_next
        p = p_next

        # Output
        if current_time_sim >= next_out_time and out_idx < nt_out:
            H_out[out_idx] = h_n
            out_idx += 1
            next_out_time += dt

    return H_out, x, np.arange(nt_out) * dt


def export_data_to_file(filename, H, x, t, L, A):
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # VISUAL boat polygon (Kept sharp for Manim)
    # Ensure this matches the radius used in get_boat_bottom_profile (radius=1.0)
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
    boat_polygon[:, 1] += A

    print(f"Saving simulation data to {filename}...")
    np.savez_compressed(
        filename, H=H, x=x, t=t, L=L, A=A, boat_polygon=boat_polygon
    )
    print("Done.")


if __name__ == "__main__":
    # Parameters
    L_VAL = 10.0
    C_VAL = 1.0
    A_VAL = 0.5  # Displacement Amplitude
    N_VAL = 801
    T_VAL = 16.0
    DT_VAL = 0.02
    VEL_VAL = -1.5  # Mach 1.5

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
