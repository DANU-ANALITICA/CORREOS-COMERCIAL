from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import ValidationError

from schemas.campaign import Campaign

CAMPAIGNS_DIR = Path(__file__).resolve().parent.parent / "campaigns"


def ensure_campaigns_dir() -> Path:
    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    return CAMPAIGNS_DIR


def list_campaigns() -> list[str]:
    ensure_campaigns_dir()
    return sorted(p.stem for p in CAMPAIGNS_DIR.glob("*.yml") if p.is_file())


def campaign_path(name: str) -> Path:
    safe_name = name.strip().replace("/", "-").replace("\\", "-")
    return ensure_campaigns_dir() / f"{safe_name}.yml"


def load_draft_dict(name: str) -> dict:
    path = campaign_path(name)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró la campaña '{name}'.")
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"El archivo '{name}.yml' no tiene un formato válido.")
    return data


def save_draft_dict(data: dict) -> Path:
    name = str(data.get("name", "")).strip()
    if not name:
        raise ValueError("Indica un nombre interno para la campaña.")
    path = campaign_path(name)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    return path


def load_campaign(name: str) -> Campaign:
    data = load_draft_dict(name)
    try:
        return Campaign.model_validate(data)
    except Exception as exc:
        raise ValueError(
            f"La campaña '{name}' está incompleta para envío. Complétala o guarda borrador."
        ) from exc


def save_campaign(campaign: Campaign) -> Path:
    return save_draft_dict(campaign.model_dump(mode="json"))


def duplicate_campaign(source_name: str, new_name: str) -> dict:
    data = load_draft_dict(source_name)
    data["name"] = new_name.strip()
    save_draft_dict(data)
    return data


def format_validation_error(exc) -> str:
    messages: list[str] = []
    for error in exc.errors():
        field = " → ".join(str(part) for part in error.get("loc", ()))
        msg = error.get("msg", "Valor inválido")
        messages.append(f"• {field}: {msg}")
    return "Revisa los siguientes campos:\n" + "\n".join(messages)
