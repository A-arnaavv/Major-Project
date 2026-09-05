from ai_ml.interview_intelligence.question_generator import (
    generate_question
)


question = generate_question(
    topic="Machine Learning",
    difficulty="medium",
    previous_questions=[
        "What is overfitting in machine learning?"
    ]
)

print(question.model_dump_json(indent=2))