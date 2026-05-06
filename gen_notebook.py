import json

def md(source, cid):
    return {"cell_type": "markdown", "id": cid, "metadata": {}, "source": source}

def code(source, cid):
    return {"cell_type": "code", "execution_count": None, "id": cid, "metadata": {}, "outputs": [], "source": source}

cells = []

# ── Cell 0 : Title ──────────────────────────────────────────────────────────
cells.append(md([
    "# 🪐 3D Solar System — Physics from `Planets.py`\n",
    "\n",
    "This notebook **ports the physics logic directly from `Planets.py`** and renders it in 3D with `matplotlib`.\n",
    "\n",
    "| What stays the same | What changes |\n",
    "|---|---|\n",
    "| `G`, `AU`, `TIME` constants (SI units) | `pygame` → `matplotlib 3D` |\n",
    "| `force_of_attraction()` formula | Scalar x/y → numpy 3-vectors |\n",
    "| `update_position()` Euler integration | Added real orbital inclinations (z-axis) |\n",
    "| Same planets & initial velocities from `main.py` | Orbit stored as numpy array |\n",
], "cell-00"))

# ── Cell 1 : Imports ────────────────────────────────────────────────────────
cells.append(code([
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.animation as animation\n",
    "from mpl_toolkits.mplot3d import Axes3D\n",
    "from IPython.display import HTML\n",
    "import math, warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "print(f'NumPy {np.__version__} | Matplotlib {plt.matplotlib.__version__}')\n",
], "cell-01"))

# ── Cell 2 : Physical constants ─────────────────────────────────────────────
cells.append(md(["## 1 · Physical Constants\n", "Same values used in `Planets.py` — full SI units.\n"], "cell-02"))

cells.append(code([
    "# ── Exact same constants as Planets.py ──────────────────────────────────\n",
    "G         = 6.67428e-11      # Gravitational constant  (m³ kg⁻¹ s⁻²)\n",
    "AU        = 149.6e6 * 1000   # 1 Astronomical Unit     (m)\n",
    "TIME_STEP = 3600 * 24        # 1 day                   (s)\n",
    "\n",
    "print(f'G         = {G} m³/(kg·s²)')\n",
    "print(f'AU        = {AU:.4e} m')\n",
    "print(f'TIME_STEP = {TIME_STEP} s  (1 day)')\n",
], "cell-03"))

# ── Cell 4 : Planet class ────────────────────────────────────────────────────
cells.append(md([
    "## 2 · `Planet` Class — Ported from `Planets.py`\n",
    "\n",
    "- `force_of_attraction()` → same formula, now returns a **3-vector** using `np.linalg.norm`\n",
    "- `update_position()` → same Euler integration, now works on **3D position/velocity**\n",
    "- `draw()` → **removed** (replaced by matplotlib)\n",
], "cell-04"))

cells.append(code([
    "class Planet:\n",
    "    \"\"\"\n",
    "    Physics ported from Planets.py.\n",
    "    2D (x, y) → 3D (x, y, z) using numpy vectors.\n",
    "    pygame drawing removed — matplotlib handles rendering.\n",
    "    \"\"\"\n",
    "\n",
    "    def __init__(self, x, y, z, mass, color, name, display_size=8):\n",
    "        self.pos          = np.array([x, y, z], dtype=float)\n",
    "        self.vel          = np.array([0.0, 0.0, 0.0])\n",
    "        self.mass         = mass\n",
    "        self.color        = color\n",
    "        self.name         = name\n",
    "        self.display_size = display_size\n",
    "        self.is_sun       = False\n",
    "        self.orbit        = []   # list of np.array snapshots\n",
    "        self.distance_to_sun = 0\n",
    "\n",
    "    # ── Ported from Planets.py ── force_of_attraction() ─────────────────\n",
    "    def force_of_attraction(self, other):\n",
    "        \"\"\"\n",
    "        F = G * m1 * m2 / r²  (same formula as Planets.py)\n",
    "        Direction: unit vector from self → other (now 3D)\n",
    "        \"\"\"\n",
    "        dr       = other.pos - self.pos                   # 3D displacement\n",
    "        distance = np.linalg.norm(dr)                     # was math.sqrt in Planets.py\n",
    "\n",
    "        if other.is_sun:\n",
    "            self.distance_to_sun = distance / 1000        # m → km\n",
    "\n",
    "        force_mag = G * self.mass * other.mass / distance**2\n",
    "        force_vec = force_mag * (dr / distance)           # apply direction\n",
    "        return force_vec\n",
    "\n",
    "    # ── Ported from Planets.py ── update_position() ──────────────────────\n",
    "    def update_position(self, planets):\n",
    "        \"\"\"\n",
    "        Euler integration — same logic as Planets.py, now 3D.\n",
    "        v += (F/m) * dt\n",
    "        x += v * dt\n",
    "        \"\"\"\n",
    "        total_force = np.zeros(3)\n",
    "        for other in planets:\n",
    "            if other is self:\n",
    "                continue\n",
    "            total_force += self.force_of_attraction(other)\n",
    "\n",
    "        acceleration  = total_force / self.mass\n",
    "        self.vel     += acceleration * TIME_STEP\n",
    "        self.pos     += self.vel * TIME_STEP\n",
    "        self.orbit.append(self.pos.copy())\n",
    "\n",
    "print('Planet class defined.')\n",
], "cell-05"))

