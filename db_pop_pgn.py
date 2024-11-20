import psycopg2 # type: ignore
import re
import requests # type: ignore
import time
import datetime
from dateutil import parser # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import sys

# Load environment variables from .env file
load_dotenv()

# Access your API key
API_KEY = os.getenv('API_KEY')

# Check if the API_KEY is recognized 
#if API_KEY:
    #print("API_KEY is found.")
    #sys.exit(1)  # Exit the script with a non-zero status to indicate an error

# Database connection parameters -- to be put in .env 
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'chess_db'
DB_USER = 'chessgeeks'
DB_PASSWORD = 'soen363'



# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()


def insert_player(player_name, elo, rating_diff, player_type, player_api_data=None):
    """Insert player into the database without updating existing players."""
    elo = safe_int(elo)
    if elo is None or not (0 <= elo <= 3000):
        print(f"Invalid Elo rating for player {player_name}. Skipping player.")
        return None
    
    # Check if player already exists
    cur.execute("SELECT playerID FROM player WHERE playername = %s", (player_name,))
    existing_player = cur.fetchone()

    if existing_player:
        print(f"Player {player_name} already exists in the database. Skipping insertion.")
        return existing_player[0]  # Return the existing playerID
    
    # Convert lastOnline timestamp (if present) from milliseconds to datetime object
    last_online = player_api_data.get('lastOnline')
    if last_online:
        last_online = datetime.datetime.fromtimestamp(last_online / 1000)  # Convert from milliseconds to seconds
    else:
        last_online = None   # Set to None if no data
    
    # Get the playTimeTotal from the player API data
    play_time_total = player_api_data.get('playTimeTotal', 0)  # Default to 0 if not provided

    # If player does not exist, insert the player
    cur.execute("""
        INSERT INTO player (playername, elo, ratingdiff, playertype, gamesplayed, wincount, drawcount, losscount, lastonline, isstreaming, playtimetotal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING playerID;
    """, (
        player_name, elo, rating_diff, player_type,
        player_api_data.get('games', 0),
        player_api_data.get('wins', 0),
        player_api_data.get('draws', 0),
        player_api_data.get('losses', 0),
        last_online,  # Insert the converted datetime or None
        player_api_data.get('streaming', False),  # Default to False if no streaming status
        play_time_total  # Insert the playTimeTotal value
    ))
    
    player_id = cur.fetchone()[0]
    
    # If player insertion failed, print an error and return None
    if player_id is None:
        print(f"Failed to insert player {player_name}. Skipping player.")
        return None
    
    return player_id

# Fetch player data from Lichess API
def get_player_api_data(username):
    """Fetch player data from Lichess API and return relevant fields."""
    url = f'https://lichess.org/api/user/{username}'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"Fetched data for {username}: {data}")  # Debug: print fetched data

        # Mapping the fields 
        return {
            'games': data.get('count', {}).get('all', 0),  # Total games played
            'wins': data.get('count', {}).get('win', 0),  # Total wins
            'draws': data.get('count', {}).get('draw', 0),  # Total draws
            'losses': data.get('count', {}).get('loss', 0),  # Total losses
            'lastOnline': data.get('seenAt'),  # Last online time (timestamp)
            'streaming': data.get('playing', False),  # Streaming status (True/False)
            'playTimeTotal': data.get('playTime', {}).get('total', 0),  # Total play time (in seconds)
        }
    else:
        print(f"Failed to fetch data for {username} (status code: {response.status_code})")
        return None  # Return None if the API request failed

