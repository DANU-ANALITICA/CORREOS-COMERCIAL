# Correos Comerciales — Danu Analítica

Herramienta para que el equipo **comercial** arme y envíe newsletters semanales sin tocar HTML.

- **App en producción:** [danucomercial.streamlit.app](https://danucomercial.streamlit.app)
- **Guía para usuarios:** [Instructivo.MD](./Instructivo.MD) (también disponible en la pestaña *Guía* dentro de la app)

## Para el equipo comercial

Abrí la app → pestaña **Guía** → seguí el flujo semanal (duplicar, editar, preview, guardar, enviar).

## Para IT / desarrollo

- Entry point: `app_comercial.py`
- Borradores: Google Drive (`GOOGLE_DRIVE.md`)
- Config local: `.env` + `secrets/google-service-account.json`

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app_comercial.py
```
