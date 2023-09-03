import database
import models
import security
from fastapi import FastAPI, Depends, HTTPException, Form, Path, Body, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import List
from models import BookDb, BookIn, UserDb, UserIn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.on_event("startup")
async def startup_db_client():
    await database.init_db()

### API: Auth & Users ###

@app.get("/users/me")
async def get_me(current_user: dict = Depends(security.get_current_user)):
    return current_user

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    return await security.login(form.username, form.password)

@app.post("/register", response_model=models.UserDb)
async def register_user(user_in: models.UserIn):
    existing_user = await database.get_user_by_username_or_email(user_in.username, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with the same username or email already exists")
    created_user = await database.create_user(user_in)
    return created_user

### API: Books ###

@app.post("/books", response_model=BookDb)
async def create_book(
    book_in: BookIn,
    current_user: UserDb = Depends(security.authenticated),
):
    created_book = await database.save_book(book_in)
    return created_book

@app.get("/books", response_model=List[BookDb])
async def list_books(current_user: UserDb = Depends(security.authenticated)):
    books = await database.list_books()
    return books

@app.put("/books/{book_id}/status")
async def update_book_status_endpoint(
    book_id: str,
    new_status: str,
    current_user: UserDb = Depends(security.authenticated)
):
    updated_book = await database.perform_update_book_status(book_id, new_status)
    if updated_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: str, current_user: UserDb = Depends(security.authenticated)):
    deleted_book = await database.delete_book(book_id)
    if deleted_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return deleted_book
