from __future__ import annotations

from datetime import date

import streamlit as st

from config.brand import (
    COMPANY_NAME,
    COMPANY_WEBSITE,
    DEFAULT_FOOTER_BANNER_ALT,
    FOOTER_BANNER_LINK,
    get_default_footer_banner_url,
    get_default_logo_url,
)
from schemas.campaign import Campaign, SidebarItem
from services.url_utils import normalize_image_url, sanitize_link_url
from services.image_urls import repair_image_url_for_preview

DEFAULT_SIDEBAR_COUNT = 2
MAX_SIDEBAR_ITEMS = 5
PLACEHOLDER_URL = COMPANY_WEBSITE
DRAFT_EMPTY = "(pendiente)"

TEXT_FIELDS = [
    "name",
    "subject",
    "preheader",
    "template_id",
    "company_name",
    "logo_url",
    "logo_link",
    "greeting",
    "hero_label",
    "hero_title",
    "hero_body",
    "hero_image",
    "hero_url",
    "cta_text",
    "cta_url",
    "cta_color",
    "sidebar_title",
    "promo_text",
    "footer_banner_url",
    "footer_banner_link",
    "footer_banner_alt",
    "legal_text",
    "subscription_reason",
    "privacy_url",
    "manage_subscription_url",
    "unsubscribe_url",
    "copyright_text",
    "company_address",
    "recipients",
]


def _default_values() -> dict[str, str]:
    return {
        "name": f"{date.today().isoformat()}-newsletter",
        "subject": "",
        "preheader": "",
        "template_id": "simple",
        "company_name": COMPANY_NAME,
        "logo_url": get_default_logo_url(),
        "logo_link": COMPANY_WEBSITE,
        "greeting": "Hola [Nombre],",
        "hero_label": f"Nuevo de {COMPANY_NAME}",
        "hero_title": "",
        "hero_body": "",
        "hero_image": "",
        "hero_url": COMPANY_WEBSITE,
        "cta_text": "Ver más",
        "cta_url": COMPANY_WEBSITE,
        "cta_color": "#2251ff",
        "sidebar_title": "También te puede interesar",
        "promo_text": "",
        "footer_banner_url": get_default_footer_banner_url(),
        "footer_banner_link": FOOTER_BANNER_LINK,
        "footer_banner_alt": DEFAULT_FOOTER_BANNER_ALT,
        "legal_text": "Este correo puede utilizar tecnología de seguimiento. Consulta nuestra",
        "subscription_reason": "Recibiste este correo porque estás suscrito a nuestras novedades.",
        "privacy_url": "",
        "manage_subscription_url": "",
        "unsubscribe_url": "",
        "copyright_text": f"© 2026 {COMPANY_NAME}. Todos los derechos reservados.",
        "company_address": "",
        "recipients": "",
    }


def _sidebar_defaults(index: int) -> dict[str, str]:
    return {
        "title": "",
        "image_url": f"https://via.placeholder.com/172x96/0066cc/ffffff?text=Articulo+{index + 1}",
        "url": COMPANY_WEBSITE,
    }


def camp_key(field: str) -> str:
    return f"camp_{field}"


def sb_key(field: str, index: int) -> str:
    return f"camp_sb_{field}_{index}"


