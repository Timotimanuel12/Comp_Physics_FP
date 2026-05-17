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

    planets      = make_planets()
    speed        = [1]      # days per frame (normal mode)
    day          = [0.0]    # simulated days elapsed (float for realtime sub-day precision)
    real_seconds = [0.0]    # real seconds elapsed (realtime mode only)
    paused       = [False]
    realtime     = [False]  # true 1:1 real-time mode

    async def receive_loop():
        """Listen for control messages from the frontend."""
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
                if "realtime" in data:
                    realtime[0] = bool(data["realtime"])
                    real_seconds[0] = 0.0
                    print(f"[WS] Real-time mode {'ON' if realtime[0] else 'OFF'}")
                if data.get("reset"):
                    planets[:]      = make_planets()
                    day[0]          = 0.0
                    real_seconds[0] = 0.0
                    paused[0]       = False
                    realtime[0]     = False
                    print("[WS] Simulation reset")
        except (WebSocketDisconnect, Exception):
            pass

    async def send_loop():
        """Run the physics and push planet positions to the frontend."""
        REALTIME_DT = 1.0          # 1 real second per physics step
        REALTIME_FPS = 60          # run at 60fps in realtime mode
        SECS_PER_DAY = 86_400.0    # convert seconds → days

        try:
            while True:
                if not paused[0]:
                    if realtime[0]:
                        # True real-time: dt = 1 second, run at 60 fps
                        # So every frame advances 1/60 of a second of physics
                        dt_frame = REALTIME_DT / REALTIME_FPS
                        for planet in planets:
                            planet.update_position(planets, dt=dt_frame)
                        real_seconds[0] += dt_frame
                        day[0] = real_seconds[0] / SECS_PER_DAY
                    else:
                        for _ in range(speed[0]):
                            for planet in planets:
                                planet.update_position(planets)
                            day[0] += 1

                # Serialize and send
                payload = {
                    "day":          int(day[0]),
                    "real_seconds": round(real_seconds[0], 2),
                    "planets":      [p.to_dict() for p in planets],
                }
                await websocket.send_text(json.dumps(payload))

                # Tick rate
                if realtime[0]:
                    await asyncio.sleep(1 / REALTIME_FPS)   # 60 fps real-time
                else:
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
