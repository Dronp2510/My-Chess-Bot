from bots.evaluation import evaluate_board , piece_score
import time

MAX_DEPTH = 5
MAX_Q_DEPTH = 8
BIG_DELTA = 900

nodes_searched = 0
cutoffs = 0
q_nodes = 0
tt_hits = 0
killer_hits = 0
history_hits = 0

transposition_table = {}
killer_moves = {}
history_table = {}

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

def find_best_move(gs, valid_moves):

    start_time = time.time()

    global nodes_searched
    global cutoffs
    global q_nodes
    global tt_hits
    global killer_moves
    global killer_hits
    global history_table
    global history_hits

    best_move = None
    killer_moves = {}
    history_table = {}

    for current_depth in range(1, MAX_DEPTH + 1):

        iteration_start = time.time()

        nodes_searched = 0
        cutoffs = 0
        q_nodes = 0
        tt_hits = 0
        killer_hits = 0
        history_hits = 0

        best_score = float('-inf')
        iteration_best_move = None

        valid_moves.sort(
            key=move_ordering,
            reverse=True
        )

        for move in valid_moves:

            gs.make_move(move)

            if not gs.move_is_legal():
                gs.undo_move()
                continue

            score = -negamax(
                gs,
                current_depth - 1,
                float('-inf'),
                float('inf'),
                1
            )

            gs.undo_move()

            if score > best_score:

                best_score = score
                iteration_best_move = move

        best_move = iteration_best_move

        # root move ordering
        if best_move in valid_moves:

            valid_moves.remove(best_move)
            valid_moves.insert(0, best_move)

        elapsed_time = time.time() - iteration_start

        pps = int(nodes_searched / elapsed_time) if elapsed_time > 0 else 0

        print(f"\n-- Depth {current_depth} --")
        print("Best Move =", best_move)
        print("Best Score =", best_score)
        print("Nodes Searched =", nodes_searched)
        print("Cutoffs =", cutoffs)
        print("Time =", round(elapsed_time, 2), "seconds")
        print("Positions Per Second =", pps)
        print("Q Nodes =", q_nodes)
        print("TT Hits =", tt_hits)
        print("Killer Hits =", killer_hits)
        print("History Hits =", history_hits)

    total_time = time.time() - start_time

    print("\n===== FINAL SEARCH COMPLETE =====")
    print("Final Best Move =", best_move)
    print("Total Time =", round(total_time, 2), "seconds")

    return best_move

def negamax(gs, depth, alpha, beta, ply=0):

    global nodes_searched
    global cutoffs
    global tt_hits
    global killer_moves
    global history_table

    nodes_searched += 1

    tt_move = None

    if depth == 0:
        return quiescence(gs, alpha, beta)

    alpha_original = alpha
    beta_original = beta

    hash_key = gs.position_hash

    # =========================
    # TRANSPOSITION LOOKUP
    # =========================

    if hash_key in transposition_table:

        tt_depth, tt_score, tt_flag, tt_move = transposition_table[hash_key]

        if tt_depth >= depth:

            tt_hits += 1
            
            if tt_flag == EXACT:
                return tt_score

            elif tt_flag == LOWERBOUND:
                alpha = max(alpha, tt_score)

            elif tt_flag == UPPERBOUND:
                beta = min(beta, tt_score)

            if alpha >= beta:
                return tt_score

    pseudo_moves = gs.get_all_pseudo_moves()

    pseudo_moves.sort(
        key=lambda move:
            move_ordering(move, tt_move, ply),
        reverse=True
    )

    best_score = float('-inf')
    best_move = None

    legal_move_found = False

    for move in pseudo_moves:

        gs.make_move(move)

        if not gs.move_is_legal():

            gs.undo_move()
            continue

        legal_move_found = True

        score = -negamax(
            gs,
            depth - 1,
            -beta,
            -alpha,
            ply + 1
        )

        gs.undo_move()

        if score > best_score:

            best_score = score
            best_move = move

        if score > alpha:
            alpha = score

        if alpha >= beta:

            cutoffs += 1

            if move.piece_captured == "--" and not move.is_pawn_promotion:
                store_killer_move(ply, move)
                store_history_move(move, depth)

            break

    # =========================
    # CHECKMATE / STALEMATE
    # =========================

    if not legal_move_found:

        if gs.is_in_check():
            return -100000

        return 0

    # =========================
    # STORE TT ENTRY
    # =========================

    if best_score <= alpha_original:
        flag = UPPERBOUND

    elif best_score >= beta_original:
        flag = LOWERBOUND

    else:
        flag = EXACT

    transposition_table[hash_key] = (
        depth,
        best_score,
        flag,
        best_move
    )

    return best_score

    
def move_ordering(move, tt_move=None, ply=0):

    score = 0
    global killer_hits
    global history_hits

    attacker = move.piece_moved[1:]
    victim = move.piece_captured[1:]

    if tt_move and move == tt_move:
        return 1000000

    if move.piece_captured == "--" and not move.is_pawn_promotion:

        killers = killer_moves.get(ply)

        if killers:

            if killers[0] and move == killers[0]:
                killer_hits += 1
                return 900000

            if killers[1] and move == killers[1]:
                killer_hits += 1
                return 800000

        history_score = history_table.get(move_history_key(move), 0)

        if history_score:
            history_hits += 1
            score += min(history_score, 700000)
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

def store_killer_move(ply, move):

    killers = killer_moves.setdefault(ply, [None, None])

    if killers[0] == move:
        return

    killers[1] = killers[0]
    killers[0] = move

def store_history_move(move, depth):

    key = move_history_key(move)
    bonus = max(1, depth) * max(1, depth)

    history_table[key] = history_table.get(key, 0) + bonus

def move_history_key(move):

    return (
        move.piece_moved,
        move.start_row,
        move.start_col,
        move.end_row,
        move.end_col
    )

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
