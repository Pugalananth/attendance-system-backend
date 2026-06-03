from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["attendance_system"]

# Collections
employees_collection = db["employees"]

attendance_collection = db["attendance"]

print("MongoDB Connected Successfully")