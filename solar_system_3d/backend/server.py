"""
server.py — FastAPI WebSocket server
Runs the physics loop (from planets.py) and streams planet positions
to the Three.js frontend in real time.

Run with:
    uvicorn server:app --reload --port 8000
"""

import asyncio
import json
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from planets import make_planets, TIME_STEP

app = FastAPI(title="Solar System 3D — Physics Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected")

    planets = make_planets()
    speed   = [1]    # steps per frame
    day     = [0]    # simulated days elapsed
    paused  = [False] # pause flag

    async def receive_loop():
        """Listen for control messages from the frontend (e.g. speed changes)."""
        try:
            while True:
                raw  = await websocket.receive_text()
                data = json.loads(raw)
                if "speed" in data:
                    speed[0] = max(1, min(365, int(data["speed"])))
                    print(f"[WS] Speed set to {speed[0]} days/frame")
                if "paused" in data:
                    paused[0] = bool(data["paused"])
                    print(f"[WS] Simulation {'paused' if paused[0] else 'resumed'}")
                if data.get("reset"):
                    planets[:] = make_planets()
                    day[0] = 0
                    paused[0] = False
                    print("[WS] Simulation reset")
        except (WebSocketDisconnect, Exception):
            pass

    async def send_loop():
        """Run the physics and push planet positions to the frontend at ~60 fps."""
        try:
            while True:
                # ── Physics steps (only when not paused) ──────────────────
                if not paused[0]:
                    for _ in range(speed[0]):
                        for planet in planets:
                            planet.update_position(planets)
                        day[0] += 1

                # ── Serialize and send ─────────────────────────────────────
                payload = {
                    "day":     day[0],
                    "planets": [p.to_dict() for p in planets],
                }
                await websocket.send_text(json.dumps(payload))

                # Tick rate scales with speed:
                #   speed=1   → ~12 fps  (slow, calm orbits)
                #   speed=30  → ~30 fps
                #   speed=100 → ~60 fps  (fast-forward, smooth)
                fps = 12 + (speed[0] - 1) * (60 - 12) / 364
                await asyncio.sleep(1 / fps)

        except (WebSocketDisconnect, Exception) as e:
            print(f"[WS] Client disconnected: {e}")

    # Run both loops concurrently
    await asyncio.gather(receive_loop(), send_loop())


# ── Serve the frontend folder at http://localhost:8000 ──────────────────────
# Must come AFTER all route/websocket definitions.
_frontend = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app.mount("/", StaticFiles(directory=_frontend, html=True), name="frontend")
