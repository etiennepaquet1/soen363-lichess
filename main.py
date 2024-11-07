import time

import chess.pgn
import requests

pgn = open("lichess_db_standard_rated_2013-01.pgn")

while True:
    game = chess.pgn.read_game(pgn)
    print(game.headers.get("Site"))
