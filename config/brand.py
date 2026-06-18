"""Enlaces e iconos fijos de Danu Analítica — no editables desde la app."""

from __future__ import annotations

import base64
from pathlib import Path

from services.url_utils import normalize_image_url

COMPANY_NAME = "Danu Analítica"
COMPANY_WEBSITE = "https://www.danuanalitica.com/#inicio"
COMPANY_CONTACT = "https://www.danuanalitica.com/#contacto"
COMPANY_LINKEDIN = "https://www.linkedin.com/company/danuanalitica/posts/?feedView=all"
COMPANY_INSTAGRAM = "https://www.instagram.com/danuanalitica"

FOOTER_BANNER_URL = (
    "https://drive.google.com/file/d/12SuaUZxqaxrKpPELP8Przbavd7VQslRu/view?usp=sharing"
)
FOOTER_BANNER_LINK = "https://calendar.app.google/hfkx5T4nMnCsaxUn6"
DEFAULT_FOOTER_BANNER_ALT = "Agenda tu Discovery Call gratuita con Danu Analítica"


def get_default_footer_banner_url() -> str:
    return normalize_image_url(FOOTER_BANNER_URL)

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "email-icons"

# URLs remotas para correos enviados (el cliente de correo las descarga al abrir el mail).
ICON_LINKEDIN_REMOTE = "https://img.icons8.com/ios-filled/50/0077B5/linkedin.png"
ICON_INSTAGRAM_REMOTE = "https://img.icons8.com/ios-filled/50/E4405F/instagram-new.png"
ICON_WEBSITE_REMOTE = "https://img.icons8.com/ios-filled/50/003366/home.png"
ICON_CONTACT_REMOTE = "https://img.icons8.com/ios-filled/50/003366/new-post.png"

_BRAND_LINKS = {
    "company_linkedin": COMPANY_LINKEDIN,
    "company_instagram": COMPANY_INSTAGRAM,
    "company_website": COMPANY_WEBSITE,
    "company_contact": COMPANY_CONTACT,
}


def _asset_data_uri(filename: str) -> str:
    path = _ASSETS_DIR / filename
    if not path.is_file():
        return ""
    raw = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".svg":
        mime = "image/svg+xml"
    elif suffix == ".png":
        mime = "image/png"
    elif suffix in {".jpg", ".jpeg"}:
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _icon(local_file: str, remote_url: str) -> str:
    return _asset_data_uri(local_file) or remote_url


def get_default_logo_url() -> str:
    return _asset_data_uri("logo-danu.png") or _asset_data_uri("logo-danu.svg") or ICON_WEBSITE_REMOTE


def get_preview_brand_context() -> dict:
    """Iconos embebidos leídos del disco en cada render (preview local y Streamlit)."""
    return {
        **_BRAND_LINKS,
        "icon_linkedin": _icon("linkedin.png", ICON_LINKEDIN_REMOTE),
        "icon_instagram": _icon("instagram.png", ICON_INSTAGRAM_REMOTE),
        "icon_home": _icon("home.png", ICON_WEBSITE_REMOTE),
        "icon_contact": _icon("contact.png", ICON_CONTACT_REMOTE),
    }


def get_email_brand_context() -> dict:
    return {
        **_BRAND_LINKS,
        "icon_linkedin": ICON_LINKEDIN_REMOTE,
        "icon_instagram": ICON_INSTAGRAM_REMOTE,
        "icon_home": ICON_WEBSITE_REMOTE,
        "icon_contact": ICON_CONTACT_REMOTE,
    }


# Compatibilidad con imports existentes.
DEFAULT_LOGO_URL = get_default_logo_url()
BRAND_CONTEXT = get_preview_brand_context()
BRAND_CONTEXT_EMAIL = get_email_brand_context()
