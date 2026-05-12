from bots.evaluation import evaluate_board

DEPTH = 3

def find_best_move(gs, valid_moves):

    best_move = None

    if gs.white_to_move:

        best_score = float('-inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax(gs, DEPTH - 1, float('-inf'), float('inf'), False)

            gs.undo_move()

            if score > best_score:

                best_score = score
                best_move = move

    else:

        best_score = float('inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax(gs, DEPTH - 1, float('-inf'), float('inf'), True)

            gs.undo_move()

            if score < best_score:

                best_score = score
                best_move = move

    return best_move

def minimax(gs, depth, alpha, beta, maximizing_player):

    valid_moves = gs.get_all_valid_moves()

    # terminal node
    if depth == 0:
        return evaluate_board(gs)

    if len(valid_moves) == 0:

        if gs.is_in_check():
            return evaluate_board(gs)

        else:
            return 0

    # WHITE (maximize)
    if maximizing_player:

        max_score = float('-inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax( gs, depth - 1, alpha, beta, False )

            gs.undo_move()

            max_score = max(max_score, score)

            alpha = max(alpha, score)

            # PRUNE
            if beta <= alpha:
                break

        return max_score

    # BLACK (minimize)
    else:

        min_score = float('inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax( gs, depth - 1, alpha, beta, True )

            gs.undo_move()

            min_score = min(min_score, score)

            beta = min(beta, score)

            # PRUNE
            if beta <= alpha:
                break

        return min_score