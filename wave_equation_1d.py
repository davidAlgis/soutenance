import numpy as np


def simulate_wave_1d_dirichlet(
    L=1.0,  # half-domain; x ∈ [-L, L]
    c=1.0,  # wave speed
    W=0.3,  # width of the central interval for the initial bell
    A=1.0,  # amplitude of the Gaussian bell
    sigma=0.08,  # std dev of the Gaussian bell
    nx=801,  # number of spatial nodes (odd recommended so x=0 is a node)
    T=2.0,  # total simulated duration
    dt=0.001,  # time step (you choose); CFL = c*dt/dx must be ≤ 1
    t0=0.0,  # time at which the truncated Gaussian is applied
):
    """
    Solve ∂²h/∂t² = c² ∂²h/∂x² on x ∈ [-L, L] with Dirichlet BCs h(-L,t)=h(L,t)=0.
    The truncated Gaussian displacement is applied at time t0 (zero velocity at t0).

    Returns:
        H : ndarray, shape (nt, nx)  (rows=time, cols=space)
        x : ndarray, shape (nx,)
        t : ndarray, shape (nt,)
    """
    # --- grids
    x = np.linspace(-L, L, nx)
    dx = x[1] - x[0]
    CFL = c * dt / dx
    if CFL > 1.0:
        raise ValueError(
            f"CFL = {CFL:.3f} > 1.0 (unstable). Reduce dt or increase nx."
        )
    if t0 < 0:
        raise ValueError("t0 must be ≥ 0.")

    nt = int(np.floor(T / dt)) + 1
    t = np.arange(nt) * dt
    lam2 = CFL**2

    # --- build the bell (truncated Gaussian)
    bell = np.zeros_like(x)
    mask = np.abs(x) <= W / 2
    bell[mask] = A * np.exp(-0.5 * (x[mask] / sigma) ** 2)

    # --- allocate output (time, space)
    H = np.zeros((nt, nx), dtype=float)

    # If t0 is beyond the simulated window, field stays zero
    if t0 >= T or nt < 2:
        return H, x, t

    # Index where the bell is applied
    n0 = int(round(t0 / dt))
    n0 = min(max(n0, 0), nt - 1)

    # Up to n0-1: still zeros (already initialized)

    # At n0: set displacement to bell, zero velocity
    u_prev = bell.copy()
    u_prev[0] = 0.0
    u_prev[-1] = 0.0
    H[n0] = u_prev

    # If there's at least one step after n0, compute u at n0+1 via Taylor (v=0)
    if n0 + 1 < nt:
        u = u_prev.copy()
        lap = np.zeros_like(u_prev)
        lap[1:-1] = u_prev[2:] - 2 * u_prev[1:-1] + u_prev[:-2]
        u[1:-1] = u_prev[1:-1] + 0.5 * lam2 * lap[1:-1]
        u[0] = 0.0
        u[-1] = 0.0
        H[n0 + 1] = u

        # Leapfrog forward
        for n in range(n0 + 1, nt - 1):
            u_next = np.empty_like(u)
            u_next[1:-1] = (
                2 * u[1:-1]
                - u_prev[1:-1]
                + lam2 * (u[2:] - 2 * u[1:-1] + u[:-2])
            )
            u_next[0] = 0.0
            u_next[-1] = 0.0
            u_prev, u = u, u_next
            H[n + 1] = u

    return H, x, t
