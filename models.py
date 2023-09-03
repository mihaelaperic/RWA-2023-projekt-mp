from pydantic import BaseModel, Field

class BookIn(BaseModel):
    title: str
    author: str
    status: str

class BookDb(BaseModel):
    id: str
    title: str
    author: str
    status: str

class UserIn(BaseModel):
    username: str
    email: str
    password: str

class UserDb(BaseModel):
    username: str = Field(alias="_id")
    email: str
    hashed_password: str