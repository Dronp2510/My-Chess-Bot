"""
Engine-wide debugging and profiling utilities.

Purpose:
- Keep debug code out of GameState and search code.
- Centralize counters and debug flags.
- Allow profiling to be enabled/disabled from one place.

This file contains NO chess logic.
"""


# ============================================================
# DEBUG FLAGS
# ============================================================

DEBUG_ENGINE = False
DEBUG_SEARCH = False
DEBUG_HASH = False
DEBUG_MOVE_GEN = False


# ============================================================
# ENGINE STATS
# ============================================================

class EngineStats:
    """
    Collects engine profiling counters.

    These counters should ONLY be used when profiling
    performance or debugging.

    They are intentionally kept outside GameState so
    engine logic stays clean.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.make_move_calls = 0
        self.undo_move_calls = 0
        self.attack_calls = 0
        self.valid_move_calls = 0
        self.all_valid_move_calls = 0

    def as_dict(self):
        return {
            "make_move_calls": self.make_move_calls,
            "undo_move_calls": self.undo_move_calls,
            "attack_calls": self.attack_calls,
            "valid_move_calls": self.valid_move_calls,
            "all_valid_move_calls": self.all_valid_move_calls,
        }

    def print_report(self):
        print("\n===== ENGINE STATS =====")

        for key, value in self.as_dict().items():
            print(f"{key}: {value}")

        print("========================\n")


# ============================================================
# GLOBAL ENGINE STATS INSTANCE
# ============================================================

engine_stats = EngineStats()


# ============================================================
# DEBUG HELPERS
# ============================================================

def debug_engine(*args, **kwargs):
    if DEBUG_ENGINE:
        print(*args, **kwargs)


def debug_search(*args, **kwargs):
    if DEBUG_SEARCH:
        print(*args, **kwargs)


def debug_hash(*args, **kwargs):
    if DEBUG_HASH:
        print(*args, **kwargs)


def debug_move_gen(*args, **kwargs):
    if DEBUG_MOVE_GEN:
        print(*args, **kwargs)