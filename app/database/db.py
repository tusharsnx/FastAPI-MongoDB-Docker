from motor import motor_asyncio
import os
import urllib.parse

username = os.environ["USERNAME"]
password = os.environ["PASS"]
password = urllib.parse.quote(password)
client = motor_asyncio.AsyncIOMotorClient(f"mongodb+srv://{username}:{password}@cluster0.i7jqe.mongodb.net")

db = client["cloud-storage"]
users = db["users"]
files = db["files"]