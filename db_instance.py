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

    # Player table - ISA TABLE -- White player vs Black Player
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player (
        playerID SERIAL PRIMARY KEY,
        playerName VARCHAR(255) NOT NULL,
        gamesPlayed INT, --API
        playTimeTotal BIGINT, --API
        winCount INT, -- API
        drawCount INT, -- API
        lossCount INT, -- API
        lastOnline TIMESTAMP, -- API
        isStreaming BOOLEAN, -- API
        elo elo_rating,  -- using the custom domain
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

     #tournament -- API -- before game because game uses tournament
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournament (
        id SERIAL PRIMARY KEY,
        tournament_id VARCHAR(255) NOT NULL,           -- Tournament ID from the API (e.g., may24lta)
        starts_at TIMESTAMPTZ,                          -- Tournament start time
        system VARCHAR(255),                            -- System type (e.g., arena)
        full_name VARCHAR(255),                         -- Full name of the tournament
        clock_limit INT,                                -- Clock limit (in seconds)
        clock_increment INT,                            -- Clock increment (in seconds)
        minutes INT,                                    -- Duration of the tournament in minutes
        variant VARCHAR(255),                           -- Variant type (e.g., standard)
        nb_players INT,                                 -- Number of players
        rated BOOLEAN,                                  -- Whether the tournament is rated
        berserkable BOOLEAN,                            -- Whether players can berserk
        is_finished BOOLEAN,                            -- Whether the tournament is finished
        UNIQUE(tournament_id)                           -- Ensure uniqueness of tournament IDs
    );

    """)

    # Event table -- ISA RELATIONSHIP : REGULAR OR TOURNAMENT
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event (
        event_id SERIAL PRIMARY KEY,
        event_name VARCHAR(255),        -- Event name (e.g., "Titled Arena May 2024")
        event_type VARCHAR(255),        -- Event type (e.g., "Regular" OR "TOURNAMENT")
        event_date TIMESTAMPTZ,         -- Date of the event
        time_control VARCHAR(255),      -- Time control setting (e.g., "bullet")
        termination VARCHAR(255),       -- Termination condition (e.g., "normal")
        url TEXT,                       -- URL to the event
        tournament_id VARCHAR(255),     -- Foreign key linking to the tournament
        FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id)
        );
    """)

    # Game table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game (
        gameID SERIAL PRIMARY KEY,
        event_id INT NOT NULL,
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
        FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE
    );
""")

    # Game move table -- WEAK ENTITY -- fully dependant on Game
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamemoves (
        moveID SERIAL PRIMARY KEY,
        gameID INT REFERENCES Game(gameID) ON DELETE CASCADE,
        moveNumber INT,
        whiteMove VARCHAR(10),
        blackMove VARCHAR(10)
    );
    """)

    # Full access views -------------------------------------------
    # player
    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_player_view AS
    SELECT playerID, playerName, elo, ratingDiff, playerType
    FROM player;
    """)

    # event
    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_event_view AS
    SELECT event_id, event_name, event_date, time_control, termination, url, tournament_id
    FROM event;
    """)

    # game
    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_game_view AS
    SELECT gameID, event_id, whitePlayerID, blackPlayerID, result, dateTime_, whiteElo, blackElo, 
        whiteRatingDiff, blackRatingDiff, eco, opening, timeControl, termination
    FROM game;
    """)

    # game moves
    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_game_moves_view AS
    SELECT moveID, gameID, moveNumber, whiteMove, blackMove
    FROM gamemoves;
    """)

    # tournament
    cursor.execute("""
    CREATE OR REPLACE VIEW full_access_tournament_view AS
    SELECT id, tournament_id, starts_at, system, full_name, clock_limit, clock_increment, 
        minutes, variant, nb_players, rated, berserkable, is_finished
    FROM tournament;
    """)

    # Restricted ----------------------------------------
    # Player
    cursor.execute("""
        CREATE OR REPLACE VIEW restricted_player_view AS
        SELECT playerID, playerName, playerType
        FROM player;
    """)

    # Event 
    cursor.execute("""
        CREATE OR REPLACE VIEW restricted_event_view AS
        SELECT event_id, event_name, event_date, event_type
        FROM event;
    """)

    # Game 
    cursor.execute("""
        CREATE OR REPLACE VIEW restricted_game_view AS
        SELECT gameID, event_id, whitePlayerID, blackPlayerID, result, dateTime_
        FROM game
        WHERE result = '1-0' OR result = '0-1';
    """)

    # GameMoves
    cursor.execute("""
        CREATE OR REPLACE VIEW restricted_game_moves_view AS
        SELECT moveID, gameID, moveNumber, whiteMove, blackMove
        FROM gamemoves
        WHERE moveNumber <= 20;
    """)

    # Tournament 
    cursor.execute("""
        CREATE OR REPLACE VIEW restricted_tournament_view AS
        SELECT tournament_id, full_name, starts_at, is_finished
        FROM tournament;
    """)

    # COMPLEX INTEGRITY FUNCTION -> TRIGGERED
    # Check if player exists function
    cursor.execute("""
        CREATE OR REPLACE FUNCTION check_player_exists() 
        RETURNS TRIGGER AS $$
        BEGIN
            -- Check if the white player exists
            IF NOT EXISTS (SELECT 1 FROM player WHERE playerID = NEW.whitePlayerID) THEN
                RAISE EXCEPTION 'White player % does not exist', NEW.whitePlayerID;
            END IF;

            -- Check if the black player exists
            IF NOT EXISTS (SELECT 1 FROM player WHERE playerID = NEW.blackPlayerID) THEN
                RAISE EXCEPTION 'Black player % does not exist', NEW.blackPlayerID;
            END IF;

            -- If both players exist, allow the insert
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Creating the trigger to invoke the above function before inserting a new game
    cursor.execute("""
        CREATE TRIGGER check_players_before_game_insert
        BEFORE INSERT ON game
        FOR EACH ROW
        EXECUTE FUNCTION check_player_exists();
    """)


    conn.commit()

    print("Schema, views and function created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()
