"""Schema versioning (ADR 002). Stored documents live for years, so old ones must load.

To change the schema in a breaking way:
  1. bump SCHEMA_VERSION in schema.py;
  2. add `MIGRATIONS[old_version] = fn` below, where fn takes the raw dict of that version
     and returns the raw dict of the next one;
  3. add a test with a document in the old shape.
"""

from collections.abc import Callable

from sitegen.schema import SCHEMA_VERSION, SiteDocument

Migration = Callable[[dict], dict]
MIGRATIONS: dict[int, Migration] = {}


class UnsupportedVersion(ValueError):
    pass


def migrate(
    data: dict, migrations: dict[int, Migration] | None = None, target: int = SCHEMA_VERSION
) -> dict:
    migrations = MIGRATIONS if migrations is None else migrations
    version = data.get("schema_version", 1)
    if version > target:
        raise UnsupportedVersion(f"document is version {version}, this build supports {target}")
    while version < target:
        if version not in migrations:
            raise UnsupportedVersion(f"no migration from schema version {version}")
        data = migrations[version](data)
        version += 1
        data["schema_version"] = version
    return data


def load_document(data: dict) -> SiteDocument:
    """The one way to turn stored/imported JSON into a SiteDocument."""
    return SiteDocument.model_validate(migrate(data))
