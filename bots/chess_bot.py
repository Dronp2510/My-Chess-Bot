from bots.evaluation import evaluate_board, piece_score
from bots.bot_profiles import (
    DEFAULT_BASE_WEIGHTS,
    load_weight_profile,
    make_weighted_evaluator,
)
import time

WHITE_BOT_PROFILE = load_weight_profile("best_white", DEFAULT_BASE_WEIGHTS)
BLACK_BOT_PROFILE = load_weight_profile("best_black", DEFAULT_BASE_WEIGHTS)

WHITE_BOT_WEIGHTS = WHITE_BOT_PROFILE["weights"]
BLACK_BOT_WEIGHTS = BLACK_BOT_PROFILE["weights"]

WHITE_BOT_EVALUATOR = make_weighted_evaluator(WHITE_BOT_WEIGHTS)
BLACK_BOT_EVALUATOR = make_weighted_evaluator(BLACK_BOT_WEIGHTS)

MAX_DEPTH = 5
MAX_Q_DEPTH = 8

# Quiescence delta pruning tuning.
# If your evaluator is still in tiny units (1, 3, 5, 9), reduce this to 1–5.
Q_DELTA_MARGIN = 150

# Null move pruning tuning.
NULL_MOVE_REDUCTION = 2
NULL_MOVE_MIN_DEPTH = 4

# Late Move Removal
LMR_MOVE_THRESHOLD = 4

nodes_searched = 0
cutoffs = 0
q_nodes = 0
tt_hits = 0
q_tt_hits = 0
killer_hits = 0
history_hits = 0
lmr_reductions = 0

transposition_table = {}
q_transposition_table = {}
killer_moves = {}
history_table = {}

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

QEXACT = 0
QLOWERBOUND = 1
QUPPERBOUND = 2


class SearchTimeout(Exception):
    pass


def find_best_move(
    gs,
    valid_moves,
    max_depth=None,
    evaluator=None,
    time_limit=None,
    quiet=False,
    clear_transposition=False
):
    start_time = time.perf_counter()
    deadline = None

    if time_limit is not None:
        deadline = start_time + time_limit

    search_depth = max_depth if max_depth is not None else MAX_DEPTH
    evaluator = evaluator or evaluate_board

    global nodes_searched
    global cutoffs
    global q_nodes
    global tt_hits
    global q_tt_hits
    global killer_moves
    global killer_hits
    global history_table
    global history_hits
    global transposition_table
    global q_transposition_table
    global lmr_reductions


    best_move = None
    killer_moves = {}
    history_table = {}

    if clear_transposition or evaluator is not evaluate_board:
        transposition_table = {}
        q_transposition_table = {}

    search_moves = list(valid_moves)

    for current_depth in range(1, search_depth + 1):
        iteration_start = time.perf_counter()

        nodes_searched = 0
        cutoffs = 0
        q_nodes = 0
        tt_hits = 0
        q_tt_hits = 0
        killer_hits = 0
        history_hits = 0
        lmr_reductions = 0
        
        best_score = float('-inf')
        iteration_best_move = None

        search_moves.sort(key=move_ordering, reverse=True)

        try:
            _check_deadline(deadline)

            for move in search_moves:
                _check_deadline(deadline)

                gs.make_move(move)

                if not gs.move_is_legal():
                    gs.undo_move()
                    continue

                try:
                    score = -negamax(
                        gs,
                        current_depth - 1,
                        float('-inf'),
                        float('inf'),
                        1,
                        evaluator,
                        deadline,
                        allow_null=True
                    )
                finally:
                    gs.undo_move()

                if score > best_score:
                    best_score = score
                    iteration_best_move = move

        except SearchTimeout:
            break

        if iteration_best_move is not None:
            best_move = iteration_best_move

        if best_move in search_moves:
            search_moves.remove(best_move)
            search_moves.insert(0, best_move)

        elapsed_time = time.perf_counter() - iteration_start
        pps = int(nodes_searched / elapsed_time) if elapsed_time > 0 else 0

        if not quiet:
            print(f"\n-- Depth {current_depth} --")
            print("Best Move =", best_move)
            print("Best Score =", best_score)
            print("Nodes Searched =", nodes_searched)
            print("Cutoffs =", cutoffs)
            print("Time =", round(elapsed_time, 2), "seconds")
            print("Positions Per Second =", pps)
            print("Q Nodes =", q_nodes)
            print("TT Hits =", tt_hits)
            print("Q TT Hits =", q_tt_hits)
            print("Killer Hits =", killer_hits)
            print("History Hits =", history_hits)
            print("LMR Reductions =", lmr_reductions)

    total_time = time.perf_counter() - start_time

    if not quiet:
        print("\n===== FINAL SEARCH COMPLETE =====")
        print("Final Best Move =", best_move)
        print("Total Time =", round(total_time, 2), "seconds")

    return best_move


