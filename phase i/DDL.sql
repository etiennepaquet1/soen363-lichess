--------------------------------- Database Design --------------------------------------

-- Statement to determine the size of the database : should be higher than 300MB
--SELECT pg_size_pretty(pg_database_size('chess_db'));


-- DROP and CREATE ENUM TYPE player_role
DROP TYPE IF EXISTS player_role;
CREATE TYPE player_role AS ENUM ('White', 'Black');

-- DROP and CREATE DOMAIN elo_rating
DROP DOMAIN IF EXISTS elo_rating;
CREATE DOMAIN elo_rating AS INT CHECK (VALUE >= 0 AND VALUE <= 3000);

-- CREATE TABLE player || -- ISA relationships
CREATE TABLE IF NOT EXISTS player (
    playerID SERIAL PRIMARY KEY,
    playerName VARCHAR(255) NOT NULL,
    gamesPlayed INT, -- API
    playTimeTotal BIGINT, -- API
    winCount INT, -- API
    drawCount INT, -- API
    lossCount INT, -- API
    lastOnline TIMESTAMP, -- API
    isStreaming BOOLEAN, -- API
    elo elo_rating,  -- using the custom domain
    ratingDiff INT,
    playerType player_role NOT NULL  -- using the ENUM type
);

-- DROP and CREATE ENUM TYPE event_type
DROP TYPE IF EXISTS event_type;
CREATE TYPE event_type AS ENUM ('Tournament', 'Regular');

-- CREATE TABLE tournament
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

-- Events  --- ISA relationship || regular or tournament
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

-- Weak Entity: Games (linked to Event)
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

-- CREATE TABLE gamemoves -- Game Moves (for detailed PGN data storage) -- fully dependent on Game -> weak entity as well
CREATE TABLE IF NOT EXISTS gamemoves (
    moveID SERIAL PRIMARY KEY,
    gameID INT REFERENCES Game(gameID) ON DELETE CASCADE,
    moveNumber INT,
    whiteMove VARCHAR(10),
    blackMove VARCHAR(10)
);
