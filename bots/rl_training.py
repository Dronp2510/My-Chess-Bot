import argparse
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bots.chess_bot import MAX_DEPTH as BOT_SEARCH_DEPTH
from bots.chess_bot import find_best_move as find_chess_bot_move
from bots.evaluation import piece_score, piece_square_tables
from engine.game_state import GameState


GENERATIONS = 20
GAMES_PER_PHASE = 120
POPULATION_SIZE = 16
MAX_PLIES = 160
MAX_SEARCH_DEPTH = 3  # BOT_SEARCH_DEPTH
MOVE_TIME_LIMIT = 0.50
CHECKMATE_REWARD = 10000
DRAW_REWARD = 0
MUTATION_RATE = 0.18
MUTATION_SCALE = 0.12
WEIGHTS_DIR = Path(__file__).resolve().parent / "weights"


BASE_WEIGHTS = {
    "p": 100.0,
    "kn": 300.0,
    "b": 350.0,
    "r": 500.0,
    "q": 900.0,
    "pst": 1.0,
    "mobility": 2.0,
    "bishop_pair": 25.0,
    "check_pressure": 35.0,
    "castling_rights": 8.0
}


def train(
    generations=GENERATIONS,
    games_per_phase=GAMES_PER_PHASE,
    seed=20260616
):
    rng = random.Random(seed)
    white_population = create_population(rng)
    black_population = create_population(rng)
    history = []
    best_white = white_population[0]
    best_black = black_population[0]

    for generation in range(1, generations + 1):
        print(f"\n===== RL GENERATION {generation}/{generations} =====")

        white_scores, black_scores = run_pool_phase(
            white_population,
            black_population,
            games_per_phase,
            rng
        )

        best_white = select_best(white_population, white_scores)
        best_black = select_best(black_population, black_scores)

        match_result = run_head_to_head(
            best_white,
            best_black,
            games_per_phase,
            rng
        )

        generation_summary = {
            "generation": generation,
            "best_white_score": round(score_for(best_white, white_scores), 2),
            "best_black_score": round(score_for(best_black, black_scores), 2),
            "head_to_head": match_result,
            "best_white": best_white.copy(),
            "best_black": best_black.copy()
        }

        history.append(generation_summary)
        print_generation_summary(generation_summary)

        white_population = next_population(best_white, rng)
        black_population = next_population(best_black, rng)

    save_weights("best_white", best_white, history, seed)
    save_weights("best_black", best_black, history, seed)

    return best_white, best_black, history


def run_pool_phase(white_population, black_population, games, rng):
    white_scores = init_scores(white_population)
    black_scores = init_scores(black_population)

    for game_index in range(games):
        white = rng.choice(white_population)
        black = rng.choice(black_population)
        result = play_game(white, black, rng)

        white_scores[id(white)]["score"] += result["white_reward"]
        white_scores[id(white)]["games"] += 1
        black_scores[id(black)]["score"] += result["black_reward"]
        black_scores[id(black)]["games"] += 1

        print_progress("pool", game_index + 1, games, result)

    return white_scores, black_scores


def run_head_to_head(white_weights, black_weights, games, rng):
    result = {
        "white_wins": 0,
        "black_wins": 0,
        "draws": 0,
        "white_reward": 0.0,
        "black_reward": 0.0
    }

    for game_index in range(games):
        game = play_game(white_weights, black_weights, rng)
        result["white_reward"] += game["white_reward"]
        result["black_reward"] += game["black_reward"]

        if game["winner"] == "w":
            result["white_wins"] += 1
        elif game["winner"] == "b":
            result["black_wins"] += 1
        else:
            result["draws"] += 1

        print_progress("match", game_index + 1, games, game)

    result["white_reward"] = round(result["white_reward"], 2)
    result["black_reward"] = round(result["black_reward"], 2)

    return result


def play_game(white_weights, black_weights, rng):
    gs = GameState()
    winner = None
    reason = "max_plies"

    for ply in range(MAX_PLIES):
        legal_moves = get_legal_moves(gs)

        if not legal_moves:
            if gs.is_in_check():
                winner = "b" if gs.white_to_move else "w"
                reason = "checkmate"
            else:
                reason = "stalemate"
            break

        weights = white_weights if gs.white_to_move else black_weights
        move = find_best_move_timed(gs, weights, rng)

        if move is None:
            move = rng.choice(legal_moves)

        gs.make_move(move)

    white_reward, black_reward = score_game(gs, winner, reason)

    return {
        "winner": winner,
        "reason": reason,
        "plies": len(gs.move_log),
        "white_reward": white_reward,
        "black_reward": black_reward
    }


def find_best_move_timed(gs, weights, rng):
    legal_moves = get_legal_moves(gs)

    if not legal_moves:
        return None

    rng.shuffle(legal_moves)

    def weighted_side_to_move_evaluator(search_state):
        return evaluate_weighted(
            search_state,
            weights,
            side_to_move(search_state)
        )

    return find_chess_bot_move(
        gs,
        legal_moves,
        max_depth=3,
        evaluator=weighted_side_to_move_evaluator,
        time_limit=MOVE_TIME_LIMIT,
        quiet=True,
        clear_transposition=True
    )


