import json


def board_to_fen(board):
    rows = []

    for row in board:
        fen_row = ""
        empty = 0

        for piece in row:
            if piece == "--":
                empty += 1
                continue

            if empty:
                fen_row += str(empty)
                empty = 0

            color = piece[0]
            p = piece[1:]

            letter_map = {
                "p": "p",
                "r": "r",
                "kn": "n",
                "b": "b",
                "q": "q",
                "k": "k",
            }

            symbol = letter_map[p]

            if color == "w":
                symbol = symbol.upper()

            fen_row += symbol

        if empty:
            fen_row += str(empty)

        rows.append(fen_row)

    return "/".join(rows)


def fen_to_board(fen_board):
    board = []

    piece_map = {
        "p": "p",
        "r": "r",
        "n": "kn",
        "b": "b",
        "q": "q",
        "k": "k",
    }

    for row_str in fen_board.split("/"):
        row = []

        for c in row_str:

            if c.isdigit():
                row.extend(["--"] * int(c))
                continue

            color = "w" if c.isupper() else "b"
            piece = piece_map[c.lower()]

            row.append(color + piece)

        board.append(row)

    return board


def metadata_to_string(metadata):
    return json.dumps(metadata, separators=(",", ":"))


def string_to_metadata(text):
    if not text:
        return {}

    try:
        return json.loads(text)
    except Exception:
        return {}