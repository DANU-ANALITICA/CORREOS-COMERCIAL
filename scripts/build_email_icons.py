"""Genera iconos PNG estilo Icons8 ios-filled para preview y correos."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "email-icons"
SIZE = 50


def _rounded_square(draw: ImageDraw.ImageDraw, size: int, fill: str, radius: int | None = None) -> None:
    if radius is None:
        radius = max(6, size // 6)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=fill)


def linkedin(size: int = SIZE) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _rounded_square(draw, size, "#0077B5")
    inset = size * 0.28
    draw.rounded_rectangle(
        (inset, inset * 1.35, inset + size * 0.14, size - inset * 0.9),
        radius=2,
        fill="white",
    )
    draw.ellipse(
        (inset, inset * 0.55, inset + size * 0.14, inset * 0.55 + size * 0.14),
        fill="white",
    )
    draw.rounded_rectangle(
        (size * 0.48, inset * 1.1, size - inset, size - inset * 0.9),
        radius=2,
        fill="white",
    )
    return img


def instagram(size: int = SIZE) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _rounded_square(draw, size, "#E4405F")
    pad = size * 0.22
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=size * 0.18,
        outline="white",
        width=max(2, size // 16),
    )
    r = size * 0.14
    cx = cy = size / 2
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline="white", width=max(2, size // 16))
    dot = size * 0.07
    draw.ellipse(
        (size * 0.68 - dot, size * 0.32 - dot, size * 0.68 + dot, size * 0.32 + dot),
        fill="white",
    )
    return img


def home(size: int = SIZE) -> Image.Image:
    """Casa blanca sobre cuadrado #003366, estilo Icons8 ios-filled."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _rounded_square(draw, size, "#003366")
    pad = size * 0.22
    w = size - pad * 2
    h = w * 0.72
    x = pad
    y = size * 0.30
    draw.polygon([(size / 2, pad * 0.85), (x, y), (x + w, y)], fill="white")
    draw.rectangle((x, y, x + w, y + h), fill="white")
    door_w = w * 0.22
    door_h = h * 0.38
    draw.rectangle(
        (size / 2 - door_w / 2, y + h - door_h, size / 2 + door_w / 2, y + h),
        fill="#003366",
    )
    return img


def contact(size: int = SIZE) -> Image.Image:
    """Sobre blanco sobre cuadrado #003366, estilo Icons8 ios-filled."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _rounded_square(draw, size, "#003366")
    pad = size * 0.18
    top = size * 0.24
    bottom = size * 0.68
    draw.polygon(
        [(pad, top), (size / 2, size * 0.42), (size - pad, top)],
        fill="white",
    )
    draw.rectangle((pad, top, size - pad, bottom), fill="white")
    draw.line(
        (pad + 1, top + 1, size / 2, size * 0.42, size - pad - 1, top + 1),
        fill="#003366",
        width=max(2, size // 20),
    )
    return img


def logo_danu(width: int = 320, height: int = 64) -> Image.Image:
    img = Image.new("RGBA", (width, height), "#003366")
    draw = ImageDraw.Draw(img)
    text = "DANU ANALITICA"
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height - th) / 2 - 2), text, fill="white", font=font)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    linkedin().save(OUT / "linkedin.png")
    instagram().save(OUT / "instagram.png")
    home().save(OUT / "home.png")
    contact().save(OUT / "contact.png")
    logo_danu().save(OUT / "logo-danu.png")
    print(f"Iconos generados en {OUT}")


if __name__ == "__main__":
    main()
