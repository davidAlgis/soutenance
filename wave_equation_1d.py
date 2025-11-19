import matplotlib

matplotlib.use("Agg")  # Force headless mode for file generation

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize


def shift_array_1d(arr, shift):
    """
    Shifts a 1D array by integer 'shift'.
    new[i] = old[i - shift]

    If shift > 0: Data moves Right (indices increase)
    If shift < 0: Data moves Left (indices decrease)
    Empty regions are padded with zeros.
    """
    out = np.zeros_like(arr)

    if shift == 0:
        return arr
    elif shift > 0:
        # Shift Right: out[shift:] takes from arr[:-shift]
        out[shift:] = arr[:-shift]
    else:
        # Shift Left: out[:shift] takes from arr[-shift:]
        out[:shift] = arr[-shift:]

    return out


def simulate_wave_1d_translated(
    L=10.0,  # half-domain size
    c=1.0,  # wave speed
    A=1.0,  # source amplitude
    radius=0.2,  # source width (half-width)
    N=401,  # grid resolution
    T=4.0,  # total time
    dt=0.01,  # output time step
    vel=-1.5,  # Grid Velocity. Negative velocity simulates forward motion (Wake trails left).
    damping=1.0,  # Damping factor d^n
):
    """
    Solves 1D wave equation with Algis Grid Translation.
    """
    nx = N
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]

    # --- CFL Condition ---
    # 1D CFL: c * dt / dx <= 1.0
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

    # --- Source Mask (Fixed at Center) ---
    # In 1D, the "circle" is a segment [-radius, radius]
    mask = np.abs(x) <= radius

    # --- Grid Translation State ---
    p = 0.0  # Continuous position
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

        # 4. Laplacian (1D Stencil)
        # lap[i] = h[i+1] - 2h[i] + h[i-1]
        lap = np.zeros_like(h_n_shifted)
        lap[1:-1] = (
            h_n_shifted[2:] - 2.0 * h_n_shifted[1:-1] + h_n_shifted[:-2]
        )

        # 5. Update Scheme (Algis)
        # h^{n+1} = d * ( lambda^2 * Lap + 2*h^n - h^{n-1} )
        h_next = damping * (
            lambda_sq * lap + 2.0 * h_n_shifted - h_nm1_shifted
        )

        # 6. Apply Source (Hard Overwrite at center)
        if A != 0.0:
            h_next[mask] = A

        # 7. Rotate & Update State
        h_nm1 = h_n
        h_n = h_next

        I_nm1 = I_n
        I_n = I_next
        p = p_next

        # 8. Output
        if current_time_sim >= next_out_time and out_idx < nt_out:
            H_out[out_idx] = h_n
            out_idx += 1
            next_out_time += dt

    return H_out, x, np.arange(nt_out) * dt


def save_animation_1d(
    H, x, L_VAL, A_VAL, VEL_VAL, C_VAL, BLUE_GREEN, UCLA_GOLD, label
):
    """
    Generates and saves the 1D wave animation GIF.
    Wraps visualization logic in a function to provide a proper scope for 'nonlocal fill'.
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    # Aesthetics
    ax.set_xlim(-L_VAL, L_VAL)
    ax.set_ylim(-1.5, 1.5)
    ax.set_title(f"1D Supersonic Source (Mach {abs(VEL_VAL)/C_VAL:.1f})")
    ax.set_xlabel("Relative Position (Source fixed at 0)")
    ax.grid(True, alpha=0.3)

    # 1. Wave Line
    (line,) = ax.plot([], [], color=BLUE_GREEN, lw=2, label="Wave Surface")

    # 2. Source Dot (Fixed at center)
    (source_dot,) = ax.plot(
        [0],
        [A_VAL],
        "o",
        color=UCLA_GOLD,
        markersize=10,
        label="Source",
        zorder=10,
    )

    # Fill
    fill = ax.fill_between(x, -2, -2, color=BLUE_GREEN, alpha=0.2)

    def init():
        line.set_data([], [])
        return line, source_dot

    def update(frame):
        y_data = H[frame]
        line.set_data(x, y_data)

        # Update fill (requires removing old poly collection and adding new one)
        nonlocal fill
        fill.remove()
        fill = ax.fill_between(x, y_data, -2, color=BLUE_GREEN, alpha=0.2)

        return line, source_dot, fill

    ani = FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=range(H.shape[0]),
        interval=30,
        blit=False,
    )

    GIF_FILENAME = f"Figures/wave_propagation_1d_{label}.gif"
    output_dir = os.path.dirname(GIF_FILENAME)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Saving animation to GIF: {GIF_FILENAME}...")
    ani.save(GIF_FILENAME, writer="pillow", fps=30, dpi=100)

    del ani
    plt.close(fig)


if __name__ == "__main__":
    # --- Parameters ---
    # Kelvin Wake analog in 1D is a trailing wave packet.
    # We need Source Speed (v) > Wave Speed (c).
    L_VAL = 10.0
    C_VAL = 1.0  # Wave Speed
    A_VAL = 1.0  # Amplitude
    RADIUS = 0.2  # "Radius" of 1D source (Width)
    N_VAL = 801  # Grid Resolution
    T_VAL = 8.0  # Duration
    DT_VAL = 0.02

    # Velocity: Negative means grid moves left, source appears to move Right (+x)
    # We set speed = 1.5 (Supersonic, Mach 1.5)
    VEL_VAL = -1.5

    scenarios = [
        {"d": 1.0, "label": "no_damping"},
        {
            "d": 0.995,
            "label": "with_damping",
        },  # Slightly lighter damping for 1D
    ]

    # --- Colors ---
    BLUE_GREEN = "#1F9CB9"
    UCLA_GOLD = "#FFB500"

    for scen in scenarios:
        d_factor = scen["d"]
        label = scen["label"]

        print(
            f"\n--- Running 1D Translation Scheme: {label} (d={d_factor}) ---"
        )

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
        print(f"Simulation complete. Frames: {H.shape[0]}")

        # Call the visualization function
        save_animation_1d(
            H, x, L_VAL, A_VAL, VEL_VAL, C_VAL, BLUE_GREEN, UCLA_GOLD, label
        )

    print("\nAll 1D simulations done.")
