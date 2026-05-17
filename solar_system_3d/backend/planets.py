"""
planets.py — Physics engine for 3D Solar System
Ported directly from Planets.py (Newton's gravity + Euler integration).
2D (x, y) upgraded to 3D (x, y, z) using numpy vectors.
Orbital inclinations added so each planet has a real z-axis tilt.
"""

import numpy as np
import math

# ── Same constants as Planets.py ────────────────────────────────────────────
G         = 6.67428e-11       # Gravitational constant  (m³ kg⁻¹ s⁻²)
AU        = 149.6e6 * 1000    # 1 Astronomical Unit     (m)
TIME_STEP = 3600 * 24         # 1 day                   (s)

# ── Planet definitions — same masses/velocities as main.py ─────────────────
# display_radius is visual only (Three.js units), not to physical scale
PLANET_DATA = [
    {
        "name": "Sun",      "x_au": 0.00,  "mass": 1.988416e30,
        "color": "#FDB813", "speed": 0,    "inc": 0.000,
        "display_radius": 1.5, "is_sun": True, "has_ring": False,
    },
    {
        "name": "Mercury",  "x_au": 0.40,  "mass": 3.3010e23,
        "color": "#b5b5b5", "speed": 4.7362e4, "inc": 7.005,
        "display_radius": 0.10, "is_sun": False, "has_ring": False,
    },
    {
        "name": "Venus",    "x_au": 0.72,  "mass": 4.8673e24,
        "color": "#E8CDA0", "speed": 3.5020e4, "inc": 3.395,
        "display_radius": 0.18, "is_sun": False, "has_ring": False,
    },
    {
        "name": "Earth",    "x_au": 1.00,  "mass": 5.9722e24,
        "color": "#1E90FF", "speed": 2.9783e4, "inc": 0.000,
        "display_radius": 0.20, "is_sun": False, "has_ring": False,
    },
    {
        "name": "Mars",     "x_au": 1.50,  "mass": 6.4169e23,
        "color": "#C1440E", "speed": 2.4077e4, "inc": 1.850,
        "display_radius": 0.14, "is_sun": False, "has_ring": False,
    },
    {
        "name": "Jupiter",  "x_au": 5.20,  "mass": 1.8981e27,
        "color": "#C88B3A", "speed": 1.3056e4, "inc": 1.303,
        "display_radius": 0.45, "is_sun": False, "has_ring": False,
    },
    {
        "name": "Saturn",   "x_au": 9.50,  "mass": 5.6832e26,
        "color": "#E4D191", "speed": 9.6391e3, "inc": 2.489,
        "display_radius": 0.38, "is_sun": False, "has_ring": True,
    },
    {
        "name": "Uranus",   "x_au": 19.00, "mass": 8.6810e25,
        "color": "#ACE5EE", "speed": 6.7991e3, "inc": 0.773,
        "display_radius": 0.28, "is_sun": False, "has_ring": False,
    },
    {
        "name": "Neptune",  "x_au": 30.06, "mass": 1.0241e26,
        "color": "#5B5DDF", "speed": 5.4349e3, "inc": 1.770,
        "display_radius": 0.27, "is_sun": False, "has_ring": False,
    },
]


class Planet:
    """
    3D planet — physics ported from Planets.py.
    Position and velocity are numpy 3-vectors (x, y, z).
    """

    def __init__(self, data: dict):
        self.name           = data["name"]
        self.mass           = data["mass"]
        self.color          = data["color"]
        self.is_sun         = data.get("is_sun", False)
        self.has_ring       = data.get("has_ring", False)
        self.display_radius = data["display_radius"]

        # Initial position: along x-axis at given distance
        x = data["x_au"] * AU
        self.pos = np.array([x, 0.0, 0.0], dtype=float)

        # Split orbital speed into y and z using inclination angle
        # (same technique as planetary_motion_3d.ipynb)
        inc   = math.radians(data.get("inc", 0.0))
        speed = data.get("speed", 0.0)
        self.vel = np.array([
            0.0,
            speed * math.cos(inc),   # vy — in-plane component
            speed * math.sin(inc),   # vz — out-of-plane (inclination)
        ], dtype=float)

        self.distance_to_sun = 0.0   # km, updated each step
        self._trail_buffer: list = []  # intermediate positions since last send

    # ── Ported from Planets.py → force_of_attraction() ──────────────────────
    def force_of_attraction(self, other: "Planet") -> np.ndarray:
        """
        F = G * m1 * m2 / r²   (same formula as Planets.py)
        Returns a 3D force vector pointing from self toward other.
        """
        dr       = other.pos - self.pos          # 3D displacement vector
        distance = np.linalg.norm(dr)            # was math.sqrt in Planets.py

        if distance == 0:
            return np.zeros(3)

        if other.is_sun:
            self.distance_to_sun = distance / 1000   # m → km

        force_mag = G * self.mass * other.mass / distance ** 2
        return force_mag * (dr / distance)       # force vector with direction

    # ── Ported from Planets.py → update_position() ──────────────────────────
    def update_position(self, all_planets: list, dt: float = TIME_STEP) -> None:
        """
        Euler integration — same logic as Planets.py, extended to 3D.
          v += (F / m) * dt
          x += v * dt
        dt defaults to TIME_STEP (1 day) but can be set to any value,
        e.g. 1 second for real-time mode.
        """
        if self.is_sun:
            return   # Sun is fixed at origin

        total_force = np.zeros(3)
        for other in all_planets:
            if other is self:
                continue
            total_force += self.force_of_attraction(other)

        acceleration  = total_force / self.mass
        self.vel     += acceleration * dt
        self.pos     += self.vel     * dt
        if not self.is_sun:
            self._trail_buffer.append(self.pos.copy())

    def flush_trail(self, max_pts: int = 80) -> list:
        """
        Return up to max_pts evenly-sampled positions from the trail buffer
        accumulated since the last call, then clear the buffer.
        This gives JS smooth trails even when speed is high.
        """
        buf = self._trail_buffer
        self._trail_buffer = []
        if not buf:
            return []
        # Sample evenly so we never send more than max_pts points
        if len(buf) <= max_pts:
            pts = buf
        else:
            step = len(buf) / max_pts
            pts  = [buf[int(i * step)] for i in range(max_pts)]
        return [[float(p[0] / AU), float(p[1] / AU), float(p[2] / AU)] for p in pts]

    def to_dict(self) -> dict:
        """Serialize current state + trail for JSON delivery to the frontend."""
        return {
            "name":        self.name,
            "color":       self.color,
            "x":           float(self.pos[0] / AU),
            "y":           float(self.pos[1] / AU),
            "z":           float(self.pos[2] / AU),
            "radius":      self.display_radius,
            "is_sun":      self.is_sun,
            "has_ring":    self.has_ring,
            "dist_sun_km": round(self.distance_to_sun),
            "trail":       self.flush_trail(),  # intermediate positions this frame
        }


def make_planets() -> list[Planet]:
    """Create a fresh set of planets — same as calling main() in main.py."""
    return [Planet(d) for d in PLANET_DATA]
