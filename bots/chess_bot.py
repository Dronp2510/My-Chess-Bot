from bots.evaluation import evaluate_board
import time

MAX_DEPTH = 5

nodes_searched = 0
cutoffs = 0

def find_best_move(gs, valid_moves):

    start_time = time.time()

    global nodes_searched
    global cutoffs

    best_move = None

    # Iterative Deepening Loop
    for current_depth in range(1, MAX_DEPTH + 1):

        iteration_start = time.time()

        nodes_searched = 0
        cutoffs = 0

        iteration_best_move = None

        # WHITE to move
        if gs.white_to_move:

            best_score = float('-inf')

            for move in valid_moves:

                gs.make_move(move)

                score = minimax(
                    gs,
                    current_depth - 1,
                    float('-inf'),
                    float('inf'),
                    False
                )

                gs.undo_move()

                if score > best_score:

                    best_score = score
                    iteration_best_move = move

        # BLACK to move
        else:

            best_score = float('inf')

            for move in valid_moves:

                gs.make_move(move)

                score = minimax(
                    gs,
                    current_depth - 1,
                    float('-inf'),
                    float('inf'),
                    True
                )

                gs.undo_move()

                if score < best_score:

                    best_score = score
                    iteration_best_move = move

        # Save best move from completed iteration
        best_move = iteration_best_move

        # Root Move Reordering
        if best_move in valid_moves:

            valid_moves.remove(best_move)
            valid_moves.insert(0, best_move)

        # Iteration statistics
        elapsed_time = time.time() - iteration_start

        pps = int(nodes_searched / elapsed_time) if elapsed_time > 0 else 0

        print(f"\n-- Depth {current_depth} --")
        print("Best Move =", best_move)
        print("Nodes Searched =", nodes_searched)
        print("Cutoffs =", cutoffs)
        print("Time =", round(elapsed_time, 2), "seconds")
        print("Positions Per Second =", pps)

    total_time = time.time() - start_time

    print("\n===== FINAL SEARCH COMPLETE =====")
    print("Final Best Move =", best_move)
    print("Total Time =", round(total_time, 2), "seconds")

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