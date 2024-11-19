import psycopg2 # type: ignore
from psycopg2 import sql # type: ignore

# Database connection details
host = "localhost"
port = "5433"
dbname = "chess_db"
user = "chessgeeks"
password = "soen363"


try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    cursor = conn.cursor()

    # TYPE 
    cursor.execute("""
    DROP TYPE IF EXISTS player_role;
    CREATE TYPE player_role AS ENUM ('White', 'Black');
    """)

    # DOMAIN
    cursor.execute("""
    DROP DOMAIN IF EXISTS elo_rating;
    CREATE DOMAIN elo_rating AS INT CHECK (VALUE >= 0 AND VALUE <= 3000);
    """)

    # Player table - ISA TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player (
        playerID SERIAL PRIMARY KEY,
        playerName VARCHAR(255) NOT NULL,
        elo elo_rating,  -- using the custom domain
        --elo INT,
        ratingDiff INT,
        playerType player_role NOT NULL  -- using the ENUM type
        --playerType VARCHAR(10) CHECK (playerType IN ('White', 'Black')) NOT NULL
    );
    """)

    # TYPE 
    cursor.execute("""
    DROP TYPE IF EXISTS event_type;
    CREATE TYPE event_type AS ENUM ('Tournament', 'Regular');
    """)

    # Event table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event (
        eventID SERIAL PRIMARY KEY,
        eventName VARCHAR(255) NOT NULL,
        eventtype event_type NOT NULL,
        --eventType VARCHAR(20) CHECK (eventType IN ('Tournament', 'Regular')) NOT NULL,
        eventDate DATE NOT NULL,
        timeControl VARCHAR(20),
        termination VARCHAR(20),
        URL VARCHAR(255)
    );
    """)

    # Game table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game (
        gameID SERIAL PRIMARY KEY,
        eventID INT NOT NULL,
        whitePlayerID INT REFERENCES Player(playerID),
        blackPlayerID INT REFERENCES Player(playerID),
        result VARCHAR(10) CHECK (result IN ('1-0', '0-1', '1/2-1/2')) NOT NULL,
        dateTime_ TIMESTAMP,
        whiteElo INT,
        blackElo INT,
        whiteRatingDiff INT,
        blackRatingDiff INT,
        eco VARCHAR(5),
        opening VARCHAR(100),
        timeControl VARCHAR(20),
        termination VARCHAR(20),
        FOREIGN KEY (eventID) REFERENCES Event(eventID) ON DELETE CASCADE
    );
    """)

    # Game move table -- WEAK ENTITY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamemoves (
        moveID SERIAL PRIMARY KEY,
        gameID INT REFERENCES Game(gameID) ON DELETE CASCADE,
        moveNumber INT,
        whiteMove VARCHAR(10),
        blackMove VARCHAR(10)
    );
    """)

    # ---------------------- Full access views ---------------------------
    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_player_view AS
    SELECT playerID, playerName, elo, ratingDiff, playerType
    FROM Player;
    """)

    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_event_view AS
    SELECT eventID, eventName, eventType, eventDate, timeControl, termination, URL
    FROM Event;
    """)

    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_game_view AS
    SELECT gameID, eventID, whitePlayerID, blackPlayerID, result, dateTime_, 
           whiteElo, blackElo, whiteRatingDiff, blackRatingDiff, eco, opening, 
           timeControl, termination
    FROM Game;
    """)

    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_game_moves_view AS
    SELECT moveID, gameID, moveNumber, whiteMove, blackMove
    FROM GameMoves;
    """)
    # -------------------------------------------------------------------------
    # ------------------------- Restricted access views -----------------------
    cursor.execute("""
    CREATE OR REPLACE VIEW restricted_player_view AS
    SELECT playerID, playerName, playerType
    FROM Player;
    """)

    cursor.execute("""
    CREATE OR REPLACE VIEW restricted_event_view AS
    SELECT eventID, eventName, eventDate, eventType
    FROM Event;
    """)

    cursor.execute("""
    CREATE OR REPLACE VIEW restricted_game_view AS
    SELECT gameID, eventID, whitePlayerID, blackPlayerID, result, dateTime_
    FROM Game
    WHERE result = '1-0' OR result = '0-1';  -- Restrict to completed games
    """)

    cursor.execute("""
    CREATE OR REPLACE VIEW restricted_game_moves_view AS
    SELECT moveID, gameID, moveNumber, whiteMove, blackMove
    FROM GameMoves
    WHERE moveNumber <= 20;  -- Limit the number of moves shown (e.g., first 20 moves)
    """)
    # -------------------------------------------------------------------------

    # ----- Trigger function to ensure valid game result --------
    cursor.execute("""
    CREATE OR REPLACE FUNCTION validate_game_result()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Check if the result is valid
        IF NEW.result NOT IN ('1-0', '0-1', '1/2-1/2') THEN
            RAISE EXCEPTION 'Invalid game result: %', NEW.result;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Trigger to execute the function before a new row is inserted or updated in the game table
    cursor.execute("""
    CREATE TRIGGER trigger_validate_game_result
    BEFORE INSERT OR UPDATE ON game
    FOR EACH ROW
    EXECUTE FUNCTION validate_game_result();
    """)
    # -------------------------------------------------------------------------

    conn.commit()

    print("Schema, views and function created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()
