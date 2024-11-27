import re

# Input moves string
moves_data = "1. e4 e5 2. Bc4 Nf6 3. d3 Bc5 4. Bg5 Bxf2+ 5. Kxf2 Nxe4+ 6. dxe4 Qxg5 7. Nf3 Qf6 8. Qd5 Nc6 9. Rf1 O-O 10. Kg1 Nb4 11. Qxe5 Qxe5 12. Nxe5 Nxc2 13. Bxf7+ Kh8 14. Bc4 Rxf1+ 15. Bxf1 Nxa1 16. Nc3 Nc2 17. Nd5 c6 18. Ne7 d6 19. Nf7# 1-0"

# Split the moves based on the move number pattern
moves = re.split(r'\d+\.', moves_data)[1:]  # Ignore the first split (empty string before "1.")

# Parse the moves into white and black
parsed_moves = []
for move_number, move in enumerate(moves, start=1):
    move_parts = move.strip().split()  # Split the moves
    white_move = move_parts[0]  # First part is always the white move
    black_move = move_parts[1] if len(move_parts) > 1 else None  # Second part is black move if it exists
    parsed_moves.append((move_number, white_move, black_move))

# Print parsed moves
print("Parsed Moves (moveNumber, whiteMove, blackMove):")
for move in parsed_moves:
    print(move)

# SQL Insert Statement (example)
insert_statements = []
gameID = 1  # Example gameID
for move_number, white_move, black_move in parsed_moves:
    insert_statements.append(
        f"INSERT INTO GameMoves (gameID, moveNumber, whiteMove, blackMove) VALUES ({gameID}, {move_number}, '{white_move}', '{black_move if black_move else 'NULL'}');"
    )

# Print SQL insert statements
print("\nSQL Insert Statements:")
for stmt in insert_statements:
    print(stmt)
