-- Basic SELECT with Simple WHERE Clause
SELECT playerName, elo
FROM Player
WHERE elo > 2000;

-- Basic SELECT with GROUP BY Clause (Without HAVING Clause)
SELECT eventType, COUNT(*) AS eventCount
FROM Event
GROUP BY eventType;

-- Basic SELECT with GROUP BY Clause (With HAVING Clause)
SELECT eventType, COUNT(*) AS eventCount
FROM Event
GROUP BY eventType
HAVING COUNT(*) > 5;

-- Simple JOIN Query
SELECT g.gameID, pw.playerName AS whitePlayer, pb.playerName AS blackPlayer, g.result
FROM Game g
JOIN Player pw ON g.whitePlayerID = pw.playerID
JOIN Player pb ON g.blackPlayerID = pb.playerID;

-- Equivalent Using Cartesian Product
SELECT g.gameID, pw.playerName AS whitePlayer, pb.playerName AS blackPlayer, g.result
FROM Game g, Player pw, Player pb
WHERE g.whitePlayerID = pw.playerID AND g.blackPlayerID = pb.playerID;

-- Demonstrating Various JOIN Types
-- Inner Join
SELECT p.playerName, g.gameID
FROM Player p
JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Left Outer Join
SELECT p.playerName, g.gameID
FROM Player p
LEFT JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Right Outer Join
SELECT p.playerName, g.gameID
FROM Player p
RIGHT JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Full Outer Join
SELECT p.playerName, g.gameID
FROM Player p
FULL OUTER JOIN Game g ON (p.playerID = g.whitePlayerID OR p.playerID = g.blackPlayerID);

-- Demonstrating Use of NULL Values
SELECT playerName
FROM Player
WHERE elo IS NULL;

SELECT gameID
FROM Game
WHERE termination IS NULL;
