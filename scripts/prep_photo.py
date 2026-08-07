#!/usr/bin/env python3
"""
prep_photo.py — Turn a raw photo into a clean, high-contrast grayscale
image ready for ASCII conversion.

Usage:
    python scripts/prep_photo.py source-photo.jpg

Output:
    source-prepped.png (grayscale, background removed, CLAHE contrast boost,
    composited onto pure white)
"""

import sys
import io
import numpy as np
import cv2
from PIL import Image

try:
    from rembg import remove
except ImportError:
    remove = None


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    with open(input_path, "rb") as f:
        raw = f.read()

    # 1. Remove the background so the subject is isolated.
    if remove is not None:
        cutout_bytes = remove(raw)
        cutout = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")
    else:
        print("rembg not installed — skipping background removal.")
        cutout = Image.open(io.BytesIO(raw)).convert("RGBA")

    # 2. Boost local contrast with CLAHE (works on grayscale). A gentler
    #    clip limit keeps midtone detail (eyes, jacket folds) instead of
    #    crushing everything to near-black.
    rgb = cutout.convert("RGB")
    gray = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)
    gray_img = Image.fromarray(gray_eq).convert("L")

    # 3. Composite onto pure white using the alpha mask from the cutout,
    #    so the background maps to the blank end of the ASCII ramp.
    alpha = cutout.split()[-1]
    white_bg = Image.new("L", gray_img.size, 255)
    result = Image.composite(gray_img, white_bg, alpha)

    result.save(output_path)
    print(f"Wrote {output_path} ({result.size[0]}x{result.size[1]})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
