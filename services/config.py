from __future__ import annotations

import json
import os


def _from_streamlit_secrets(key: str) -> str:
    try:
        import streamlit as st
    except ImportError:
        return ""

    if key not in st.secrets:
        return ""

    value = st.secrets[key]
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value).strip()


def get_config(key: str, default: str = "") -> str:
    env_value = os.environ.get(key, "").strip()
    if env_value:
        return env_value
    return _from_streamlit_secrets(key) or default


def apply_streamlit_secrets_to_environ() -> None:
    """Streamlit Cloud guarda Secrets en st.secrets; los reflejamos en os.environ."""
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
        "GOOGLE_SERVICE_ACCOUNT_JSON",
    ]

    for key in keys:
        if os.environ.get(key, "").strip():
            continue
        value = _from_streamlit_secrets(key)
        if value:
            os.environ[key] = value

    # Alternativa: sección anidada en Secrets
    try:
        import streamlit as st

        if not os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip():
            if "google_service_account" in st.secrets:
                os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"] = json.dumps(
                    dict(st.secrets["google_service_account"])
                )
    except Exception:
        pass
