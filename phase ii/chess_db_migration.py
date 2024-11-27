import psycopg2
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv  # type: ignore
import os
import logging
import time
from collections import defaultdict
import bson
from pymongo.errors import BulkWriteError, AutoReconnect

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# MongoDB connection info
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB with increased timeouts
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    socketTimeoutMS=60000,  # Increase socket timeout to 60 seconds
    connectTimeoutMS=20000,  # Increase connect timeout to 20 seconds
    maxPoolSize=100  # Adjust pool size as needed
)
db = client['chess-db-cluster']
players_collection = db['players']
tournaments_collection = db['tournaments']
events_collection = db['events']

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# Function to migrate players with batching
def migrate_players():
    logging.info("Migrating players...")
    cursor.execute("SELECT * FROM player")
    players = cursor.fetchall()
    logging.info(f"Fetched {len(players)} players from PostgreSQL")

    if not players:
        logging.info("No players found.")
        return

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

    # Delete existing records to avoid duplicates
    players_collection.delete_many({})
    if player_records:
        batch_size = 1000  # Adjust the batch size as needed
        total_batches = (len(player_records) + batch_size - 1) // batch_size
        for i in range(0, len(player_records), batch_size):
            batch = player_records[i:i + batch_size]
            try:
                players_collection.insert_many(batch)
                logging.info(f"Inserted batch {i // batch_size + 1}/{total_batches} containing {len(batch)} player records into MongoDB")
            except BulkWriteError as bwe:
                logging.error(f"Bulk write error: {bwe.details}")
            except Exception as e:
                logging.error(f"Error inserting player records: {e}")
                break
    else:
        logging.info("No player records to insert into MongoDB")

# Function to migrate tournaments with batching
def migrate_tournaments():
    logging.info("Migrating tournaments...")
    cursor.execute("SELECT * FROM tournament")
    tournaments = cursor.fetchall()
    logging.info(f"Fetched {len(tournaments)} tournaments from PostgreSQL")

    if not tournaments:
        logging.info("No tournaments found.")
        return

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

    # Delete existing records to avoid duplicates
    tournaments_collection.delete_many({})
    if tournament_records:
        batch_size = 10000  # Adjust the batch size as needed
        total_batches = (len(tournament_records) + batch_size - 1) // batch_size
        for i in range(0, len(tournament_records), batch_size):
            batch = tournament_records[i:i + batch_size]
            try:
                tournaments_collection.insert_many(batch)
                logging.info(f"Inserted batch {i // batch_size + 1}/{total_batches} containing {len(batch)} tournament records into MongoDB")
            except BulkWriteError as bwe:
                logging.error(f"Bulk write error: {bwe.details}")
            except Exception as e:
                logging.error(f"Error inserting tournament records: {e}")
                break
    else:
        logging.info("No tournament records to insert into MongoDB")

# Function to migrate events with batching and document size checks
def migrate_events():
    logging.info("Migrating events...")
    # Fetch all events
    cursor.execute("SELECT * FROM event")
    events = cursor.fetchall()
    logging.info(f"Fetched {len(events)} events from PostgreSQL")

    if not events:
        logging.info("No events found.")
        return

    # Extract event IDs
    event_ids = [row[0] for row in events]  # Assuming row[0] is event_id

    # Fetch all games associated with these events
    logging.info("Fetching all games associated with events...")
    if event_ids:
        format_strings = ','.join(['%s'] * len(event_ids))
        cursor.execute(f"SELECT * FROM game WHERE event_id IN ({format_strings})", tuple(event_ids))
        games = cursor.fetchall()
        logging.info(f"Fetched {len(games)} games from PostgreSQL")
    else:
        games = []
        logging.info("No events to fetch games for.")

    # Group games by event_id
    games_by_event = defaultdict(list)
    for game_row in games:
        event_id = game_row[1]  # Assuming game_row[1] is event_id
        games_by_event[event_id].append(game_row)

    # Extract all gameIDs
    game_ids = [game_row[0] for game_row in games]  # Assuming game_row[0] is gameID

    # Fetch all gamemoves associated with these games
    logging.info("Fetching all gamemoves associated with games...")
    if game_ids:
        format_strings = ','.join(['%s'] * len(game_ids))
        cursor.execute(f"SELECT * FROM gamemoves WHERE gameID IN ({format_strings})", tuple(game_ids))
        gamemoves = cursor.fetchall()
        logging.info(f"Fetched {len(gamemoves)} gamemoves from PostgreSQL")
    else:
        gamemoves = []
        logging.info("No games found to fetch gamemoves for.")

    # Group gamemoves by gameID
    gamemoves_by_game = defaultdict(list)
    for gamemove_row in gamemoves:
        gameID = gamemove_row[1]  # Assuming gamemove_row[1] is gameID
        gamemoves_by_game[gameID].append(gamemove_row)

    # Build event records
    event_records = []
    oversized_docs = []
    for row in events:
        event_id = row[0]
        # Fetch associated games
        event_games = games_by_event.get(event_id, [])
        logging.info(f"Processing {len(event_games)} games for event '{row[1]}'")
        game_records = []
        for game_row in event_games:
            gameID = game_row[0]
            # Fetch associated gamemoves
            game_moves = gamemoves_by_game.get(gameID, [])
            logging.info(f"Processing {len(game_moves)} gamemoves for game {gameID}")
            gamemove_records = []
            for gamemove_row in game_moves:
                gamemove_record = {
                    "moveNumber": gamemove_row[2],
                    "whiteMove": gamemove_row[3],
                    "blackMove": gamemove_row[4]
                }
                gamemove_records.append(gamemove_record)
            # Create the game document
            game_record = {
                "gameID": gameID,
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
        # Check for oversized document
        doc_size = len(bson.BSON.encode(event_record))
        if doc_size > 16 * 1024 * 1024:
            oversized_docs.append(row[1])  # Assuming row[1] is event_name
            logging.error(f"Event '{row[1]}' exceeds the maximum BSON document size and will be skipped.")
        else:
            event_records.append(event_record)

    # Delete existing records to avoid duplicates
    events_collection.delete_many({})
    if event_records:
        batch_size = 100  # Adjust the batch size as needed
        total_batches = (len(event_records) + batch_size - 1) // batch_size
        for i in range(0, len(event_records), batch_size):
            batch = event_records[i:i + batch_size]
            try:
                events_collection.insert_many(batch)
                logging.info(f"Inserted batch {i // batch_size + 1}/{total_batches} containing {len(batch)} event records into MongoDB")
            except BulkWriteError as bwe:
                logging.error(f"Bulk write error: {bwe.details}")
            except AutoReconnect as e:
                logging.error(f"AutoReconnect error: {e}")
                # Optionally implement a retry mechanism
                break
            except Exception as e:
                logging.error(f"Error inserting event records: {e}")
                break
    else:
        logging.info("No event records to insert into MongoDB")

    if oversized_docs:
        logging.error(f"Skipped {len(oversized_docs)} oversized event documents due to size limitations.")

# Running the migration functions
if __name__ == "__main__":
    start_time = time.time()

    try:
        migrate_players()
        migrate_tournaments()
        migrate_events()  # This includes embedding games and gamemoves within events
    except Exception as e:
        logging.error(f"Migration failed: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
        client.close()

    end_time = time.time()
    logging.info(f"Data migration completed in {end_time - start_time:.2f} seconds")
