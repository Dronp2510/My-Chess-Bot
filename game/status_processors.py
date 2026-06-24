import math
import random

def apply_misfortunate_filter(moves,misfortunate_status):

    if not moves:
        return moves

    reduction = ( misfortunate_status.reduction_percent )

    remove_count = math.floor( len(moves) * reduction )

    if remove_count <= 0:
        return moves

    rng = random.Random( misfortunate_status.seed )

    move_indexes = list( range(len(moves)) )

    removed_indexes = set( rng.sample(move_indexes,remove_count) )

    filtered = []

    for idx, move in enumerate(moves):

        if idx in removed_indexes:
            continue

        filtered.append(move)

    return filtered