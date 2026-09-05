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
            "strengths": [],
            "weaknesses": [],
        }

    total_questions = len(history)

    total_score = 0
    total_technical = 0
    total_relevance = 0
    total_clarity = 0
    total_completeness = 0

    strengths = []
    weaknesses = []

    for record in history:
        evaluation = record["evaluation"]

        total_score += evaluation["overall_score"]
        total_technical += evaluation["technical_accuracy"]
        total_relevance += evaluation["relevance"]
        total_clarity += evaluation["clarity"]
        total_completeness += evaluation["completeness"]

        strengths.extend(evaluation["strengths"])
        weaknesses.extend(evaluation["weaknesses"])

    return {
        "total_questions": total_questions,

        "average_score": round(
            total_score / total_questions, 2
        ),

        "average_technical_accuracy": round(
            total_technical / total_questions, 2
        ),

        "average_relevance": round(
            total_relevance / total_questions, 2
        ),

        "average_clarity": round(
            total_clarity / total_questions, 2
        ),

        "average_completeness": round(
            total_completeness / total_questions, 2
        ),

        "strengths": strengths,

        "weaknesses": weaknesses
    }