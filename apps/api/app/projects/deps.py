from dataclasses import dataclass

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.models import User
from app.db import get_db
from app.permissions import Role, can
from app.projects.models import Project, ProjectMember


@dataclass
class Access:
    project: Project
    role: Role
    user: User


def project_access(action: str):
    """Dependency factory: loads the project and requires that the caller's role may `action`.

    Non-members get 404 (not 403) so project ids cannot be probed.
    """

    def dependency(
        project_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Access:
        row = db.execute(
            select(Project, ProjectMember.role)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(Project.id == project_id, ProjectMember.user_id == user.id)
        ).first()
        if row is None:
            raise HTTPException(404, "Project not found")
        project, role = row[0], Role(row[1])
        if not can(role, action):
            raise HTTPException(403, f"Your role ({role}) may not {action.replace('_', ' ')}")
        return Access(project, role, user)

    return dependency


# Ready-made dependencies, one per action (module-level so route signatures stay simple).
VIEW = Depends(project_access("view"))
RENAME = Depends(project_access("rename"))
EDIT_STRUCTURE = Depends(project_access("edit_structure"))
DELETE = Depends(project_access("delete_project"))
