-- PHASE I : 

--Examples of a hard-coded views that filters some rows and columns, based on the user
--access rights (i.e. a full access user may see all columns while a low-key user may only see certain columns and for a subset of data.

CREATE OR REPLACE VIEW restricted_player_view AS
SELECT playerID, playerName, playerType
FROM Player;

CREATE OR REPLACE VIEW restricted_event_view AS
SELECT eventID, eventName, eventDate, eventType
FROM Event;

CREATE OR REPLACE VIEW restricted_game_view AS
SELECT gameID, eventID, whitePlayerID, blackPlayerID, result, dateTime_
FROM Game
WHERE result = '1-0' OR result = '0-1';  -- Restrict to completed games

CREATE OR REPLACE VIEW restricted_game_moves_view AS
SELECT moveID, gameID, moveNumber, whiteMove, blackMove
FROM GameMoves
WHERE moveNumber <= 20;  -- Limit the number of moves shown (e.g., first 20 moves)
