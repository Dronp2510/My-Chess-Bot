from bots.evaluation import evaluate_board
import time

DEPTH = 3

nodes_searched = 0
cutoffs = 0

def find_best_move(gs, valid_moves):

    start_time = time.time()

    global nodes_searched
    nodes_searched = 0

    global cutoffs
    cutoffs = 0

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

    elapsed_time = time.time() - start_time
    pps = int(nodes_searched / elapsed_time)
    search_info = {
    "nodes": nodes_searched,
    "cutoffs": cutoffs,
    "time": elapsed_time,
    "pps": pps
    }
    print('Nodes_searched = ' , search_info['nodes'])
    print('Time elasped = ' , round(search_info['time'], 2), 'seconds')
    print('Positions per second = ' , search_info['pps'])
    print('cutoffs = ' , search_info['cutoffs'])
    return best_move

def minimax(gs, depth, alpha, beta, maximizing_player):
    
    global nodes_searched
    nodes_searched += 1

    global cutoffs

    valid_moves = gs.get_all_valid_moves()
    valid_moves.sort(
        key=move_ordering,
        reverse=True
    )

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
                cutoffs += 1
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
                cutoffs += 1
                break

        return min_score
    

def move_ordering(move):

    score = 0

    # captures
    if move.piece_captured != "--":
        score += 10

    # promotions
    if move.is_pawn_promotion:
        score += 20

    # castling
    if move.is_castle_move:
        score += 5

    return score