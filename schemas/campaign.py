from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from config.brand import (
    COMPANY_NAME,
    COMPANY_WEBSITE,
    DEFAULT_FOOTER_BANNER_ALT,
    FOOTER_BANNER_LINK,
    get_default_footer_banner_url,
)
from config.templates import DEFAULT_TEMPLATE_ID
from services.url_utils import normalize_image_url

DEFAULT_URL = COMPANY_WEBSITE


def _validate_http_or_data_url(value: str) -> str:
    normalized = normalize_image_url(str(value).strip())
    if not normalized:
        raise ValueError("La URL de imagen no puede estar vacía.")
    if normalized.startswith("data:"):
        return normalized
    HttpUrl(normalized)
    return normalized


class SidebarItem(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    image_url: Annotated[str, Field(min_length=1)]
    url: HttpUrl

    @field_validator("image_url", mode="before")
    @classmethod
    def normalize_image(cls, value: str) -> str:
        return _validate_http_or_data_url(value)


class Campaign(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    subject: Annotated[str, Field(min_length=1, max_length=200)]
    preheader: Annotated[str, Field(min_length=1, max_length=200)]

    template_id: Literal["simple", "editorial"] = DEFAULT_TEMPLATE_ID

    company_name: str = COMPANY_NAME
    logo_url: Annotated[str, Field(min_length=1)]
    logo_link: HttpUrl = DEFAULT_URL

    greeting: str = "Hola [Nombre],"
    hero_label: str = f"Nuevo de {COMPANY_NAME}"
    hero_title: str = ""
    hero_body: Annotated[str, Field(min_length=1, max_length=5000)]
    hero_image: str | None = None
    hero_url: HttpUrl | None = None

    cta_text: str = "Ver más"
    cta_url: HttpUrl
    cta_color: str = "#2251ff"

    sidebar_title: str = "También te puede interesar"
    sidebar_items: list[SidebarItem] = Field(default_factory=list, max_length=5)

    promo_text: str = ""

    footer_banner_enabled: bool = True
    footer_banner_url: Annotated[str, Field(min_length=1, default_factory=get_default_footer_banner_url)]
    footer_banner_link: HttpUrl = FOOTER_BANNER_LINK
    footer_banner_alt: str = DEFAULT_FOOTER_BANNER_ALT

    legal_text: str = "Este correo puede utilizar tecnología de seguimiento. Consulta nuestra"
    subscription_reason: str = "Recibiste este correo porque estás suscrito a nuestras novedades."
    privacy_url: HttpUrl | None = None
    manage_subscription_url: HttpUrl | None = None
    unsubscribe_url: HttpUrl | None = None
    copyright_text: str = f"© 2026 {COMPANY_NAME}. Todos los derechos reservados."
    company_address: str = ""

    @field_validator("hero_image", "logo_url", mode="before")
    @classmethod
    def normalize_images(cls, value: str | None) -> str | None:
        if value is None or str(value).strip() == "":
            return None
        return _validate_http_or_data_url(str(value))

    @field_validator("footer_banner_url", mode="before")
    @classmethod
    def normalize_footer_banner(cls, value: str | None) -> str:
        cleaned = str(value).strip() if value is not None else ""
        if not cleaned:
            return get_default_footer_banner_url()
        return _validate_http_or_data_url(cleaned)

    @field_validator("hero_url", "privacy_url", "manage_subscription_url", "unsubscribe_url", mode="before")
    @classmethod
    def empty_url_to_none(cls, value: str | None) -> str | None:
        if value is None or str(value).strip() == "":
            return None
        return str(value)

    @field_validator("cta_color")
    @classmethod
    def validate_hex_color(cls, value: str) -> str:
        if not value.startswith("#") or len(value) not in (4, 7):
            raise ValueError("El color del botón debe ser un código hexadecimal (ej. #2251ff).")
        return value
