
piece_score = {
    'p' : 1 ,
    'kn': 3 ,
    'b' : 3.5,
    'r' : 5 ,
    'q' : 9 ,
    'k' : 0 
}

CHECKMATE = 1000
STALEMATE = 0

def evaluate_board(gs):

    # terminal positions
    if gs.checkmate:

        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE

    elif gs.stalemate:
        return STALEMATE

    score = 0

    for row in gs.board:
        for piece in row:

            if piece == "--":
                continue

            piece_type = piece[1:]

            if piece[0] == 'w':
                score += piece_score[piece_type]

            else:
                score -= piece_score[piece_type]

    return score