# ── Cell 6 : Init planets ────────────────────────────────────────────────────
cells.append(md([
    "## 3 · Initialize Planets\n",
    "\n",
    "Same masses and initial velocities as `main.py`.  \n",
    "Added **real orbital inclinations** so orbits have visible z-offsets in 3D.\n",
], "cell-06"))

cells.append(code([
    "def make_planets():\n",
    "    \"\"\"Same planets as main.py. Velocities split into vy, vz using inclination angles.\"\"\"\n",
    "\n",
    "    # Real orbital inclinations relative to the ecliptic (degrees → radians)\n",
    "    inc = {\n",
    "        'mercury': math.radians(7.005),\n",
    "        'venus':   math.radians(3.395),\n",
    "        'earth':   math.radians(0.000),\n",
    "        'mars':    math.radians(1.850),\n",
    "        'jupiter': math.radians(1.303),\n",
    "        'saturn':  math.radians(2.489),\n",
    "        'uranus':  math.radians(0.773),\n",
    "        'neptune': math.radians(1.770),\n",
    "    }\n",
    "\n",
    "    def set_vel(planet, v_orbital, key):\n",
    "        \"\"\"Split orbital speed into vy and vz components using inclination.\"\"\"\n",
    "        planet.vel[1] = v_orbital * math.cos(inc[key])\n",
    "        planet.vel[2] = v_orbital * math.sin(inc[key])\n",
    "\n",
    "    # Sun — same mass as main.py\n",
    "    sun = Planet(0, 0, 0, 1.988416e30, '#FDB813', 'Sun', 20)\n",
    "    sun.is_sun = True\n",
    "\n",
    "    # Planets — same x positions, masses, and orbital speeds as main.py\n",
    "    mercury = Planet(0.40*AU, 0, 0, 3.3010e23, '#b5b5b5', 'Mercury', 8)\n",
    "    set_vel(mercury, 4.7362e4, 'mercury')\n",
    "\n",
    "    venus = Planet(0.72*AU, 0, 0, 4.8673e24, '#E8CDA0', 'Venus', 14)\n",
    "    set_vel(venus, 3.5020e4, 'venus')\n",
    "\n",
    "    earth = Planet(1.00*AU, 0, 0, 5.9722e24, '#1E90FF', 'Earth', 16)\n",
    "    set_vel(earth, 29.783e3, 'earth')\n",
    "\n",
    "    mars = Planet(1.50*AU, 0, 0, 6.4169e23, '#C1440E', 'Mars', 12)\n",
    "    set_vel(mars, 24.077e3, 'mars')\n",
    "\n",
    "    jupiter = Planet(5.20*AU, 0, 0, 1.8981e27, '#C88B3A', 'Jupiter', 23)\n",
    "    set_vel(jupiter, 1.3056e4, 'jupiter')\n",
    "\n",
    "    saturn = Planet(9.50*AU, 0, 0, 5.6832e26, '#E4D191', 'Saturn', 21)\n",
    "    set_vel(saturn, 9.6391e3, 'saturn')\n",
    "\n",
    "    uranus = Planet(19.0*AU, 0, 0, 8.6810e25, '#ACE5EE', 'Uranus', 19)\n",
    "    set_vel(uranus, 6.7991e3, 'uranus')\n",
    "\n",
    "    neptune = Planet(30.06*AU, 0, 0, 1.0241e26, '#5B5DDF', 'Neptune', 19)\n",
    "    set_vel(neptune, 5.4349e3, 'neptune')\n",
    "\n",
    "    return [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]\n",
    "\n",
    "\n",
    "planets = make_planets()\n",
    "print(f'Created {len(planets)} bodies:')\n",
    "for p in planets:\n",
    "    print(f'  {p.name:8s}  pos={p.pos[0]/AU:6.2f} AU   mass={p.mass:.3e} kg   vel_y={p.vel[1]:.0f} m/s')\n",
], "cell-07"))

