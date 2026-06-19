"""Shared helpers for loading bot weight profiles and building weighted evaluators."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from bots.evaluation import piece_score, piece_square_tables

WEIGHTS_DIR = Path(__file__).resolve().parent / "weights"

DEFAULT_BASE_WEIGHTS = {
    "p": 100.0,
    "kn": 300.0,
    "b": 350.0,
    "r": 500.0,
    "q": 900.0,
    "pst": 1.0,
    "mobility": 2.0,
    "bishop_pair": 25.0,
    "check_pressure": 35.0,
    "castling_rights": 8.0,
}

def load_weight_profile(name: str, fallback_weights: dict[str, float] | None = None) -> dict[str, Any]:
    """Load a saved weight profile JSON. Falls back to supplied/default weights if missing."""
    fallback = (fallback_weights or DEFAULT_BASE_WEIGHTS).copy()
    path = WEIGHTS_DIR / f"{name}.json"

    if not path.is_file():
        return {
            "name": name,
            "weights": fallback,
            "history": [],
        }

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except Exception:
        return {
            "name": name,
            "weights": fallback,
            "history": [],
        }

    weights = payload.get("weights", fallback)
    if not isinstance(weights, dict):
        weights = fallback

    payload["weights"] = weights
    payload.setdefault("history", [])
    payload.setdefault("name", name)
    return payload

def side_to_move(gs) -> str:
    return "w" if gs.white_to_move else "b"

def enemy_of(color: str) -> str:
    return "b" if color == "w" else "w"

def pst_score(piece: str, row: int, col: int) -> float:
    table = piece_square_tables[piece[1:]]
    if piece[0] == "w":
        return table[row][col]
    return table[7 - row][col]

def evaluate_weighted(gs, weights: dict[str, float], perspective: str) -> float:
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
            value += weights.get("pst", 0.0) * pst_score(piece, row, col)

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

def side_bonus(gs, color: str, bishops: dict[str, int], weights: dict[str, float]) -> float:
    bonus = 0.0

    if bishops[color] >= 2:
        bonus += weights.get("bishop_pair", 0.0)

    if color == "w":
        if gs.castling_rights["wks"] or gs.castling_rights["wqs"]:
            bonus += weights.get("castling_rights", 0.0)
    else:
        if gs.castling_rights["bks"] or gs.castling_rights["bqs"]:
            bonus += weights.get("castling_rights", 0.0)

    return bonus

def mobility_score(gs, color: str, weights: dict[str, float]) -> float:
    old_turn = gs.white_to_move
    gs.white_to_move = color == "w"
    moves = len(gs.get_all_pseudo_moves())
    gs.white_to_move = old_turn
    return moves * weights.get("mobility", 0.0)

def pressure_score(gs, color: str, weights: dict[str, float]) -> float:
    enemy_king = gs.black_king_pos if color == "w" else gs.white_king_pos
    if gs.is_square_attacked(enemy_king[0], enemy_king[1], color):
        return weights.get("check_pressure", 0.0)
    return 0.0

def make_weighted_evaluator(weights: dict[str, float]) -> Callable[[Any], float]:
    def evaluator(search_state):
        return evaluate_weighted(search_state, weights, side_to_move(search_state))
    return evaluator
