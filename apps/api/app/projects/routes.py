import json

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import ValidationError
from sitegen import SiteDocument
from sitegen.migrations import UnsupportedVersion, load_document
from sitegen.starters import list_starters, load_starter, starter_info
from sitegen.validate import check
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.models import User
from app.db import get_db, utcnow
from app.permissions import Role, can
from app.projects import service
from app.projects.content_guard import content_violations
from app.projects.deps import DELETE, EDIT_CONTENT, RENAME, VIEW, Access
from app.projects.models import Project, ProjectMember
from app.projects.schemas import (
    DocIn,
    DocOut,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    SavedOut,
)

router = APIRouter(tags=["projects"])


def project_out(project: Project, role: str) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        name=project.name,
        slug=project.slug,
        template_id=project.template_id,
        role=str(role),
        revision=project.revision,
        updated_at=project.updated_at,
    )


@router.get("/templates")
def templates(_: User = Depends(get_current_user)) -> list[dict]:
    return starter_info()


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(
    body: ProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if body.template not in list_starters():
        raise HTTPException(422, f"Unknown template {body.template!r}")
    doc = load_starter(body.template, site_name=body.name)
    project = Project(
        name=body.name,
        slug=service.unique_slug(db, body.name),
        template_id=body.template,
        draft_doc=doc.model_dump(mode="json"),
        created_by=user.id,
    )
    db.add(project)
    db.flush()
    db.add(ProjectMember(project_id=project.id, user_id=user.id, role=Role.owner))
    return project_out(project, Role.owner)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Project, ProjectMember.role)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user.id)
        .order_by(Project.updated_at.desc())
    ).all()
    return [project_out(p, r) for p, r in rows]


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(access: Access = VIEW):
    return project_out(access.project, access.role)


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def rename_project(body: ProjectUpdate, access: Access = RENAME):
    access.project.name = body.name
    return project_out(access.project, access.role)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(access: Access = DELETE, db: Session = Depends(get_db)):
    db.delete(access.project)
    # members are removed by ON DELETE CASCADE; SQLite needs the explicit statement:
    for m in db.scalars(select(ProjectMember).where(ProjectMember.project_id == access.project.id)):
        db.delete(m)
    return Response(status_code=204)


@router.get("/projects/{project_id}/doc", response_model=DocOut)
def get_doc(access: Access = VIEW):
    return DocOut(doc=access.project.draft_doc, revision=access.project.revision)


def parse_document(raw: dict) -> SiteDocument:
    """Validate a document from the client; invalid input becomes a 422 listing every problem."""
    try:
        return load_document(raw)
    except ValidationError as exc:
        raise HTTPException(422, json.loads(exc.json(include_url=False))) from exc
    except UnsupportedVersion as exc:
        raise HTTPException(422, str(exc)) from exc


@router.put("/projects/{project_id}/doc", response_model=SavedOut)
def save_doc(
    body: DocIn,
    access: Access = EDIT_CONTENT,
    db: Session = Depends(get_db),
):
    doc = parse_document(body.doc)
    if not can(access.role, "edit_structure"):
        # a client may only change content: compare against what is stored (ADR 005)
        violations = content_violations(access.project.draft_doc, doc.model_dump(mode="json"))
        if violations:
            raise HTTPException(
                403,
                {
                    "message": "Your role may only edit content, not structure or design.",
                    "paths": violations[:10],
                },
            )
    # Compare-and-swap: the UPDATE only matches if nobody saved since `base_revision`, so two
    # simultaneous saves cannot both win (a read-then-write check would race).
    result = db.execute(
        update(Project)
        .where(Project.id == access.project.id, Project.revision == body.base_revision)
        .values(
            draft_doc=doc.model_dump(mode="json"),
            revision=body.base_revision + 1,
            updated_at=utcnow(),
        )
    )
    if result.rowcount == 0:
        db.rollback()
        current = db.scalar(select(Project.revision).where(Project.id == access.project.id))
        raise HTTPException(
            409, {"message": "The site was changed by someone else", "current_revision": current}
        )
    warnings = [i.__dict__ for i in check(doc) if i.level == "warning"]
    return SavedOut(revision=body.base_revision + 1, warnings=warnings)
