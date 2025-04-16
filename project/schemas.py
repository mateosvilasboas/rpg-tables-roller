from pydantic import BaseModel, model_serializer, EmailStr

class UserSchema(BaseModel):
    name: str
    email: EmailStr

class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: list[UserPublic]

class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100