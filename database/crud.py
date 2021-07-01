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
        await users.insert_one({
            "name": name,
            "username": username,
            "remaining_size": 5,
            "files": []
        })
        return True

# deletes user
async def delete_user(username: str):
    result = await users.delete_one({"username": username})
    if result["deletedCount"]:
        return True
    else: 
        return False

# returns all user's files
async def get_files(username: str):
    user = await users.find_one({"username": username}, {"_id": 0})
    return user["files"]

async def update_user(username: str, data: dict):
    result = await users.update_one({"username": username}, {"$set": data})
    if result["modifiedCount"]:
        return True
    else: 
        return False

        
# loop = asyncio.get_event_loop()
# result = loop.run_until_complete(read_users())
# print(result)

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
    await users.update_one({"username": username}, {"$push": {"files": file}})
    return file_id

# returns user's file details
async def read_file(file_id: str, username: str):
    pass
#     file = await users.find_one({"username": username, "files.file_id": file_id}, {"_id": 0, "files": 1})
#     return file


# deletes user's file
async def delete_file(file_id: str, username: str):
    pass
#     await users.update_one({"$set": {"$pull": {"files": file}}})