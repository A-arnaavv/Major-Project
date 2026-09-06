from ai_ml.interview_intelligence.session import InterviewSession


session = InterviewSession(
    topic="Machine Learning",
    difficulty="medium"
)

print("\n===== AI INTERVIEW STARTED =====\n")

for i in range(3):

    generated = session.generate_next_question()

    print(f"\nQuestion {i + 1}:")
    print(generated.question)

    candidate_answer = input("\nYour answer: ")

    result = session.submit_answer(
        candidate_answer=candidate_answer
    )

    evaluation = result["evaluation"]

    print("\n--- Evaluation ---")
    print("Technical Accuracy:", evaluation["technical_accuracy"])
    print("Relevance:", evaluation["relevance"])
    print("Clarity:", evaluation["clarity"])
    print("Completeness:", evaluation["completeness"])
    print("Overall Score:", evaluation["overall_score"])

    print("\nFeedback:")
    print(evaluation["feedback"])

    print("\nNext Difficulty:")
    print(result["next_difficulty"])


# IMPORTANT:
# This section must be OUTSIDE the for-loop.

print("\n===== INTERVIEW COMPLETED =====")

report = session.get_final_report()

print("\n===== NUMERICAL REPORT =====")
print("Total Questions:", report["total_questions"])
print("Average Score:", report["average_score"])
print("Technical Accuracy:", report["average_technical_accuracy"])
print("Relevance:", report["average_relevance"])
print("Clarity:", report["average_clarity"])
print("Completeness:", report["average_completeness"])


print("\n===== AI PERFORMANCE SUMMARY =====")

summary = session.get_ai_performance_summary()

print("\nOverall Performance:")
print(summary.overall_performance)

print("\nStrong Areas:")
for area in summary.strong_areas:
    print("-", area)

print("\nWeak Areas:")
for area in summary.weak_areas:
    print("-", area)

print("\nRecommended Topics:")
for index, topic in enumerate(
    summary.recommended_topics,
    start=1
):
    print(f"{index}. {topic}")

print("\nFinal Feedback:")
print(summary.final_feedback)