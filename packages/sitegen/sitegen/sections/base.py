from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from sitegen.models import BaseSection, fields_in_group

SECTIONS_DIR = Path(__file__).parent


@dataclass(frozen=True)
class SectionDef:
    """Everything the system knows about one section type.

    A section type lives in sections/<type>/ with model.py, template.html.j2 and style.css.
    """

    type: str
    label: str
    section_model: type[BaseSection]
    props_model: type[BaseModel]

    @property
    def folder(self) -> Path:
        return SECTIONS_DIR / self.type

    @property
    def template(self) -> str:
        return f"{self.type}/template.html.j2"

    def css(self) -> str:
        path = self.folder / "style.css"
        return path.read_text() if path.exists() else ""

    @property
    def translatable(self) -> set[str]:
        return fields_in_group(self.props_model, "content")
