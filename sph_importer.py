#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sph_importer.py

Lightweight CSV importer for SPH simulation states exported as one row per
particle and per time step.

The function import_sph_states(path) returns a list of SphFrame objects,
each holding NumPy arrays that are convenient to use with Matplotlib or Manim.

Expected CSV columns (comma-separated, header required):
    currentTime,index,
    pos_x,pos_y,pos_z,
    vel_x,vel_y,vel_z,
    density,
    type,
    viscosityFx,viscosityFy,viscosityFz,
    pressureFx,pressureFy,pressureFz,
    pressure,
    massSolid,
    isSurface,
    mass

All values are parsed as floats except:
    - index      -> int
    - type       -> int
    - isSurface  -> bool (0/1 accepted)
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class SphFrame:
    """
    Container for one simulation frame at a given time.

    Attributes
    ----------
    current_time : float
        Simulation time in seconds for this frame.
    pos : np.ndarray
        Shape (N, 3), particle positions.
    vel : np.ndarray
        Shape (N, 3), particle velocities.
    density : np.ndarray
        Shape (N,), particle densities.
    types : np.ndarray
        Shape (N,), integer particle types.
    viscosity_forces : np.ndarray
        Shape (N, 3), viscosity forces.
    pressure_forces : np.ndarray
        Shape (N, 3), pressure forces.
    pressure : np.ndarray
        Shape (N,), particle pressures.
    mass_solid : np.ndarray
        Shape (N,), per-particle mass for solids (0.0 for fluids).
    is_surface : np.ndarray
        Shape (N,), boolean mask (True if particle is marked as surface).
    mass : float
        Global particle mass value stored in the CSV (assumed constant).
    """

    current_time: float
    pos: np.ndarray
    vel: np.ndarray
    density: np.ndarray
    types: np.ndarray
    viscosity_forces: np.ndarray
    pressure_forces: np.ndarray
    pressure: np.ndarray
    mass_solid: np.ndarray
    is_surface: np.ndarray
    mass: float

    @property
    def n(self) -> int:
        """
        Number of particles in this frame.
        """
        return int(self.pos.shape[0])


def _as_bool01(value: str) -> bool:
    """
    Convert "0"/"1" or any float-like string to a boolean.
    Non-zero becomes True, zero becomes False.
    """
    try:
        return float(value) != 0.0
    except Exception:
        return False


def import_sph_states(path: str) -> List[SphFrame]:
    """
    Read SPH states from a CSV file and group them by time step.

    The CSV is expected to contain one row per particle, including a
    "currentTime" and "index" column. Rows are grouped by currentTime and
    sorted by index within each group to build consistent arrays.

    Parameters
    ----------
    path : str
        Path to the CSV file produced by the exporter.

    Returns
    -------
    List[SphFrame]
        A list of frames ordered by increasing time. Each frame contains
        NumPy arrays ready for plotting (Matplotlib) or animation (Manim).

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the CSV header is missing required columns.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"CSV file not found: {path}")

    required = [
        "currentTime",
        "index",
        "pos_x",
        "pos_y",
        "pos_z",
        "vel_x",
        "vel_y",
        "vel_z",
        "density",
        "type",
        "viscosityFx",
        "viscosityFy",
        "viscosityFz",
        "pressureFx",
        "pressureFy",
        "pressureFz",
        "pressure",
        "massSolid",
        "isSurface",
        "mass",
    ]

    # Group rows by time
    by_time = {}  # dict[float] -> list[dict]
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header. A header row is required.")

        # Check required columns
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        for row in reader:
            # Skip empty lines if any
            if not row or all(
                (v is None or v.strip() == "") for v in row.values()
            ):
                continue

            try:
                t = float(row["currentTime"])
            except Exception:
                # Skip malformed line
                continue

            by_time.setdefault(t, []).append(row)

    if not by_time:
        return []

    # Build frames ordered by time
    frames: List[SphFrame] = []
    for t in sorted(by_time.keys()):
        rows = by_time[t]

        # Sort by particle index for reproducible ordering
        def _safe_index(r: dict) -> int:
            try:
                return int(r["index"])
            except Exception:
                return 0

        rows.sort(key=_safe_index)

        n = len(rows)

        # Allocate arrays
        pos = np.zeros((n, 3), dtype=np.float32)
        vel = np.zeros((n, 3), dtype=np.float32)
        density = np.zeros((n,), dtype=np.float32)
        ptype = np.zeros((n,), dtype=np.int32)
        visc = np.zeros((n, 3), dtype=np.float32)
        pfor = np.zeros((n, 3), dtype=np.float32)
        pressure = np.zeros((n,), dtype=np.float32)
        mass_solid = np.zeros((n,), dtype=np.float32)
        is_surface = np.zeros((n,), dtype=bool)

        mass_value = None

        # Fill arrays
        write_i = 0
        for r in rows:
            try:
                pos[write_i, 0] = float(r["pos_x"])
                pos[write_i, 1] = float(r["pos_y"])
                pos[write_i, 2] = float(r["pos_z"])

                vel[write_i, 0] = float(r["vel_x"])
                vel[write_i, 1] = float(r["vel_y"])
                vel[write_i, 2] = float(r["vel_z"])

                density[write_i] = float(r["density"])
                ptype[write_i] = int(float(r["type"]))

                visc[write_i, 0] = float(r["viscosityFx"])
                visc[write_i, 1] = float(r["viscosityFy"])
                visc[write_i, 2] = float(r["viscosityFz"])

                pfor[write_i, 0] = float(r["pressureFx"])
                pfor[write_i, 1] = float(r["pressureFy"])
                pfor[write_i, 2] = float(r["pressureFz"])

                pressure[write_i] = float(r["pressure"])
                mass_solid[write_i] = float(r["massSolid"])
                is_surface[write_i] = _as_bool01(r["isSurface"])

                # Keep the first mass value we encounter; assume constant
                if mass_value is None:
                    mass_value = float(r["mass"])

                write_i += 1
            except Exception:
                # Skip malformed row; shrink arrays if needed
                continue

        # If some rows were malformed and skipped, trim arrays
        if write_i != n:
            pos = pos[:write_i]
            vel = vel[:write_i]
            density = density[:write_i]
            ptype = ptype[:write_i]
            visc = visc[:write_i]
            pfor = pfor[:write_i]
            pressure = pressure[:write_i]
            mass_solid = mass_solid[:write_i]
            is_surface = is_surface[:write_i]

        if mass_value is None:
            # Default to 0.0 if not present; keeps API simple and safe
            mass_value = 0.0

        frames.append(
            SphFrame(
                current_time=float(t),
                pos=pos,
                vel=vel,
                density=density,
                types=ptype,
                viscosity_forces=visc,
                pressure_forces=pfor,
                pressure=pressure,
                mass_solid=mass_solid,
                is_surface=is_surface,
                mass=float(mass_value),
            )
        )

    return frames
