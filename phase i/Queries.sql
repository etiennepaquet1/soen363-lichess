-- Basic SELECT with Simple WHERE Clause - tested
SELECT playerName, elo
FROM Player
WHERE elo > 1000;

-- Basic SELECT with GROUP BY Clause (Without HAVING Clause) - tested
SELECT event_type, COUNT(*) AS event_count
FROM event
GROUP BY event_type;

-- Basic SELECT with GROUP BY Clause (With HAVING Clause) - changed because it gives the exact same result as the one above (as if the 'having' has no effect)
SELECT whitePlayerID, COUNT(*) AS games_played
FROM game
GROUP BY whitePlayerID
HAVING COUNT(*) > 5;

-- Simple JOIN Query -- tested 
SELECT g.gameID, pw.playerName AS whitePlayer, pb.playerName AS blackPlayer, g.result
FROM Game g
JOIN Player pw ON g.whitePlayerID = pw.playerID
JOIN Player pb ON g.blackPlayerID = pb.playerID;

-- Equivalent Using Cartesian Product -- tested
SELECT g.gameID, pw.playerName AS whitePlayer, pb.playerName AS blackPlayer, g.result
FROM Game g, Player pw, Player pb
WHERE g.whitePlayerID = pw.playerID AND g.blackPlayerID = pb.playerID;

-- Demonstrating Various JOIN Types
-- Inner Join -- tested
SELECT p.playerName, g.gameID
FROM Player p
JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Left Outer Join -- tested
SELECT p.playerName, g.gameID
FROM Player p
LEFT JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Right Outer Join -- tested
SELECT p.playerName, g.gameID
FROM Player p
RIGHT JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Full Join -> can be performed using a UNION of left and right joins
---SELECT p.playerName, g.gameID -- not working
---FROM Player p
---FULL OUTER JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID); -- ERROR:  FULL JOIN is only supported with merge-joinable or hash-joinable join conditions 

-- (LEFT JOIN)
SELECT p.playerName, g.gameID
FROM player p
LEFT JOIN game g ON p.playerID = g.whitePlayerID

UNION

-- (RIGHT JOIN)
SELECT p.playerName, g.gameID
FROM player p
RIGHT JOIN game g ON p.playerID = g.blackPlayerID;


-- Demonstrating Use of NULL Values
SELECT playerName
FROM Player
WHERE lastOnline IS NULL; -- i have null values only on the lastOnline column

-- The event that are not tournaments (aka. Regular)
SELECT event_name, event_type, termination, time_control
FROM Event
WHERE tournament_id IS NULL;


-- Demonstrate correlated queries (the following 2)

-- Finds players with more wins than losses
SELECT playerName
FROM player p
WHERE (
    SELECT COUNT(*) 
    FROM game g
    WHERE (g.whitePlayerID = p.playerID AND g.result = '1-0') --player from inner query
       OR (g.blackPlayerID = p.playerID AND g.result = '0-1') 
) > (
    SELECT COUNT(*) 
    FROM game g
    WHERE (g.whitePlayerID = p.playerID AND g.result = '0-1') --player from inner query
       OR (g.blackPlayerID = p.playerID AND g.result = '1-0') 
);

-- Finds players who played at least 1 game
SELECT playerName
FROM player p
WHERE EXISTS (
    SELECT 1
    FROM game g
    WHERE (g.whitePlayerID = p.playerID OR g.blackPlayerID = p.playerID) --player from outer query
);

-- Examples of set operations vs their equivalencies without set operation

--Union (berserkable tournaments or tournaments that have over 50 players)
SELECT tournament_id, full_name
FROM tournament
WHERE berserkable = TRUE
UNION
SELECT tournament_id, full_name
FROM tournament
WHERE nb_players > 50;

-- Union without set operation
SELECT tournament_id, full_name
FROM tournament
WHERE berserkable = TRUE OR nb_players > 50;

--Intersect (players with over 100 games played and have a draw count higher than 30)
SELECT playerID, playerName
FROM player
WHERE gamesPlayed > 100

INTERSECT

SELECT playerID, playerName
FROM player
WHERE drawCount > 30;

-- Intersect without set operation
SELECT playerID, playerName
FROM player
WHERE gamesPlayed > 100
AND drawCount > 30;

-- Difference (games where white elo is higher than 1200, but lower than 1500)
SELECT gameID
FROM game g
WHERE g.whiteelo > 1200
EXCEPT
SELECT gameID
FROM game g
WHERE g.whiteelo > 1500

-- Difference without set operation

SELECT g1.gameID
FROM game g1
WHERE g1.whiteelo > 1200
AND NOT EXISTS (
    SELECT 1
    FROM game g2
    WHERE g2.gameID = g1.gameID
    AND g2.whiteelo > 1500
);

-- View with hard-coded criteria

CREATE VIEW high_elo_games AS
SELECT gameID, whitePlayerID, blackPlayerID, whiteelo, blackelo, result
FROM game
WHERE whiteelo > 1500; --Hard-coded criteria with games where white elo is higher than 1500

-- Overlap Contraint where checks if whiteplayerID or blackplayerID exists before inserting)
-- Attempt to insert a game with non-existent players (It will fail)
INSERT INTO game (event_id, whitePlayerID, blackPlayerID, result, dateTime_, whiteElo, blackElo, whiteRatingDiff, blackRatingDiff, eco, opening, timeControl, termination)
VALUES 
(1, 9999, 9998, '1-0', '2024-11-21 10:00:00', 1500, 1400, 10, -10, 'C10', 'French Defense', 'bullet', 'normal');

-- Covering Constraint
-- Attempt to insert a game where result is an illegal value (It will fail)
INSERT INTO game (event_id, whitePlayerID, blackPlayerID, result)
VALUES (4, 1, 2, '3/2');


-- Division operator
-- Find every player who has achieved every type of game termination as white
-- a) rested query using NOT IN

SELECT * FROM game
WHERE whiteplayerid NOT IN (
   SELECT whiteplayerid FROM (
      (SELECT whiteplayerid , termination FROM (SELECT termination FROM event ) AS p CROSS JOIN (SELECT DISTINCT whiteplayerid FROM game) AS sp)
        EXCEPT
       (SELECT whiteplayerid , termination FROM game))
     AS r
);

-- b) correlated query using NOT EXISTS and EXCEPT

SELECT * FROM game AS sx
WHERE NOT EXISTS (
           (SELECT p.termination FROM event AS p )
            EXCEPT
           (SELECT sp.termination FROM game AS sp WHERE sp.whiteplayerid = sx.whiteplayerid )
);