def _check_deadline(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise SearchTimeout

def clear_search_cache():
    global transposition_table
    global q_transposition_table
    global killer_moves
    global history_table

    transposition_table = {}
    q_transposition_table = {}
    killer_moves = {}
    history_table = {}


def get_bot_weights(color: str):
    return WHITE_BOT_WEIGHTS if color == "w" else BLACK_BOT_WEIGHTS

def get_bot_evaluator(color: str):
    return WHITE_BOT_EVALUATOR if color == "w" else BLACK_BOT_EVALUATOR

def _has_enough_material_for_null(gs):
    # Avoid null-move pruning in very low-material positions.
    # This helps reduce zugzwang blunders.
    material = 0
    for row in gs.board:
        for piece in row:
            if piece == "--":
                continue
            t = piece[1:]
            if t in ("q", "r", "b", "kn"):
                material += piece_score[t]
    return material >= piece_score["b"]


def negamax(gs, depth, alpha, beta, ply=0, evaluator=None, deadline=None, allow_null=True):
    global nodes_searched
    global cutoffs
    global tt_hits
    global killer_moves
    global history_table
    global transposition_table

    nodes_searched += 1
    _check_deadline(deadline)
    evaluator = evaluator or evaluate_board

    tt_move = None

    if depth <= 0:
        return quiescence(gs, alpha, beta, evaluator=evaluator, deadline=deadline)

    alpha_original = alpha
    beta_original = beta

    hash_key = gs.position_hash

    # -------------------------
    # TT lookup
    # -------------------------
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

    # # -------------------------
    # # Null move pruning
    # # -------------------------
    # if (
    #     allow_null
    #     and depth >= NULL_MOVE_MIN_DEPTH
    #     and not gs.is_in_check()
    #     and _has_enough_material_for_null(gs)
    # ):
    #     gs.make_null_move()
    #     try:
    #         reduced_depth = max(0, depth - 1 - NULL_MOVE_REDUCTION)
    #         null_score = -negamax(
    #             gs,
    #             reduced_depth,
    #             -beta,
    #             -beta + 1,
    #             ply + 1,
    #             evaluator,
    #             deadline,
    #             allow_null=False
    #         )
    #     finally:
    #         gs.undo_null_move()

    #     if null_score >= beta:
    #         transposition_table[hash_key] = (depth, beta, LOWERBOUND, None)
    #         return beta

    pseudo_moves = gs.get_all_pseudo_moves()
    pseudo_moves.sort(
        key=lambda move: move_ordering(move, tt_move, ply),
        reverse=True
    )

    best_score = float('-inf')
    best_move = None
    legal_move_found = False

    for move_number,move in enumerate(pseudo_moves, start=1):
        gs.make_move(move)

        if not gs.move_is_legal():
            gs.undo_move()
            continue

        legal_move_found = True

        try:
            # =========================
            # LMR
            # =========================

            is_quiet = (
                move.piece_captured == "--"
                and not move.is_pawn_promotion
            )

            use_lmr = (
                depth >= 3
                and move_number > LMR_MOVE_THRESHOLD
                and is_quiet
                and not gs.is_in_check()
            )

            if use_lmr:

                global lmr_reductions
                lmr_reductions += 1
                
                # reduced search
                score = -negamax(
                    gs,
                    depth - 2,
                    -alpha - 1,
                    -alpha,
                    ply + 1,
                    evaluator,
                    deadline,
                    allow_null=True
                )

                # re-search if promising
                if score > alpha:

                    score = -negamax(
                        gs,
                        depth - 1,
                        -beta,
                        -alpha,
                        ply + 1,
                        evaluator,
                        deadline,
                        allow_null=True
                    )

            else:

                score = -negamax(
                    gs,
                    depth - 1,
                    -beta,
                    -alpha,
                    ply + 1,
                    evaluator,
                    deadline,
                    allow_null=True
                )

        finally:
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

    # Checkmate / stalemate
    if not legal_move_found:
        if gs.is_in_check():
            best_score = -100000
        else:
            best_score = 0

        transposition_table[hash_key] = (depth, best_score, EXACT, None)
        return best_score

    # Store TT entry
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

    if best_score == float('-inf'):
        print("ERROR: -inf returned")
        print("Depth =", depth)
        print("Hash =", hash_key)
    
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

    if move.piece_captured != "--":
        victim_value = piece_score[victim]
        attacker_value = piece_score[attacker]
        score += (10 * victim_value) - attacker_value

    if move.is_pawn_promotion:
        score += 800

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


def _should_delta_prune(move, stand_pat, alpha):

    if move.piece_captured == "--":
        return False

    victim = move.piece_captured[1:]

    gain = piece_score[victim]

    if move.is_pawn_promotion:
        gain += 800

    return stand_pat + gain + 150 < alpha


def quiescence(gs, alpha, beta, depth=0, evaluator=None, deadline=None):
    global q_nodes
    global q_tt_hits
    global q_transposition_table

    q_nodes += 1
    _check_deadline(deadline)
    evaluator = evaluator or evaluate_board

    alpha_original = alpha
    beta_original = beta
    hash_key = gs.position_hash

    # -------------------------
    # Q-TT lookup
    # -------------------------
    entry = q_transposition_table.get(hash_key)
    if entry is not None:
        tt_depth, tt_score, tt_flag = entry
        if tt_depth >= depth:
            q_tt_hits += 1

            if tt_flag == QEXACT:
                return tt_score
            elif tt_flag == QLOWERBOUND:
                alpha = max(alpha, tt_score)
            elif tt_flag == QUPPERBOUND:
                beta = min(beta, tt_score)

            if alpha >= beta:
                return tt_score

    if depth >= MAX_Q_DEPTH:
        score = evaluator(gs)
        q_transposition_table[hash_key] = (depth, score, QEXACT)
        return score

    stand_pat = evaluator(gs)

    if stand_pat >= beta:
        q_transposition_table[hash_key] = (depth, beta, QLOWERBOUND)
        return beta

    if stand_pat > alpha:
        alpha = stand_pat

    capture_moves = gs.get_all_capture_moves()
    if len(capture_moves) > 1:
        capture_moves.sort(key=move_ordering, reverse=True)

    for move in capture_moves:
        if _should_delta_prune(move, stand_pat, alpha):
            continue

        gs.make_move(move)

        if not gs.move_is_legal():
            gs.undo_move()
            continue

        try:
            score = -quiescence(
                gs,
                -beta,
                -alpha,
                depth + 1,
                evaluator,
                deadline
            )
        finally:
            gs.undo_move()

        if score >= beta:
            q_transposition_table[hash_key] = (depth, beta, QLOWERBOUND)
            return beta

        if score > alpha:
            alpha = score

    if alpha <= alpha_original:
        flag = QUPPERBOUND
    elif alpha >= beta_original:
        flag = QLOWERBOUND
    else:
        flag = QEXACT

    q_transposition_table[hash_key] = (depth, alpha, flag)
    return alpha