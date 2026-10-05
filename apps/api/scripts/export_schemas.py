"""Writes the API contract for the frontend: OpenAPI + the site-document JSON Schema.

Run from apps/api:  uv run python scripts/export_schemas.py
The web app turns these into TypeScript types (npm run gen), so the backend models stay the
single source of truth.
"""

import json
from pathlib import Path

from app.main import create_app
from sitegen import SiteDocument

OUT = Path(__file__).resolve().parents[2] / "web" / "src" / "api" / "generated"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "openapi.json").write_text(json.dumps(create_app().openapi(), indent=2) + "\n")
    schema = SiteDocument.model_json_schema(
        mode="serialization"
    )  # fields with defaults are always present
    (OUT / "document.schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    print(f"wrote schemas to {OUT}")


if __name__ == "__main__":
    main()
