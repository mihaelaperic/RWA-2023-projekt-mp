from fastapi.encoders import jsonable_encoder
import pymongo
import models
import security
import uuid
import os
import motor.motor_asyncio
from dotenv import load_dotenv
from models import BookIn, BookDb, UserDb
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
db = mongodb_client["booktracker_db"]
books_collection = db["books"]

async def init_db():
    print("Connecting to the MongoDB database...")
    client = mongodb_client
    db = client["booktracker_db"]
    books_collection = db.get_collection("books")
    await books_collection.create_index([("_id", pymongo.ASCENDING)])

    print("Connected to the MongoDB database!")

### User ###

async def create_user(user_in: models.UserIn):
    user_id = str(uuid.uuid4())
    hashed_password = security.hash_password(user_in.password)
    user_db = models.UserDb(
        _id=user_id,
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password, 
    )
    new_user = await db["users"].insert_one(jsonable_encoder(user_db))
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    created_user["_id"] = str(created_user["_id"])
    return created_user

async def get_user_by_username_or_email(username: str, email: str):
    user = await db["users"].find_one({"$or": [{"username": username}, {"email": email}]})
    return user

async def get_user(username: str, password: str = None):
    document = await db["users"].find_one({"_id": username})
    print(f'database.get_user({username}, {password}): {document}')
    if document:
        user = models.UserDb(**document)
        if password:
            if security.verify_password(password, user.hashed_password):
                return user
        else:
            return user

### Book ###

async def save_book(book_in: models.BookIn):
    user_id = str(uuid.uuid4())
    book_db = models.BookDb(
        _id=user_id,
        title=book_in.title,
        author=book_in.author,
        status=book_in.status,
        user_id=user_id,
    )
    new_book = await db["books"].insert_one(jsonable_encoder(book_db))
    created_book = await db["books"].find_one({"_id": new_book.inserted_id})

    created_book["_id"] = str(created_book["_id"])
    return created_book

async def perform_update_book_status(book_id: str, new_status: str):
    updated_book = await update_book_status(book_id, new_status)
    return updated_book

async def update_book_status(book_id: str, new_status: str):
    updated_book = await db["books"].find_one_and_update(
        {"_id": book_id},
        {"$set": {"status": new_status}},
        return_document=True
    )
    return updated_book

async def delete_book(book_id: str):
    deleted_book = await db["books"].find_one_and_delete({"_id": book_id})
    return deleted_book

async def list_books():
    books = []
    async for book in db["books"].find():
        book["_id"] = str(book["_id"])
        books.append(book)
    return books
