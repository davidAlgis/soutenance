import csv
import math
import random

import matplotlib.pyplot as plt


def is_far_enough(new_particle, particles, min_distance=0.05):
    for particle in particles:
        distance = math.sqrt(
            (new_particle[0] - particle[0]) ** 2
            + (new_particle[1] - particle[1]) ** 2
        )
        if distance < min_distance:
            return False
    return True


def place_particles(
    N, seed=42, filename="states_sph/particles.csv", min_distance=0.05
):
    random.seed(seed)
    particles = []
    attempts = 0
    max_attempts = 10000  # Prevent infinite loops

    while len(particles) < N and attempts < max_attempts:
        x = random.uniform(0.1, 0.9)  # Random x-coordinate in [0.1, 0.9]
        y = random.uniform(0.1, 0.9)  # Random y-coordinate in [0.1, 0.9]
        new_particle = (x, y)

        if not particles or is_far_enough(
            new_particle, particles, min_distance
        ):
            particles.append(new_particle)
        attempts += 1

    if len(particles) < N:
        print(
            f"Warning: Only placed {len(particles)} particles due to distance constraints."
        )

    # Save to CSV
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Particle", "X", "Y"])
        for i, (x, y) in enumerate(particles, 1):
            writer.writerow([i, f"{x:.4f}", f"{y:.4f}"])

    return particles


def plot_particles(particles):
    x_coords, y_coords = zip(*particles)
    plt.figure(figsize=(6, 6))
    plt.scatter(x_coords, y_coords, color="blue", s=50, alpha=0.7)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title("Randomly Placed Particles in [0.1,0.9]x[0.1,0.9] Square")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()


# Example usage:
N = 30  # Number of particles
seed = 1  # You can change this to any integer for different sequences
particles = place_particles(N, seed)

print(
    f"Positions of {len(particles)} particles saved to 'particles.csv' with seed={seed}."
)
plot_particles(particles)
