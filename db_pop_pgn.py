import psycopg2 # type: ignore
from psycopg2 import sql # type: ignore
import re

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

# Function to insert player data
def insert_player(player_name, elo, rating_diff, player_type):
    cur.execute("""
        INSERT INTO player (playername, elo, ratingdiff, playertype)
        VALUES (%s, %s, %s, %s)
        RETURNING playerID;
    """, (player_name, elo, rating_diff, player_type))
    player_id = cur.fetchone()[0]
    return player_id

# Function to insert event data
def insert_event(event_name, event_type, event_date, time_control, termination, url):
    cur.execute("""
        INSERT INTO event (eventName, eventtype, eventdate, timecontrol, termination, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING eventID;
    """, (event_name, event_type, event_date, time_control, termination, url))
    event_id = cur.fetchone()[0]
    return event_id

# Function to insert game data
def insert_game(event_id, white_player_id, black_player_id, result, date_time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination):
    cur.execute("""
        INSERT INTO game (eventid, whitePlayerid, blackPlayerid, result, dateTime_, whiteelo, blackelo, whiteratingdiff, blackratingdiff, eco, opening, timecontrol, termination)
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

# safely convert Elo ratings and rating differences --> terminal error
def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return None  # or you can return 0 if that's preferable

def parse_pgn_and_insert(pgn_file_path):
    with open(pgn_file_path, 'r') as file:
        pgn_data = file.read()

    # Regular expression patterns to capture the PGN details
    game_pattern = r'\[Event "([^"]+)"\].*?\[Site "([^"]+)"\].*?\[White "([^"]+)"\].*?\[Black "([^"]+)"\].*?\[Result "([^"]+)"\].*?\[UTCDate "([^"]+)"\].*?\[UTCTime "([^"]+)"\].*?\[WhiteElo "([^"]+)"\].*?\[BlackElo "([^"]+)"\].*?\[WhiteRatingDiff "([^"]+)"\].*?\[BlackRatingDiff "([^"]+)"\].*?\[ECO "([^"]+)"\].*?\[Opening "([^"]+)"\].*?\[TimeControl "([^"]+)"\].*?\[Termination "([^"]+)"\](.*?)\n\n'

    # Find all games in the PGN file
    games = re.findall(game_pattern, pgn_data, re.DOTALL)

    for game in games:
        event_name, site, white_name, black_name, result, date, time, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination, moves = game

        # Parse event and insert into the database
        event_date = f"{date} {time}"  # Combining date and time
        event_id = insert_event(event_name, 'Regular', event_date, time_control, termination, site)

        # Safely convert Elo ratings and rating differences
        white_elo = safe_int(white_elo)
        black_elo = safe_int(black_elo)
        white_rating_diff = safe_int(white_rating_diff)
        black_rating_diff = safe_int(black_rating_diff)

        # Insert players
        white_player_id = insert_player(white_name, white_elo, white_rating_diff, 'White')
        black_player_id = insert_player(black_name, black_elo, black_rating_diff, 'Black')

        # Insert game
        game_id = insert_game(event_id, white_player_id, black_player_id, result, event_date, white_elo, black_elo, white_rating_diff, black_rating_diff, eco, opening, time_control, termination)

        # Parse game moves
        move_list = moves.strip().split(" ")
        move_number = 1
        for i in range(0, len(move_list), 2):
            white_move = move_list[i]
            black_move = move_list[i + 1] if i + 1 < len(move_list) else None
            insert_game_moves(game_id, move_number, white_move, black_move)
            move_number += 1

    # Commit and close the connection
    conn.commit()

# Run the function to insert data from the PGN file
parse_pgn_and_insert('lichess_db_standard_rated_2013-01.pgn')

# Close the connection
cur.close()
conn.close()
