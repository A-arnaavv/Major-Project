from typing import Literal

Difficulty = Literal["easy", "medium", "hard"]


def get_next_difficulty(
    current_difficulty: Difficulty,
    overall_score: float
) -> Difficulty:

    levels = ["easy", "medium", "hard"]
    current_index = levels.index(current_difficulty)

    if overall_score > 7:
        new_index = min(current_index + 1, len(levels) - 1)

    elif overall_score < 5:
        new_index = max(current_index - 1, 0)

    else:
        new_index = current_index

    return levels[new_index]