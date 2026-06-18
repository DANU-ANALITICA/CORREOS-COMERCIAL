"""Enlaces e iconos fijos de Danu Analítica — no editables desde la app."""

from services.url_utils import normalize_image_url

COMPANY_NAME = "Danu Analítica"
COMPANY_WEBSITE = "https://www.danuanalitica.com/#inicio"
COMPANY_CONTACT = "https://www.danuanalitica.com/#contacto"
COMPANY_LINKEDIN = "https://www.linkedin.com/company/danuanalitica/posts/?feedView=all"
COMPANY_INSTAGRAM = "https://www.instagram.com/danuanalitica"

FOOTER_BANNER_URL = (
    "https://drive.google.com/file/d/12SuaUZxqaxrKpPELP8Przbavd7VQslRu/view?usp=sharing"
)
FOOTER_BANNER_LINK = "https://calendar.app.google/hfkx5T4nMnCsaxUn6"

# Iconos públicos compatibles con clientes de correo
ICON_LINKEDIN = "https://img.icons8.com/ios-filled/50/0077B5/linkedin.png"
ICON_INSTAGRAM = "https://img.icons8.com/ios-filled/50/E4405F/instagram-new.png"
ICON_WEBSITE = "https://img.icons8.com/ios-filled/50/003366/home.png"
ICON_CONTACT = "https://img.icons8.com/ios-filled/50/003366/new-post.png"

BRAND_CONTEXT = {
    "company_linkedin": COMPANY_LINKEDIN,
    "company_instagram": COMPANY_INSTAGRAM,
    "company_website": COMPANY_WEBSITE,
    "company_contact": COMPANY_CONTACT,
    "icon_linkedin": ICON_LINKEDIN,
    "icon_instagram": ICON_INSTAGRAM,
    "icon_website": ICON_WEBSITE,
    "icon_contact": ICON_CONTACT,
    "footer_banner_url": normalize_image_url(FOOTER_BANNER_URL),
    "footer_banner_link": FOOTER_BANNER_LINK,
}
