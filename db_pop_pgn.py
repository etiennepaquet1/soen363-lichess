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
    # Ensure the Elo rating is within the domain limits
    elo = safe_int(elo)
    if elo is None or not (0 <= elo <= 3000):
        print(f"Invalid Elo rating for player {player_name}. Skipping player.")
        return None

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
    """ Safely convert a value to an integer, return None if invalid. """
    if value is None:
        return None  # Or return a default value like 0 if that fits your logic
    try:
        return int(value)
    except (ValueError, TypeError):
        return None  # Return None if conversion fails


RECORD_LIMIT = 200  # we have more than 20K lines of data in the .pgn file, it takes a lot of time to process all those lines, for this, we limited the reading to 200 first records only

def parse_pgn_and_insert(pgn_file_path):
    with open(pgn_file_path, 'r') as file:
        pgn_data = file.read()

    # Regular expression patterns to capture the PGN details
    # The moves section is now captured more reliably at the end
    game_pattern = r'\[Event "([^"]+)"\].*?\[Site "([^"]+)"\].*?\[White "([^"]+)"\].*?\[Black "([^"]+)"\].*?\[Result "([^"]+)"\].*?\[UTCDate "([^"]+)"\].*?\[UTCTime "([^"]+)"\].*?\[WhiteElo "([^"]+)"\].*?\[BlackElo "([^"]+)"\].*?\[WhiteRatingDiff "([^"]+)"\].*?\[BlackRatingDiff "([^"]+)"\].*?\[ECO "([^"]+)"\].*?\[Opening "([^"]+)"\].*?\[TimeControl "([^"]+)"\].*?\[Termination "([^"]+)"\](.*?)\n*(?=\[|\Z)'

    # Find all games in the PGN file
    games = re.findall(game_pattern, pgn_data, re.DOTALL)

    record_count = 0

    for game in games:

        if record_count >= RECORD_LIMIT:
            print(f"Record limit of {RECORD_LIMIT} reached. Stopping insertion.")
            break

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

        # Insert the moves
        if moves:
            move_list = parse_moves(moves)
            #for move in move_list: 
            insert_move(game_id, move_list)

        record_count += 1
        print(record_count)

    # Commit and close the connection
    conn.commit()

def parse_moves(moves_str):
    """
    Parse a string of moves into a list of individual moves, 
    alternating between White and Black's moves.
    If there's an odd number of moves, the last Black move will be None.
    """
    move_pattern = re.compile(r'\d+\.\s*([a-zA-Z0-9+#-]+)\s+([a-zA-Z0-9+#-]+)')
    move_pairs = move_pattern.findall(moves_str)

    # If the number of move pairs is odd, we add a None for the missing Black move
    if len(move_pairs) % 2 != 0:
        last_white_move = move_pairs[-1][0]
        move_pairs[-1] = (last_white_move, None)

    # Filter out any move pairs that might be malformed or None / malformed pairs get inserted as null
    return [pair for pair in move_pairs if pair is not None]


def insert_move(game_id, moves):
    """
    Insert moves into the database, alternating between white and black moves.
    If there's an odd number of moves, the last Black move will be None.
    """
    move_number = 1
    for move_pair in moves:
        # Ensure move_pair is not None and contains exactly two elements
        if move_pair is not None and len(move_pair) == 2:
            white_move, black_move = move_pair
            print(f"Inserting move: {white_move} and {black_move}")  # Debugging: log the moves being inserted
            # Insert the move for White and Black
            cur.execute("""
                INSERT INTO gamemoves (gameid, movenumber, whitemove, blackmove)
                VALUES (%s, %s, %s, %s);
            """, (game_id, move_number, white_move, black_move if black_move else None))
            move_number += 1
        else:
            print(f"Skipping invalid move pair: {move_pair}")  # debug test: log invalid pairs

# Run the function to insert data from the PGN file
parse_pgn_and_insert('lichess_db_standard_rated_2013-01.pgn')
print("Successfully inserted")

# Close the connection
cur.close()
conn.close()
