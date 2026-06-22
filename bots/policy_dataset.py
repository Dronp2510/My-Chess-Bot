import json

import numpy as np

import torch
from torch.utils.data import Dataset


PIECE_TO_PLANE = {
    "P": 0,
    "N": 1,
    "B": 2,
    "R": 3,
    "Q": 4,
    "K": 5,
    "p": 6,
    "n": 7,
    "b": 8,
    "r": 9,
    "q": 10,
    "k": 11,
}


def fen_to_tensor(fen):

    board_part = fen.split()[0]

    tensor = np.zeros(
        (12, 8, 8),
        dtype=np.float32
    )

    rows = board_part.split("/")

    for r, row in enumerate(rows):

        c = 0

        for char in row:

            if char.isdigit():

                c += int(char)
                continue

            plane = PIECE_TO_PLANE[char]

            tensor[plane][r][c] = 1

            c += 1

    return tensor


class MoveVocabulary:

    def __init__(self):

        self.move_to_idx = {}
        self.idx_to_move = {}

    def build(self, dataset_file):

        unique_moves = set()

        with open(dataset_file, encoding="utf-8") as f:

            for line in f:

                sample = json.loads(line)

                unique_moves.add(
                    sample["move"]
                )

        unique_moves = sorted(
            unique_moves
        )

        for idx, move in enumerate(
            unique_moves
        ):

            self.move_to_idx[move] = idx
            self.idx_to_move[idx] = move

    def save(self, path):

        with open(path, "w") as f:

            json.dump(
                self.move_to_idx,
                f,
                indent=2
            )


class ChessDataset(Dataset):

    def __init__(
        self,
        dataset_file,
        vocab
    ):

        self.samples = []

        with open(dataset_file, encoding="utf-8") as f:

            for line in f:

                self.samples.append(
                    json.loads(line)
                )

        self.vocab = vocab

    def __len__(self):

        return len(self.samples)

    def __getitem__(self, idx):

        sample = self.samples[idx]

        x = fen_to_tensor(
            sample["fen"]
        )

        y = self.vocab.move_to_idx[
            sample["move"]
        ]

        return (
            torch.tensor(
                x,
                dtype=torch.float32
            ),
            torch.tensor(
                y,
                dtype=torch.long
            )
        )