def _clean_loaded_value(value: object, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if text == DRAFT_EMPTY:
        return ""
    return text


def _clean_loaded_image_url(value: object, default: str = "") -> str:
    text = _clean_loaded_value(value, default)
    if not text:
        return default
    repaired = repair_image_url_for_preview(text, fallback=default or get_default_logo_url())
    return repaired or default


def init_form_state() -> None:
    defaults = _default_values()
    for field, value in defaults.items():
        st.session_state.setdefault(camp_key(field), value)

    st.session_state.setdefault("camp_sidebar_count", DEFAULT_SIDEBAR_COUNT)
    st.session_state.setdefault(camp_key("footer_banner_enabled"), True)

    for i in range(MAX_SIDEBAR_ITEMS):
        item_defaults = _sidebar_defaults(i)
        for field, value in item_defaults.items():
            st.session_state.setdefault(sb_key(field, i), value)


def export_state_to_draft() -> dict:
    name = st.session_state.get(camp_key("name"), "").strip()
    if not name:
        raise ValueError("Indica un nombre interno para la campaña.")

    data: dict = {"name": name}
    for field in TEXT_FIELDS:
        if field == "name":
            continue
        data[field] = st.session_state.get(camp_key(field), "")

    sidebar_items = []
    count = st.session_state.get("camp_sidebar_count", DEFAULT_SIDEBAR_COUNT)
    for i in range(count):
        sidebar_items.append(
            {
                "title": st.session_state.get(sb_key("title", i), ""),
                "image_url": st.session_state.get(sb_key("image_url", i), ""),
                "url": st.session_state.get(sb_key("url", i), ""),
            }
        )
    data["sidebar_items"] = sidebar_items
    data["footer_banner_enabled"] = bool(st.session_state.get(camp_key("footer_banner_enabled"), True))
    return data


def load_draft_into_state(data: dict) -> None:
    defaults = _default_values()

    for field in TEXT_FIELDS:
        raw = data.get(field, defaults.get(field, ""))
        if field == "logo_url":
            st.session_state[camp_key(field)] = _clean_loaded_image_url(
                raw, defaults.get("logo_url", get_default_logo_url())
            )
            continue
        if field in {"hero_image", "footer_banner_url"}:
            default = defaults.get(field, "")
            if field == "footer_banner_url" and not default:
                default = get_default_footer_banner_url()
            st.session_state[camp_key(field)] = _clean_loaded_image_url(raw, default)
            continue
        st.session_state[camp_key(field)] = _clean_loaded_value(raw, defaults.get(field, ""))

    st.session_state[camp_key("footer_banner_enabled")] = bool(
        data.get("footer_banner_enabled", defaults.get("footer_banner_enabled", True))
    )

    items = data.get("sidebar_items") or []
    if items:
        st.session_state["camp_sidebar_count"] = min(max(len(items), 1), MAX_SIDEBAR_ITEMS)
    else:
        st.session_state["camp_sidebar_count"] = DEFAULT_SIDEBAR_COUNT

    count = st.session_state["camp_sidebar_count"]
    for i in range(MAX_SIDEBAR_ITEMS):
        if i < len(items):
            item = items[i]
            st.session_state[sb_key("title", i)] = _clean_loaded_value(item.get("title", ""))
            st.session_state[sb_key("image_url", i)] = _clean_loaded_image_url(
                item.get("image_url", ""), _sidebar_defaults(i)["image_url"]
            )
            st.session_state[sb_key("url", i)] = _clean_loaded_value(
                item.get("url", ""), COMPANY_WEBSITE
            )
        else:
            item_defaults = _sidebar_defaults(i)
            st.session_state[sb_key("title", i)] = item_defaults["title"]
            st.session_state[sb_key("image_url", i)] = item_defaults["image_url"]
            st.session_state[sb_key("url", i)] = item_defaults["url"]


def load_campaign_into_state(campaign: Campaign) -> None:
    load_draft_into_state(campaign.model_dump(mode="json"))


def _optional_url(value: str) -> str | None:
    cleaned = sanitize_link_url(value.strip())
    return cleaned if cleaned else None


def _required_text(value: str, field_label: str, for_send: bool, placeholder: str = DRAFT_EMPTY) -> str:
    cleaned = value.strip()
    if for_send and not cleaned:
        raise ValueError(f"Falta completar: {field_label}")
    return cleaned or placeholder


def _required_url(value: str, field_label: str, for_send: bool) -> str:
    cleaned = sanitize_link_url(value.strip())
    if for_send and not cleaned:
        raise ValueError(f"Falta completar: {field_label}")
    return cleaned or str(PLACEHOLDER_URL)


def build_campaign_from_state(for_send: bool = False) -> Campaign:
    name = st.session_state[camp_key("name")].strip()
    if not name:
        raise ValueError("Indica un nombre interno para la campaña.")

    template_id = st.session_state.get(camp_key("template_id"), "simple")
    if template_id not in ("simple", "editorial"):
        template_id = "simple"
    editorial = template_id == "editorial"

    sidebar_items: list[SidebarItem] = []
    if editorial:
        count = st.session_state.get("camp_sidebar_count", DEFAULT_SIDEBAR_COUNT)
        for i in range(count):
            title = st.session_state.get(sb_key("title", i), "").strip()
            if not title:
                continue
            sidebar_items.append(
                SidebarItem(
                    title=title,
                    image_url=normalize_image_url(st.session_state.get(sb_key("image_url", i), "")),
                    url=_required_url(
                        st.session_state.get(sb_key("url", i), ""),
                        f"URL del artículo {i + 1}",
                        for_send,
                    ),
                )
            )

    hero_image_raw = st.session_state.get(camp_key("hero_image"), "").strip()
    hero_image = None
    if hero_image_raw:
        hero_image = normalize_image_url(hero_image_raw)
    elif editorial and for_send:
        raise ValueError("Falta completar: Imagen principal")

    hero_url_raw = st.session_state.get(camp_key("hero_url"), "").strip()
    hero_url = sanitize_link_url(hero_url_raw) if hero_url_raw else None
    if editorial and for_send and not hero_url:
        raise ValueError("Falta completar: URL del artículo")

    return Campaign(
        name=name,
        subject=_required_text(st.session_state[camp_key("subject")], "Asunto del correo", for_send),
        preheader=_required_text(st.session_state[camp_key("preheader")], "Vista previa en bandeja", for_send),
        template_id=template_id,
        company_name=st.session_state[camp_key("company_name")].strip() or COMPANY_NAME,
        logo_url=normalize_image_url(
            _required_url(st.session_state[camp_key("logo_url")], "URL del logo", for_send)
        ),
        logo_link=_required_url(st.session_state[camp_key("logo_link")], "Enlace del logo", for_send),
        greeting=st.session_state.get(camp_key("greeting"), "Hola [Nombre],").strip() or "Hola [Nombre],",
        hero_label=st.session_state[camp_key("hero_label")].strip(),
        hero_title=_required_text(
            st.session_state[camp_key("hero_title")], "Titular", for_send and editorial
        ),
        hero_body=_required_text(st.session_state[camp_key("hero_body")], "Cuerpo del mensaje", for_send),
        hero_image=hero_image,
        hero_url=hero_url,
        cta_text=st.session_state[camp_key("cta_text")].strip() or "Ver más",
        cta_url=_required_url(st.session_state[camp_key("cta_url")], "URL del botón", for_send),
        cta_color=st.session_state[camp_key("cta_color")].strip() or "#2251ff",
        sidebar_title=st.session_state[camp_key("sidebar_title")].strip(),
        sidebar_items=sidebar_items,
        promo_text=st.session_state[camp_key("promo_text")].strip(),
        footer_banner_enabled=bool(st.session_state.get(camp_key("footer_banner_enabled"), True)),
        footer_banner_url=normalize_image_url(
            st.session_state.get(camp_key("footer_banner_url"), "").strip()
            or get_default_footer_banner_url()
        ),
        footer_banner_link=_required_url(
            st.session_state.get(camp_key("footer_banner_link"), FOOTER_BANNER_LINK),
            "Enlace del banner",
            for_send,
        ),
        footer_banner_alt=st.session_state.get(camp_key("footer_banner_alt"), DEFAULT_FOOTER_BANNER_ALT).strip()
        or DEFAULT_FOOTER_BANNER_ALT,
        legal_text=st.session_state[camp_key("legal_text")].strip(),
        subscription_reason=st.session_state[camp_key("subscription_reason")].strip(),
        privacy_url=_optional_url(st.session_state[camp_key("privacy_url")]),
        manage_subscription_url=_optional_url(st.session_state[camp_key("manage_subscription_url")]),
        unsubscribe_url=_optional_url(st.session_state[camp_key("unsubscribe_url")]),
        copyright_text=st.session_state[camp_key("copyright_text")].strip(),
        company_address=st.session_state[camp_key("company_address")].strip(),
    )
