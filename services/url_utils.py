from __future__ import annotations

import json
import os
import re

DRIVE_FILE_IN_PATH = re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)")
DRIVE_OPEN = re.compile(r"drive\.google\.com/open\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_UC = re.compile(r"drive\.google\.com/uc\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_ANY_ID = re.compile(r"[?&]id=([a-zA-Z0-9_-]+)")
DOCS_UC = re.compile(r"docs\.google\.com/uc\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")
DRIVE_THUMBNAIL = re.compile(r"drive\.google\.com/thumbnail\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)")


def extract_drive_file_id(url: str) -> str | None:
    for pattern in (
        DRIVE_FILE_IN_PATH,
        DRIVE_OPEN,
        DRIVE_UC,
        DOCS_UC,
        DRIVE_THUMBNAIL,
    ):
        match = pattern.search(url)
        if match:
            return match.group(1)

    if "drive.google.com" in url or "docs.google.com" in url:
        match = DRIVE_ANY_ID.search(url)
        if match:
            return match.group(1)
    return None


def drive_direct_image_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def is_drive_url(url: str) -> bool:
    return extract_drive_file_id(url) is not None


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
