import json
from pymongo import MongoClient
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

# MongoDB connection info
MONGO_URI = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['chess-db-cluster']  # Name of your database
tournaments_collection = db['tournaments']  # Name of your collection

# ---------------------------- Query Implementation ---------------------------

################# Query 1 ####################

# Search for a tournament by its tournament_id
tournament_id = "1hzj7nct"
result = tournaments_collection.find({"tournament_id": tournament_id})

# Print the results
for tournament in result:
    #print(tournament)
    print(json.dumps(tournament, indent=4, default=str)) # makes the result looks pretty in the terminal


################### Query 2 #####################

# Aggregate query: count tournaments where "rated" is True
pipeline = [
    {"$match": {"rated": True}},  # filter: Only tournaments where "rated" is True
    {"$count": "rated_tournaments"}  # counting the documents matching the filter
]

result = tournaments_collection.aggregate(pipeline)
for count in result:
    print(f"Number of rated tournaments: {count['rated_tournaments']}")