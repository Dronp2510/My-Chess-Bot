from dataclasses import dataclass

from game.artifact_effects import get_effect_for_path


@dataclass(frozen=True)
class Artifact:
    """
    A passive item crafted from a single Concept at a shop.

    Power scales with the STAGE OF THE SOURCE CONCEPT it was crafted from,
    NOT the player's current stage -- a Stage 5 concept always makes a
    weak artifact and a Stage 1 concept always makes a strong one, even if
    crafted much later in the run. (Per design doc: "the higher the stage
    of concept, the higher the passive buffs".)
    """
    path_name: str
    source_stage: int

    @classmethod
    def craft_from_concept(cls, concept):
        return cls(path_name=concept.path_name, source_stage=concept.stage)

    def get_effect(self):
        return get_effect_for_path(self.path_name, self.source_stage)


class ArtifactLoadout:
    """
    Equipped artifacts. Slot COUNT depends on the player's CURRENT stage
    (not any individual artifact's source stage):
        Stage 5-4 -> 1 slot
        Stage 3-2 -> 2 slots
        Stage 1-0 -> 3 slots

    If the player advances to a stage with fewer available slots than
    they currently have equipped (not possible given the table only grows
    as stage decreases, but kept defensive for future Path variations),
    max_slots() is still the source of truth -- equip() will simply refuse
    new equips until slots free up.
    """

    STAGE_SLOT_TABLE = {
        5: 1, 4: 1,
        3: 2, 2: 2,
        1: 3, 0: 3,
    }

    def __init__(self):
        self._equipped = []

    def max_slots(self, player_stage):
        return self.STAGE_SLOT_TABLE.get(player_stage, 1)

    def equip(self, artifact, player_stage):
        if len(self._equipped) >= self.max_slots(player_stage):
            return False

        self._equipped.append(artifact)
        return True

    def unequip(self, artifact):
        if artifact in self._equipped:
            self._equipped.remove(artifact)

    def active_effects(self):
        return [artifact.get_effect() for artifact in self._equipped]

    def __iter__(self):
        return iter(self._equipped)

    def __len__(self):
        return len(self._equipped)