from motor import motor_asyncio

client = motor_asyncio.AsyncIOMotorClient("mongodb://admin:123@localhost:27017/")

db = client["cloud-storage"]
users = db["users"]
files = db["files"]
