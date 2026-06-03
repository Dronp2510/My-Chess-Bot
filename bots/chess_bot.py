from bots.evaluation import evaluate_board , piece_score
import time

MAX_DEPTH = 5
MAX_Q_DEPTH = 8
BIG_DELTA = 900

nodes_searched = 0
cutoffs = 0
q_nodes = 0

def find_best_move(gs, valid_moves):

    start_time = time.time()

    global nodes_searched
    global cutoffs
    global q_nodes

    best_move = None

    # Iterative Deepening Loop
    for current_depth in range(1, MAX_DEPTH + 1):

        iteration_start = time.time()

        nodes_searched = 0
        cutoffs = 0
        q_nodes = 0
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
        print("q search nodes = ", q_nodes)

    total_time = time.time() - start_time

    print("\n===== FINAL SEARCH COMPLETE =====")
    print("Final Best Move =", best_move)
    print("Total Time =", round(total_time, 2), "seconds")

    print("\n------------function call counters------------")
    print("Make Move Calls =", gs.make_move_calls)
    print("Undo Move Calls =", gs.undo_move_calls)
    print("Attack Calls =", gs.attack_calls)
    print("Valid Move Calls =", gs.valid_move_calls)
    print("All Valid Move Calls =", gs.all_valid_move_calls)

    return best_move

def minimax(gs, depth, alpha, beta, maximizing_player):

    global nodes_searched
    nodes_searched += 1

    global cutoffs

    # terminal depth
    if depth == 0:
        return quiescence(gs , alpha , beta)

    pseudo_moves = gs.get_all_pseudo_moves()

    pseudo_moves.sort(
        key=move_ordering,
        reverse=True
    )

    # =========================
    # WHITE (maximize)
    # =========================

    if maximizing_player:

        max_score = float('-inf')

        legal_move_found = False

        for move in pseudo_moves:

            gs.make_move(move)

            # legality filtering
            if not gs.move_is_legal():

                gs.undo_move()
                continue

            legal_move_found = True

            score = minimax(
                gs,
                depth - 1,
                alpha,
                beta,
                False
            )

            gs.undo_move()

            max_score = max(max_score, score)

            alpha = max(alpha, score)

            # alpha-beta prune
            if beta <= alpha:

                cutoffs += 1
                break

        # checkmate / stalemate
        if not legal_move_found:

            if gs.is_in_check():
                return evaluate_board(gs)
            else:
                return 0

        return max_score

    # =========================
    # BLACK (minimize)
    # =========================

    else:

        min_score = float('inf')

        legal_move_found = False

        for move in pseudo_moves:

            gs.make_move(move)

            # legality filtering
            if not gs.move_is_legal():

                gs.undo_move()
                continue

            legal_move_found = True

            score = minimax(
                gs,
                depth - 1,
                alpha,
                beta,
                True
            )

            gs.undo_move()

            min_score = min(min_score, score)

            beta = min(beta, score)

            # alpha-beta prune
            if beta <= alpha:

                cutoffs += 1
                break

        # checkmate / stalemate
        if not legal_move_found:

            if gs.is_in_check():
                return evaluate_board(gs)
            else:
                return 0

        return min_score
    
def move_ordering(move):

    score = 0

    attacker = move.piece_moved[1:]
    victim = move.piece_captured[1:]

    # =========================
    # MVV-LVA CAPTURE SCORING
    # =========================

    if move.piece_captured != "--":

        victim_value = piece_score[victim]
        attacker_value = piece_score[attacker]

        score += (10 * victim_value) - attacker_value

    # promotions
    if move.is_pawn_promotion:
        score += 800

    # castling
    if move.is_castle_move:
        score += 50

    return score

def quiescence(gs, alpha, beta, depth=0):

    global q_nodes
    q_nodes += 1

    if depth >= MAX_Q_DEPTH:
        return evaluate_board(gs) 
    
    stand_pat = evaluate_board(gs)
    
    if stand_pat >= beta:
        return beta

    if stand_pat + BIG_DELTA < alpha:
        return alpha
    
    if stand_pat > alpha:
        alpha = stand_pat
    
    capture_moves = gs.get_all_capture_moves()

    capture_moves.sort(key=move_ordering, reverse=True)
    

    
    for move in capture_moves:

        gs.make_move(move)

        if not gs.move_is_legal():
            gs.undo_move()
            continue

        score = -quiescence(gs, -beta, -alpha, depth + 1)

        gs.undo_move()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score
        


    return alpha