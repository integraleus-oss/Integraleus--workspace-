#!/usr/bin/env python3
"""
Image generation tool — DALL-E 3 + Flux (fal.ai)
Usage:
  python imagegen.py "a cat in space" --engine dalle --size 1024x1024
  python imagegen.py "a cat in space" --engine flux --size landscape_16_9
  python imagegen.py "a cat in space"  # defaults to dalle

Env vars (from .env or environment):
  OPENAI_API_KEY   — for DALL-E 3
  FAL_KEY          — for Flux via fal.ai
"""

import argparse
import os
import sys
import time
import json
import base64
from pathlib import Path

# Load .env from script directory or workspace root
def load_env():
    for env_path in [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
        Path("/root/.openclaw/workspace/agents/main/.env"),
    ]:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        value = value.strip().strip("'\"")
                        if key.strip() not in os.environ:
                            os.environ[key.strip()] = value
            break

load_env()

OUTPUT_DIR = Path("/root/.openclaw/workspace/agents/main/generated_images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_dalle(prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid") -> str:
    """Generate image via DALL-E 3. Returns path to saved image."""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"Generating with DALL-E 3: '{prompt}' ({size}, {quality}, {style})...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        style=style,
        n=1,
        response_format="b64_json",
    )

    image_data = base64.b64decode(response.data[0].b64_json)
    revised_prompt = response.data[0].revised_prompt

    ts = int(time.time())
    filename = f"dalle_{ts}.png"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "wb") as f:
        f.write(image_data)

    print(f"Revised prompt: {revised_prompt}")
    print(f"Saved: {filepath}")
    return str(filepath)


def generate_flux(prompt: str, size: str = "landscape_16_9", model: str = "fal-ai/flux/schnell") -> str:
    """Generate image via Flux on fal.ai. Returns path to saved image."""
    import fal_client

    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        print("ERROR: FAL_KEY not set", file=sys.stderr)
        sys.exit(1)

    os.environ["FAL_KEY"] = fal_key

    print(f"Generating with Flux ({model}): '{prompt}' ({size})...")

    result = fal_client.subscribe(
        model,
        arguments={
            "prompt": prompt,
            "image_size": size,
            "num_images": 1,
            "enable_safety_checker": True,
        },
    )

    image_url = result["images"][0]["url"]

    # Download image
    import httpx
    resp = httpx.get(image_url)
    resp.raise_for_status()

    ts = int(time.time())
    filename = f"flux_{ts}.png"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "wb") as f:
        f.write(resp.content)

    print(f"Saved: {filepath}")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Generate images via DALL-E 3 or Flux")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--engine", choices=["dalle", "flux"], default="dalle", help="Engine to use")
    parser.add_argument("--size", default=None, help="Image size (DALL-E: 1024x1024/1792x1024/1024x1792; Flux: square/landscape_16_9/portrait_16_9/etc)")
    parser.add_argument("--quality", default="standard", help="DALL-E quality: standard or hd")
    parser.add_argument("--style", default="vivid", help="DALL-E style: vivid or natural")
    parser.add_argument("--model", default="fal-ai/flux/schnell", help="Flux model (schnell=fast/free, pro=quality)")

    args = parser.parse_args()

    if args.engine == "dalle":
        size = args.size or "1024x1024"
        path = generate_dalle(args.prompt, size=size, quality=args.quality, style=args.style)
    else:
        size = args.size or "landscape_16_9"
        path = generate_flux(args.prompt, size=size, model=args.model)

    # Output JSON for easy parsing
    print(json.dumps({"engine": args.engine, "path": path, "prompt": args.prompt}))


if __name__ == "__main__":
    main()
