import itertools
from dataclasses import dataclass, field

_concept_ids = itertools.count(1)


@dataclass(frozen=True)
class Concept:
    """
    Dropped by a defeated enemy. Tagged with the Path it came from and the
    Stage of the enemy it was harvested from.

    Consumed one of two ways:
      - Path advancement: exactly ONE Concept, of the player's OWN Path,
        whose stage is EXACTLY player_stage - 1. A Stage 5 player holding
        a Stage 3 Fortune concept can NOT use it yet -- they need Stage 4
        first. (Confirmed design rule.)
      - Artifact crafting at a shop: any Path, any stage. Crafted from the
        UI by the player clicking the concept in their inventory and
        choosing "Advance" (if eligible) or crafting it away at a shop.

    `concept_id` exists purely so two Concepts that happen to share
    path_name/stage (e.g. two Stage-4 Fortune drops) remain distinguishable
    objects in the Inventory -- frozen dataclasses would otherwise compare
    equal and make List.remove() ambiguous about which one it deletes.
    """
    path_name: str
    stage: int
    concept_id: int = field(default_factory=lambda: next(_concept_ids))

    def can_advance(self, player_path_name: str, player_stage: int) -> bool:
        """
        True only if this Concept is the exact next stage of the player's
        current Path. This is intentionally strict per the confirmed rule:
        same Path AND stage == player_stage - 1. Anything else (wrong
        Path, or the right Path but the wrong stage gap) is craft-only.
        """
        return (
            self.path_name == player_path_name
            and self.stage == player_stage - 1
        )