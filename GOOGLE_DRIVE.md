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

```toml
GOOGLE_DRIVE_FOLDER_ID = "id-de-carpeta-en-unidad-compartida"

GOOGLE_SERVICE_ACCOUNT_JSON = """
{ ... contenido completo del JSON ... }
"""
```

---

## Imágenes desde Google Drive

Enlaces aceptados:
- `https://drive.google.com/file/d/ID/view?usp=sharing`
- `https://drive.google.com/open?id=ID`

Cada imagen debe estar en **"Cualquier persona con el enlace"**.

---

## Sin Drive configurado

Los borradores se guardan en `campaigns/` local.
