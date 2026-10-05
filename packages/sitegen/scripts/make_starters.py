"""Generate the industry starters in sitegen/starters/. Run: uv run python scripts/make_starters.py

Each starter is art-directed to look good without photos (type, colour, rhythm), and lists the
photo slots the owner should fill. The output is plain JSON, validated against the schema.
"""

import json
from pathlib import Path

from sitegen.schema import SiteDocument

OUT = Path(__file__).parent.parent / "sitegen" / "starters"


def link(page=None, url=None):
    return {"page": page, "url": url, "asset": None}


def btn(label, page=None, url=None, style="primary"):
    return {"label": label, "href": link(page, url), "style": style}


def sec(sid, type_, variant, props, bg="default", spacing="normal", align="start"):
    return {
        "id": sid,
        "type": type_,
        "variant": variant,
        "i18n": {},
        "style": {"background": bg, "spacing": spacing, "align": align},
        "props": props,
    }


def page(pid, slug, title, desc, sections):
    return {
        "id": pid,
        "slug": slug,
        "title": title,
        "i18n": {},
        "sections": sections,
        "seo": {"title": None, "description": desc, "social_image": None, "noindex": False},
    }


def hours(*rows):
    return [
        {"label": r[0], "closed": True}
        if len(r) == 1
        else {"label": r[0], "open": r[1], "close": r[2]}
        for r in rows
    ]