# ── Cell 8 : Run simulation ──────────────────────────────────────────────────
cells.append(md([
    "## 4 · Run Simulation\n",
    "\n",
    "Calls `update_position()` (ported from `Planets.py`) for each planet each day.\n",
], "cell-08"))

cells.append(code([
    "SIM_YEARS = 5\n",
    "SIM_DAYS  = int(SIM_YEARS * 365.25)\n",
    "\n",
    "print(f'Simulating {SIM_YEARS} years ({SIM_DAYS} steps of 1 day) ...')\n",
    "\n",
    "for step in range(SIM_DAYS):\n",
    "    for planet in planets:\n",
    "        planet.update_position(planets)\n",
    "\n",
    "print('Done!')\n",
    "for p in planets:\n",
    "    if not p.is_sun:\n",
    "        print(f'  {p.name:8s}  orbit pts={len(p.orbit):4d}  dist_sun={p.distance_to_sun:,.0f} km')\n",
], "cell-09"))

# ── Cell 10 : Static 3D plot ─────────────────────────────────────────────────
cells.append(md([
    "## 5 · Static 3D Orbit Plot\n",
    "\n",
    "Full orbital paths for all planets over the simulated period.\n",
], "cell-10"))

cells.append(code([
    "fig = plt.figure(figsize=(15, 12), facecolor='#0a0a0f')\n",
    "ax  = fig.add_subplot(111, projection='3d')\n",
    "ax.set_facecolor('#0a0a0f')\n",
    "\n",
    "for spine in ax.spines.values():\n",
    "    spine.set_visible(False)\n",
    "\n",
    "ax.xaxis.pane.fill = False\n",
    "ax.yaxis.pane.fill = False\n",
    "ax.zaxis.pane.fill = False\n",
    "ax.xaxis.pane.set_edgecolor('#222')\n",
    "ax.yaxis.pane.set_edgecolor('#222')\n",
    "ax.zaxis.pane.set_edgecolor('#222')\n",
    "ax.grid(color='#222', linewidth=0.5)\n",
    "\n",
    "for planet in planets:\n",
    "    orbit = np.array(planet.orbit) / AU if planet.orbit else None\n",
    "\n",
    "    if orbit is not None and len(orbit) > 1:\n",
    "        ax.plot(orbit[:, 0], orbit[:, 1], orbit[:, 2],\n",
    "                color=planet.color, linewidth=0.8, alpha=0.55)\n",
    "\n",
    "    pos_au = planet.pos / AU\n",
    "    ax.scatter(*pos_au, color=planet.color,\n",
    "               s=planet.display_size ** 1.6, zorder=6, label=planet.name)\n",
    "\n",
    "ax.set_xlabel('X (AU)', color='#888', labelpad=10)\n",
    "ax.set_ylabel('Y (AU)', color='#888', labelpad=10)\n",
    "ax.set_zlabel('Z (AU)', color='#888', labelpad=10)\n",
    "ax.tick_params(colors='#555')\n",
    "ax.set_title('Solar System — 3D Orbital Simulation\\n'\n",
    "             'Physics from Planets.py  |  Rendered with matplotlib',\n",
    "             color='white', fontsize=13, pad=15)\n",
    "\n",
    "legend = ax.legend(loc='upper left', fontsize=9,\n",
    "                   facecolor='#111', framealpha=0.7)\n",
    "for text in legend.get_texts():\n",
    "    text.set_color('white')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.savefig('orbits_3d_ported.png', dpi=150, bbox_inches='tight',\n",
    "            facecolor='#0a0a0f')\n",
    "plt.show()\n",
    "print('Saved: orbits_3d_ported.png')\n",
], "cell-11"))

# ── Cell 12 : Inner solar system closeup ────────────────────────────────────
cells.append(md(["## 6 · Inner Solar System (Mercury → Mars)\n"], "cell-12"))

