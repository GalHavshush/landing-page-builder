"""One place that says what each role may do (ADR 005). Endpoints ask `can(role, action)`;
nothing else in the code base should compare roles directly."""

from enum import StrEnum


class Role(StrEnum):
    owner = "owner"
    designer = "designer"
    editor = "editor"  # the client: content only


ALL = {Role.owner, Role.designer, Role.editor}
DESIGNERS = {Role.owner, Role.designer}

ACTIONS: dict[str, set[Role]] = {
    "view": ALL,
    "edit_content": ALL,  # text, images, posts
    "edit_structure": DESIGNERS,  # sections, design props, theme, settings
    "export": ALL,
    "rename": DESIGNERS,
    "manage_members": {Role.owner},
    "delete_project": {Role.owner},
}


def can(role: Role, action: str) -> bool:
    return role in ACTIONS[action]
