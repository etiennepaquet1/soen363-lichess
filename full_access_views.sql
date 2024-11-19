-- PHASE I : 

--Examples of a hard-coded views that filters some rows and columns, based on the user
--access rights (i.e. a full access user may see all columns while a low-key user may only see certain columns and for a subset of data.


CREATE OR REPLACE VIEW full_access_player_view AS
SELECT playerID, playerName, elo, ratingDiff, playerType
FROM Player;

CREATE OR REPLACE VIEW full_access_event_view AS
SELECT eventID, eventName, eventType, eventDate, timeControl, termination, URL
FROM Event;

CREATE OR REPLACE VIEW full_access_game_view AS
SELECT gameID, eventID, whitePlayerID, blackPlayerID, result, dateTime_, whiteElo, blackElo, 
       whiteRatingDiff, blackRatingDiff, eco, opening, timeControl, termination
FROM Game;

CREATE OR REPLACE VIEW full_access_game_moves_view AS
SELECT moveID, gameID, moveNumber, whiteMove, blackMove
FROM GameMoves;
