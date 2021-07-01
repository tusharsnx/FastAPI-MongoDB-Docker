from motor import motor_asyncio

client = motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")

db = client["cloud-storage"]
users = db["users"]
files = db["files"]
