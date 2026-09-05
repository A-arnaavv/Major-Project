from ai_ml.interview_intelligence.session import InterviewSession


session = InterviewSession(
    topic="Machine Learning",
    difficulty="medium"
)

result = session.submit_answer(
    question="What is overfitting in machine learning?",
    candidate_answer=(
        "Overfitting happens when a model learns the training data "
        "too closely and performs poorly on unseen data."
    ),
    expected_concepts=(
        "generalization, validation data, regularization, high variance"
    )
)

print("\n--- RESULT ---\n")
print(result)

print("\n--- CURRENT DIFFICULTY ---\n")
print(session.current_difficulty)

print("\n--- SESSION HISTORY ---\n")
print(session.get_history())