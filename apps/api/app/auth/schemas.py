import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    """Lower-cased, trimmed, and shaped like name@domain.tld; raises ValueError otherwise."""
    value = value.strip().lower()
    if not _EMAIL.match(value):
        raise ValueError("invalid email address")
    return value


class Credentials(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return normalize_email(v)


class RegisterRequest(Credentials):
    name: str = Field(default="", max_length=200)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
