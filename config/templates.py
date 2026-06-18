"""Registro de plantillas de correo disponibles."""

from __future__ import annotations

TEMPLATES: dict[str, dict[str, str]] = {
    "simple": {
        "file": "newsletter.html.j2",
        "label": "Carta comercial",
        "description": "Saludo personalizado, texto, botón, banner Discovery Call y footer. Sin sidebar.",
    },
    "editorial": {
        "file": "newsletter_editorial.html.j2",
        "label": "Newsletter",
        "description": "Imagen principal grande, titular, sidebar con artículos relacionados y footer.",
    },
}

DEFAULT_TEMPLATE_ID = "simple"


def get_template_file(template_id: str) -> str:
    entry = TEMPLATES.get(template_id) or TEMPLATES[DEFAULT_TEMPLATE_ID]
    return entry["file"]
