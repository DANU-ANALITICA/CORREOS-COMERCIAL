from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

_secrets_data: dict[str, Any] | None = None
_secrets_loaded = False
_secrets_error: str | None = None


class ConfigError(Exception):
    pass


def secrets_parse_error() -> str | None:
    _ensure_secrets_loaded()
    return _secrets_error


def _as_plain_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes)):
        return {str(key): _as_plain_value(value[key]) for key in value.keys()}
    return None


def _as_plain_value(value: Any) -> Any:
    nested = _as_plain_dict(value)
    if nested is not None:
        return nested
    return value


def _normalize_secrets_root(root: Any) -> dict[str, Any]:
    if not isinstance(root, Mapping):
        return {}
    return {str(key): _as_plain_value(root[key]) for key in root.keys()}


def _ensure_secrets_loaded() -> None:
    global _secrets_data, _secrets_loaded, _secrets_error
    if _secrets_loaded:
        return
    _secrets_loaded = True
    try:
        import streamlit as st

        _secrets_data = _normalize_secrets_root(st.secrets)
    except Exception as exc:
        _secrets_data = None
        _secrets_error = (
            "No se pudieron leer los Secrets de Streamlit. "
            "Revisa la sintaxis TOML en Manage app → Settings → Secrets. "
            f"Detalle: {exc}"
        )


def _from_streamlit_secrets(key: str) -> Any | None:
    _ensure_secrets_loaded()
    if _secrets_data and key in _secrets_data:
        return _secrets_data[key]

    try:
        import streamlit as st

        if key in st.secrets:
            return _as_plain_value(st.secrets[key])
    except Exception:
        pass
    return None


def get_config(key: str, default: str = "") -> str:
    env_value = os.environ.get(key, "").strip()
    if env_value:
        return env_value

    value = _from_streamlit_secrets(key)
    if value is None:
        return default
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value).strip()


def _parse_service_account_json(raw: str) -> dict:
    text = raw.strip()
    if not text:
        raise ConfigError("GOOGLE_SERVICE_ACCOUNT_JSON está vacío.")

    candidates = [
        text,
        text.replace("\r\n", "\n"),
        text.replace("\n", "\\n"),
    ]

    last_error: json.JSONDecodeError | None = None
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(data, dict):
            return data

    raise ConfigError(
        "GOOGLE_SERVICE_ACCOUNT_JSON no es un JSON válido. "
        "En Streamlit Secrets usa la sección [google_service_account] "
        "(ver GOOGLE_DRIVE.md)."
    ) from last_error


def get_service_account_info() -> dict:
    nested = _from_streamlit_secrets("google_service_account")
    if isinstance(nested, dict) and nested.get("type") == "service_account":
        return nested

    secret_value = _from_streamlit_secrets("GOOGLE_SERVICE_ACCOUNT_JSON")
    if isinstance(secret_value, dict) and secret_value.get("type") == "service_account":
        return secret_value
    if isinstance(secret_value, str) and secret_value.strip():
        return _parse_service_account_json(secret_value)

    env_raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if env_raw:
        return _parse_service_account_json(env_raw)

    file_path = get_config("GOOGLE_SERVICE_ACCOUNT_FILE")
    if file_path:
        try:
            with open(file_path, encoding="utf-8") as handle:
                data = json.load(handle)
        except OSError as exc:
            raise ConfigError(
                f"No se pudo leer GOOGLE_SERVICE_ACCOUNT_FILE: {file_path}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ConfigError(
                "El archivo de service account no contiene JSON válido."
            ) from exc
        if isinstance(data, dict):
            return data
        raise ConfigError("El archivo de service account debe ser un objeto JSON.")

    raise ConfigError(
        "Configura Google Drive en Secrets: GOOGLE_DRIVE_FOLDER_ID y "
        "[google_service_account] o GOOGLE_SERVICE_ACCOUNT_JSON."
    )


def apply_streamlit_secrets_to_environ() -> None:
    """Refleja Secrets de Streamlit en os.environ. Llamar solo desde main()."""
    keys = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "DEFAULT_FROM",
        "EMISOR",
        "PASSWORD",
        "RECEPTOR",
        "GOOGLE_DRIVE_FOLDER_ID",
        "GOOGLE_SERVICE_ACCOUNT_FILE",
    ]

    for key in keys:
        if os.environ.get(key, "").strip():
            continue
        value = _from_streamlit_secrets(key)
        if value is None:
            continue
        if isinstance(value, dict):
            os.environ[key] = json.dumps(value)
        else:
            os.environ[key] = str(value).strip()

    if not os.environ.get("SMTP_PASSWORD", "").strip():
        password = get_config("PASSWORD")
        if password:
            os.environ["SMTP_PASSWORD"] = password

    if not os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip():
        try:
            info = get_service_account_info()
            os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"] = json.dumps(info)
        except ConfigError:
            pass
