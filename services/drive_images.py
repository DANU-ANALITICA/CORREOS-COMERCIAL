from __future__ import annotations

import base64
import copy
import io
import logging

from googleapiclient.http import MediaIoBaseDownload

from services.drive_storage import DriveStorageError, _execute, _read_kwargs, _service, is_drive_enabled
from services.url_utils import extract_drive_file_id

logger = logging.getLogger(__name__)

IMAGE_FIELDS = ("logo_url", "hero_image")


def fetch_drive_image_data_url(file_id: str) -> str | None:
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
        mime_type = meta.get("mimeType", "image/png")
        if not mime_type.startswith("image/"):
            return None

        buffer = io.BytesIO()
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
    except (DriveStorageError, OSError, ValueError) as exc:
        logger.warning("No se pudo cargar imagen %s desde Drive: %s", file_id, exc)
        return None


def resolve_image_for_display(url: str) -> tuple[str, str | None]:
    """Devuelve (url_final, mensaje_de_error_opcional)."""
    file_id = extract_drive_file_id(str(url))
    if not file_id:
        return str(url), None

    data_url = fetch_drive_image_data_url(file_id)
    if data_url:
        return data_url, None

    return str(url), (
        "Google no permite mostrar esta imagen sin acceso. "
        "Compartila como **Cualquier persona con el enlace** "
        "o agregá como lector a "
        "`correos-comercial-drive-882@ai-labs-478922.iam.gserviceaccount.com` "
        "si está en Drive de la organización."
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
            warnings.append(f"{field}: {warning}")

    for index, item in enumerate(result.get("sidebar_items", [])):
        raw = str(item.get("image_url", ""))
        if not extract_drive_file_id(raw):
            continue
        resolved, warning = resolve_image_for_display(raw)
        item["image_url"] = resolved
        if warning:
            warnings.append(f"sidebar_items[{index}].image_url: {warning}")

    return result, warnings
