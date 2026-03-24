#!/usr/bin/env python3
"""
Universal image generator: Flux Pro (fal.ai), GPT-5 Image (OpenAI), Flux free (Pollinations).

Usage:
  python3 generate_image.py "prompt" [--model flux|gpt|free] [--size 1024x1024] [--seed 42]

Environment:
  FAL_KEY        - fal.ai API key (for flux)
  OPENAI_API_KEY - OpenAI API key (for gpt)
"""

import sys
import os
import argparse
import json
import base64
import urllib.parse
from datetime import datetime

OUT_DIR = "/root/.openclaw/workspace/agents/main/generated"


def generate_flux_pro(prompt, width=1024, height=1024, seed=None):
    """Generate via fal.ai Flux Pro."""
    import fal_client

    args = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
        "enable_safety_checker": False,
    }
    if seed is not None:
        args["seed"] = seed

    result = fal_client.subscribe("fal-ai/flux-pro/v1.1", arguments=args)

    image_url = result["images"][0]["url"]

    import requests
    resp = requests.get(image_url, timeout=120)
    resp.raise_for_status()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "jpg" if "jpeg" in resp.headers.get("content-type", "") else "png"
    out_path = os.path.join(OUT_DIR, f"flux_pro_{ts}.{ext}")
    with open(out_path, "wb") as f:
        f.write(resp.content)

    return out_path


def generate_gpt_image(prompt, width=1024, height=1024, seed=None):
    """Generate via OpenAI GPT-5 Image Mini (gpt-image-1)."""
    import requests

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # Map dimensions to size parameter
    if width > height:
        size = "1536x1024"
    elif height > width:
        size = "1024x1536"
    else:
        size = "1024x1024"

    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "medium",
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()

    b64 = data["data"][0]["b64_json"]
    img_bytes = base64.b64decode(b64)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUT_DIR, f"gpt_{ts}.png")
    with open(out_path, "wb") as f:
        f.write(img_bytes)

    return out_path


def generate_free(prompt, width=1024, height=1024, seed=None):
    """Generate via Pollinations.ai (free Flux)."""
    import requests

    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&nologo=true"
    if seed is not None:
        url += f"&seed={seed}"

    resp = requests.get(url, timeout=180, allow_redirects=True)
    resp.raise_for_status()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "jpg" if "jpeg" in resp.headers.get("content-type", "") else "png"
    out_path = os.path.join(OUT_DIR, f"flux_free_{ts}.{ext}")
    with open(out_path, "wb") as f:
        f.write(resp.content)

    return out_path


GENERATORS = {
    "flux": generate_flux_pro,
    "gpt": generate_gpt_image,
    "free": generate_free,
}


def main():
    parser = argparse.ArgumentParser(description="Generate images")
    parser.add_argument("prompt", help="Image prompt")
    parser.add_argument("--model", "-m", choices=["flux", "gpt", "free"], default="flux",
                        help="Model: flux (fal.ai Pro), gpt (OpenAI), free (Pollinations)")
    parser.add_argument("--size", "-s", default="1024x1024", help="WxH, e.g. 1024x1024")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    w, h = map(int, args.size.split("x"))
    os.makedirs(OUT_DIR, exist_ok=True)

    gen = GENERATORS[args.model]
    out_path = gen(args.prompt, width=w, height=h, seed=args.seed)
    print(out_path)


if __name__ == "__main__":
    main()
