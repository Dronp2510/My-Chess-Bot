class InventoryFullError(Exception):
    pass


class Inventory:
    """
    Holds up to MAX_SLOTS Concepts at once. A Concept leaves the Inventory
    either by being consumed for Path advancement (Concept.can_advance())
    or by being crafted into an Artifact at a shop -- both are one-way,
    the Concept object itself is destroyed either way.
    """

    MAX_SLOTS = 9

    def __init__(self):
        self._concepts = []

    def __len__(self):
        return len(self._concepts)

    def __iter__(self):
        return iter(self._concepts)

    def is_full(self):
        return len(self._concepts) >= self.MAX_SLOTS

    def slots_remaining(self):
        return self.MAX_SLOTS - len(self._concepts)

    def add(self, concept):
        if self.is_full():
            raise InventoryFullError(
                f"Inventory is full ({self.MAX_SLOTS} slots) -- "
                f"the player must craft or advance before picking up more."
            )
        self._concepts.append(concept)

    def remove(self, concept):
        self._concepts.remove(concept)

    def concepts_eligible_for_advancement(self, player_path_name, player_stage):
        """
        Concepts the UI should show an "Advance" option for when the
        player clicks on them in the inventory -- i.e. same Path, exactly
        one stage below the player's current stage.
        """
        return [
            c for c in self._concepts
            if c.can_advance(player_path_name, player_stage)
        ]

    def all_concepts(self):
        return list(self._concepts)