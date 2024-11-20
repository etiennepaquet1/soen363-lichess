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