# Function to fetch tournament details from Lichess API and insert into database
def fetch_and_insert_tournament(event_name):
    """Check if event is part of a tournament and insert tournament details."""
    # Extract tournament ID from event name (if present)
    tournament_id_match = re.search(r'tournament/([a-zA-Z0-9]+)', event_name)
    
    if not tournament_id_match:
        print(f"Event '{event_name}' is not part of a tournament. Skipping tournament fetch.")
        return None  # This is not a tournament event, return None
    
    tournament_id = tournament_id_match.group(1)  # Extract the tournament ID
    
    # Check if tournament already exists in database
    cur.execute("SELECT tournament_id FROM tournament WHERE tournament_id = %s", (tournament_id,))
    existing_tournament = cur.fetchone()
    
    if existing_tournament:
        print(f"Tournament {tournament_id} already exists in the database. Skipping insertion.")
        return existing_tournament[0]  # Return the existing tournament_id
    
    print(f'Attempting to fetch tournament {tournament_id}')
    
    # Make the request to Lichess API for tournament details
    request = requests.get(f'https://lichess.org/api/tournament/{tournament_id}')
    
    # Handle rate limiting (status code 427)
    while request.status_code == 427:
        print(f'Got a 427 for tournament {tournament_id}. Retrying in 10 minutes...')
        time.sleep(600)  # Wait 10 minutes before retrying
        request = requests.get(f'https://lichess.org/api/tournament/{tournament_id}')
    
    if request.status_code != 200:
        print(f"Failed to fetch data for tournament {tournament_id} (status code: {request.status_code})")
        return None  # If the request fails, return None
    
    tournament_data = request.json()
    print(f"Fetched tournament data: {tournament_data}")  # Debugging the API response

    # Ensure tournament data is valid and not empty
    if not tournament_data:
        print(f"No data returned for tournament {tournament_id}. Skipping.")
        return None

    # Extract tournament data
    tournament_id = tournament_data.get('id')
    
    # Ensure 'startsAt' is in a correct format (ISO 8601 string)
    starts_at_timestamp = tournament_data.get('startsAt')
    if starts_at_timestamp:
        starts_at = parser.parse(starts_at_timestamp)  # Use dateutil.parser.parse
    else:
        starts_at = None
    
    system = tournament_data.get('system')
    full_name = tournament_data.get('fullName')
    clock_limit = tournament_data.get('clock', {}).get('limit')
    clock_increment = tournament_data.get('clock', {}).get('increment')
    minutes = tournament_data.get('minutes')
    variant = tournament_data.get('variant')
    nb_players = tournament_data.get('nbPlayers')
    rated = tournament_data.get('rated')
    berserkable = tournament_data.get('berserkable') == True
    isfinished = tournament_data.get('isFinished')

    # Insert tournament into database
    cur.execute("""
        INSERT INTO tournament (
            tournament_id, starts_at, system, full_name, clock_limit, clock_increment, 
            minutes, variant, nb_players, rated, berserkable, is_finished
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING tournament_id;
    """, (tournament_id, starts_at, system, full_name, clock_limit, clock_increment, 
          minutes, variant, nb_players, rated, berserkable, isfinished))
    
    tournament_id = cur.fetchone()[0]  # Get the inserted tournament_id
    conn.commit()  # Commit to save the tournament
    print(f"Tournament {tournament_id} inserted into database.")
    return tournament_id  # Return the tournament ID after insertion

# Function to insert event data
def insert_event(event_data, tournament_id=None):
    if tournament_id is None:
        print(f"Warning: No tournament_id provided for event {event_data['event_name']}")
    # Insert event into the database
    cur.execute("""
        INSERT INTO event (event_name, event_type, event_date, time_control, termination, url, tournament_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING event_id
    """, (event_data['event_name'], event_data['event_type'], event_data['event_date'], 
          event_data['time_control'], event_data['termination'], event_data['url'], tournament_id))
    
    event_id = cur.fetchone()[0]
    conn.commit()
    print(f"Event {event_data['event_name']} inserted into database with event_id {event_id}.")
    return event_id

def safe_int(value):
    """Safely convert a value to an integer, return None if invalid."""
    if value is None or value == '?' or value == '':  # handle empty string too
        return None  # Return None if value is '?' or None or empty string
    try:
        return int(value)
    except (ValueError, TypeError):
        return None  # Return None if conversion fails

# Function to insert game data
def insert_game(event_id, white_player_id, black_player_id, result, date_time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination):
    # Ensure that both players exist before attempting to insert the game
    if white_player_id is None or black_player_id is None:
        print(f"Skipping game due to missing player IDs: white_player_id={white_player_id}, black_player_id={black_player_id}")
        return None
    
    # Proceed with inserting the game
    cur.execute("""
        INSERT INTO game (event_id, whitePlayerid, blackPlayerid, result, dateTime_, whiteelo, blackelo, whiteratingdiff, blackratingdiff, eco, opening, timecontrol, termination)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING gameid;
    """, (event_id, white_player_id, black_player_id, result, date_time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination))
    
    game_id = cur.fetchone()[0]
    return game_id

# Function to insert game moves data
def insert_game_moves(game_id, move_number, white_move, black_move):
    cur.execute("""
        INSERT INTO gamemoves (gameid, movenumber, whitemove, blackmove)
        VALUES (%s, %s, %s, %s);
    """, (game_id, move_number, white_move, black_move))