cells.append(code([
    "fig2, ax2 = plt.subplots(figsize=(10, 10),\n",
    "                          subplot_kw={'projection': '3d'},\n",
    "                          facecolor='#0a0a0f')\n",
    "ax2.set_facecolor('#0a0a0f')\n",
    "ax2.xaxis.pane.fill = ax2.yaxis.pane.fill = ax2.zaxis.pane.fill = False\n",
    "ax2.grid(color='#222', linewidth=0.4)\n",
    "\n",
    "inner = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars']\n",
    "for planet in planets:\n",
    "    if planet.name not in inner:\n",
    "        continue\n",
    "    orbit = np.array(planet.orbit) / AU if planet.orbit else None\n",
    "    if orbit is not None and len(orbit) > 1:\n",
    "        ax2.plot(orbit[:, 0], orbit[:, 1], orbit[:, 2],\n",
    "                 color=planet.color, linewidth=1.2, alpha=0.7)\n",
    "    pos_au = planet.pos / AU\n",
    "    ax2.scatter(*pos_au, color=planet.color,\n",
    "                s=planet.display_size ** 1.8, zorder=6, label=planet.name)\n",
    "\n",
    "ax2.set_xlim(-2, 2); ax2.set_ylim(-2, 2); ax2.set_zlim(-0.3, 0.3)\n",
    "ax2.set_xlabel('X (AU)', color='#888')\n",
    "ax2.set_ylabel('Y (AU)', color='#888')\n",
    "ax2.set_zlabel('Z (AU)', color='#888')\n",
    "ax2.tick_params(colors='#555')\n",
    "ax2.set_title('Inner Solar System — 3D', color='white', fontsize=12)\n",
    "legend2 = ax2.legend(fontsize=9, facecolor='#111', framealpha=0.7)\n",
    "for t in legend2.get_texts(): t.set_color('white')\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
], "cell-13"))

# ── Cell 14 : Animation ───────────────────────────────────────────────────────
cells.append(md([
    "## 7 · Animated 3D Simulation\n",
    "\n",
    "Inner planets animated with a **fading trail** — same trail concept as `Planets.py`'s `draw()` method.\n",
], "cell-14"))

cells.append(code([
    "# Fresh planets for animation\n",
    "anim_planets = make_planets()\n",
    "\n",
    "# Warm-up: run 1 year to build initial trails\n",
    "WARMUP = 365\n",
    "for _ in range(WARMUP):\n",
    "    for p in anim_planets:\n",
    "        p.update_position(anim_planets)\n",
    "\n",
    "# Only animate inner solar system for clarity\n",
    "shown = [p for p in anim_planets if p.name in ('Sun','Mercury','Venus','Earth','Mars')]\n",
    "\n",
    "fig_a = plt.figure(figsize=(10, 8), facecolor='#0a0a0f')\n",
    "ax_a  = fig_a.add_subplot(111, projection='3d')\n",
    "ax_a.set_facecolor('#0a0a0f')\n",
    "ax_a.xaxis.pane.fill = ax_a.yaxis.pane.fill = ax_a.zaxis.pane.fill = False\n",
    "ax_a.grid(color='#1a1a2e', linewidth=0.4)\n",
    "ax_a.set_xlim(-2, 2); ax_a.set_ylim(-2, 2); ax_a.set_zlim(-0.3, 0.3)\n",
    "ax_a.set_xlabel('X (AU)', color='#666')\n",
    "ax_a.set_ylabel('Y (AU)', color='#666')\n",
    "ax_a.set_zlabel('Z (AU)', color='#666')\n",
    "ax_a.tick_params(colors='#444')\n",
    "ax_a.set_title('Inner Solar System — Live 3D Animation', color='white')\n",
    "\n",
    "TRAIL = 120   # days of trail to show\n",
    "STEPS_PER_FRAME = 3\n",
    "\n",
    "dots  = [ax_a.scatter([], [], [], color=p.color,\n",
    "                       s=p.display_size**1.8, zorder=6) for p in shown]\n",
    "lines = [ax_a.plot([], [], [], color=p.color,\n",
    "                   lw=1.2, alpha=0.7)[0]              for p in shown]\n",
    "\n",
    "def update_anim(frame):\n",
    "    for _ in range(STEPS_PER_FRAME):\n",
    "        for p in anim_planets:\n",
    "            p.update_position(anim_planets)\n",
    "\n",
    "    for i, p in enumerate(shown):\n",
    "        px, py, pz = p.pos / AU\n",
    "        dots[i]._offsets3d = ([px], [py], [pz])\n",
    "\n",
    "        trail_pts = np.array(p.orbit[-TRAIL:]) / AU\n",
    "        if len(trail_pts) > 1:\n",
    "            lines[i].set_data(trail_pts[:, 0], trail_pts[:, 1])\n",
    "            lines[i].set_3d_properties(trail_pts[:, 2])\n",
    "\n",
    "    return dots + lines\n",
    "\n",
    "ani = animation.FuncAnimation(fig_a, update_anim, frames=250,\n",
    "                               interval=40, blit=False)\n",
    "plt.close()\n",
    "HTML(ani.to_jshtml())\n",
], "cell-15"))

# ── Assemble notebook ────────────────────────────────────────────────────────
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out = "planetary_motion_3d.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Created: {out}")
