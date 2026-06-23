import json
from pathlib import Path

import numpy as np
import torch

from bots.policy_network import PolicyNetwork
from bots.ml_constants import *

def gamestate_to_tensor(gs):

    tensor = np.zeros(
        (NUM_PLANES, BOARD_SIZE, BOARD_SIZE),
        dtype=np.float32
    )

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):

            piece = gs.board[r][c]

            if piece == "--":
                continue

            color = piece[0]
            piece_type = piece[1]

            lookup = {
                "p": "P",
                "kn": "N",
                "b": "B",
                "r": "R",
                "q": "Q",
                "k": "K",
            }

            symbol = lookup[piece_type]

            if color == "b":
                symbol = symbol.lower()

            plane = PIECE_TO_PLANE[symbol]

            tensor[plane][r][c] = 1

    return tensor

def move_to_policy_string(move):

    start = (
        move.get_rank_file(
            move.start_row,
            move.start_col
        )
    )

    end = (
        move.get_rank_file(
            move.end_row,
            move.end_col
        )
    )

    result = start + end

    if move.is_pawn_promotion:
        result += "q"

    return result

MODEL_PATH = Path("models/policy.pt")
VOCAB_PATH = Path("models/move_vocab.json")

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

_policy_model = None
_move_to_idx = None
_idx_to_move = None

def load_policy():

    global _policy_model
    global _move_to_idx
    global _idx_to_move

    if _policy_model is not None:
        return

    with open(VOCAB_PATH) as f:
        _move_to_idx = json.load(f)

    _idx_to_move = {
        v: k
        for k, v in _move_to_idx.items()
    }

    model = PolicyNetwork(
        len(_move_to_idx)
    )

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=device
        )
    )

    model.eval()
    model.to(device)

    _policy_model = model

    print(
        f"[Policy] Loaded "
        f"{len(_move_to_idx)} moves"
    )

@torch.no_grad()
def get_legal_move_scores(
    gs,
    legal_moves
):

    x = (
        torch.tensor(
            gamestate_to_tensor(gs)
        )
        .unsqueeze(0)
        .float()
        .to(device)
    )

    logits = _policy_model(x)

    probs = torch.softmax(
        logits,
        dim=1
    )[0]

    scores = {}

    for move in legal_moves:

        move_string = move_to_policy_string(move)

        idx = _move_to_idx.get(move_string)

        if idx is None:
            scores[move_string] = 0.0
            continue

        scores[move_string] = float(
            probs[idx]
        )

    return scores

@torch.no_grad()
def get_position_policy(gs):

    x = (
        torch.tensor(
            gamestate_to_tensor(gs)
        )
        .unsqueeze(0)
        .float()
        .to(device)
    )

    logits = _policy_model(x)

    probs = torch.softmax(
        logits,
        dim=1
    )[0]

    result = {}

    for idx, move_string in _idx_to_move.items():
        result[move_string] = float(
            probs[idx]
        )

    return result