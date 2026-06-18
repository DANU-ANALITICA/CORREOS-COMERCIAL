# Instructivo — Correos Comerciales

Guía para el equipo de comercial. No necesitas editar HTML ni código.

## Instalación (solo la primera vez — pide ayuda a IT)

```bash
cd "/Users/luciaballi/Documents/Correos - Comercial DANU"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con el correo y la App Password de Gmail (IT te la genera).

## Abrir la aplicación

```bash
cd "/Users/luciaballi/Documents/Correos - Comercial DANU"
source venv/bin/activate
streamlit run app_comercial.py
```

Se abrirá en el navegador.

## Flujo semanal (~15 minutos)

1. **Cargar campaña anterior** — en el panel izquierdo, elige la campaña de la semana pasada y pulsa *Duplicar*.
2. **Editar contenido** — pestaña *Contenido*: asunto, titular, imagen, botón, footer.
3. **Sidebar** — pestaña *Sidebar*: agrega o quita artículos relacionados (máx. 5).
4. **Vista previa** — pestaña *Vista previa*: revisa cómo se verá el correo.
5. **Guardar** — pulsa *Guardar campaña* antes de enviar.
6. **Enviar prueba** — pestaña *Enviar*: envía a tu correo para revisar en la bandeja real.
7. **Enviar campaña** — pega la lista de destinatarios y pulsa *Enviar campaña*.

## Campos obligatorios

- Asunto del correo
- Vista previa en bandeja (preheader)
- URL del logo y enlace
- Titular, cuerpo, imagen y URL del artículo principal
- URL del botón CTA

## Imágenes

Usa URLs públicas (`https://...`). No uses archivos de tu computadora.
Sube las imágenes a tu sitio web, Google Drive (enlace público) o similar.

## Destinatarios

En la pestaña *Enviar*, escribe correos separados por coma o uno por línea:

```
cliente1@empresa.com, cliente2@empresa.com
```

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| Faltan credenciales SMTP | Pide a IT que configure el archivo `.env` |
| URL inválida | Verifica que el enlace empiece con `https://` |
| Correos inválidos | Revisa que no haya espacios ni typos en los destinatarios |
| No se pudo autenticar | Usa App Password de Google, no la contraseña normal |

## Estructura del proyecto

- `app_comercial.py` — aplicación que usas tú
- `campaigns/` — campañas guardadas (una por semana)
- `templates/` — diseño fijo del correo (no tocar)
