-- An example of a complex referential integrity (i.e. using assertions or triggers).

-- function that will be triggered before an INSERT into the game table
CREATE OR REPLACE FUNCTION check_player_exists() 
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the white player exists
    IF NOT EXISTS (SELECT 1 FROM player WHERE playerID = NEW.whitePlayerID) THEN
        RAISE EXCEPTION 'White player % does not exist', NEW.whitePlayerID;
    END IF;

    -- Check if the black player exists
    IF NOT EXISTS (SELECT 1 FROM player WHERE playerID = NEW.blackPlayerID) THEN
        RAISE EXCEPTION 'Black player % does not exist', NEW.blackPlayerID;
    END IF;

    -- If both players exist, allow the insert
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creating the trigger to invoke the above function before inserting a new game
CREATE TRIGGER check_players_before_game_insert
BEFORE INSERT ON game
FOR EACH ROW
EXECUTE FUNCTION check_player_exists();

