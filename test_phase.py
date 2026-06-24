from game.battle_state import BattleState
from game.paths.fortune_path import FortunePath
from game.paths.fortune_abilities import LuckyOne

path = FortunePath(stage=3)

battle = BattleState(path)

ability = LuckyOne()

ability.activate(
    battle,
    [
        (7, 1),
        (7, 6),
        (6, 4),
        (6, 3)
    ]
)

print(battle.statuses)
print(battle.cz.current_cz)