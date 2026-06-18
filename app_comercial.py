from __future__ import annotations

from datetime import date

import streamlit as st
from pydantic import ValidationError

from services.config import apply_streamlit_secrets_to_environ, get_config, secrets_parse_error

from config.brand import COMPANY_INSTAGRAM, COMPANY_LINKEDIN, COMPANY_WEBSITE
from services.campaign_store import (
    duplicate_campaign,
    format_validation_error,
    list_campaigns,
    load_draft_dict,
    save_draft_dict,
    storage_mode,
)
from services.drive_storage import DriveStorageError, drive_config_error
from services.email_sender import parse_recipients, render_campaign, send_html_email
from services.drive_images import embed_drive_images_in_data, fetch_drive_image_data_url
from services.url_utils import drive_image_link_error, extract_drive_file_id, is_drive_url, normalize_image_url
from services.form_state import (
    MAX_SIDEBAR_ITEMS,
    build_campaign_from_state,
    camp_key,
    export_state_to_draft,
    init_form_state,
    load_draft_into_state,
    sb_key,
)

st.set_page_config(
    page_title="Correos Comerciales — Danu",
    page_icon="📧",
    layout="wide",
)


def save_draft_and_keep_editing() -> str:
    draft = export_state_to_draft()
    result = save_draft_dict(draft)
    name = draft["name"]
    st.session_state["camp_last_saved"] = name
    st.session_state["camp_last_loaded"] = name
    # No tocar camp_selector aquí: el selectbox ya se renderizó en este run.
    st.session_state["camp_pending_selector"] = name
    return result.name if hasattr(result, "name") else str(result)


def campaign_select_options(campaigns: list[str]) -> list[str]:
    options = ["— Nueva —", *campaigns]
    for name in (
        st.session_state.get(camp_key("name"), "").strip(),
        st.session_state.get("camp_last_saved", "").strip(),
        st.session_state.get("camp_pending_selector", "").strip(),
        st.session_state.get("camp_selector", "").strip(),
    ):
        if name and name not in options:
            options.append(name)
    return options


def sync_campaign_selector() -> None:
    pending = st.session_state.pop("camp_pending_selector", None)
    if pending:
        st.session_state["camp_selector"] = pending


def load_selected_campaign() -> None:
    selected = st.session_state.get("camp_selector", "— Nueva —")
    if selected == "— Nueva —":
        return
    if selected == st.session_state.get("camp_last_loaded"):
        return
    try:
        draft = load_draft_dict(selected)
        load_draft_into_state(draft)
        st.session_state["camp_last_saved"] = selected
        st.session_state["camp_last_loaded"] = selected
        st.session_state.pop("camp_load_error", None)
    except (FileNotFoundError, ValueError, DriveStorageError) as exc:
        st.session_state["camp_load_error"] = str(exc)


def render_sidebar_fields() -> None:
    st.subheader("Sidebar — artículos relacionados")
    count = st.session_state["camp_sidebar_count"]
    b1, b2, _ = st.columns([1, 1, 2])
    with b1:
        if st.button("➕ Agregar artículo", disabled=count >= MAX_SIDEBAR_ITEMS):
            st.session_state["camp_sidebar_count"] = count + 1
            st.rerun()
    with b2:
        if st.button("➖ Quitar artículo", disabled=count <= 0):
            st.session_state["camp_sidebar_count"] = count - 1
            st.rerun()

    st.text_input("Título del sidebar", key=camp_key("sidebar_title"))

    for i in range(st.session_state["camp_sidebar_count"]):
        st.markdown(f"**Artículo {i + 1}**")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input(f"Título #{i + 1}", key=sb_key("title", i))
            st.text_input(f"URL #{i + 1}", key=sb_key("url", i))
        with c2:
            st.text_input(
                f"Imagen URL #{i + 1}",
                key=sb_key("image_url", i),
                help="Link directo o enlace de Google Drive (compartido públicamente).",
            )


