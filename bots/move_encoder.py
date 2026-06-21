FILES = "abcdefgh"


def move_to_string(move):

    return (
        FILES[move.from_square % 8]
        + str(move.from_square // 8 + 1)
        + FILES[move.to_square % 8]
        + str(move.to_square // 8 + 1)
    )


def promotion_suffix(move):

    if move.promotion is None:
        return ""

    mapping = {
        5: "q",
        4: "r",
        3: "b",
        2: "n"
    }

    return mapping.get(move.promotion, "")