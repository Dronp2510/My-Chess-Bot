import json
from pathlib import Path

import chess
import chess.pgn


DATASET_DIR = Path("training_data/datasets")
DATASET_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATASET_DIR / "move_dataset.jsonl"


USERNAME = "Shadow2510"

class DatasetBuilder:

    def __init__(self):

        self.samples = []

    def add_sample(
        self,
        fen,
        move_uci,
        result,
        ply
    ):

        self.samples.append(
            {
                "fen": fen,
                "move": move_uci,
                "result": result,
                "ply" : ply
            }
        )

    def process_game(self, game):

        board = game.board()

        headers = game.headers

        white = headers.get("White", "")
        black = headers.get("Black", "")

        result = headers.get("Result", "*")

        if result == "1-0":
            game_result = 1

        elif result == "0-1":
            game_result = -1

        else:
            game_result = 0

        node = game

        while node.variations:

            move = node.variation(0)

            current_fen = board.fen()

            played_move = move.move.uci()

            is_my_move = (
                (board.turn and white == USERNAME)
                or
                (not board.turn and black == USERNAME)
            )

            if is_my_move:

                self.add_sample(
                    current_fen,
                    played_move,
                    game_result,
                    len(board.move_stack)
                )

            board.push(move.move)

            node = move

    def save(self):

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            for sample in self.samples:

                f.write(
                    json.dumps(sample)
                    + "\n"
                )

def build_dataset():

    builder = DatasetBuilder()

    pgn_dir = Path("training_data/pgns")

    files = list(
        pgn_dir.glob("*.pgn")
    )

    for file in files:

        print(
            f"Processing {file.name}"
        )

        with open(
            file,
            encoding="utf-8"
        ) as pgn_file:

            while True:

                game = chess.pgn.read_game(
                    pgn_file
                )

                if game is None:
                    break

                builder.process_game(
                    game
                )

    builder.save()

    print(
        f"Generated "
        f"{len(builder.samples)} samples"
    )


if __name__ == "__main__":

    build_dataset()