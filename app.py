import database
import models
import security
import motor
from fastapi import FastAPI, Depends, HTTPException, Form, Path, Body, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import Annotated, List
from models import BookDb, BookIn, UserDb, UserIn
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.on_event("startup")
async def startup_db_client():
    await database.init_db()


### API: Auth & Users ###

async def authenticated(token: str = Depends(oauth2_scheme)):
    return await security.authenticated(token)

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    return await security.login(form.username, form.password)

@app.post("/users", response_model=models.UserIn)
async def create_user(user: models.UserIn = Body(...)):
    hashed_password = security.hash_password(user.password)
    user_db = models.UserDb(
        _id = user.username,
        email = user.email,
        hashed_password = hashed_password
    )

    print(f'user_db: = {user_db}')

    new_user = await database.db["users"].insert_one(jsonable_encoder(user_db))
    created_user = await database.db["users"].find_one({"_id": new_user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


@app.get("/users/me", response_model=models.UserDb)
async def get_me(current_user: models.UserDb = Depends(authenticated)):
    return jsonable_encoder(current_user)


### API: Books ###

@app.post("/books", response_model=models.BookDb)
async def create_book(
    book_in: BookIn,
    current_user: models.UserDb = Depends(security.get_current_user), 
    ):
    created_book = await database.save_book(book_in)
    return created_book

@app.get("/books", response_model=List[models.BookDb])
async def list_books(current_user: models.UserDb = Depends(security.get_current_user)):
    books = await database.list_books()
    return books

@app.put("/books/{book_id}/status")
async def update_book_status_endpoint(
    book_id: str,
    new_status: str,
    current_user: models.UserDb = Depends(security.authenticated)
):
    updated_book = await database.perform_update_book_status(book_id, new_status)
    if updated_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: str, current_user: models.UserDb = Depends(security.authenticated)):
    deleted_book = await database.delete_book(book_id)
    if deleted_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return deleted_book
