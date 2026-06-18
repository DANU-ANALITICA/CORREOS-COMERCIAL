from __future__ import annotations

import base64
import copy
import io
import logging
import urllib.error
import urllib.request

from googleapiclient.http import MediaIoBaseDownload

from services.drive_storage import DriveStorageError, _execute, _read_kwargs, _service, is_drive_enabled
from services.url_utils import drive_direct_image_url, extract_drive_file_id

logger = logging.getLogger(__name__)

IMAGE_FIELDS = ("logo_url", "hero_image")
USER_AGENT = "Mozilla/5.0 (compatible; DanuCorreos/1.0)"


def _bytes_to_data_url(data: bytes, mime_type: str) -> str:
    if not mime_type.startswith("image/"):
        mime_type = "image/jpeg"
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _fetch_public_drive_bytes(file_id: str) -> tuple[bytes, str] | None:
    candidates = [
        drive_direct_image_url(file_id),
        f"https://drive.google.com/uc?export=view&id={file_id}",
        f"https://drive.usercontent.google.com/download?id={file_id}&export=view",
    ]
    for url in candidates:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=20) as response:
                mime_type = response.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                data = response.read()
                if len(data) < 128:
                    continue
                if mime_type.startswith("text/") or mime_type == "application/json":
                    continue
                return data, mime_type
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            logger.debug("Fetch público falló para %s (%s): %s", file_id, url, exc)
    return None


def _fetch_with_service_account(file_id: str) -> str | None:
    if not is_drive_enabled():
        return None

    try:
        service = _service()
        meta = _execute(
            service.files().get(
                fileId=file_id,
                fields="mimeType",
                **_read_kwargs(),
            )
        )
        mime_type = meta.get("mimeType", "image/jpeg")
        if not mime_type.startswith("image/"):
            return None

        buffer = io.BytesIO()
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        return _bytes_to_data_url(buffer.getvalue(), mime_type)
    except (DriveStorageError, OSError, ValueError) as exc:
        logger.warning("Service account no pudo leer imagen %s: %s", file_id, exc)
        return None


def fetch_drive_image_data_url(file_id: str) -> str | None:
    data_url = _fetch_with_service_account(file_id)
    if data_url:
        return data_url

    public = _fetch_public_drive_bytes(file_id)
    if public:
        data, mime_type = public
        return _bytes_to_data_url(data, mime_type)

    return None


def resolve_image_for_display(url: str) -> tuple[str, str | None]:
    file_id = extract_drive_file_id(str(url))
    if not file_id:
        return str(url), None

    data_url = fetch_drive_image_data_url(file_id)
    if data_url:
        return data_url, None

    return drive_direct_image_url(file_id), (
        "No se pudo cargar esta imagen desde Drive. "
        "Compartila como **Cualquier persona con el enlace** (Lector) "
        "y verifica que sea JPG o PNG, no SVG."
    )


def embed_drive_images_in_data(data: dict) -> tuple[dict, list[str]]:
    result = copy.deepcopy(data)
    warnings: list[str] = []

    for field in IMAGE_FIELDS:
        raw = str(result.get(field, ""))
        if not extract_drive_file_id(raw):
            continue
        resolved, warning = resolve_image_for_display(raw)
        result[field] = resolved
        if warning:
            warnings.append(f"**{field}:** {warning}")

    for index, item in enumerate(result.get("sidebar_items", [])):
        raw = str(item.get("image_url", ""))
        if not extract_drive_file_id(raw):
            continue
        resolved, warning = resolve_image_for_display(raw)
        item["image_url"] = resolved
        if warning:
            warnings.append(f"**Sidebar #{index + 1}:** {warning}")

    return result, warnings
