from __future__ import annotations

import io
import json
import os

import yaml
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
MIME_YAML = "application/x-yaml"

SHARED_DRIVE_HELP = (
    "Las service accounts no pueden guardar en 'Mi unidad' personal. "
    "Crea la carpeta dentro de una **Unidad compartida** de Google Workspace "
    "y agrega el email de la service account como miembro (Administrador de contenido). "
    "Ver GOOGLE_DRIVE.md"
)


from services.config import ConfigError, get_config, get_service_account_info


class DriveStorageError(Exception):
    pass


def is_drive_enabled() -> bool:
    if not get_config("GOOGLE_DRIVE_FOLDER_ID"):
        return False
    try:
        get_service_account_info()
        return True
    except ConfigError:
        return False


def drive_config_error() -> str | None:
    if not get_config("GOOGLE_DRIVE_FOLDER_ID"):
        return None
    try:
        get_service_account_info()
        return None
    except ConfigError as exc:
        return str(exc)


def _load_service_account_info() -> dict:
    try:
        return get_service_account_info()
    except ConfigError as exc:
        raise DriveStorageError(str(exc)) from exc


def _folder_id() -> str:
    folder_id = get_config("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise DriveStorageError("Falta GOOGLE_DRIVE_FOLDER_ID en la configuración.")
    return folder_id


def _service():
    info = _load_service_account_info()
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=[DRIVE_SCOPE]
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _safe_filename(name: str) -> str:
    safe = name.strip().replace("/", "-").replace("\\", "-")
    return f"{safe}.yml"


def _list_kwargs() -> dict:
    return {"supportsAllDrives": True, "includeItemsFromAllDrives": True}


def _write_kwargs() -> dict:
    return {"supportsAllDrives": True}


def _execute(request):
    try:
        return request.execute()
    except HttpError as exc:
        body = exc.error_details if hasattr(exc, "error_details") else []
        reasons = [item.get("reason", "") for item in body if isinstance(item, dict)]
        if exc.resp.status == 403 and (
            "storageQuotaExceeded" in reasons
            or "storage quota" in str(exc).lower()
            or "do not have storage quota" in str(exc).lower()
        ):
            raise DriveStorageError(SHARED_DRIVE_HELP) from exc
        raise DriveStorageError(f"Error de Google Drive: {exc}") from exc


def _find_file_id(service, filename: str) -> str | None:
    folder_id = _folder_id()
    query = (
        f"'{folder_id}' in parents and name='{filename}' "
        "and trashed=false and mimeType!='application/vnd.google-apps.folder'"
    )
    response = _execute(
        service.files().list(q=query, fields="files(id,name)", **_list_kwargs())
    )
    files = response.get("files", [])
    return files[0]["id"] if files else None


def list_campaigns() -> list[str]:
    service = _service()
    folder_id = _folder_id()
    query = (
        f"'{folder_id}' in parents and trashed=false and name contains '.yml' "
        "and mimeType!='application/vnd.google-apps.folder'"
    )
    response = _execute(
        service.files().list(q=query, fields="files(name)", **_list_kwargs())
    )
    names = []
    for item in response.get("files", []):
        name = item.get("name", "")
        if name.endswith(".yml"):
            names.append(name[:-4])
    return sorted(names)


def load_draft_dict(name: str) -> dict:
    service = _service()
    filename = _safe_filename(name)
    file_id = _find_file_id(service, filename)
    if not file_id:
        raise FileNotFoundError(f"No se encontró la campaña '{name}' en Google Drive.")

    buffer = io.BytesIO()
    request = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    data = yaml.safe_load(buffer.getvalue().decode("utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"El borrador '{name}' no tiene un formato válido.")
    return data


def save_draft_dict(data: dict) -> str:
    name = str(data.get("name", "")).strip()
    if not name:
        raise ValueError("Indica un nombre interno para la campaña.")

    service = _service()
    filename = _safe_filename(name)
    content = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")),
        mimetype=MIME_YAML,
        resumable=False,
    )

    file_id = _find_file_id(service, filename)
    if file_id:
        _execute(
            service.files().update(
                fileId=file_id,
                media_body=media,
                **_write_kwargs(),
            )
        )
    else:
        _execute(
            service.files().create(
                body={"name": filename, "parents": [_folder_id()]},
                media_body=media,
                fields="id",
                **_write_kwargs(),
            )
        )

    return filename
