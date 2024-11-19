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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Player (
        playerID SERIAL PRIMARY KEY,
        playerName VARCHAR(255) NOT NULL,
        elo INT,
        ratingDiff INT,
        playerType VARCHAR(10) CHECK (playerType IN ('White', 'Black')) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Event (
        eventID SERIAL PRIMARY KEY,
        eventName VARCHAR(255) NOT NULL,
        eventType VARCHAR(20) CHECK (eventType IN ('Tournament', 'Regular')) NOT NULL,
        eventDate DATE NOT NULL,
        timeControl VARCHAR(20),
        termination VARCHAR(20),
        URL VARCHAR(255)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Game (
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GameMoves (
        moveID SERIAL PRIMARY KEY,
        gameID INT REFERENCES Game(gameID) ON DELETE CASCADE,
        moveNumber INT,
        whiteMove VARCHAR(10),
        blackMove VARCHAR(10)
    );
    """)

    conn.commit()

    print("Schema created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if conn:
        cursor.close()
        conn.close()
