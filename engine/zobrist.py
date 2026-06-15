import random

random.seed(2025)

PIECES = [
    "wp", "wr", "wkn", "wb", "wq", "wk",
    "bp", "br", "bkn", "bb", "bq", "bk"
]

zobrist_piece_keys = {}

for piece in PIECES:

    zobrist_piece_keys[piece] = [
        [random.getrandbits(64) for _ in range(8)]
        for _ in range(8)
    ]

# side to move
side_to_move_key = random.getrandbits(64)

# castling rights
castling_keys = {
    "wks": random.getrandbits(64),
    "wqs": random.getrandbits(64),
    "bks": random.getrandbits(64),
    "bqs": random.getrandbits(64)
}

# en passant file hashes
en_passant_keys = [
    random.getrandbits(64)
    for _ in range(8)
]