class CZPool:
    """
    Conceptualization Energy
    """

    def __init__(self, max_cz, recovery):
        self.max_cz = max_cz
        self.current_cz = max_cz
        self.recovery = recovery

    def regenerate(self):
        self.current_cz = min(
            self.max_cz,
            self.current_cz + self.recovery
        )

    def can_afford(self, amount):
        return self.current_cz >= amount

    def spend(self, amount):
        if not self.can_afford(amount):
            return False

        self.current_cz -= amount
        return True