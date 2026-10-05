"""Fixed UI strings used by generated sites (button labels etc.), per language.

Anything a user can type lives in the document; this is only text the generator itself emits.
Unknown languages fall back to English.
"""

STRINGS = {
    "en": {
        "skip": "Skip to content",
        "learn_more": "Learn more",
        "contact": "Contact",
        "hours": "Hours",
        "closed": "Closed",
        "menu": "Menu",
    },
    "he": {
        "skip": "דלג לתוכן",
        "learn_more": "למידע נוסף",
        "contact": "צור קשר",
        "hours": "שעות פעילות",
        "closed": "סגור",
        "menu": "תפריט",
    },
    "es": {
        "skip": "Saltar al contenido",
        "learn_more": "Más información",
        "contact": "Contacto",
        "hours": "Horario",
        "closed": "Cerrado",
        "menu": "Menú",
    },
    "de": {
        "skip": "Zum Inhalt springen",
        "learn_more": "Mehr erfahren",
        "contact": "Kontakt",
        "hours": "Öffnungszeiten",
        "closed": "Geschlossen",
        "menu": "Menü",
    },
    "fr": {
        "skip": "Aller au contenu",
        "learn_more": "En savoir plus",
        "contact": "Contact",
        "hours": "Horaires",
        "closed": "Fermé",
        "menu": "Menu",
    },
    "ar": {
        "skip": "انتقل إلى المحتوى",
        "learn_more": "اعرف المزيد",
        "contact": "اتصل بنا",
        "hours": "ساعات العمل",
        "closed": "مغلق",
        "menu": "القائمة",
    },
}


def get(lang: str, key: str) -> str:
    table = STRINGS.get(lang) or STRINGS.get(lang.split("-")[0]) or STRINGS["en"]
    return table.get(key) or STRINGS["en"][key]
