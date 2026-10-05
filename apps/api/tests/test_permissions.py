import pytest
from app.permissions import ACTIONS, Role, can


def test_every_action_is_granted_to_someone():
    assert all(ACTIONS[a] for a in ACTIONS)


@pytest.mark.parametrize(
    ("role", "action", "allowed"),
    [
        (Role.owner, "manage_members", True),
        (Role.designer, "manage_members", False),
        (Role.designer, "edit_structure", True),
        (Role.editor, "edit_structure", False),
        (Role.editor, "edit_content", True),
        (Role.editor, "delete_project", False),
    ],
)
def test_matrix(role, action, allowed):
    assert can(role, action) is allowed
