import json
from pymongo import MongoClient
from dotenv import load_dotenv # type: ignore
import os
import time
load_dotenv()

# MongoDB connection info
MONGO_URI = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['chess-db-cluster']  # Name of your database
tournaments_collection = db['tournaments']  # Name of your collection
players_collection = db['players']
games_collection = db['games']

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


################### Query 3 #####################

# Top n entities satisfying a criteria, sorted by an attribute

# Top 5 players with win count greater than 500, sorted by elo (Descending)
n = 3

result = players_collection.find({"winCount": {"$gt": 500}}).sort("elo", -1).limit(n)

print(f"The top {n} players with win count greater than 500, sorted by elo (descending) are:")

# For better display in terminal
top_players_list = list(result)
print(json.dumps(top_players_list, indent=4, default=str))




################### Query 4 #####################

# Simulate a relational group by query in NoSQL (aggregate per category).
result = games_collection.aggregate([
    {
        '$group': {
            '_id': '$whitePlayerID',
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            '_id': 1
        }
    }
])

print(f"Number of games played as White by each player: ")
games_as_white_list = list(result)
print(json.dumps(games_as_white_list, indent=4, default=str))

################### Query 6 #####################

# Demonstrate a full text search. Show the performance improvement using indexes

# The following 2 queries will find documents where dateTime_ has a 12 in it

# Query without index using regex
start_time = time.perf_counter()
query_without_index = {"dateTime_": {"$regex": "12", "$options": "i"}}  # Searching for partial match
results_without_index = list(games_collection.find(query_without_index).limit(1000))
duration_without_index = time.perf_counter() - start_time
print(f"Query without index (partial match) took: {duration_without_index * 1000:.6f} milliseconds")

# Query with text index
start_time = time.perf_counter()
query_with_index = {"$text": {"$search": "12"}}  # Searching for partial match
results_with_index = list(games_collection.find(query_with_index).limit(1000))
duration_with_index = time.perf_counter() - start_time
print(f"Query with text index (partial match) took: {duration_with_index * 1000:.6f} milliseconds")

# Note: This process cam take some time

client.close()





