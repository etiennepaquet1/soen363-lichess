import psycopg2
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()


# MongoDB connection info
MONGO_URI = os.getenv("MONGO_URI")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['chess-db-cluster']
players_collection = db['players']
tournaments_collection = db['tournaments']
events_collection = db['events']
#games_collection = db['games']
#gamemoves_collection = db['gamemoves']

# Function to migrate players
def migrate_players():
    cursor.execute("SELECT * FROM player")
    players = cursor.fetchall()
    player_records = []
    for row in players:
        player_record = {
            "playerID": row[0],
            "playerName": row[1],
            "gamesPlayed": row[2],
            "playTimeTotal": row[3],
            "winCount": row[4],
            "drawCount": row[5],
            "lossCount": row[6],
            "lastOnline": row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
            "isStreaming": row[8],
            "elo": row[9],
            "ratingDiff": row[10],
            "playerType": row[11]
        }
        player_records.append(player_record)
    players_collection.insert_many(player_records)

# Function to migrate tournaments
def migrate_tournaments():
    cursor.execute("SELECT * FROM tournament")
    tournaments = cursor.fetchall()
    tournament_records = []
    for row in tournaments:
        tournament_record = {
            "tournament_id": row[1],
            "starts_at": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
            "system": row[3],
            "full_name": row[4],
            "clock_limit": row[5],
            "clock_increment": row[6],
            "minutes": row[7],
            "variant": row[8],
            "nb_players": row[9],
            "rated": row[10],
            "berserkable": row[11],
            "is_finished": row[12]
        }
        tournament_records.append(tournament_record)
    tournaments_collection.insert_many(tournament_records)

# Function to migrate events
def migrate_events():
    cursor.execute("SELECT * FROM event")
    events = cursor.fetchall()
    event_records = []
    for row in events:
        # Fetch associated games
        cursor.execute("SELECT * FROM game WHERE event_id = %s", (row[0],))
        games = cursor.fetchall()
        game_records = []
        for game_row in games:
            # Fetch associated game moves
            cursor.execute("SELECT * FROM gamemoves WHERE gameID = %s", (game_row[0],))
            gamemoves = cursor.fetchall()
            gamemove_records = []
            for gamemove_row in gamemoves:
                gamemove_record = {
                    "moveNumber": gamemove_row[2],
                    "whiteMove": gamemove_row[3],
                    "blackMove": gamemove_row[4]
                }
                gamemove_records.append(gamemove_record)

            # Create the game document
            game_record = {
                "gameID": game_row[0],
                "whitePlayerID": game_row[2],
                "blackPlayerID": game_row[3],
                "result": game_row[4],
                "dateTime_": game_row[5].strftime('%Y-%m-%d %H:%M:%S') if game_row[5] else None,
                "whiteElo": game_row[6],
                "blackElo": game_row[7],
                "whiteRatingDiff": game_row[8],
                "blackRatingDiff": game_row[9],
                "eco": game_row[10],
                "opening": game_row[11],
                "timeControl": game_row[12],
                "termination": game_row[13],
                "gamemoves": gamemove_records  # Embed gamemoves in the game
            }
            game_records.append(game_record)

        # Create the event document, embedding games
        event_record = {
            "event_name": row[1],
            "event_type": row[2],
            "event_date": row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,
            "time_control": row[4],
            "termination": row[5],
            "url": row[6],
            "tournament_id": row[7],
            "games": game_records  # Embed games in the event
        }
        event_records.append(event_record)

    events_collection.insert_many(event_records)

# Function to migrate game data (optional) - we don't need it since it's stored with the event
'''def migrate_games():
    cursor.execute("SELECT * FROM game")
    games = cursor.fetchall()
    game_records = []
    for row in games:
        game_record = {
            "gameID": row[0],
            "event_id": row[1],
            "whitePlayerID": row[2],
            "blackPlayerID": row[3],
            "result": row[4],
            "dateTime_": row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None,
            "whiteElo": row[6],
            "blackElo": row[7],
            "whiteRatingDiff": row[8],
            "blackRatingDiff": row[9],
            "eco": row[10],
            "opening": row[11],
            "timeControl": row[12],
            "termination": row[13]
        }
        game_records.append(game_record)
    games_collection.insert_many(game_records)

# Function to migrate gamemoves data
def migrate_gamemoves():
    cursor.execute("SELECT * FROM gamemoves")
    gamemoves = cursor.fetchall()
    gamemove_records = []
    for row in gamemoves:
        gamemove_record = {
            "gameID": row[1],
            "moveNumber": row[2],
            "whiteMove": row[3],
            "blackMove": row[4]
        }
        gamemove_records.append(gamemove_record)
    gamemoves_collection.insert_many(gamemove_records)'''

# Running the migration functions
migrate_players()
migrate_tournaments()
migrate_events()  # This includes embedding games and gamemoves within events
#migrate_games()   
#migrate_gamemoves() 

# Close the cursor and connection
cursor.close()
conn.close()

print("Data migration completed successfully!")
