import random

PIECES = [
    "wp", "wr", "wkn", "wb", "wq", "wk",
    "bp", "br", "bkn", "bb", "bq", "bk"
]

zobrist_piece_keys = {}

for piece in PIECES:

    zobrist_piece_keys[piece] = []

    for row in range(8):

        row_keys = []

        for col in range(8):

            row_keys.append(
                random.getrandbits(64)
            )

        zobrist_piece_keys[piece].append(row_keys)

side_to_move_key = random.getrandbits(64)