def make(slug, name, tagline, theme, business, pages, nav, header=None, footer_style="columns"):
    site = {
        "name": name,
        "tagline": tagline,
        "default_language": "en",
        "languages": ["en"],
        "base_url": "",
        "business": business,
        "seo": {"title_template": "{page} | {site}", "default_description": tagline},
        "nav": [{"label": lbl, "page": pid, "labels": {}} for lbl, pid in nav],
        "footer": {"text": "", "show_business_info": True, "style": footer_style},
    }
    if header:
        site["header"] = header
    doc = {
        "schema_version": 1,
        "site": site,
        "pages": pages,
        "theme": {
            "template": slug,
            "radius": "md",
            "button_style": "solid",
            "spacing": "normal",
            **theme,
        },
    }
    SiteDocument.model_validate(doc)  # fail loudly on schema drift
    (OUT / f"{slug}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def pal(primary, accent, background, surface, text):
    return {
        "primary": primary,
        "accent": accent,
        "background": background,
        "surface": surface,
        "text": text,
    }


def contact_page(pid, intro, heading="Get in touch"):
    return page(
        pid,
        "contact",
        "Contact",
        f"Contact us. {intro}",
        [
            sec(
                "sec_ct_form",
                "contact",
                "split",
                {
                    "heading": heading,
                    "text": intro,
                    "show_business_info": True,
                    "show_form": True,
                    "submit_label": "Send",
                    "form_endpoint": "",
                },
            ),
            sec(
                "sec_ct_hours",
                "hours",
                "split",
                {
                    "heading": "Opening hours",
                    "subheading": "",
                    "note": "",
                    "show_contact": False,
                    "show_address": True,
                },
                bg="alt",
            ),
            sec(
                "sec_ct_map",
                "map",
                "embedded",
                {"heading": "Find us", "subheading": "", "query": "", "height": "medium"},
            ),
        ],
    )


# 1. Restaurant ---------------------------------------------------------------------------
make(
    "restaurant",
    "Olive & Ember",
    "Wood-fired cooking, seasonal and local.",
    {
        "palette": pal("#8C2F1B", "#C9A25E", "#FBF7F0", "#F1E9DB", "#241913"),
        "fonts": {"heading": "fraunces", "body": "dm-sans"},
        "radius": "sm",
        "card_style": "flat",
        "image_style": "square",
        "heading_style": "tight",
    },
    {
        "phone": "+1 555 0142",
        "email": "table@example.com",
        "address": "8 Harbour Row, Portland",
        "hours": hours(
            ("Tue-Thu", "17:00", "22:00"),
            ("Fri-Sat", "17:00", "23:30"),
            ("Sun", "12:00", "21:00"),
            ("Mon",),
        ),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "A seasonal wood-fired kitchen. Book a table.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "banner",
                    {
                        "eyebrow": "Wood-fired kitchen",
                        "heading": "Dinner, cooked over open flame.",
                        "subheading": "A short seasonal menu built around what the farms bring us that week.",
                        "image": None,
                        "buttons": [
                            btn("Book a table", "pg_visit"),
                            btn("See the menu", "pg_menu", style="outline"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    bg="dark",
                    spacing="spacious",
                ),
                sec(
                    "sec_h_feat",
                    "features",
                    "numbered",
                    {
                        "heading": "How we cook",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "icon": "leaf",
                                "title": "Local first",
                                "text": "Most of our produce comes from farms within fifty miles.",
                            },
                            {
                                "icon": "bolt",
                                "title": "Real fire",
                                "text": "Everything touches the oak-fired grill or the stone oven.",
                            },
                            {
                                "icon": "heart",
                                "title": "Made in-house",
                                "text": "Bread, butter, ferments and sauces, every day.",
                            },
                        ],
                    },
                ),
                sec(
                    "sec_h_quote",
                    "testimonials",
                    "quote",
                    {
                        "heading": "",
                        "subheading": "",
                        "items": [
                            {
                                "quote": "The best meal we had all year. Simple, confident cooking.",
                                "author": "Maya R.",
                                "role": "Regular",
                                "avatar": None,
                            }
                        ],
                    },
                    bg="alt",
                    align="center",
                ),
                sec(
                    "sec_h_cta",
                    "cta",
                    "banner",
                    {
                        "heading": "Tables fill up on weekends",
                        "text": "Book ahead for Friday and Saturday.",
                        "buttons": [btn("Reserve a table", "pg_visit", style="primary")],
                    },
                    bg="primary",
                    align="center",
                ),
            ],
        ),
        page(
            "pg_menu",
            "menu",
            "Menu",
            "Our current dinner menu.",
            [
                sec(
                    "sec_m_start",
                    "services",
                    "list",
                    {
                        "heading": "To start",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Charred flatbread",
                                "description": "Whipped ricotta, honey, thyme.",
                                "price": "$9",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Smoked beet",
                                "description": "Goat curd, walnut, sorrel.",
                                "price": "$12",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Grilled prawns",
                                "description": "Garlic butter, lemon, chilli.",
                                "price": "$16",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                ),
                sec(
                    "sec_m_main",
                    "services",
                    "list",
                    {
                        "heading": "To follow",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Whole fish",
                                "description": "Today's catch, fennel, salsa verde.",
                                "price": "$34",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Oak-grilled ribeye",
                                "description": "Bone marrow butter, watercress.",
                                "price": "$42",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Roasted cauliflower",
                                "description": "Tahini, pomegranate, dukkah.",
                                "price": "$22",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_m_faq",
                    "faq",
                    "accordion",
                    {
                        "heading": "Good to know",
                        "subheading": "",
                        "items": [
                            {
                                "question": "Do you cater for allergies?",
                                "answer": "Yes. Tell us when you book and the kitchen will plan around you.",
                            },
                            {
                                "question": "Can I bring a large group?",
                                "answer": "We seat parties up to twelve. For more, get in touch.",
                            },
                        ],
                    },
                ),
            ],
        ),
        page(
            "pg_visit",
            "visit",
            "Visit",
            "Book a table and find us.",
            [
                sec(
                    "sec_v_contact",
                    "contact",
                    "split",
                    {
                        "heading": "Book a table",
                        "text": "Tell us the date, time and party size and we will confirm within the day.",
                        "show_business_info": True,
                        "show_form": True,
                        "submit_label": "Request a table",
                        "form_endpoint": "",
                    },
                ),
                sec(
                    "sec_v_hours",
                    "hours",
                    "card",
                    {
                        "heading": "Opening hours",
                        "subheading": "",
                        "note": "Kitchen closes thirty minutes before.",
                        "show_contact": False,
                        "show_address": True,
                    },
                    bg="alt",
                ),
                sec(
                    "sec_v_map",
                    "map",
                    "embedded",
                    {"heading": "Find us", "subheading": "", "query": "", "height": "medium"},
                ),
            ],
        ),
    ],
    [("Home", "pg_home"), ("Menu", "pg_menu"), ("Visit", "pg_visit")],
    header={"style": "centered", "sticky": True, "transparent": False},
    footer_style="centered",
)

# 2. Salon --------------------------------------------------------------------------------
make(
    "salon",
    "Mara Hair Studio",
    "Cuts, colour and care in a calm studio.",
    {
        "palette": pal("#3D3A36", "#C98B6B", "#FFFFFF", "#F6F1EC", "#26231F"),
        "fonts": {"heading": "source-serif", "body": "manrope"},
        "radius": "full",
        "button_style": "outline",
        "card_style": "flat",
        "image_style": "soft",
        "heading_style": "light",
        "spacing": "spacious",
    },
    {
        "phone": "+1 555 0177",
        "email": "book@example.com",
        "address": "21 Elm Street, Austin",
        "hours": hours(("Tue-Fri", "10:00", "19:00"), ("Sat", "09:00", "16:00"), ("Sun-Mon",)),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "A calm hair studio. Book your appointment.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "centered",
                    {
                        "eyebrow": "Hair studio",
                        "heading": "Hair that feels like you, only better.",
                        "subheading": "Considered cuts and colour, in an unhurried studio.",
                        "image": None,
                        "buttons": [btn("Book now", "pg_contact")],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    bg="alt",
                    spacing="spacious",
                    align="center",
                ),
                sec(
                    "sec_h_svc",
                    "services",
                    "list",
                    {
                        "heading": "Services",
                        "subheading": "Prices are a guide. We confirm after a short consultation.",
                        "items": [
                            {
                                "title": "Cut & finish",
                                "description": "Consultation, wash, cut and blow-dry.",
                                "price": "from $65",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Colour",
                                "description": "Root touch-up, all-over colour or gloss.",
                                "price": "from $90",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Balayage",
                                "description": "Hand-painted, soft and low maintenance.",
                                "price": "from $180",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Treatments",
                                "description": "Deep conditioning and scalp care.",
                                "price": "from $35",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                ),
                sec(
                    "sec_h_team",
                    "team",
                    "round",
                    {
                        "heading": "Your stylists",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "name": "Mara Ellis",
                                "role": "Founder, colour specialist",
                                "bio": "",
                                "photo": None,
                            },
                            {
                                "name": "Jonah Reyes",
                                "role": "Senior stylist",
                                "bio": "",
                                "photo": None,
                            },
                            {"name": "Ines Park", "role": "Stylist", "bio": "", "photo": None},
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_q",
                    "testimonials",
                    "cards",
                    {
                        "heading": "Kind words",
                        "subheading": "",
                        "items": [
                            {
                                "quote": "First time I have left a salon feeling exactly as I imagined.",
                                "author": "Claire B.",
                                "role": "",
                                "avatar": None,
                            },
                            {
                                "quote": "Calm, thoughtful and brilliant at colour.",
                                "author": "Dana W.",
                                "role": "",
                                "avatar": None,
                            },
                        ],
                    },
                ),
            ],
        ),
        page(
            "pg_prices",
            "prices",
            "Prices",
            "Full price list.",
            [
                sec(
                    "sec_p_price",
                    "pricing",
                    "cards",
                    {
                        "heading": "Membership",
                        "subheading": "",
                        "plans": [
                            {
                                "name": "Trim club",
                                "price": "$45",
                                "period": "every 8 weeks",
                                "description": "",
                                "features": "Dry trim\nPriority booking",
                                "highlighted": False,
                                "cta_label": "Book",
                                "cta_link": link("pg_contact"),
                            },
                            {
                                "name": "Colour club",
                                "price": "$110",
                                "period": "every 8 weeks",
                                "description": "",
                                "features": "Colour refresh\nGloss and finish\nPriority booking",
                                "highlighted": True,
                                "cta_label": "Book",
                                "cta_link": link("pg_contact"),
                            },
                        ],
                    },
                ),
                sec(
                    "sec_p_faq",
                    "faq",
                    "accordion",
                    {
                        "heading": "Questions",
                        "subheading": "",
                        "items": [
                            {
                                "question": "Do I need a patch test?",
                                "answer": "For colour, yes, at least 48 hours before your first appointment.",
                            },
                            {
                                "question": "What is your cancellation policy?",
                                "answer": "Please give us 24 hours notice.",
                            },
                        ],
                    },
                    bg="alt",
                ),
            ],
        ),
        contact_page(
            "pg_contact", "Book an appointment or ask us anything.", "Book an appointment"
        ),
    ],
    [("Home", "pg_home"), ("Prices", "pg_prices"), ("Book", "pg_contact")],
    header={"style": "split", "sticky": True, "transparent": False},
    footer_style="centered",
)

# 3. Trades -------------------------------------------------------------------------------
make(
    "trades",
    "Hartley Plumbing & Heating",
    "Fast, honest plumbing and heating repairs.",
    {
        "palette": pal("#0B5FA5", "#F5A524", "#FFFFFF", "#EEF3F8", "#0F1B2A"),
        "fonts": {"heading": "rubik", "body": "dm-sans"},
        "radius": "md",
        "card_style": "elevated",
        "heading_style": "tight",
    },
    {
        "phone": "+1 555 0110",
        "email": "jobs@example.com",
        "address": "Serving Dayton and surrounding areas",
        "hours": hours(("Mon-Fri", "07:30", "18:00"), ("Sat", "08:00", "13:00"), ("Sun",)),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "Local plumbers and heating engineers. Call for a quick quote.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "split",
                    {
                        "eyebrow": "Local and insured",
                        "heading": "Plumbing problems fixed properly, the first time.",
                        "subheading": "Leaks, boilers, bathrooms and emergencies. Upfront prices and a clear arrival window.",
                        "image": None,
                        "buttons": [
                            btn("Call 555 0110", url="tel:+15550110"),
                            btn("Get a quote", "pg_contact", style="outline"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    spacing="spacious",
                ),
                sec(
                    "sec_h_stats",
                    "stats",
                    "cards",
                    {
                        "heading": "",
                        "subheading": "",
                        "items": [
                            {"value": "15+", "label": "Years in business"},
                            {"value": "4,000", "label": "Jobs completed"},
                            {"value": "60 min", "label": "Emergency response"},
                            {"value": "4.9", "label": "Average review"},
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_svc",
                    "services",
                    "cards",
                    {
                        "heading": "What we do",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Emergency repairs",
                                "description": "Burst pipes, leaks and blocked drains, day or night.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Boilers & heating",
                                "description": "Servicing, repairs and full replacements.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Bathrooms",
                                "description": "Design, supply and installation, start to finish.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                ),
                sec(
                    "sec_h_steps",
                    "steps",
                    "horizontal",
                    {
                        "heading": "How it works",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Call or message",
                                "text": "Tell us what is wrong. We reply fast.",
                            },
                            {
                                "title": "Fixed quote",
                                "text": "A clear price before any work starts.",
                            },
                            {"title": "Job done", "text": "We tidy up and check everything works."},
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_cta",
                    "cta",
                    "banner",
                    {
                        "heading": "Need someone today?",
                        "text": "Call us now. We will give you an honest answer on the phone.",
                        "buttons": [btn("Call 555 0110", url="tel:+15550110", style="primary")],
                    },
                    bg="primary",
                    align="center",
                ),
            ],
        ),
        page(
            "pg_services",
            "services",
            "Services",
            "Plumbing and heating services.",
            [
                sec(
                    "sec_s_list",
                    "services",
                    "alternating",
                    {
                        "heading": "Services",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Leaks and repairs",
                                "description": "We find the cause, not just the symptom.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Heating and boilers",
                                "description": "Gas Safe registered engineers.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Bathroom installs",
                                "description": "One team from rip-out to final sealant.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                ),
                sec(
                    "sec_s_faq",
                    "faq",
                    "split",
                    {
                        "heading": "Common questions",
                        "subheading": "",
                        "items": [
                            {
                                "question": "Do you charge a call-out fee?",
                                "answer": "No. Quotes are free and the price you are given is the price you pay.",
                            },
                            {
                                "question": "Are you insured?",
                                "answer": "Yes, fully insured and every job is guaranteed.",
                            },
                        ],
                    },
                    bg="alt",
                ),
            ],
        ),
        contact_page(
            "pg_contact", "Describe the job and we will come back with a price.", "Get a free quote"
        ),
    ],
    [("Home", "pg_home"), ("Services", "pg_services"), ("Contact", "pg_contact")],
)

# 4. Clinic -------------------------------------------------------------------------------
make(
    "clinic",
    "Riverside Family Clinic",
    "Clear, caring healthcare for the whole family.",
    {
        "palette": pal("#0E7490", "#F59E0B", "#FFFFFF", "#F0F7F9", "#12232B"),
        "fonts": {"heading": "manrope", "body": "manrope"},
        "radius": "lg",
        "card_style": "outlined",
        "image_style": "rounded",
    },
    {
        "phone": "+1 555 0190",
        "email": "reception@example.com",
        "address": "40 Riverside Drive, Madison",
        "hours": hours(("Mon-Fri", "08:00", "18:00"), ("Sat", "09:00", "13:00"), ("Sun",)),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "Family healthcare in Madison. New patients welcome.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "split",
                    {
                        "eyebrow": "New patients welcome",
                        "heading": "Healthcare that listens.",
                        "subheading": "Unhurried appointments with doctors who know your family.",
                        "image": None,
                        "buttons": [
                            btn("Book an appointment", "pg_contact"),
                            btn("Our services", "pg_services", style="outline"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    bg="alt",
                    spacing="spacious",
                ),
                sec(
                    "sec_h_feat",
                    "features",
                    "cards",
                    {
                        "heading": "Why families choose us",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "icon": "clock",
                                "title": "Longer visits",
                                "text": "Twenty-minute appointments as standard.",
                            },
                            {
                                "icon": "heart",
                                "title": "Continuity of care",
                                "text": "See the same doctor each time.",
                            },
                            {
                                "icon": "check",
                                "title": "Same-week access",
                                "text": "Urgent concerns seen within days.",
                            },
                        ],
                    },
                ),
                sec(
                    "sec_h_team",
                    "team",
                    "cards",
                    {
                        "heading": "Meet the doctors",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "name": "Dr. Amira Hassan",
                                "role": "General practitioner",
                                "bio": "Special interest in women's health.",
                                "photo": None,
                            },
                            {
                                "name": "Dr. Tom Whitfield",
                                "role": "General practitioner",
                                "bio": "Paediatrics and family medicine.",
                                "photo": None,
                            },
                            {
                                "name": "Nina Cole, RN",
                                "role": "Practice nurse",
                                "bio": "Vaccinations and chronic care.",
                                "photo": None,
                            },
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_hours",
                    "hours",
                    "split",
                    {
                        "heading": "When we are open",
                        "subheading": "",
                        "note": "For emergencies call 911.",
                        "show_contact": True,
                        "show_address": True,
                    },
                ),
            ],
        ),
        page(
            "pg_services",
            "services",
            "Services",
            "Our clinical services.",
            [
                sec(
                    "sec_s_svc",
                    "services",
                    "cards",
                    {
                        "heading": "Our services",
                        "subheading": "",
                        "items": [
                            {
                                "title": "General care",
                                "description": "Checkups, illness and long-term conditions.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Vaccinations",
                                "description": "Childhood, travel and seasonal vaccines.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Women's health",
                                "description": "Screening, contraception and advice.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                ),
                sec(
                    "sec_s_faq",
                    "faq",
                    "accordion",
                    {
                        "heading": "New patient FAQ",
                        "subheading": "",
                        "items": [
                            {
                                "question": "How do I register?",
                                "answer": "Fill in the contact form or call reception. We will do the rest.",
                            },
                            {
                                "question": "Do you accept insurance?",
                                "answer": "We accept most major plans. Call us to check yours.",
                            },
                        ],
                    },
                    bg="alt",
                ),
            ],
        ),
        contact_page(
            "pg_contact", "Book an appointment or register as a new patient.", "Book an appointment"
        ),
    ],
    [("Home", "pg_home"), ("Services", "pg_services"), ("Contact", "pg_contact")],
)

# 5. Photographer -------------------------------------------------------------------------
make(
    "photographer",
    "Elise Hart Photography",
    "Natural, unposed photographs of people and places.",
    {
        "palette": pal("#111111", "#B08968", "#FAFAF8", "#EFEDE8", "#111111"),
        "fonts": {"heading": "source-serif", "body": "dm-sans"},
        "radius": "none",
        "button_style": "outline",
        "card_style": "flat",
        "image_style": "square",
        "heading_style": "light",
        "spacing": "spacious",
    },
    {
        "phone": "",
        "email": "hello@example.com",
        "address": "Based in Brooklyn, travelling worldwide",
        "hours": [],
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "Portrait and wedding photography.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "centered",
                    {
                        "eyebrow": "Portrait & wedding photography",
                        "heading": "Honest pictures of people being themselves.",
                        "subheading": "",
                        "image": None,
                        "buttons": [
                            btn("View portfolio", "pg_work", style="link"),
                            btn("Enquire", "pg_contact"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    spacing="spacious",
                    align="center",
                ),
                sec(
                    "sec_h_gal",
                    "gallery",
                    "mosaic",
                    {"heading": "", "subheading": "", "items": [], "columns": 3},
                ),
                sec(
                    "sec_h_q",
                    "testimonials",
                    "quote",
                    {
                        "heading": "",
                        "subheading": "",
                        "items": [
                            {
                                "quote": "Elise made us forget the camera was there. The pictures are us.",
                                "author": "Hannah & Luis",
                                "role": "Wedding, Hudson Valley",
                                "avatar": None,
                            }
                        ],
                    },
                    bg="alt",
                    align="center",
                ),
            ],
        ),
        page(
            "pg_work",
            "work",
            "Portfolio",
            "Selected work.",
            [
                sec(
                    "sec_w_gal",
                    "gallery",
                    "masonry",
                    {"heading": "Selected work", "subheading": "", "items": [], "columns": 3},
                ),
            ],
        ),
        page(
            "pg_about",
            "about",
            "About",
            "About Elise.",
            [
                sec(
                    "sec_a_text",
                    "text",
                    "split",
                    {
                        "heading": "About",
                        "body": "I have photographed weddings and families for twelve years. I work quietly, in natural light, and I would rather catch a real moment than set up a perfect one.\n\nI take a limited number of commissions each year so every project gets full attention.",
                    },
                ),
                sec(
                    "sec_a_steps",
                    "steps",
                    "timeline",
                    {
                        "heading": "Working together",
                        "subheading": "",
                        "items": [
                            {"title": "Say hello", "text": "Tell me about your day or project."},
                            {
                                "title": "Plan",
                                "text": "We talk through timing, places and what matters most.",
                            },
                            {"title": "Shoot", "text": "I stay out of the way and make it easy."},
                            {"title": "Deliver", "text": "A private gallery within three weeks."},
                        ],
                    },
                    bg="alt",
                ),
            ],
        ),
        contact_page(
            "pg_contact", "Tell me about your date, place and what you are after.", "Enquire"
        ),
    ],
    [("Work", "pg_work"), ("About", "pg_about"), ("Contact", "pg_contact")],
    header={"style": "centered", "sticky": False, "transparent": False},
    footer_style="minimal",
)

# 6. Consultant ---------------------------------------------------------------------------
make(
    "consultant",
    "Northfield Advisory",
    "Practical strategy for growing companies.",
    {
        "palette": pal("#1F3A5F", "#C8963E", "#FFFFFF", "#F3F5F8", "#14202E"),
        "fonts": {"heading": "plus-jakarta", "body": "dm-sans"},
        "radius": "sm",
        "card_style": "outlined",
        "heading_style": "tight",
    },
    {
        "phone": "+1 555 0123",
        "email": "enquiries@example.com",
        "address": "Chicago, Illinois",
        "hours": hours(("Mon-Fri", "09:00", "17:30")),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "Strategy and operations consulting for growing companies.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "banner",
                    {
                        "eyebrow": "Strategy & operations",
                        "heading": "Clear plans for companies that are growing faster than their systems.",
                        "subheading": "We work alongside leadership teams to fix what slows them down.",
                        "image": None,
                        "buttons": [
                            btn("Book a call", "pg_contact"),
                            btn("How we work", "pg_about", style="outline"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    bg="dark",
                    spacing="spacious",
                ),
                sec("sec_h_logos", "logos", "row", {"heading": "Trusted by teams at", "items": []}),
                sec(
                    "sec_h_svc",
                    "services",
                    "cards",
                    {
                        "heading": "How we help",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Growth strategy",
                                "description": "Where to play and how to win in the next three years.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Operating model",
                                "description": "Roles, rhythm and reporting that scale.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Interim leadership",
                                "description": "Experienced operators when you need them most.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_stats",
                    "stats",
                    "row",
                    {
                        "heading": "",
                        "subheading": "",
                        "items": [
                            {"value": "120+", "label": "Engagements"},
                            {"value": "18", "label": "Industries"},
                            {"value": "92%", "label": "Repeat clients"},
                        ],
                    },
                ),
                sec(
                    "sec_h_cta",
                    "cta",
                    "split",
                    {
                        "heading": "Start with a conversation",
                        "text": "Thirty minutes, no slides. We will tell you honestly whether we can help.",
                        "buttons": [btn("Book a call", "pg_contact")],
                    },
                    bg="primary",
                ),
            ],
        ),
        page(
            "pg_about",
            "about",
            "About",
            "How we work.",
            [
                sec(
                    "sec_a_text",
                    "text",
                    "lead",
                    {
                        "heading": "Our approach",
                        "body": "We keep teams small and senior. You work with the people who do the thinking, not a layer of junior analysts.\n\nWe write things down, agree the outcome up front and measure it afterwards.",
                    },
                ),
                sec(
                    "sec_a_steps",
                    "steps",
                    "horizontal",
                    {
                        "heading": "A typical engagement",
                        "subheading": "",
                        "items": [
                            {"title": "Diagnose", "text": "Two weeks of interviews and data."},
                            {
                                "title": "Design",
                                "text": "A short, specific plan agreed with your team.",
                            },
                            {"title": "Deliver", "text": "We stay until it works."},
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_a_team",
                    "team",
                    "cards",
                    {
                        "heading": "Partners",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "name": "Dana Whitaker",
                                "role": "Managing partner",
                                "bio": "Former COO, two exits.",
                                "photo": None,
                            },
                            {
                                "name": "Rahul Menon",
                                "role": "Partner",
                                "bio": "Operations and finance.",
                                "photo": None,
                            },
                        ],
                    },
                ),
            ],
        ),
        contact_page(
            "pg_contact",
            "Tell us a little about your company and what you are trying to solve.",
            "Book a call",
        ),
    ],
    [("Home", "pg_home"), ("About", "pg_about"), ("Contact", "pg_contact")],
)

# 7. Gym ----------------------------------------------------------------------------------
make(
    "gym",
    "Forge Strength Club",
    "Small-group strength training that actually sticks.",
    {
        "palette": pal("#E4572E", "#FFC857", "#0E0E10", "#1A1A1E", "#F4F4F5"),
        "fonts": {"heading": "rubik", "body": "dm-sans"},
        "radius": "sm",
        "card_style": "flat",
        "heading_style": "caps",
    },
    {
        "phone": "+1 555 0166",
        "email": "join@example.com",
        "address": "5 Foundry Lane, Denver",
        "hours": hours(("Mon-Fri", "05:30", "21:00"), ("Sat-Sun", "07:00", "15:00")),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "Small-group strength training. Book a free trial.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "banner",
                    {
                        "eyebrow": "Strength club",
                        "heading": "Get strong. Stay consistent.",
                        "subheading": "Coached small-group sessions for every level. No mirrors, no ego.",
                        "image": None,
                        "buttons": [
                            btn("Free trial class", "pg_contact"),
                            btn("See memberships", "pg_join", style="outline"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    spacing="spacious",
                ),
                sec(
                    "sec_h_stats",
                    "stats",
                    "row",
                    {
                        "heading": "",
                        "subheading": "",
                        "items": [
                            {"value": "600+", "label": "Members"},
                            {"value": "6", "label": "Coaches"},
                            {"value": "42", "label": "Classes a week"},
                        ],
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_feat",
                    "features",
                    "list",
                    {
                        "heading": "What you get",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "icon": "check",
                                "title": "Coached every rep",
                                "text": "Maximum eight people per class.",
                            },
                            {
                                "icon": "clock",
                                "title": "Early and late",
                                "text": "Sessions from 5:30 am to 8 pm.",
                            },
                            {
                                "icon": "heart",
                                "title": "A real community",
                                "text": "Members stay because they like each other.",
                            },
                        ],
                    },
                ),
                sec(
                    "sec_h_cta",
                    "cta",
                    "banner",
                    {
                        "heading": "Your first class is free",
                        "text": "Come once. See how it feels.",
                        "buttons": [btn("Book a free trial", "pg_contact")],
                    },
                    bg="primary",
                    align="center",
                ),
            ],
        ),
        page(
            "pg_join",
            "join",
            "Memberships",
            "Memberships and pricing.",
            [
                sec(
                    "sec_j_price",
                    "pricing",
                    "cards",
                    {
                        "heading": "Memberships",
                        "subheading": "No joining fee. Cancel any time.",
                        "plans": [
                            {
                                "name": "Drop-in",
                                "price": "$25",
                                "period": "per class",
                                "description": "",
                                "features": "Any class\nNo commitment",
                                "highlighted": False,
                                "cta_label": "Book",
                                "cta_link": link("pg_contact"),
                            },
                            {
                                "name": "Unlimited",
                                "price": "$129",
                                "period": "per month",
                                "description": "",
                                "features": "Unlimited classes\nFree body-composition check\nGuest passes",
                                "highlighted": True,
                                "cta_label": "Join",
                                "cta_link": link("pg_contact"),
                            },
                            {
                                "name": "Twice a week",
                                "price": "$89",
                                "period": "per month",
                                "description": "",
                                "features": "8 classes a month\nRollover for one month",
                                "highlighted": False,
                                "cta_label": "Join",
                                "cta_link": link("pg_contact"),
                            },
                        ],
                    },
                ),
                sec(
                    "sec_j_faq",
                    "faq",
                    "accordion",
                    {
                        "heading": "FAQ",
                        "subheading": "",
                        "items": [
                            {
                                "question": "Do I need experience?",
                                "answer": "No. Coaches scale every session to you.",
                            },
                            {
                                "question": "What should I bring?",
                                "answer": "Trainers and a water bottle. We have the rest.",
                            },
                        ],
                    },
                    bg="alt",
                ),
            ],
        ),
        page(
            "pg_team",
            "coaches",
            "Coaches",
            "Meet the coaches.",
            [
                sec(
                    "sec_t_team",
                    "team",
                    "cards",
                    {
                        "heading": "Coaches",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "name": "Jess Okafor",
                                "role": "Head coach",
                                "bio": "Powerlifter, ten years coaching.",
                                "photo": None,
                            },
                            {
                                "name": "Mike Brandt",
                                "role": "Coach",
                                "bio": "Conditioning and mobility.",
                                "photo": None,
                            },
                            {
                                "name": "Sofia Lindgren",
                                "role": "Coach",
                                "bio": "Beginners and returners.",
                                "photo": None,
                            },
                        ],
                    },
                ),
            ],
        ),
        contact_page("pg_contact", "Pick a time for your free trial class.", "Book a free trial"),
    ],
    [
        ("Home", "pg_home"),
        ("Memberships", "pg_join"),
        ("Coaches", "pg_team"),
        ("Contact", "pg_contact"),
    ],
)

# 8. Landscaping --------------------------------------------------------------------------
make(
    "landscaping",
    "Greenway Gardens",
    "Garden design and care, done by people who love plants.",
    {
        "palette": pal("#3F6B3A", "#D69E2E", "#FCFCF8", "#EEF2E6", "#1C2B1A"),
        "fonts": {"heading": "fraunces", "body": "manrope"},
        "radius": "lg",
        "card_style": "elevated",
        "image_style": "soft",
    },
    {
        "phone": "+1 555 0155",
        "email": "hello@example.com",
        "address": "Serving Asheville and the valley",
        "hours": hours(("Mon-Fri", "08:00", "17:00"), ("Sat", "09:00", "12:00")),
        "social": {},
    },
    [
        page(
            "pg_home",
            "",
            "Home",
            "Garden design, planting and maintenance.",
            [
                sec(
                    "sec_h_hero",
                    "hero",
                    "split",
                    {
                        "eyebrow": "Garden design & care",
                        "heading": "Outdoor spaces you will actually want to sit in.",
                        "subheading": "From a tidy-up to a full redesign, we make gardens that look good all year.",
                        "image": None,
                        "buttons": [
                            btn("Request a visit", "pg_contact"),
                            btn("See our services", "pg_services", style="outline"),
                        ],
                        "image_position": "end",
                        "video_url": "",
                        "overlay": "dark",
                        "height": "tall",
                    },
                    bg="alt",
                    spacing="spacious",
                ),
                sec(
                    "sec_h_feat",
                    "features",
                    "cards",
                    {
                        "heading": "Why Greenway",
                        "subheading": "",
                        "columns": 3,
                        "items": [
                            {
                                "icon": "leaf",
                                "title": "Plants that suit your plot",
                                "text": "Chosen for your soil, light and climate.",
                            },
                            {
                                "icon": "heart",
                                "title": "Small crew, big care",
                                "text": "The same two people on your garden every visit.",
                            },
                            {
                                "icon": "check",
                                "title": "Fixed quotes",
                                "text": "No surprises on the invoice.",
                            },
                        ],
                    },
                ),
                sec(
                    "sec_h_compare",
                    "compare",
                    "wide",
                    {
                        "heading": "The difference",
                        "subheading": "",
                        "before": None,
                        "after": None,
                        "before_label": "Before",
                        "after_label": "After",
                        "caption": "Backyard redesign, Weaverville",
                    },
                    bg="alt",
                ),
                sec(
                    "sec_h_cta",
                    "cta",
                    "card",
                    {
                        "heading": "Let's look at your garden",
                        "text": "A free site visit and a written quote within a week.",
                        "buttons": [btn("Request a visit", "pg_contact")],
                    },
                ),
            ],
        ),
        page(
            "pg_services",
            "services",
            "Services",
            "Garden services.",
            [
                sec(
                    "sec_s_list",
                    "services",
                    "cards",
                    {
                        "heading": "What we do",
                        "subheading": "",
                        "items": [
                            {
                                "title": "Design & planting",
                                "description": "A plan drawn for your space, then built.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Regular maintenance",
                                "description": "Seasonal visits that keep it looking its best.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                            {
                                "title": "Lawns & hedges",
                                "description": "Cutting, feeding and shaping.",
                                "price": "",
                                "image": None,
                                "link": None,
                            },
                        ],
                    },
                ),
                sec(
                    "sec_s_steps",
                    "steps",
                    "timeline",
                    {
                        "heading": "How a project runs",
                        "subheading": "",
                        "items": [
                            {"title": "Visit", "text": "We walk the garden with you."},
                            {"title": "Plan", "text": "A drawing and a fixed quote."},
                            {"title": "Build", "text": "Planted and finished, site left clean."},
                        ],
                    },
                    bg="alt",
                ),
            ],
        ),
        contact_page(
            "pg_contact", "Tell us about your garden and when would suit.", "Request a visit"
        ),
    ],
    [("Home", "pg_home"), ("Services", "pg_services"), ("Contact", "pg_contact")],
)
print("wrote starters")
