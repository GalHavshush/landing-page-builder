"""Fixed UI strings used by generated sites (button labels etc.), per language.

Anything a user can type lives in the document; this is only text the generator itself emits.
Unknown languages fall back to English.
"""

KEYS = (
    "skip",
    "learn_more",
    "contact",
    "hours",
    "closed",
    "menu",
    "not_found_title",
    "not_found_text",
    "back_home",
)

STRINGS = {
    "en": (
        "Skip to content",
        "Learn more",
        "Contact",
        "Hours",
        "Closed",
        "Menu",
        "Page not found",
        "The page you are looking for does not exist.",
        "Back to home",
    ),
    "he": (
        "דלג לתוכן",
        "למידע נוסף",
        "צור קשר",
        "שעות פעילות",
        "סגור",
        "תפריט",
        "הדף לא נמצא",
        "הדף שחיפשת אינו קיים.",
        "חזרה לדף הבית",
    ),
    "es": (
        "Saltar al contenido",
        "Más información",
        "Contacto",
        "Horario",
        "Cerrado",
        "Menú",
        "Página no encontrada",
        "La página que buscas no existe.",
        "Volver al inicio",
    ),
    "de": (
        "Zum Inhalt springen",
        "Mehr erfahren",
        "Kontakt",
        "Öffnungszeiten",
        "Geschlossen",
        "Menü",
        "Seite nicht gefunden",
        "Die gesuchte Seite existiert nicht.",
        "Zur Startseite",
    ),
    "fr": (
        "Aller au contenu",
        "En savoir plus",
        "Contact",
        "Horaires",
        "Fermé",
        "Menu",
        "Page introuvable",
        "La page que vous cherchez n'existe pas.",
        "Retour à l'accueil",
    ),
    "ar": (
        "انتقل إلى المحتوى",
        "اعرف المزيد",
        "اتصل بنا",
        "ساعات العمل",
        "مغلق",
        "القائمة",
        "الصفحة غير موجودة",
        "الصفحة التي تبحث عنها غير موجودة.",
        "العودة إلى الرئيسية",
    ),
}
_TABLES = {lang: dict(zip(KEYS, values, strict=True)) for lang, values in STRINGS.items()}


def get(lang: str, key: str) -> str:
    table = _TABLES.get(lang) or _TABLES.get(lang.split("-")[0]) or _TABLES["en"]
    return table[key]


LANGUAGE_NAMES = {
    "en": "English",
    "he": "עברית",
    "ar": "العربية",
    "es": "Español",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
    "pl": "Polski",
    "ru": "Русский",
    "tr": "Türkçe",
    "ja": "日本語",
    "zh": "中文",
    "fa": "فارسی",
}


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code) or LANGUAGE_NAMES.get(code.split("-")[0]) or code
