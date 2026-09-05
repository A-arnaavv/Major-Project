from ai_ml.interview_intelligence.adaptive_engine import (
    get_next_difficulty
)


print("Test 1:", get_next_difficulty("medium", 8.5))
# Expected: hard

print("Test 2:", get_next_difficulty("medium", 6.0))
# Expected: medium

print("Test 3:", get_next_difficulty("medium", 3.5))
# Expected: easy

print("Test 4:", get_next_difficulty("hard", 9.0))
# Expected: hard

print("Test 5:", get_next_difficulty("easy", 2.0))
# Expected: easy