from __future__ import annotations

import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config.brand import BRAND_CONTEXT, COMPANY_NAME, COMPANY_WEBSITE
from schemas.campaign import Campaign
from services.url_utils import normalize_image_url

from services.config import apply_streamlit_secrets_to_environ, get_config

load_dotenv()
apply_streamlit_secrets_to_environ()

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
    )


def render_campaign(campaign: Campaign) -> str:
    env = get_jinja_env()
    template = env.get_template("newsletter.html.j2")
    data = campaign.model_dump(mode="python")
    data.update(BRAND_CONTEXT)
    return template.render(**data)


def parse_recipients(raw: str) -> list[str]:
    parts = re.split(r"[,;\n]+", raw.strip())
    recipients = [p.strip() for p in parts if p.strip()]
    invalid = [r for r in recipients if not EMAIL_PATTERN.match(r)]
    if invalid:
        raise ValueError(
            "Correos inválidos: " + ", ".join(invalid)
        )
    if not recipients:
        raise ValueError("Debes indicar al menos un destinatario.")
    return recipients


def send_html_email(subject: str, html: str, recipients: list[str]) -> None:
    smtp_user = get_config("SMTP_USER") or get_config("EMISOR")
    smtp_password = get_config("SMTP_PASSWORD") or get_config("PASSWORD")
    smtp_host = get_config("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(get_config("SMTP_PORT", "465"))
    default_from = get_config("DEFAULT_FROM") or smtp_user

    if not smtp_user or not smtp_password:
        raise ValueError(
            "Faltan credenciales SMTP. Configura SMTP_USER y SMTP_PASSWORD en el archivo .env."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = default_from
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_password)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        raise ValueError(
            "No se pudo autenticar con Gmail. Verifica SMTP_USER y SMTP_PASSWORD (usa una App Password)."
        ) from exc
    except smtplib.SMTPException as exc:
        raise ValueError(f"Error al enviar el correo: {exc}") from exc
