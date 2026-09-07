from typing import Dict, List, Any


def generate_learning_plan(
    subtopic_performance: Dict[str, float]
) -> List[Dict[str, Any]]:

    if not subtopic_performance:
        return []

    sorted_topics = sorted(
        subtopic_performance.items(),
        key=lambda item: item[1]
    )

    learning_plan = []

    for priority, (subtopic, score) in enumerate(
        sorted_topics,
        start=1
    ):
        if score >= 8:
            level = "Strong"
            recommendation = (
                "Maintain this skill and practice advanced questions."
            )

        elif score >= 6:
            level = "Moderate"
            recommendation = (
                "Review key concepts and practice medium-level questions."
            )

        elif score >= 4:
            level = "Weak"
            recommendation = (
                "Revisit fundamentals and solve guided practice questions."
            )

        else:
            level = "Critical"
            recommendation = (
                "Study the fundamentals before attempting advanced questions."
            )

        learning_plan.append({
            "priority": priority,
            "subtopic": subtopic,
            "current_score": score,
            "performance_level": level,
            "recommended_action": recommendation
        })

    return learning_plan