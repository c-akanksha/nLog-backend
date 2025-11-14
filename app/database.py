from pymongo import MongoClient
from app.core.config import settings
from urllib.parse import quote_plus


username = quote_plus(settings.USERNAME)
password = quote_plus(settings.PASSWORD)

client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.8w7xc2w.mongodb.net/')
db = client["nLog_db"]

print("Database name:", db.name)
print("Collections:", db.list_collection_names())

users_collection = db["users"]
notes_collection = db["notes"]
