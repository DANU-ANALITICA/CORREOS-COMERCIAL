from __future__ import annotations

import re

DRIVE_FILE_PATTERN = re.compile(
    r"https?://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)"
)
DRIVE_OPEN_PATTERN = re.compile(
    r"https?://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)"
)


def normalize_image_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned:
        return cleaned

    if cleaned.startswith("//"):
        cleaned = f"https:{cleaned}"
    elif not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"

    drive_match = DRIVE_FILE_PATTERN.match(cleaned)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    open_match = DRIVE_OPEN_PATTERN.match(cleaned)
    if open_match:
        file_id = open_match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    return cleaned
