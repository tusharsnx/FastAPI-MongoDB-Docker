from datetime import datetime
from uuid import uuid4
from database.db import db, users
import asyncio
# from passlib.context import CryptContext

# hasher = CryptContext(schemes=["bcrypt"])

### user cruds

# returns users details upto limit
async def read_users(limit: int = 10):
    limit = max(limit, 100)
    cursor = users.find({}, {"_id": 0}).limit(limit)
    users_info = await cursor.to_list(length=limit)
    return users_info

# returns user details
async def read_user(username: str):
    user = await users.find_one({"username": username}, {"_id": 0})
    return user

# creates new user if user does not exist
async def create_user(name: str, username: str):
    if await read_user(username):
        return False
    else:
        result = await users.insert_one({
            "name": name,
            "username": username,
            "remaining_size": 5,
            "files": []
        })
        if result.inserted_id:
            return True
        else:
            return False

# deletes user
async def delete_user(username: str):
    result = await users.delete_one({"username": username})
    if result.deleted_count:
        return True
    else: 
        return False

### file cruds

# returns all user's files
async def get_files(username: str):
    user = await users.find_one({"username": username}, {"_id": 0})
    for file in user["files"]:
        file["date_added"] = file["date_added"].date()
    return user["files"]

async def update_user(username: str, data: dict):
    result = await users.update_one({"username": username}, {"$set": data})
    if result.modified_count:
        return True
    else: 
        return False

# create user's file
async def create_file(file_name: str, username: str, size: float, dir: str):
    file_id = uuid4()
    file = {
        "file_id": str(file_id),
        "name": file_name,
        "path": f"{dir}/{file_id}",
        "size": size,
        "date_added": datetime.now()
    }
    await users.update_one({"username": username}, {"$push": {"files": file}, "$inc": {"remaining_size": -file["size"]}})
    return file_id

# returns user's file details
async def read_file(file_id: str, username: str):

    # aggreate function to use powerful unwind operator
    latent_cursor = users.aggregate([
        {"$unwind": "$files"},
        {"$match": {"username": username, "files.file_id": file_id}},
        {"$project": {"_id": 0, "files":1}}
    ])
    try:
        # cannot index after coroutine
        doc = await latent_cursor.next()
        #  getting the file detail document
        file = doc["files"]
        return file
    except:
        return None

# deletes user's file
async def delete_file(file_id: str, username: str):
    latent_cursor = users.aggregate([
        {"$unwind": "$files"},
        {"$match": {"username": username, "files.file_id": file_id}},
        {"$project": {"_id": 0, "files":1}},
    ])
    try:
        doc = await latent_cursor.next()
        file = doc["files"]
        result = await users.update_one({"files": file}, {"$pull": {"files": file}, "$inc": {"remaining_size": file["size"]}})
        if result.modified_count:
            return True
        else:
            return False
    except:
        return False

# delete when file doc is given
# no need to do aggregate call saves one databse io
async def delete_after_read_file(file: dict):
    result = await users.update_one({"files": file}, {"$pull": {"files": file}, "$inc": {"remaining_size": file["size"]}})
    if result.modified_count:
        return True
    else:
        return False

async def update_file(username: str, file_id: str, data: dict):
    latent_cursor = users.aggregate([
        {"$unwind": "$files"},
        {"$match": {"username": username, "files.file_id": file_id}},
        {"$project": {"_id": 0, "files": 1}}
    ])
    try:
        doc = await latent_cursor.next()
        file = doc["files"]

        # pull the file subdoc
        result = await users.update_one({"files": file}, {"$pull": {"files": file}})
        if result.modified_count:
            # modify the file doc
            file.update(data)
            await users.update_one({"username": username}, {"$push": {"files": file}})
            return True
    except:
        return False
    
    