--------------------------------- Database Design --------------------------------------

-- Players (Users) -- ISA relationships
CREATE TABLE Player (
    playerID SERIAL PRIMARY KEY,
    playerName VARCHAR(255) NOT NULL,
    elo INT,
    ratingDiff INT,
    playerType VARCHAR(10) CHECK (playerType IN ('White', 'Black')) NOT NULL
);

-- Events  --- ISA relationship
CREATE TABLE Event (
    eventID SERIAL PRIMARY KEY,
    eventName VARCHAR(255) NOT NULL,
    eventType VARCHAR(20) CHECK (eventType IN ('Tournament', 'Regular')) NOT NULL,
    eventDate DATE NOT NULL,
    timeControl VARCHAR(20),
    termination VARCHAR(20),
    --opening VARCHAR(100), -> it's in game table 
    URL VARCHAR(255)
);

-- Weak Entity: Games (linked to Event)
CREATE TABLE Game (
    gameID SERIAL PRIMARY KEY,
    eventID INT NOT NULL,
    whitePlayerID INT REFERENCES Player(PlayerID),
    blackPlayerID INT REFERENCES Player(PlayerID),
    result VARCHAR(10) CHECK (Result IN ('1-0', '0-1', '1/2-1/2')) NOT NULL,
    dateTime_ TIMESTAMP,
    whiteElo INT,
    blackElo INT,
    whiteRatingDiff INT,
    blackRatingDiff INT,
    eco VARCHAR(5),
    opening VARCHAR(100),
    timeControl VARCHAR(20),
    termination VARCHAR(20),
    FOREIGN KEY (EventID) REFERENCES Event(eventID) ON DELETE CASCADE
);

-- Game Moves (for detailed PGN data storage) -- fully dependent on Game -> weak entity as well
CREATE TABLE GameMoves (
    moveID SERIAL PRIMARY KEY,
    gameID INT REFERENCES game(gameID) ON DELETE CASCADE,
    moveNumber INT,
    whiteMove VARCHAR(10),
    blackMove VARCHAR(10)
);

-- Player Statistics View
CREATE VIEW PlayerStatistics AS
SELECT
    p.playerID,
    p.playerName,
    SUM(CASE WHEN g.Result = '1-0' AND g.whitePlayerID = p.PlayerID THEN 1 
             WHEN g.Result = '0-1' AND g.blackPlayerID = p.PlayerID THEN 1 ELSE 0 END) AS Wins,
    SUM(CASE WHEN g.Result = '0-1' AND g.whitePlayerID = p.PlayerID THEN 1 
             WHEN g.Result = '1-0' AND g.blackPlayerID = p.PlayerID THEN 1 ELSE 0 END) AS Losses,
    SUM(CASE WHEN g.Result = '1/2-1/2' AND (g.whitePlayerID = p.PlayerID OR g.BlackPlayerID = p.PlayerID) THEN 1 ELSE 0 END) AS Draws,
    AVG(CASE WHEN g.WhitePlayerID = p.PlayerID THEN g.WhiteElo ELSE g.BlackElo END) AS AverageElo,
    AVG(CASE WHEN g.WhitePlayerID = p.PlayerID THEN g.WhiteRatingDiff ELSE g.BlackRatingDiff END) AS AverageRatingDiff
FROM player p
LEFT JOIN game g ON (g.WhitePlayerID = p.PlayerID OR g.BlackPlayerID = p.PlayerID)
GROUP BY p.PlayerID, p.PlayerName;

-- Insert Example Data (just for tests)
INSERT INTO Event (EventName, EventType, EventDate, TimeControl, Termination, Opening, URL)
VALUES ('Rated Classical game', 'Regular', '2012-12-31', '600+8', 'Normal', 'French Defense: Normal Variation', 'https://lichess.org/j1dkb5dw');

INSERT INTO Player (PlayerName, Elo, RatingDiff, PlayerType)
VALUES ('BFG9k', 1639, 5, 'White'), ('mamalak', 1403, -8, 'Black');

INSERT INTO Game (EventID, WhitePlayerID, BlackPlayerID, Result, DateTime, WhiteElo, BlackElo, WhiteRatingDiff, BlackRatingDiff, ECO, Opening, TimeControl, Termination)
VALUES (1, 1, 2, '1-0', '2012-12-31 23:01:03', 1639, 1403, 5, -8, 'C00', 'French Defense: Normal Variation', '600+8', 'Normal');

INSERT INTO GameMoves (GameID, MoveNumber, WhiteMove, BlackMove)
VALUES (1, 1, 'e4', 'e6'), (1, 2, 'd4', 'b6');
