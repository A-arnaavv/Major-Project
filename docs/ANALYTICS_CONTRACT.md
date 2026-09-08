# InterviewGPT AI/ML → Analytics Contract

## Purpose

This document defines the interface between the InterviewGPT AI/ML pipeline and the analytics/dashboard layer.

The AI/ML system is responsible for generating interview intelligence. The analytics layer should consume these outputs for aggregation, visualization, comparison, KPI generation, and reporting.

Analytics should not independently recalculate AI-generated evaluation scores, feedback, performance summaries, or learning recommendations.

---

## Data Flow

```text
Resume
  |
  v
AI/ML Resume Intelligence
  |
  v
Adaptive Interview
  |
  v
Answer Evaluation
  |
  +--> Question-Level Analytics
  |
  v
Performance Aggregation
  |
  +--> Interview-Level Analytics
  |
  v
Analytics / Dashboard Layer
```

---

# 1. Question-Level Analytics

Each answered interview question produces one question-level analytics record.

## Schema

```json
{
  "session_id": "candidate-session-001",
  "question_number": 1,
  "topic": "Machine Learning",
  "subtopic": "Overfitting",
  "difficulty": "medium",
  "question": "What is overfitting and how can it be reduced?",
  "candidate_answer": "Candidate response...",
  "technical_accuracy": 8.0,
  "relevance": 9.0,
  "clarity": 7.0,
  "completeness": 8.0,
  "overall_score": 8.0,
  "strengths": [
    "Correct explanation"
  ],
  "weaknesses": [
    "Could discuss regularization further"
  ],
  "feedback": "Good answer, but expand on prevention techniques.",
  "improved_answer": "An improved response...",
  "next_difficulty": "hard"
}
```

## Field Definitions

| Field | Description |
|---|---|
| `session_id` | Unique interview session identifier |
| `question_number` | Position of the question within the interview |
| `topic` | Main interview topic |
| `subtopic` | AI-generated or selected subtopic |
| `difficulty` | Difficulty used for the current question |
| `question` | Interview question shown to the candidate |
| `candidate_answer` | Candidate response |
| `technical_accuracy` | AI-generated technical correctness score |
| `relevance` | AI-generated relevance score |
| `clarity` | AI-generated communication/clarity score |
| `completeness` | AI-generated completeness score |
| `overall_score` | Combined overall performance score |
| `strengths` | Strengths identified by the evaluator |
| `weaknesses` | Weaknesses identified by the evaluator |
| `feedback` | Detailed AI-generated feedback |
| `improved_answer` | AI-generated improved version of the answer |
| `next_difficulty` | Difficulty selected for the following question |

---

# 2. Interview-Level Summary Analytics

After an interview is completed, AI/ML produces an interview-level analytics summary.

## Schema

```json
{
  "session_id": "candidate-session-001",
  "total_questions": 5,
  "average_score": 7.8,
  "average_technical_accuracy": 8.0,
  "average_relevance": 8.2,
  "average_clarity": 7.4,
  "average_completeness": 7.6,
  "subtopic_performance": {
    "Overfitting": 8.5,
    "Regularization": 6.5
  },
  "overall_performance": "Good",
  "strong_areas": [
    "Overfitting"
  ],
  "weak_areas": [
    "Regularization"
  ],
  "recommended_topics": [
    "Regularization"
  ],
  "learning_plan": [
    {
      "priority": 1,
      "subtopic": "Regularization",
      "current_score": 6.5,
      "performance_level": "Needs Improvement",
      "recommended_action": "Review this topic and practice targeted interview questions."
    }
  ]
}
```

## Field Definitions

| Field | Description |
|---|---|
| `session_id` | Unique interview session identifier |
| `total_questions` | Number of answered interview questions |
| `average_score` | Average overall interview score |
| `average_technical_accuracy` | Average technical accuracy |
| `average_relevance` | Average relevance |
| `average_clarity` | Average clarity |
| `average_completeness` | Average completeness |
| `subtopic_performance` | Average performance grouped by subtopic |
| `overall_performance` | AI-generated overall performance category |
| `strong_areas` | Strongest identified areas |
| `weak_areas` | Areas requiring improvement |
| `recommended_topics` | Topics recommended for additional study |
| `learning_plan` | Prioritized personalized learning recommendations |

---

# 3. Learning Plan Item

Each entry in `learning_plan` follows:

```json
{
  "priority": 1,
  "subtopic": "Regularization",
  "current_score": 6.5,
  "performance_level": "Needs Improvement",
  "recommended_action": "Review this topic and practice targeted interview questions."
}
```

Fields:

| Field | Description |
|---|---|
| `priority` | Recommendation priority |
| `subtopic` | Topic/subtopic requiring attention |
| `current_score` | Current measured performance |
| `performance_level` | Human-readable performance classification |
| `recommended_action` | Suggested next learning action |