def render_content_fields() -> None:
    st.subheader("Identificación")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Nombre interno de campaña *", key=camp_key("name"))
        st.text_input("Asunto del correo *", key=camp_key("subject"))
    with c2:
        st.text_input("Vista previa en bandeja *", key=camp_key("preheader"))
        st.text_input("Nombre de empresa", key=camp_key("company_name"))

    st.subheader("Header")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("URL del logo *", key=camp_key("logo_url"))
    with c2:
        st.text_input("Enlace del logo *", key=camp_key("logo_link"))

    st.subheader("Artículo principal")
    st.text_input("Etiqueta superior", key=camp_key("hero_label"))
    st.text_input("Titular *", key=camp_key("hero_title"))
    st.text_area("Cuerpo *", key=camp_key("hero_body"), height=120)
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(
            "URL imagen principal *",
            key=camp_key("hero_image"),
            help="Acepta links de Google Drive. La imagen debe estar compartida como 'Cualquier persona con el enlace'.",
        )
    with c2:
        st.text_input("URL del artículo *", key=camp_key("hero_url"))

    st.subheader("Botón CTA")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("Texto del botón", key=camp_key("cta_text"))
    with c2:
        st.text_input("URL del botón *", key=camp_key("cta_url"))
    with c3:
        st.text_input("Color del botón", key=camp_key("cta_color"))

    st.subheader("Footer legal")
    st.text_input("Texto legal", key=camp_key("legal_text"))
    st.text_input("Por qué recibió el correo", key=camp_key("subscription_reason"))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("URL privacidad", key=camp_key("privacy_url"))
    with c2:
        st.text_input("URL gestionar suscripción", key=camp_key("manage_subscription_url"))
    with c3:
        st.text_input("URL darse de baja", key=camp_key("unsubscribe_url"))
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Copyright", key=camp_key("copyright_text"))
    with c2:
        st.text_input("Dirección", key=camp_key("company_address"))

    st.subheader("Promo (opcional)")
    st.text_input("Texto promo", key=camp_key("promo_text"))


