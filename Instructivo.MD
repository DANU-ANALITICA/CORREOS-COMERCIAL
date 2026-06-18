# Guía de uso — Correos Comerciales Danu

Esta guía es para el **equipo comercial**. No necesitás saber programar ni editar HTML.

**App:** [danucomercial.streamlit.app](https://danucomercial.streamlit.app)

---

## Qué hace esta herramienta

Armás el **contenido semanal** del newsletter (textos, imágenes, enlaces). El **diseño del correo es fijo**: colores, tipografías, iconos de redes y datos de contacto los define Danu — **no se editan desde acá**.

Los borradores se guardan en **Google Drive** (carpeta de la organización). Varios usuarios pueden retomar la misma campaña.

---

## Flujo semanal recomendado (~15 min)

1. **Duplicar** la campaña de la semana pasada (panel izquierdo).
2. **Editar** en las pestañas *Contenido* y *Sidebar*.
3. **Revisar** en *Vista previa*.
4. **Guardar borrador** (cuantas veces quieras).
5. **Enviar prueba** a tu correo (*Enviar*).
6. Cuando esté OK → **Enviar campaña** con la lista de destinatarios.

---

## Panel izquierdo — Campañas

| Acción | Cuándo usarla |
|--------|----------------|
| **Desplegable + Cargar** | Para **abrir otra campaña** guardada en Drive. Elegí el nombre y pulsa *Cargar*. |
| **Duplicar** | Para empezar la semana: copia la campaña anterior con un nombre nuevo (ej. `2026-06-25-newsletter`). |
| **Guardar borrador** | Guarda en Drive **sin salir** de lo que estás editando. Podés seguir cambiando campos después. |
| **— Nueva —** | Solo si querés arrancar desde cero (poco habitual). |

**Importante:** después de *Guardar borrador* **no hace falta** pulsar *Cargar* otra vez. Solo usá *Cargar* si cambiaste a **otra** campaña en el desplegable.

---

## Pestaña Contenido

### Identificación

| Campo | Qué poner |
|-------|-----------|
| **Nombre interno de campaña** | Identificador único, sin espacios raros. Ej: `2026-06-25-newsletter`. Es el nombre del archivo en Drive. |
| **Asunto del correo** | Lo que ven en la bandeja. Obligatorio para enviar. |
| **Vista previa en bandeja** | Texto corto bajo el asunto (preheader). Obligatorio para enviar. |
| **Nombre de empresa** | Por defecto: Danu Analítica. |

### Header (logo)

| Campo | Qué poner |
|-------|-----------|
| **URL del logo** | Link a la **imagen** del logo (JPG o PNG). Ver sección [Imágenes](#imágenes-en-google-drive). |
| **Enlace del logo** | Página a la que va al hacer clic (ej. `https://www.danuanalitica.com`). Debe empezar con `https://` **una sola vez**. |

### Artículo principal

| Campo | Qué poner |
|-------|-----------|
| **Etiqueta superior** | Texto chico arriba del titular. Ej: `Nuevo de Danu Analítica`. |
| **Titular** | Título grande del artículo. Obligatorio para enviar. |
| **Cuerpo** | Párrafo del artículo. Obligatorio para enviar. |
| **URL imagen principal** | Imagen grande del artículo (JPG/PNG en Drive). |
| **URL del artículo** | Link al leer más (web, blog, landing). |

### Botón CTA

| Campo | Qué poner |
|-------|-----------|
| **Texto del botón** | Ej: `Ver más`, `Conocé más`. |
| **URL del botón** | Destino del botón. Obligatorio para enviar. |
| **Color del botón** | Código hex. Por defecto azul Danu: `#2251ff`. |

### Footer legal

Completar según corresponda cada envío: texto legal, privacidad, suscripción, dirección, etc. Los enlaces de footer son opcionales salvo que legal los requiera.

---

## Pestaña Sidebar

Artículos secundarios en la columna derecha del correo.

- **Título del sidebar:** encabezado de la sección (ej. `También te puede interesar`).
- Por cada artículo: **título**, **URL de imagen** y **URL del artículo**.
- **Título obligatorio:** si un artículo no tiene título, **no aparece** en el correo aunque tenga imagen.
- Máximo **5 artículos** (*Agregar* / *Quitar artículo*).

---

## Pestaña Vista previa

Muestra cómo se verá el correo. Revisá:

- Logo e imagen principal
- Textos cortados o erróneos
- Botón y links

Si una imagen de Drive no se ve, revisá permisos (abajo). A veces el preview falla pero el **correo enviado sí se ve bien** — confirmá con *Enviar prueba*.

---

## Pestaña Enviar

1. Pegá los **destinatarios** (coma, punto y coma o un correo por línea).
2. **Enviar prueba** — manda a esa lista para revisar en Gmail/Outlook real.
3. **Enviar campaña** — envío definitivo (también guarda borrador).

Ambos botones usan **la misma lista** de destinatarios del cuadro de arriba.

Ejemplo de destinatarios:

```
cliente1@empresa.com, cliente2@empresa.com
otro@empresa.com
```

---

## Imágenes en Google Drive

### Formatos recomendados

| Formato | Uso |
|---------|-----|
| **PNG** | Logo (mejor si tiene fondo transparente) |
| **JPEG / JPG** | Fotos e imagen principal |
| **SVG** | Evitar — muchos clientes de correo no lo muestran |

### Cómo subir y compartir

1. Subí la imagen a Google Drive.
2. Clic derecho → **Compartir**.
3. **Acceso general** → **Cualquier persona con el enlace** → **Lector**.
4. Copiá el enlace del **archivo** (no de la carpeta).

Enlace válido (ejemplo):

```
https://drive.google.com/file/d/XXXXXXXX/view?usp=sharing
```

**No uses** enlaces de carpeta (`/drive/folders/...`).

### Dos campos distintos

- **URL del logo / URL imagen** → link de la **imagen** en Drive.
- **Enlace del logo / URL del artículo** → página web al hacer clic (danuanalitica.com, blog, etc.).

---

## Qué NO editar

- Código HTML ni plantillas.
- Iconos de LinkedIn, Instagram, web y contacto (son fijos).
- **Banner de Discovery Call** al final del correo (imagen + link al calendario).
- Configuración de correo (SMTP) ni credenciales de Drive — eso lo ve IT.

---

## Campos obligatorios para enviar

Si falta alguno, la app avisa antes de enviar:

- Asunto y vista previa en bandeja
- URL del logo y enlace del logo
- Titular, cuerpo, imagen principal y URL del artículo
- URL del botón CTA
- Al menos un destinatario

Para **guardar borrador** solo hace falta el **nombre interno** de campaña.

---

## Problemas frecuentes

| Problema | Solución |
|----------|----------|
| La imagen no se ve en preview | Compartir como *Cualquier persona con el enlace*; usar PNG/JPG; probar *Enviar prueba*. |
| Link de carpeta en vez de archivo | Abrí la imagen → *Obtener enlace* del archivo (`/file/d/...`). |
| Después de guardar “perdí” el borrador | No hace falta *Cargar* de nuevo; seguí editando. Solo *Cargar* si abrís **otra** campaña. |
| `https://www.https://...` | Corregí el enlace: una sola vez `https://` al inicio. |
| Sidebar vacío | Cada artículo necesita **título** además de la imagen. |
| Error al enviar | Revisá destinatarios sin espacios raros; pedí a IT si dice error SMTP. |
| Borradores: carpeta local (amarillo) | IT debe configurar Google Drive en la app en la nube. |

---

## Contacto

- **Contenido del correo:** equipo comercial.
- **App caída, correo no sale, Drive:** IT / quien administra Streamlit y Google Cloud.

---

*Última actualización: junio 2026*
