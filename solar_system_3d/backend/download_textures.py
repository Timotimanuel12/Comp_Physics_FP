"""
download_textures.py — Downloads free planet texture maps.
Source: Solar System Scope (free for educational use)
Run once: python download_textures.py
"""

import urllib.request
import urllib.error
import os, sys

TEXTURES = {
    'sun.jpg':         'https://www.solarsystemscope.com/textures/download/2k_sun.jpg',
    'mercury.jpg':     'https://www.solarsystemscope.com/textures/download/2k_mercury.jpg',
    'venus.jpg':       'https://www.solarsystemscope.com/textures/download/2k_venus_surface.jpg',
    'earth.jpg':       'https://www.solarsystemscope.com/textures/download/2k_earth_daymap.jpg',
    'mars.jpg':        'https://www.solarsystemscope.com/textures/download/2k_mars.jpg',
    'jupiter.jpg':     'https://www.solarsystemscope.com/textures/download/2k_jupiter.jpg',
    'saturn.jpg':      'https://www.solarsystemscope.com/textures/download/2k_saturn.jpg',
    'saturn_ring.png': 'https://www.solarsystemscope.com/textures/download/2k_saturn_ring_alpha.png',
    'uranus.jpg':      'https://www.solarsystemscope.com/textures/download/2k_uranus.jpg',
    'neptune.jpg':     'https://www.solarsystemscope.com/textures/download/2k_neptune.jpg',
    'stars.jpg':       'https://www.solarsystemscope.com/textures/download/2k_stars_milky_way.jpg',
}

# Mimic a real browser visit — adds Referer so the site allows the download
HEADERS = {
    'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer':         'https://www.solarsystemscope.com/textures/',
    'Accept':          'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection':      'keep-alive',
}

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'textures')
os.makedirs(out_dir, exist_ok=True)

total = len(TEXTURES)
for i, (filename, url) in enumerate(TEXTURES.items(), 1):
    out_path = os.path.join(out_dir, filename)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10_000:
        print(f'[{i}/{total}] {filename} — already exists, skipping.')
        continue
    print(f'[{i}/{total}] Downloading {filename} ...', end=' ', flush=True)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(out_path, 'wb') as f:
            f.write(data)
        print(f'done  ({len(data)//1024} KB)')
    except Exception as e:
        print(f'FAILED → {e}')
        sys.exit(1)

print('\n✅  All textures saved to frontend/textures/')
