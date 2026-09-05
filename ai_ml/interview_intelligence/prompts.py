EVALUATION_PROMPT = """
You are an experienced technical interviewer.

Evaluate the candidate's answer objectively.

Question:
{question}

Candidate Answer:
{candidate_answer}

Expected Concepts:
{expected_concepts}

Current Difficulty:
{difficulty}

Evaluate the candidate on:

1. Technical Accuracy - score from 0 to 10
2. Relevance - score from 0 to 10
3. Clarity - score from 0 to 10
4. Completeness - score from 0 to 10

Also provide:

- Overall score out of 10
- Strengths
- Weaknesses
- Constructive feedback
- An improved version of the candidate's answer

For next difficulty:

If overall_score < 5:
next_difficulty = "easier"

If overall_score is between 5 and 7:
next_difficulty = "same"

If overall_score > 7:
next_difficulty = "harder"

Do not penalize the candidate simply for using different wording
if the technical meaning is correct.
"""