def evaluate_weighted(gs, weights, perspective):
    score = 0.0
    bishops = {"w": 0, "b": 0}

    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]

            if piece == "--":
                continue

            color = piece[0]
            piece_type = piece[1:]
            value = weights.get(piece_type, piece_score[piece_type])
            value += weights["pst"] * pst_score(piece, row, col)

            if piece_type == "b":
                bishops[color] += 1

            if color == perspective:
                score += value
            else:
                score -= value

    score += side_bonus(gs, perspective, bishops, weights)
    score -= side_bonus(gs, enemy_of(perspective), bishops, weights)
    score += mobility_score(gs, perspective, weights)
    score -= mobility_score(gs, enemy_of(perspective), weights)
    score += pressure_score(gs, perspective, weights)
    score -= pressure_score(gs, enemy_of(perspective), weights)

    return score


def score_game(gs, winner, reason):
    if winner == "w":
        return CHECKMATE_REWARD, -CHECKMATE_REWARD

    if winner == "b":
        return -CHECKMATE_REWARD, CHECKMATE_REWARD

    material = material_balance(gs)

    if reason == "stalemate":
        return DRAW_REWARD, DRAW_REWARD

    return material * 0.05, -material * 0.05


def material_balance(gs):
    score = 0.0

    for row in gs.board:
        for piece in row:
            if piece == "--":
                continue

            value = piece_score[piece[1:]]

            if piece[0] == "w":
                score += value
            else:
                score -= value

    return score


def mobility_score(gs, color, weights):
    old_turn = gs.white_to_move
    gs.white_to_move = color == "w"
    moves = len(gs.get_all_pseudo_moves())
    gs.white_to_move = old_turn

    return moves * weights["mobility"]


def pressure_score(gs, color, weights):
    enemy_king = gs.black_king_pos if color == "w" else gs.white_king_pos

    if gs.is_square_attacked(enemy_king[0], enemy_king[1], color):
        return weights["check_pressure"]

    return 0.0


def side_bonus(gs, color, bishops, weights):
    bonus = 0.0

    if bishops[color] >= 2:
        bonus += weights["bishop_pair"]

    if color == "w":
        if gs.castling_rights["wks"] or gs.castling_rights["wqs"]:
            bonus += weights["castling_rights"]
    else:
        if gs.castling_rights["bks"] or gs.castling_rights["bqs"]:
            bonus += weights["castling_rights"]

    return bonus


def get_legal_moves(gs):
    legal_moves = []

    for move in gs.get_all_pseudo_moves():
        gs.make_move(move)

        if gs.move_is_legal():
            legal_moves.append(move)

        gs.undo_move()

    return legal_moves


def pst_score(piece, row, col):
    table = piece_square_tables[piece[1:]]

    if piece[0] == "w":
        return table[row][col]

    return table[7 - row][col]


def create_population(rng):
    population = [BASE_WEIGHTS.copy()]

    while len(population) < POPULATION_SIZE:
        population.append(mutate(BASE_WEIGHTS, rng))

    return population


def next_population(best_weights, rng):
    population = [best_weights.copy()]

    while len(population) < POPULATION_SIZE:
        population.append(mutate(best_weights, rng))

    return population


def mutate(weights, rng):
    child = weights.copy()

    for key, value in list(child.items()):
        if rng.random() > MUTATION_RATE:
            continue

        change = 1.0 + rng.uniform(-MUTATION_SCALE, MUTATION_SCALE)
        child[key] = max(0.0, round(value * change, 3))

    return child


def init_scores(population):
    return {
        id(weights): {
            "weights": weights,
            "score": 0.0,
            "games": 0
        }
        for weights in population
    }


def select_best(population, scores):
    return max(
        population,
        key=lambda weights: score_for(weights, scores)
    )


def score_for(weights, scores):
    data = scores[id(weights)]

    if data["games"] == 0:
        return float("-inf")

    return data["score"] / data["games"]


def save_weights(name, weights, history, seed):
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    path = WEIGHTS_DIR / f"{name}.json"

    payload = {
        "name": name,
        "seed": seed,
        "move_time_limit": MOVE_TIME_LIMIT,
        "max_search_depth": MAX_SEARCH_DEPTH,
        "max_plies": MAX_PLIES,
        "weights": weights,
        "history": history
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    print(f"saved {name}: {path}")


def print_progress(phase, current, total, result):
    winner = result["winner"] if result["winner"] else "draw"

    print(
        f"{phase} game {current}/{total}: "
        f"{winner} by {result['reason']} "
        f"({result['plies']} plies)"
    )


def print_generation_summary(summary):
    match = summary["head_to_head"]

    print("\nGeneration summary")
    print("Best white score:", summary["best_white_score"])
    print("Best black score:", summary["best_black_score"])
    print(
        "Head-to-head:",
        f"W {match['white_wins']}",
        f"B {match['black_wins']}",
        f"D {match['draws']}"
    )


def side_to_move(gs):
    return "w" if gs.white_to_move else "b"


def enemy_of(color):
    return "b" if color == "w" else "w"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=GENERATIONS)
    parser.add_argument("--games", type=int, default=GAMES_PER_PHASE)
    parser.add_argument("--seed", type=int, default=20260616)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(args.generations, args.games, args.seed)
