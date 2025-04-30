import re
from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class FrameworkSchema(BaseModel):
    name: str
    entries: dict[str, str] = {
        'row_0': 'string',
        'row_1': 'string',
        'row_2': 'string',
    }

    @model_validator(mode='after')
    def validate_entries(self):
        pattern = re.compile(r'^row_\d+$')

        invalid_keys = [
            key for key in self.entries.keys() if not pattern.match(key)
        ]

        if invalid_keys:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"""The following keys do not follow 'row_X' pattern: {
                    ', '.join(invalid_keys)
                }""",
            )

        numbers = [int(key.split('_')[1]) for key in self.entries.keys()]
        expected_numbers_sequence = list(range(0, len(numbers)))

        if numbers != expected_numbers_sequence:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f'Line numbers in dict keys are not sequencial and/or not ordered',  # noqa
            )
        return self


class FrameworkPublic(BaseModel):
    id: int
    name: str
    entries: dict

    model_config = ConfigDict(from_attributes=True)


class FrameworkPublicList(BaseModel):
    frameworks: list[FrameworkPublic]


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