---

# 4. API Access

Analytics data is available through the FastAPI backend.

```text
GET /interview/{session_id}/analytics
```

Example:

```text
GET /interview/candidate-session-001/analytics
```

The analytics team can use this endpoint to obtain the AI/ML-produced analytics payload for an interview session.

The final interview report is available through:

```text
GET /interview/{session_id}/report
```

---

# 5. Recommended Analytics Tables

The analytics implementation may normalize the API output into tables such as:

## Interview Sessions

```text
session_id
total_questions
average_score
average_technical_accuracy
average_relevance
average_clarity
average_completeness
overall_performance
```

## Question Performance

```text
session_id
question_number
topic
subtopic
difficulty
technical_accuracy
relevance
clarity
completeness
overall_score
next_difficulty
```

## Subtopic Performance

```text
session_id
subtopic
average_score
```

## Learning Recommendations

```text
session_id
priority
subtopic
current_score
performance_level
recommended_action
```

These are recommendations for analytics storage design, not additional AI/ML API requirements.

---

# 6. Ownership Boundary

## AI/ML Owns

The AI/ML layer is responsible for:

- resume parsing
- resume analysis
- candidate profile generation
- embeddings
- candidate-isolated vector storage
- dense and sparse retrieval
- Reciprocal Rank Fusion
- interview context construction
- question generation
- adaptive difficulty
- answer evaluation
- technical accuracy
- relevance
- clarity
- completeness
- overall score
- strengths
- weaknesses
- feedback
- improved answers
- subtopic performance
- overall performance classification
- final performance summary
- recommended topics
- personalized learning plan

## Analytics Owns

The analytics layer is responsible for:

- consuming AI/ML outputs
- storing analytics records
- aggregating results
- KPI generation
- trend analysis
- comparisons
- visualizations
- dashboards
- BI/reporting
- longitudinal candidate analysis

---

# 7. Important Rule: Do Not Recalculate AI Scores

The analytics layer should treat fields such as:

```text
technical_accuracy
relevance
clarity
completeness
overall_score
subtopic_performance
overall_performance
recommended_topics
learning_plan
```

as upstream AI/ML outputs.

Analytics may aggregate, filter, group, compare, and visualize these values.

It should not redefine the AI/ML evaluation formulas independently.

This keeps scoring behavior consistent across the platform.

---

# 8. Candidate Identity and Session Identity

## Current Demo Behavior

The current integrated AI/ML demo uses:

```text
session_id
```

as the candidate isolation key for resume embeddings and retrieval.

This provides safe isolation between interview sessions.

For example:

```text
session_001 -> Milvus collection A
session_002 -> Milvus collection B
```

This prevents one session from retrieving another session's resume context.

## Future Longitudinal Analytics

For analytics across multiple interviews completed by the same person, introduce a persistent:

```text
candidate_id
```

separately from:

```text
session_id
```

Recommended model:

```text
candidate_id: candidate_123
    |
    +-- session_id: interview_001
    +-- session_id: interview_002
    +-- session_id: interview_003
```

This allows analytics to calculate:

- candidate improvement over time
- score trends
- repeated weak areas
- repeated strong areas
- topic-level progression
- difficulty progression
- historical interview comparisons

without changing the meaning of an individual interview session.

---

# 9. Integration Guidance for Analytics Team

The recommended integration sequence is:

```text
1. Call the analytics endpoint for a completed session.

2. Store question-level records.

3. Store the interview-level summary.

4. Use session_id as the current interview identifier.

5. Aggregate AI/ML scores for dashboards.

6. Visualize subtopic performance.

7. Visualize strong and weak areas.

8. Surface learning recommendations.

9. Introduce candidate_id later if cross-session
   candidate analytics are required.
```

---

# 10. Example Dashboard Metrics

Analytics can directly derive metrics such as:

- average interview score
- average technical accuracy
- average relevance
- average clarity
- average completeness
- performance by subtopic
- performance by difficulty
- strongest topics
- weakest topics
- difficulty progression
- question-by-question score progression
- recommended learning topics
- interview completion count
- candidate improvement across sessions once `candidate_id` is introduced

---

# 11. Contract Stability

The structures documented here form the handoff boundary between AI/ML and analytics.

If analytics requires additional fields, the preferred process is:

```text
Analytics requirement
        |
        v
Review existing AI/ML output
        |
        +--> Field already exists
        |       |
        |       v
        |   Consume directly
        |
        +--> Field does not exist
                |
                v
        Define contract change
                |
                v
        Update AI/ML schema + tests
                |
                v
        Update this document
```

The AI/ML layer should remain stable unless a concrete integration requirement or bug requires a change.
