import psycopg2 # type: ignore
import re
import requests # type: ignore
import datetime

# Database connection parameters -- to be put in .env 
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'chess_db'
DB_USER = 'chessgeeks'
DB_PASSWORD = 'soen363'

API_KEY = 'lip_cCtQVPpg50AfVhvHAiht'  # Lichess API key

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
        last_online = None  # Set to None if no data
    
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


# Function to insert event data
def insert_event(event_name, event_type, event_date, time_control, termination, url):
    """Insert event data."""
    cur.execute("""
        INSERT INTO event (eventName, eventtype, eventdate, timecontrol, termination, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING eventID;
    """, (event_name, event_type, event_date, time_control, termination, url))
    event_id = cur.fetchone()[0]
    return event_id


# Function to insert tournament data
def insert_tournament(tournament_name, start_date, end_date, tournament_type, total_rounds, current_round, event_id):
    cur.execute("""
        INSERT INTO tournament (tournamentName, startDate, endDate, tournamentType, totalRounds, currentRound, eventID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING tournamentID;
    """, (tournament_name, start_date, end_date, tournament_type, total_rounds, current_round, event_id))
    tournament_id = cur.fetchone()[0]
    return tournament_id

# Function to insert game data
def insert_game(event_id, white_player_id, black_player_id, result, date_time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination, tournament_id=None):
    cur.execute("""
        INSERT INTO game (eventid, whitePlayerid, blackPlayerid, result, dateTime_, whiteelo, blackelo, whiteratingdiff, blackratingdiff, eco, opening, timecontrol, termination, tournamentid)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING gameid;
    """, (event_id, white_player_id, black_player_id, result, date_time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination, tournament_id))
    game_id = cur.fetchone()[0]
    return game_id

# Function to insert game moves data
def insert_game_moves(game_id, move_number, white_move, black_move):
    cur.execute("""
        INSERT INTO gamemoves (gameid, movenumber, whitemove, blackmove)
        VALUES (%s, %s, %s, %s);
    """, (game_id, move_number, white_move, black_move))

# safely convert Elo ratings and rating differences
def safe_int(value):
    """Safely convert a value to an integer, return None if invalid."""
    if value is None or value == '?':
        return None  # Return None if value is '?' or None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None  # Return None if conversion fails


RECORD_LIMIT = 20  # Limit to 20 records

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

        # Parse event and insert into the database
        event_date = f"{date} {time}"  # Combining date and time
        event_id = insert_event(event_name, 'Regular', event_date, time_control, termination, site)

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

# Run the function to insert data from the PGN file
parse_pgn_and_insert('lichess_db_standard_rated_2013-01.pgn')
print("Successfully inserted")

# Close the connection
cur.close()
conn.close()
