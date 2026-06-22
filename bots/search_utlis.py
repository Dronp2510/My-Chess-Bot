def side_to_move(gs):

    return (
        "w"
        if gs.white_to_move
        else "b"
    )


def enemy_of(color):

    return (
        "b"
        if color == "w"
        else "w"
    )