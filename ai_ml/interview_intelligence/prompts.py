EVALUATION_PROMPT = """
You are an expert technical interviewer.

Evaluate the candidate's answer objectively.

Question:
{question}

Candidate Answer:
{candidate_answer}

Expected Concepts:
{expected_concepts}

Difficulty:
{difficulty}

Score the answer on:
- Technical Accuracy: 0-10
- Relevance: 0-10
- Clarity: 0-10
- Completeness: 0-10

Also provide:
- Overall score out of 10
- Strengths
- Weaknesses
- Constructive feedback
- An improved answer
- Recommended next difficulty

Difficulty rule:
- Below 5: easier
- 5 to 7: same
- Above 7: harder
"""