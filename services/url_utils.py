from __future__ import annotations

import re

DRIVE_FILE_IN_PATH = re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)")
DRIVE_OPEN = re.compile(r"drive\.google\.com/open\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_UC = re.compile(r"drive\.google\.com/uc\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_ANY_ID = re.compile(r"[?&]id=([a-zA-Z0-9_-]+)")
DOCS_UC = re.compile(r"docs\.google\.com/uc\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_THUMBNAIL = re.compile(r"drive\.google\.com/thumbnail\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_FOLDER = re.compile(r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)")
DRIVE_USERCONTENT = re.compile(
    r"drive\.usercontent\.google\.com/download\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)"
)
LH3_GOOGLE = re.compile(r"lh3\.googleusercontent\.com/d/([a-zA-Z0-9_-]+)")


def extract_drive_file_id(url: str) -> str | None:
    cleaned = url.strip()
    if not cleaned:
        return None

    if DRIVE_FOLDER.search(cleaned):
        return None

    for pattern in (
        DRIVE_FILE_IN_PATH,
        DRIVE_OPEN,
        DRIVE_UC,
        DOCS_UC,
        DRIVE_THUMBNAIL,
        DRIVE_USERCONTENT,
        LH3_GOOGLE,
    ):
        match = pattern.search(cleaned)
        if match:
            return match.group(1)

    if "drive.google.com" in cleaned or "docs.google.com" in cleaned:
        match = DRIVE_ANY_ID.search(cleaned)
        if match:
            return match.group(1)
    return None


def is_drive_folder_url(url: str) -> bool:
    return bool(DRIVE_FOLDER.search(url.strip()))


def drive_direct_image_url(file_id: str, *, width: int = 2000) -> str:
    # Thumbnail suele funcionar mejor que uc?export=view en <img> y en iframes.
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}"


def is_drive_url(url: str) -> bool:
    return extract_drive_file_id(url) is not None


def drive_image_link_error(url: str) -> str | None:
    cleaned = url.strip()
    if not cleaned:
        return None
    if is_drive_folder_url(cleaned):
        return (
            "Ese enlace es de una **carpeta** de Drive, no de una imagen. "
            "Abrí la imagen → clic derecho → *Obtener enlace* (debe ser `/file/d/...`)."
        )
    if "drive.google.com" in cleaned and not is_drive_url(cleaned):
        return (
            "No se reconoció el ID del archivo en ese enlace de Drive. "
            "Usa el enlace del archivo, por ejemplo: "
            "`https://drive.google.com/file/d/ID/view?usp=sharing`"
        )
    return None


def sanitize_link_url(url: str) -> str:
    cleaned = url.strip()
    cleaned = re.sub(r"^https://www\.https://", "https://", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^http://www\.http://", "http://", cleaned, flags=re.IGNORECASE)
    return cleaned


def normalize_image_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned:
        return cleaned

    if cleaned.startswith("//"):
        cleaned = f"https:{cleaned}"
    elif not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"

    file_id = extract_drive_file_id(cleaned)
    if file_id:
        return drive_direct_image_url(file_id)

    return cleaned
