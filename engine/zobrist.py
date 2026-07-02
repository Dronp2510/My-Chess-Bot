import random
import hashlib

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


def status_key(row, col, status_name):
    """
    Deterministic 64-bit key for a status effect occupying a square.

    IMPORTANT: unlike the piece/castling/en-passant keys above, this is NOT
    generated from the module-level `random` sequence. Status names are
    defined per-Path (Fortune, future Paths, etc.) and we don't want key
    generation order -- which depends on import order across an expanding
    set of Path modules -- to silently change historical hash values.
    Hashing a stable string instead makes this key reproducible forever,
    regardless of how many Paths get added later.
    """
    raw = f"status|{row}|{col}|{status_name}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def compute_full_hash(gs):

    h = 0

    for row in range(8):
        for col in range(8):

            piece = gs.board[row][col]

            if piece != "--":
                h ^= zobrist_piece_keys[piece][row][col]

    if gs.white_to_move:
        h ^= side_to_move_key

    for right, enabled in gs.castling_rights.items():

        if enabled:
            h ^= castling_keys[right]

    if gs.en_passant_square:

        ep_file = gs.en_passant_square[1]

        h ^= en_passant_keys[ep_file]

    return h