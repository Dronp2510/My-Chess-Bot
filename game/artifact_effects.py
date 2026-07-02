from abc import ABC, abstractmethod


class ArtifactEffect(ABC):
    """
    Base class for a single equipped Artifact's passive bonus. Kept
    generic (same shape as StatusEffect/Ability) so future Paths don't
    need bespoke plumbing to add their own Artifact effects later.
    """

    def __init__(self, path_name, source_stage, bonus_percent):
        self.path_name = path_name
        self.source_stage = source_stage
        self.bonus_percent = bonus_percent

    @abstractmethod
    def apply(self, context):
        """
        `context` is whatever the caller needs modified -- e.g. an
        ability instance about to be activated, or a CZPool about to
        regenerate. Each Path's ArtifactEffect subclass decides what it
        reads/writes on context; the base class doesn't assume a shape.
        """
        raise NotImplementedError


class FortuneAbilityPotencyEffect(ArtifactEffect):
    """
    Placeholder passive: boosts the effect strength of Fortune abilities
    (e.g. move-reduction percent, Army coverage percent) by bonus_percent.

    The exact hook-up point -- which specific ability fields this scales,
    and whether it's additive or multiplicative -- is a Phase-2 decision
    once real Fortune abilities are wired to read from equipped artifacts.
    This class exists so Concept -> Artifact -> Effect resolves end to
    end today; `apply()` is deliberately conservative until that design
    is settled.
    """

    def apply(self, context):
        context.ability_potency_multiplier = (
            getattr(context, "ability_potency_multiplier", 1.0)
            + self.bonus_percent
        )


# ------------------------------------------------------------------
# NOTE: placeholder scaling -- explicitly flagged as "needs balancing"
# in the same way CZ costs are in the design doc. Only two data points
# were given (Stage 5 -> 5%, Stage 3 -> 15%); Stage 4/2/1/0 below are a
# linear interpolation/extrapolation and should be treated as a guess,
# not a balanced value, until playtested.
# ------------------------------------------------------------------
FORTUNE_ARTIFACT_BONUS_BY_STAGE = {
    5: 0.05,
    4: 0.10,
    3: 0.15,
    2: 0.20,
    1: 0.25,
    0: 0.30,
}

_PATH_EFFECT_FACTORIES = {
    "Fortune": lambda stage: FortuneAbilityPotencyEffect(
        path_name="Fortune",
        source_stage=stage,
        bonus_percent=FORTUNE_ARTIFACT_BONUS_BY_STAGE.get(stage, 0.0),
    ),
}


def get_effect_for_path(path_name, source_stage):
    factory = _PATH_EFFECT_FACTORIES.get(path_name)

    if factory is None:
        raise ValueError(
            f"No artifact effect registered for Path '{path_name}'. "
            f"Add an entry to _PATH_EFFECT_FACTORIES when that Path ships."
        )

    return factory(source_stage)