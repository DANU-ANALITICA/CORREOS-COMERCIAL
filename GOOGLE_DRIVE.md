# Configurar Google Drive para borradores

Los borradores (`.yml`) se guardan en **Google Drive**, no en GitHub ni en el servidor de Streamlit.

## IMPORTANTE: usar Unidad compartida (no "Mi unidad")

Las **service accounts no tienen espacio** en "Mi unidad" personal.
Si compartes una carpeta normal con el email de la service account, verás este error:

> Service Accounts do not have storage quota

**Solución:** la carpeta debe estar dentro de una **Unidad compartida** de Google Workspace.

---

## 1. Crear carpeta en una Unidad compartida

1. Abre [Google Drive](https://drive.google.com)
2. Menú izquierdo → **Unidades compartidas** (Shared drives)
3. Usa una existente de Danu o crea una, ej: `Danu — Comercial`
4. Clic en la unidad → **Administrar miembros**
5. Agrega como **Administrador de contenido**:
   ```
   correos-comercial-drive-882@ai-labs-478922.iam.gserviceaccount.com
   ```
6. Dentro de la unidad, crea la carpeta: `Correos Comercial — Borradores`
7. Copia el **ID** de la URL de esa carpeta:
   ```
   https://drive.google.com/drive/folders/ESTE_ES_EL_ID
   ```
8. Actualiza `GOOGLE_DRIVE_FOLDER_ID` en `.env` y Streamlit Secrets

---

## 2. Service Account en Google Cloud

1. [Google Cloud Console](https://console.cloud.google.com) → proyecto `ai-labs-478922`
2. **APIs & Services → Library** → activa **Google Drive API**
3. **IAM → Service Accounts** → descarga JSON key

---

## 3. Configuración local (.env)

```env
GOOGLE_DRIVE_FOLDER_ID=id-de-carpeta-en-unidad-compartida
GOOGLE_SERVICE_ACCOUNT_FILE=/ruta/a/secrets/google-service-account.json
```

---

## 4. Streamlit Cloud (Secrets)

**Formato recomendado** — pega cada campo del JSON como sección TOML (evita errores con la clave privada):

```toml
GOOGLE_DRIVE_FOLDER_ID = "1wgRFabB1zukOG56C2Z_QJ-PyEaeybD6r"

[google_service_account]
type = "service_account"
project_id = "ai-labs-478922"
private_key_id = "..."
private_key = """
-----BEGIN PRIVATE KEY-----
(lineas de la clave tal cual vienen en el JSON)
-----END PRIVATE KEY-----
"""
client_email = "correos-comercial-drive-882@ai-labs-478922.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

Copia los valores **exactos** del archivo `.json` descargado de Google Cloud.

Alternativa (más propensa a error): una sola variable con el JSON completo en una línea, sin saltos de línea dentro del string.

---

## Imágenes desde Google Drive

1. Sube la imagen a Drive (JPG o PNG).
2. Clic derecho → **Compartir** → **Cualquier persona con el enlace** → **Lector**.
3. Copia el enlace del **archivo** (no de la carpeta).

Enlaces válidos:
- `https://drive.google.com/file/d/ID/view?usp=sharing`
- `https://drive.google.com/open?id=ID`

**No uses** enlaces de carpeta (`/drive/folders/...`) — esos no son imágenes.

Si la imagen no se ve en la vista previa:
- Verifica que sea enlace de **archivo**, no de carpeta.
- Verifica permisos: *Cualquier persona con el enlace*.
- Algunos navegadores bloquean imágenes de Drive en iframes; el correo enviado por SMTP puede verse bien aunque el preview falle.

---

## Sin Drive configurado

Los borradores se guardan en `campaigns/` local.
