from ai_ml.interview_intelligence.evaluator import evaluate_answer

result = evaluate_answer(
    question="What is overfitting in machine learning?",
    candidate_answer=(
        "Overfitting happens when the model learns the training data "
        "too well and performs poorly on unseen data."
    ),
    expected_concepts=(
        "training performance, generalization, validation data, "
        "regularization"
    ),
    difficulty="medium"
)

print(result.model_dump_json(indent=2))