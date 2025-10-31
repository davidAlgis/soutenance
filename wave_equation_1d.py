import numpy as np


def simulate_wave_1d_dirichlet(
    L=1.0,  # half-domain; x ∈ [-L, L]
    c=1.0,  # wave speed
    W=0.3,  # width of the central interval for the initial bell
    A=1.0,  # amplitude of the Gaussian bell
    sigma=0.08,  # std dev of the Gaussian bell
    nx=801,  # number of spatial nodes (odd recommended so x=0 is a node)
    T=2.0,  # total simulated duration
    dt=0.001,  # user-requested output sampling step; solver may use a smaller internal dt
    t0=0.0,  # time at which the truncated Gaussian is applied
):
    """
    Solve ∂²h/∂t² = c² ∂²h/∂x² on x ∈ [-L, L] with Dirichlet BCs h(-L,t)=h(L,t)=0.
    The truncated Gaussian displacement is applied at time t0 (zero velocity at t0).

    Stability handling:
      - If the user-provided dt violates CFL (c*dt/dx > 1), the function automatically
        reduces the *internal* simulation step to dt_sim = dx/c (so CFL = 1).
      - The solver runs at dt_sim, but the returned time series is downsampled so that
        the output `t` matches the user-requested dt grid: t = [0, dt, 2*dt, ..., ≤ T].

    Returns:
        H : ndarray, shape (nt_out, nx)  (rows=time, cols=space) sampled at user dt
        x : ndarray, shape (nx,)
        t : ndarray, shape (nt_out,) matching the user-requested dt
    """
    if t0 < 0:
        raise ValueError("t0 must be ≥ 0.")

    # --- grids
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]

    # Handle c = 0 (degenerate: no propagation)
    if c == 0.0:
        # Build bell at t0 and keep it forever (zero velocity and zero Laplacian propagation)
        nt_out = int(np.floor(T / dt)) + 1
        t_out = np.arange(nt_out) * dt
        bell = np.zeros_like(x)
        mask = np.abs(x) <= W / 2
        bell[mask] = A * np.exp(-0.5 * (x[mask] / sigma) ** 2)
        H_out = np.zeros((nt_out, nx), dtype=float)
        if 0.0 <= t0 <= T:
            # Put the bell from t >= t0
            start_idx = int(round(t0 / dt))
            start_idx = min(max(start_idx, 0), nt_out - 1)
            H_out[start_idx:] = bell
        return H_out, x, t_out

    # --- choose internal dt to satisfy CFL ≤ 1
    dt_user = dt
    dt_sim = dt_user
    if c * dt_user / dx > 1.0:
        dt_sim = dx / c  # CFL = 1 (stable)

    # --- build the bell (truncated Gaussian)
    bell = np.zeros_like(x)
    mask = np.abs(x) <= W / 2
    bell[mask] = A * np.exp(-0.5 * (x[mask] / sigma) ** 2)

    # --- allocate internal simulation arrays
    nt_sim = int(np.floor(T / dt_sim)) + 1
    t_sim = np.arange(nt_sim) * dt_sim
    lam2 = (c * dt_sim / dx) ** 2

    H_sim = np.zeros((nt_sim, nx), dtype=float)

    # If t0 is beyond the simulated window or nothing to simulate
    if t0 >= T or nt_sim < 2:
        # Return zero field sampled at user dt
        nt_out = int(np.floor(T / dt_user)) + 1
        t_out = np.arange(nt_out) * dt_user
        H_out = np.zeros((nt_out, nx), dtype=float)
        return H_out, x, t_out

    # Index where the bell is applied (internal timeline)
    n0 = int(round(t0 / dt_sim))
    n0 = min(max(n0, 0), nt_sim - 1)

    # At n0: set displacement to bell, zero velocity
    u_prev = bell.copy()
    u_prev[0] = 0.0
    u_prev[-1] = 0.0
    H_sim[n0] = u_prev

    # If there's at least one step after n0, compute u at n0+1 via Taylor (v=0)
    if n0 + 1 < nt_sim:
        u = u_prev.copy()
        lap = np.zeros_like(u_prev)
        lap[1:-1] = u_prev[2:] - 2 * u_prev[1:-1] + u_prev[:-2]
        u[1:-1] = u_prev[1:-1] + 0.5 * lam2 * lap[1:-1]
        u[0] = 0.0
        u[-1] = 0.0
        H_sim[n0 + 1] = u

        # Leapfrog forward on internal grid
        for n in range(n0 + 1, nt_sim - 1):
            u_next = np.empty_like(u)
            u_next[1:-1] = (
                2 * u[1:-1]
                - u_prev[1:-1]
                + lam2 * (u[2:] - 2 * u[1:-1] + u[:-2])
            )
            u_next[0] = 0.0
            u_next[-1] = 0.0
            u_prev, u = u, u_next
            H_sim[n + 1] = u

    # --- Downsample to user-requested timeline
    nt_out = int(np.floor(T / dt_user)) + 1
    t_out = np.arange(nt_out) * dt_user

    # Map each t_out[k] to the nearest internal index
    # (robust against floating rounding; clip to valid range)
    idx_out = np.round(t_out / dt_sim).astype(int)
    idx_out = np.clip(idx_out, 0, nt_sim - 1)

    H_out = H_sim[idx_out]

    return H_out, x, t_out
