from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr


class FrameworkSchema(BaseModel):
    name: str
    entries: dict[str, Any]


class FrameworkPublic(BaseModel):
    id: int
    name: str
    entries: dict

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    name: str
    email: EmailStr


class UserSchemaCreate(UserSchema):
    password: str


class UserSchemaUpdate(UserSchema):
    password: str | None = None


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    frameworks: list[FrameworkPublic]

    model_config = ConfigDict(from_attributes=True)


class UserPublicList(BaseModel):
    users: list[UserPublic]


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    detail: str
