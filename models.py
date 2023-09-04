from pydantic import BaseModel, Field
from typing import Optional

class BookIn(BaseModel):
    title: str
    author: str
    status: Optional[str]

class BookDb(BaseModel):
    id: str = Field(alias="_id")
    title: str
    author: str
    status: Optional[str]
    user_id: str

class UserIn(BaseModel):
    username: str
    email: str
    password: str

class UserDb(BaseModel):
    username: str = Field(alias="_id")
    email: str
    hashed_password: str