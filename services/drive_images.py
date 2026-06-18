from __future__ import annotations

import base64
import copy
import io
import logging
import urllib.error
import urllib.request

from googleapiclient.http import MediaIoBaseDownload

from services.drive_storage import DriveStorageError, _execute, _read_kwargs, _service, is_drive_enabled
from services.image_urls import repair_image_url_for_preview
from services.url_utils import drive_direct_image_url, extract_drive_file_id

logger = logging.getLogger(__name__)

IMAGE_FIELDS = ("logo_url", "hero_image", "footer_banner_url")
BRAND_IMAGE_FIELDS: tuple[str, ...] = ()
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
    except Exception as exc:
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


def fetch_http_image_data_url(url: str) -> str | None:
    cleaned = str(url).strip()
    if not cleaned or cleaned.startswith("data:"):
        return cleaned or None

    file_id = extract_drive_file_id(cleaned)
    if file_id:
        return fetch_drive_image_data_url(file_id)

    try:
        request = urllib.request.Request(cleaned, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=20) as response:
            mime_type = response.headers.get("Content-Type", "image/png").split(";")[0].strip()
            data = response.read()
            if len(data) < 64:
                return None
            if mime_type.startswith("text/") or mime_type == "application/json":
                return None
            return _bytes_to_data_url(data, mime_type)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.debug("No se pudo embeber imagen %s: %s", cleaned, exc)
        return None


def _embed_url_field(result: dict, key: str, warnings: list[str], label: str | None = None) -> None:
    raw = str(result.get(key, "")).strip()
    if not raw:
        return
    if raw.startswith("data:"):
        return

    from config.brand import get_default_logo_url

    default_logo = get_default_logo_url()
    fallback = default_logo if key == "logo_url" else ""
    raw = repair_image_url_for_preview(raw, fallback=fallback)
    result[key] = raw
    if raw.startswith("data:"):
        return

    embedded = fetch_http_image_data_url(raw)
    if embedded:
        result[key] = embedded
        return
    if key == "logo_url" and default_logo.startswith("data:"):
        result[key] = default_logo
        return
    if extract_drive_file_id(raw):
        warnings.append(
            f"**{label or key}:** no se pudo cargar desde Drive. "
            "Usa *Cualquier persona con el enlace* o probá *Enviar prueba*."
        )


def embed_drive_images_in_data(data: dict) -> tuple[dict, list[str]]:
    result = copy.deepcopy(data)
    warnings: list[str] = []

    for field in IMAGE_FIELDS:
        _embed_url_field(result, field, warnings, field)

    for field in BRAND_IMAGE_FIELDS:
        _embed_url_field(result, field, warnings, field)

    for index, item in enumerate(result.get("sidebar_items", [])):
        raw = str(item.get("image_url", "")).strip()
        if not raw:
            continue
        raw = repair_image_url_for_preview(raw)
        if raw.startswith("data:"):
            item["image_url"] = raw
            continue
        embedded = fetch_http_image_data_url(raw)
        if embedded:
            item["image_url"] = embedded
        elif extract_drive_file_id(raw):
            warnings.append(f"**Sidebar #{index + 1}:** no se pudo cargar la imagen.")

    return result, warnings
