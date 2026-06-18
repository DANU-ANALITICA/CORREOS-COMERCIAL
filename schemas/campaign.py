from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, field_validator

from config.brand import COMPANY_NAME, COMPANY_WEBSITE
from services.url_utils import normalize_image_url

DEFAULT_URL = COMPANY_WEBSITE


class SidebarItem(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    image_url: HttpUrl
    url: HttpUrl

    @field_validator("image_url", mode="before")
    @classmethod
    def normalize_image(cls, value: str) -> str:
        return normalize_image_url(str(value))


class Campaign(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    subject: Annotated[str, Field(min_length=1, max_length=200)]
    preheader: Annotated[str, Field(min_length=1, max_length=200)]

    company_name: str = COMPANY_NAME
    logo_url: HttpUrl
    logo_link: HttpUrl = DEFAULT_URL

    hero_label: str = f"Nuevo de {COMPANY_NAME}"
    hero_title: Annotated[str, Field(min_length=1, max_length=300)]
    hero_body: Annotated[str, Field(min_length=1, max_length=2000)]
    hero_image: HttpUrl
    hero_url: HttpUrl

    cta_text: str = "Ver más"
    cta_url: HttpUrl
    cta_color: str = "#2251ff"

    sidebar_title: str = "También te puede interesar"
    sidebar_items: list[SidebarItem] = Field(default_factory=list, max_length=5)

    promo_text: str = ""

    legal_text: str = "Este correo puede utilizar tecnología de seguimiento. Consulta nuestra"
    subscription_reason: str = "Recibiste este correo porque estás suscrito a nuestras novedades."
    privacy_url: HttpUrl | None = None
    manage_subscription_url: HttpUrl | None = None
    unsubscribe_url: HttpUrl | None = None
    copyright_text: str = f"© 2026 {COMPANY_NAME}. Todos los derechos reservados."
    company_address: str = ""

    @field_validator("hero_image", "logo_url", mode="before")
    @classmethod
    def normalize_images(cls, value: str) -> str:
        return normalize_image_url(str(value))

    @field_validator("cta_color")
    @classmethod
    def validate_hex_color(cls, value: str) -> str:
        if not value.startswith("#") or len(value) not in (4, 7):
            raise ValueError("El color del botón debe ser un código hexadecimal (ej. #2251ff).")
        return value