def main() -> None:
    apply_streamlit_secrets_to_environ()
    init_form_state()
    sync_campaign_selector()

    st.title("📧 Correos Comerciales — Danu Analítica")
    st.caption("Edita el contenido semanal sin tocar HTML. Redes sociales y contacto son fijos.")

    secrets_error = secrets_parse_error()
    if secrets_error:
        st.error(secrets_error)

    with st.sidebar:
        st.header("Campañas")

        drive_error = drive_config_error()
        if drive_error:
            st.error(f"Google Drive mal configurado: {drive_error}")

        try:
            campaigns = list_campaigns()
        except DriveStorageError as exc:
            st.error(str(exc))
            campaigns = []

        options = campaign_select_options(campaigns)

        if "camp_selector" not in st.session_state:
            last = st.session_state.get("camp_last_saved")
            st.session_state["camp_selector"] = last if last in options else "— Nueva —"

        selected = st.session_state.get("camp_selector", "— Nueva —")
        if selected != "— Nueva —" and selected != st.session_state.get("camp_last_loaded"):
            load_selected_campaign()

        selected = st.selectbox(
            "Cambiar campaña",
            options=options,
            key="camp_selector",
            on_change=load_selected_campaign,
        )

        load_error = st.session_state.pop("camp_load_error", None)
        if load_error:
            st.error(load_error)

        editing = st.session_state.get(camp_key("name"), "").strip()
        if editing and editing == st.session_state.get("camp_last_loaded"):
            st.caption(f"Editando: **{editing}**")
        elif selected != "— Nueva —":
            st.caption(f"Seleccionada: **{selected}** (carga automática al cambiar)")

        dup_name = st.text_input("Duplicar como", value=f"{date.today().isoformat()}-newsletter")
        if st.button("Duplicar", use_container_width=True, disabled=selected == "— Nueva —"):
            try:
                draft = duplicate_campaign(selected, dup_name.strip())
                load_draft_into_state(draft)
                st.session_state["camp_last_saved"] = draft["name"]
                st.session_state["camp_last_loaded"] = draft["name"]
                st.session_state["camp_pending_selector"] = draft["name"]
                st.rerun()
            except (FileNotFoundError, ValueError) as exc:
                st.error(str(exc))

        if st.button("💾 Guardar borrador", use_container_width=True, type="primary"):
            try:
                filename = save_draft_and_keep_editing()
                st.success(f"Guardado: {filename}")
                st.rerun()
            except (ValueError, DriveStorageError) as exc:
                st.error(str(exc))

        if st.session_state.get("camp_last_saved"):
            st.info(f"Última guardada: **{st.session_state['camp_last_saved']}**")

        st.caption("Tras *Guardar borrador* seguí editando: no hace falta recargar. El desplegable solo sirve para abrir otra campaña.")

        if storage_mode() == "drive":
            st.success("Borradores: Google Drive (organización)")
        else:
            st.warning("Borradores: carpeta local (configura Drive en Secrets)")

        st.divider()
        st.markdown("**Enlaces fijos (no editables)**")
        st.markdown(f"- [LinkedIn]({COMPANY_LINKEDIN})")
        st.markdown(f"- [Instagram]({COMPANY_INSTAGRAM})")
        st.markdown(f"- [Web]({COMPANY_WEBSITE})")

        st.divider()
        smtp_user = get_config("SMTP_USER") or get_config("EMISOR")
        if smtp_user:
            st.success(f"SMTP: {smtp_user}")
        else:
            st.warning("Configura .env")

    tab_content, tab_sidebar, tab_preview, tab_send = st.tabs(
        ["Contenido", "Sidebar", "Vista previa", "Enviar"]
    )

    with tab_content:
        render_content_fields()

    with tab_sidebar:
        render_sidebar_fields()

    with tab_preview:
        st.subheader("Vista previa del correo")

        image_fields = [
            ("Logo", camp_key("logo_url")),
            ("Imagen principal", camp_key("hero_image")),
        ]
        count = st.session_state.get("camp_sidebar_count", 2)
        for i in range(count):
            image_fields.append((f"Sidebar #{i + 1}", sb_key("image_url", i)))

        drive_warnings: list[str] = []
        for label, key in image_fields:
            raw = st.session_state.get(key, "").strip()
            if not raw:
                continue
            error = drive_image_link_error(raw)
            if error:
                drive_warnings.append(f"**{label}:** {error}")
            elif is_drive_url(raw):
                loaded = fetch_drive_image_data_url(extract_drive_file_id(raw) or "")
                status = "✅ cargada para preview" if loaded else "⚠️ revisa permisos (Cualquier persona con el enlace)"
                st.caption(f"{label} → `{normalize_image_url(raw)}` ({status})")

        for warning in drive_warnings:
            st.warning(warning, icon="⚠️")

        try:
            campaign = build_campaign_from_state(for_send=False)
            _, embed_warnings = embed_drive_images_in_data(campaign.model_dump(mode="python"))
            for warning in embed_warnings:
                st.warning(warning, icon="⚠️")
            html = render_campaign(campaign, embed_drive_images=True)
            st.components.v1.html(html, height=800, scrolling=True)
        except ValidationError as exc:
            st.error(format_validation_error(exc))
        except Exception as exc:
            st.error(f"No se pudo generar la vista previa: {exc}")

    with tab_send:
        st.subheader("Enviar correo")
        st.text_area(
            "Destinatarios * (separados por coma o salto de línea)",
            key=camp_key("recipients"),
            placeholder="cliente@empresa.com, otro@empresa.com",
            height=100,
        )
        st.caption("**Enviar prueba** y **Enviar campaña** usan la lista de destinatarios de arriba.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✉️ Enviar prueba", use_container_width=True):
                try:
                    campaign = build_campaign_from_state(for_send=True)
                    html = render_campaign(campaign)
                    recipients = parse_recipients(st.session_state[camp_key("recipients")])
                    send_html_email(campaign.subject, html, recipients)
                    save_draft_and_keep_editing()
                    st.success(f"Correo enviado a: {', '.join(recipients)}")
                except ValidationError as exc:
                    st.error(format_validation_error(exc))
                except (ValueError, DriveStorageError) as exc:
                    st.error(str(exc))
        with c2:
            if st.button("🚀 Enviar campaña", type="primary", use_container_width=True):
                try:
                    campaign = build_campaign_from_state(for_send=True)
                    html = render_campaign(campaign)
                    recipients = parse_recipients(st.session_state[camp_key("recipients")])
                    send_html_email(campaign.subject, html, recipients)
                    filename = save_draft_and_keep_editing()
                    st.success(f"Enviado a {len(recipients)} destinatario(s). Guardado: {filename}")
                except ValidationError as exc:
                    st.error(format_validation_error(exc))
                except (ValueError, DriveStorageError) as exc:
                    st.error(str(exc))


if __name__ == "__main__":
    main()
