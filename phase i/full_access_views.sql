-- PHASE I

--Examples of a hard-coded views that filters some rows and columns, based on the user
--access rights (i.e. a full access user may see all columns while a low-key user may only see certain columns and for a subset of data.

-- Full access view for Player (Player table)
CREATE OR REPLACE VIEW full_access_player_view AS
SELECT playerID, playerName, elo, ratingDiff, playerType
FROM player;  -- 'Player' table name should be lowercase to match the schema.

-- Full access view for Event (Event table)
CREATE OR REPLACE VIEW full_access_event_view AS
SELECT event_id, event_name, event_date, time_control, termination, url, tournament_id
FROM event;  -- 'Event' table name should be lowercase to match the schema.

-- Full access view for Game (Game table)
CREATE OR REPLACE VIEW full_access_game_view AS
SELECT gameID, event_id, whitePlayerID, blackPlayerID, result, dateTime_, whiteElo, blackElo, 
       whiteRatingDiff, blackRatingDiff, eco, opening, timeControl, termination
FROM game;  -- 'Game' table name should be lowercase to match the schema.

-- Full access view for GameMoves (GameMoves table)
CREATE OR REPLACE VIEW full_access_game_moves_view AS
SELECT moveID, gameID, moveNumber, whiteMove, blackMove
FROM gamemoves;  -- 'GameMoves' table name should be lowercase to match the schema.

-- Full access view for Tournament (Tournament table)
CREATE OR REPLACE VIEW full_access_tournament_view AS
SELECT id, tournament_id, starts_at, system, full_name, clock_limit, clock_increment, 
       minutes, variant, nb_players, rated, berserkable, is_finished
FROM tournament;  -- 'Tournament' table name should be lowercase to match the schema.
