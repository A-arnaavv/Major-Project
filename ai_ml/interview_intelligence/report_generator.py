from typing import List, Dict, Any


def generate_final_report(
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not history:
        return {
            "total_questions": 0,
            "average_score": 0,
            "average_technical_accuracy": 0,
            "average_relevance": 0,
            "average_clarity": 0,
            "average_completeness": 0,
            "topic_performance": {},
            "subtopic_performance": {},
            "strengths": [],
            "weaknesses": []
        }

    total_questions = len(history)

    total_score = 0
    total_technical = 0
    total_relevance = 0
    total_clarity = 0
    total_completeness = 0

    strengths = []
    weaknesses = []

    topic_scores = {}
    subtopic_scores = {}

    for record in history:
        evaluation = record["evaluation"]
        topic = record.get("topic", "General")

        total_score += evaluation["overall_score"]
        total_technical += evaluation["technical_accuracy"]
        total_relevance += evaluation["relevance"]
        total_clarity += evaluation["clarity"]
        total_completeness += evaluation["completeness"]

        subtopic = record.get(
            "subtopic",
            record.get("topic", "General")
        )

        if subtopic not in subtopic_scores:
            subtopic_scores[subtopic] = {
                "total_score": 0,
                "questions": 0
            }

        subtopic_scores[subtopic]["total_score"] += (
            evaluation["overall_score"]
        )

        subtopic_scores[subtopic]["questions"] += 1
        strengths.extend(evaluation["strengths"])
        weaknesses.extend(evaluation["weaknesses"])

        if topic not in topic_scores:
            topic_scores[topic] = {
                "total_score": 0,
                "questions": 0
            }

        topic_scores[topic]["total_score"] += evaluation["overall_score"]
        topic_scores[topic]["questions"] += 1

    topic_performance = {}

    for topic, data in topic_scores.items():
        topic_performance[topic] = round(
            data["total_score"] / data["questions"],
            2
        )

    subtopic_performance = {}

    for subtopic, data in subtopic_scores.items():
        subtopic_performance[subtopic] = round(
            data["total_score"] / data["questions"],
            2
        )

    return {
        "total_questions": total_questions,
        "average_score": round(
            total_score / total_questions,
            2
        ),
        "average_technical_accuracy": round(
            total_technical / total_questions,
            2
        ),
        "average_relevance": round(
            total_relevance / total_questions,
            2
        ),
        "average_clarity": round(
            total_clarity / total_questions,
            2
        ),
        "average_completeness": round(
            total_completeness / total_questions,
            2
        ),
        "topic_performance": topic_performance,
        "subtopic_performance": subtopic_performance,
        "strengths": strengths,
        "weaknesses": weaknesses
    }