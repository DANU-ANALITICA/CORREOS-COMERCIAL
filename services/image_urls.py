"""Helpers para URLs de imagen en preview y correos."""

from __future__ import annotations

from config.brand import get_default_logo_url

UNRELIABLE_PREVIEW_HOSTS = (
    "via.placeholder.com",
    "placeholder.com",
    "placehold.co",
    "dummyimage.com",
)


def is_unreliable_preview_image_url(url: str) -> bool:
    cleaned = str(url).strip().lower()
    if not cleaned:
        return False
    if cleaned.startswith(("http://data:", "https://data:")):
        return True
    return any(host in cleaned for host in UNRELIABLE_PREVIEW_HOSTS)


def repair_image_url_for_preview(url: str, *, fallback: str | None = None) -> str:
    if fallback is None:
        fallback = get_default_logo_url()
    cleaned = str(url).strip()
    if cleaned.lower().startswith("https://data:"):
        return cleaned.split("://", 1)[1]
    if cleaned.lower().startswith("http://data:"):
        return cleaned.split("://", 1)[1]
    if is_unreliable_preview_image_url(cleaned) and fallback:
        return fallback
    return cleaned