RECORD_LIMIT = 100  # Limit to 200 records

# Inside parse_pgn_and_insert function
def parse_pgn_and_insert(pgn_file_path):
    with open(pgn_file_path, 'r') as file:
        pgn_data = file.read()

    # Regular expression patterns to capture the PGN details
    game_pattern = r'\[Event "([^"]+)"\].*?\[Site "([^"]+)"\].*?\[White "([^"]+)"\].*?\[Black "([^"]+)"\].*?\[Result "([^"]+)"\].*?\[UTCDate "([^"]+)"\].*?\[UTCTime "([^"]+)"\].*?\[WhiteElo "([^"]+)"\].*?\[BlackElo "([^"]+)"\].*?\[WhiteRatingDiff "([^"]+)"\].*?\[BlackRatingDiff "([^"]+)"\].*?\[ECO "([^"]+)"\].*?\[Opening "([^"]+)"\].*?\[TimeControl "([^"]+)"\].*?\[Termination "([^"]+)"\](.*?)\n*(?=\[|\Z)'

    games = re.findall(game_pattern, pgn_data, re.DOTALL)

    record_count = 0

    for game in games:
        if record_count >= RECORD_LIMIT:
            print(f"Record limit of {RECORD_LIMIT} reached. Stopping insertion.")
            break

        event_name, site, white_name, black_name, result, date, time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination, moves = game

        # Fetch additional data from the Lichess API for players
        white_api_data = get_player_api_data(white_name)
        black_api_data = get_player_api_data(black_name)

        # Check if event is part of a tournament
        tournament_id = fetch_and_insert_tournament(event_name)
        
        # Parse event and insert into the database
        event_date = f"{date} {time}"
        event_data = {
            'event_name': event_name,
            'event_type': 'Regular' if not tournament_id else 'Tournament',  # Use 'Tournament' or 'Regular' based on the presence of tournament_id
            'event_date': event_date,
            'time_control': time_control,
            'termination': termination,
            'url': site
        }
        
        # Insert event into the database
        event_id = insert_event(event_data, tournament_id)

        # Insert players (including additional API data)
        white_player_id = insert_player(white_name, white_elo, white_rating_diff, 'White', white_api_data)
        black_player_id = insert_player(black_name, black_elo, black_rating_diff, 'Black', black_api_data)

        # Insert game
        game_id = insert_game(event_id, white_player_id, black_player_id, result, event_date, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination)

        # Insert the moves
        if moves:
            move_list = parse_moves(moves)
            insert_move(game_id, move_list)

        record_count += 1
        print(f"Inserted game {record_count}")

    # Commit and close the connection
    conn.commit()

# Parsing moves from PGN
def parse_moves(moves_str):
    move_pattern = re.compile(r'\d+\.\s*([a-zA-Z0-9+#-]+)\s+([a-zA-Z0-9+#-]+)')
    move_pairs = move_pattern.findall(moves_str)

    if len(move_pairs) % 2 != 0:
        last_white_move = move_pairs[-1][0]
        move_pairs[-1] = (last_white_move, None)

    return [pair for pair in move_pairs if pair is not None]

def insert_move(game_id, moves):
    move_number = 1
    for move_pair in moves:
        if move_pair is not None and len(move_pair) == 2:
            white_move, black_move = move_pair
            cur.execute("""
                INSERT INTO gamemoves (gameid, movenumber, whitemove, blackmove)
                VALUES (%s, %s, %s, %s);
            """, (game_id, move_number, white_move, black_move if black_move else None))
            move_number += 1

def process_pgn_and_tournaments(pgn_file_path):
    with open(pgn_file_path, 'r') as file:
        pgn_data = file.read()
    
    # Regex to find all tournament IDs in the PGN file (if available)
    tournament_pattern = r'\[Event "Rated.*tournament.*https://lichess.org/tournament/([^"]+)"\]'
    tournament_ids = re.findall(tournament_pattern, pgn_data)

    for tournament_id in tournament_ids:
        fetch_and_insert_tournament(tournament_id)
    
    # Parse and insert game data from PGN file
    parse_pgn_and_insert(pgn_file_path)

# Run the function to insert data from the PGN file
#parse_pgn_and_insert('lichess_db_standard_rated_2013-01.pgn')
process_pgn_and_tournaments('lichess_db_standard_rated_2013-01.pgn')
print("Successfully inserted")

# Close the connection
cur.close()
conn.close()
