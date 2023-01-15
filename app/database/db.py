from motor import motor_asyncio
import os
import urllib.parse

username = os.environ["MONGO_USER"]
password = os.environ["MONGO_PASS"]
password = urllib.parse.quote_plus(password)
client = motor_asyncio.AsyncIOMotorClient(f"mongodb+srv://{username}:{password}@cluster0.i7jqe.mongodb.net/?retryWrites=true&w=majority")

db = client["cloud-storage"]
users = db["users"]
files = db["files"]