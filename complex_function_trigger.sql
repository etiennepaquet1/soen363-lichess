-- An example of a complex referential integrity (i.e. using assertions or triggers).

-- Trigger function to validate that the game result matches player participation

CREATE OR REPLACE FUNCTION validate_game_result()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the result is valid for the white player
    IF NEW.result = '1-0' AND NEW.whitePlayerID IS NULL THEN
        RAISE EXCEPTION 'White player is missing for this game result.';
    ELSIF NEW.result = '0-1' AND NEW.blackPlayerID IS NULL THEN
        RAISE EXCEPTION 'Black player is missing for this game result.';
    END IF;

    -- Ensure the result corresponds to the correct player (i.e., the winner)
    IF (NEW.result = '1-0' AND NEW.whitePlayerID IS NULL) OR
       (NEW.result = '0-1' AND NEW.blackPlayerID IS NULL) THEN
        RAISE EXCEPTION 'The result does not match the player participation in this game.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger to validate the game result before insertion
CREATE TRIGGER trigger_validate_game_result
BEFORE INSERT ON Game
FOR EACH ROW
EXECUTE FUNCTION validate_game_result();
