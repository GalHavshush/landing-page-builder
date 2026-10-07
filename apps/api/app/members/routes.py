from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.models import User
from app.auth.schemas import normalize_email
from app.auth.security import hash_token, new_token
from app.db import get_db, utcnow
from app.members.models import Invitation
from app.permissions import Role
from app.projects.deps import MANAGE_MEMBERS, Access
from app.projects.models import Project, ProjectMember

router = APIRouter(tags=["members"])
INVITE_DAYS = 7
InvitableRole = Literal["designer", "editor"]  # owners are not created by invitation


class MemberOut(BaseModel):
    user_id: int
    email: str
    name: str
    role: str


class InvitationOut(BaseModel):
    id: int
    role: str
    email: str | None
    expires_at: str


class InvitationCreated(InvitationOut):
    token: str  # shown once; only its hash is stored


class InviteIn(BaseModel):
    role: InvitableRole
    email: str | None = Field(default=None, max_length=320)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None  # no email: the link works for anyone
        return normalize_email(v)


class RoleIn(BaseModel):
    role: InvitableRole


class InvitePreview(BaseModel):
    project_name: str
    role: str
    email: str | None


def _inv_out(i: Invitation) -> dict:
    return {"id": i.id, "role": i.role, "email": i.email, "expires_at": i.expires_at.isoformat()}


@router.get("/projects/{project_id}/members")
def list_members(access: Access = MANAGE_MEMBERS, db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(User, ProjectMember.role)
        .join(ProjectMember, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == access.project.id)
        .order_by(User.email)
    ).all()
    pending = db.scalars(
        select(Invitation).where(
            Invitation.project_id == access.project.id,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > utcnow(),
        )
    )
    return {
        "members": [
            MemberOut(user_id=u.id, email=u.email, name=u.name, role=r).model_dump()
            for u, r in rows
        ],
        "invitations": [_inv_out(i) for i in pending],
    }


@router.post(
    "/projects/{project_id}/invitations", response_model=InvitationCreated, status_code=201
)
def create_invitation(
    body: InviteIn, access: Access = MANAGE_MEMBERS, db: Session = Depends(get_db)
):
    token = new_token()
    inv = Invitation(
        project_id=access.project.id,
        role=body.role,
        email=body.email,
        token_hash=hash_token(token),
        created_by=access.user.id,
        expires_at=utcnow() + timedelta(days=INVITE_DAYS),
    )
    db.add(inv)
    db.flush()
    return {**_inv_out(inv), "token": token}


@router.delete("/projects/{project_id}/invitations/{invitation_id}", status_code=204)
def revoke_invitation(
    invitation_id: int, access: Access = MANAGE_MEMBERS, db: Session = Depends(get_db)
):
    inv = db.get(Invitation, invitation_id)
    if inv is None or inv.project_id != access.project.id:
        raise HTTPException(404, "Invitation not found")
    db.delete(inv)
    return Response(status_code=204)


def _member(db: Session, project_id: int, user_id: int) -> ProjectMember:
    m = db.get(ProjectMember, (project_id, user_id))
    if m is None:
        raise HTTPException(404, "Member not found")
    return m


@router.patch("/projects/{project_id}/members/{user_id}", response_model=MemberOut)
def change_role(
    user_id: int, body: RoleIn, access: Access = MANAGE_MEMBERS, db: Session = Depends(get_db)
):
    member = _member(db, access.project.id, user_id)
    if member.role == Role.owner:
        raise HTTPException(409, "The owner's role cannot be changed")
    member.role = body.role
    user = db.get(User, user_id)
    return MemberOut(user_id=user.id, email=user.email, name=user.name, role=member.role)


@router.delete("/projects/{project_id}/members/{user_id}", status_code=204)
def remove_member(user_id: int, access: Access = MANAGE_MEMBERS, db: Session = Depends(get_db)):
    member = _member(db, access.project.id, user_id)
    if member.role == Role.owner:
        raise HTTPException(409, "The owner cannot be removed")
    db.delete(member)
    return Response(status_code=204)


# ---- accepting an invite (any logged-in user holding the link) ----------------------------


def _valid_invite(db: Session, token: str) -> Invitation:
    inv = db.scalar(select(Invitation).where(Invitation.token_hash == hash_token(token)))
    if inv is None or inv.accepted_at is not None or inv.expires_at <= utcnow():
        raise HTTPException(404, "This invitation is invalid or has expired")
    return inv


@router.get("/invitations/{token}", response_model=InvitePreview)
def preview_invitation(
    token: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    inv = _valid_invite(db, token)
    return {
        "project_name": db.get(Project, inv.project_id).name,
        "role": inv.role,
        "email": inv.email,
    }


@router.post("/invitations/{token}/accept")
def accept_invitation(
    token: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    inv = _valid_invite(db, token)
    if inv.email and inv.email != user.email:
        raise HTTPException(
            403, f"This invitation was sent to {inv.email}. Sign in with that account."
        )
    if db.get(ProjectMember, (inv.project_id, user.id)):
        raise HTTPException(409, "You already have access to this site")
    db.add(ProjectMember(project_id=inv.project_id, user_id=user.id, role=inv.role))
    inv.accepted_at, inv.accepted_by = utcnow(), user.id
    return {"project_id": inv.project_id, "role": inv.role}
