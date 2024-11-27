-- PHASE I : 

--Examples of a hard-coded views that filters some rows and columns, based on the user
--access rights (i.e. a full access user may see all columns while a low-key user may only see certain columns and for a subset of data.

-- Restricted access view for Player (Player table)
CREATE OR REPLACE VIEW restricted_player_view AS
SELECT playerID, playerName, playerType
FROM player;  -- 'Player' table name should be lowercase to match the schema.

-- Restricted access view for Event (Event table)
CREATE OR REPLACE VIEW restricted_event_view AS
SELECT event_id, event_name, event_date, event_type
FROM event;  -- 'Event' table name should be lowercase to match the schema.

-- Restricted access view for Game (Game table)
CREATE OR REPLACE VIEW restricted_game_view AS
SELECT gameID, event_id, whitePlayerID, blackPlayerID, result, dateTime_
FROM game
WHERE result = '1-0' OR result = '0-1';  -- Restrict to completed games

-- Restricted access view for GameMoves (GameMoves table)
CREATE OR REPLACE VIEW restricted_game_moves_view AS
SELECT moveID, gameID, moveNumber, whiteMove, blackMove
FROM gamemoves
WHERE moveNumber <= 20;  -- Limit the number of moves shown (e.g., first 20 moves)

-- Restricted access view for Tournament (Tournament table)
CREATE OR REPLACE VIEW restricted_tournament_view AS
SELECT tournament_id, full_name, starts_at, is_finished
FROM tournament;  -- 'Tournament' table name should be lowercase to match the schema.
