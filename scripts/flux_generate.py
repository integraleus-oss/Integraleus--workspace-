#!/usr/bin/env python3
"""Generate images via Pollinations.ai FLUX API (free, no key needed)."""

import sys
import os
import urllib.parse
import requests
from datetime import datetime

def generate(prompt, width=1024, height=1024, model="flux", seed=None):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={model}&nologo=true"
    if seed is not None:
        url += f"&seed={seed}"

    resp = requests.get(url, timeout=180, allow_redirects=True)
    resp.raise_for_status()

    if "image" not in resp.headers.get("content-type", ""):
        raise RuntimeError(f"Unexpected response: {resp.text[:200]}")

    out_dir = "/root/.openclaw/workspace/agents/main/generated"
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "jpg" if "jpeg" in resp.headers.get("content-type", "") else "png"
    out_path = os.path.join(out_dir, f"flux_{ts}.{ext}")

    with open(out_path, "wb") as f:
        f.write(resp.content)

    print(out_path)
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: flux_generate.py 'prompt' [width] [height] [seed]")
        sys.exit(1)
    prompt = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    s = int(sys.argv[4]) if len(sys.argv) > 4 else None
    generate(prompt, width=w, height=h, seed=s)
