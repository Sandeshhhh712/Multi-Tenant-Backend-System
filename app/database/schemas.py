from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)

    model_config = {"extra": "forbid"}

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token : str
    token_type : str

class Tokendata(BaseModel):
    username : str

class OrganizationCreate(BaseModel):
    name : str = Field(max_length=255)

    model_config = {"extra":"forbid"}