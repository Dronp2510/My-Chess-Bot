from bots.evaluation import evaluate_board

DEPTH = 2

def find_best_move(gs, valid_moves):

    best_move = None

    if gs.white_to_move:

        best_score = float('-inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax(gs, DEPTH - 1, False)

            gs.undo_move()

            if score > best_score:

                best_score = score
                best_move = move

    else:

        best_score = float('inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax(gs, DEPTH - 1, True)

            gs.undo_move()

            if score < best_score:

                best_score = score
                best_move = move

    return best_move

def minimax(gs, depth, maximizing_player):

    state = gs.get_game_state()

    # terminal node or depth reached
    if depth == 0 or state != "ongoing":

        return evaluate_board(gs)

    valid_moves = gs.get_all_valid_moves()

    # WHITE (maximize)
    if maximizing_player:

        max_score = float('-inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax(gs, depth - 1, False)

            gs.undo_move()

            max_score = max(max_score, score)

        return max_score

    # BLACK (minimize)
    else:

        min_score = float('inf')

        for move in valid_moves:

            gs.make_move(move)

            score = minimax(gs, depth - 1, True)

            gs.undo_move()

            min_score = min(min_score, score)

        return min_score