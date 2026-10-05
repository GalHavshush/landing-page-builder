from pydantic import BaseModel, ConfigDict, Field, field_validator


class Credentials(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or v.startswith("@") or v.endswith("@"):
            raise ValueError("invalid email address")
        return v


class RegisterRequest(Credentials):
    name: str = Field(default="", max_length=200)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
