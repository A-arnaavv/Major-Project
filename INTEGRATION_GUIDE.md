# InterviewGPT AI – Integration Guide

## Purpose

This document explains how other team members should integrate with the **Interview Intelligence** module implemented under:

```text
ai_ml/interview_intelligence/
```

This module owns:

* AI interviewer flow
* adaptive question difficulty
* LLM-based answer evaluation
* structured scoring
* strengths and weaknesses
* constructive feedback
* improved answer generation
* interview session tracking
* performance summaries
* personalized learning recommendations
* analytics-ready export records

The module is designed to consume outputs from AI/ML Part 1 and expose structured outputs to backend, analytics, and dashboard components.

---

# 1. AI/ML Part 1 → Interview Intelligence

The first AI/ML module may provide candidate- and company-specific context.

The expected input contract is represented by:

```text
ai_ml/interview_intelligence/integration_schemas.py
```

Schema:

```python
class InterviewContext(BaseModel):
    topic: str
    difficulty: str = "medium"
    total_questions: int = 5
    resume_context: str | None = None
    job_role: str | None = None
    company_context: str | None = None
    retrieved_context: str | None = None
```

Example:

```json
{
  "topic": "Machine Learning",
  "difficulty": "medium",
  "total_questions": 5,
  "resume_context": "Candidate has experience with Python, NLP and scikit-learn.",
  "job_role": "Machine Learning Engineer",
  "company_context": "The company works on recommendation systems.",
  "retrieved_context": "Relevant retrieved concepts include embeddings, ranking models and cold-start techniques."
}
```

The additional context fields are optional.

If they are not provided, the interview system still works using the topic and difficulty.

The Interview Intelligence module should not perform resume parsing, RAG retrieval, embedding generation, vector search, or company research itself. Those responsibilities belong to AI/ML Part 1.

---

# 2. Starting an Interview Through the API

The FastAPI backend is implemented in:

```text
backend/main.py
```

Run it with:

```bash
uvicorn backend.main:app --reload
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Start an interview with:

```text
POST /interview/start
```

Example request:

```json
{
  "session_id": "candidate_001",
  "topic": "Machine Learning",
  "difficulty": "medium",
  "total_questions": 5,
  "resume_context": "Python and NLP experience",
  "job_role": "ML Engineer",
  "company_context": "Recommendation systems",
  "retrieved_context": "Embeddings and ranking models"
}
```

Example response:

```json
{
  "session_id": "candidate_001",
  "status": "started",
  "question": "Generated interview question",
  "difficulty": "medium",
  "topic": "Machine Learning",
  "subtopic": "Recommendation Systems"
}
```

---

# 3. Submitting Candidate Answers

Use:

```text
POST /interview/answer
```

Example request:

```json
{
  "session_id": "candidate_001",
  "candidate_answer": "The candidate's answer goes here."
}
```

The response contains structured evaluation fields such as:

```json
{
  "technical_accuracy": 7,
  "relevance": 8,
  "clarity": 7,
  "completeness": 6,
  "overall_score": 7.0,
  "strengths": [
    "Relevant explanation"
  ],
  "weaknesses": [
    "Needs more technical depth"
  ],
  "feedback": "Expand the explanation with implementation details.",
  "improved_answer": "A stronger answer would explain...",
  "next_difficulty": "medium"
}
```

The interview automatically adapts the next question difficulty based on the evaluation score.

The deterministic adaptive engine is the source of truth for difficulty progression.

---

# 4. Adaptive Difficulty Logic

Difficulty levels:

```text
easy
medium
hard
```

Rules:

```text
overall_score > 7  → increase difficulty
overall_score < 5  → decrease difficulty
otherwise          → keep same difficulty
```

Difficulty is bounded between `easy` and `hard`.

---

# 5. Final Performance Report

After the configured number of questions is completed, the API returns a final report containing:

```text
numerical_report
ai_summary
learning_plan
```

The numerical report contains aggregate metrics such as:

* total questions
* average score
* average technical accuracy
* average relevance
* average clarity
* average completeness
* subtopic performance

The AI summary contains:

* overall performance
* strong areas
* weak areas
* recommended topics
* final feedback

The learning plan prioritizes weaker subtopics and gives recommended next actions.

---

# 6. Analytics Integration

Analytics-ready outputs can be obtained through:

```text
GET /interview/{session_id}/analytics
```

Example:

```text
GET /interview/candidate_001/analytics
```

The response contains:

```json
{
  "session_id": "candidate_001",
  "question_records": [],
  "summary": {}
}
```

## Question-Level Analytics Record

Each interview question is exported using the `QuestionAnalyticsRecord` schema.

Fields include:

```text
session_id
question_number
topic
subtopic
difficulty
question
candidate_answer
technical_accuracy
relevance
clarity
completeness
overall_score
strengths
weaknesses
feedback
improved_answer
next_difficulty
```

Example:

```json
{
  "session_id": "candidate_001",
  "question_number": 1,
  "topic": "Machine Learning",
  "subtopic": "Regularization",
  "difficulty": "medium",
  "question": "What is regularization?",
  "candidate_answer": "It helps reduce overfitting.",
  "technical_accuracy": 7,
  "relevance": 8,
  "clarity": 7,
  "completeness": 6,
  "overall_score": 7.0,
  "strengths": [
    "Relevant answer"
  ],
  "weaknesses": [
    "Needs more detail"
  ],
  "feedback": "Explain L1 and L2 regularization.",
  "improved_answer": "Regularization adds a penalty term...",
  "next_difficulty": "medium"
}
```

---

# 7. Session-Level Analytics Summary

The analytics summary contains:

```text
session_id
total_questions
average_score
average_technical_accuracy
average_relevance
average_clarity
average_completeness
subtopic_performance
overall_performance
strong_areas
weak_areas
recommended_topics
learning_plan
```

This object is intended for:

* candidate performance dashboards
* topic/subtopic performance charts
* interview comparison dashboards
* learning recommendation views
* historical performance tracking

---

# 8. Analytics Team Recommendation

For storage, the analytics team can conceptually maintain two datasets.

## Question-Level Dataset

One row per interview question.

Suggested columns:

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

Additional text fields such as feedback, strengths, weaknesses, and improved answers may also be stored if needed.

## Session-Level Dataset

One row per completed interview.

Suggested columns:

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

`subtopic_performance` and `learning_plan` can be stored as JSON or normalized into separate tables depending on the analytics architecture.

---

# 9. Current Storage Behavior

Interview sessions are currently stored in memory inside the FastAPI application.

This means:

* restarting the server clears sessions
* sessions are not yet persisted to a database
* the existing structure is suitable for development and integration testing

Persistent storage should be handled during team integration.

Possible future targets include:

* PostgreSQL
* MongoDB
* another project-selected database

The Interview Intelligence module itself should remain separated from database-specific logic where possible.

---

# 10. LLM Modes

The project supports two execution modes.

## Mock Mode

Recommended for:

* development
* automated tests
* integration work
* frontend development
* analytics testing

Configure:

```env
LLM_MODE=mock
```

Mock mode avoids Gemini API calls and produces deterministic outputs.

## Real Gemini Mode

Used for real AI-generated interview behavior.

Configure:

```env
LLM_MODE=real
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=YOUR_MODEL
```

Never commit `.env` or API credentials to Git.

---

# 11. Gemini Reliability

Gemini calls use a retry helper for transient failures.

Handled transient conditions include:

```text
408
429
500
502
503
504
connection failures
timeouts
```

The current application performs limited retry attempts with exponential backoff.

Invalid structured Gemini responses are converted into controlled runtime errors.

---

# 12. Multi-Agent Architecture

The Interview Intelligence module uses:

```text
InterviewSession
      ↓
InterviewOrchestrator
      ↓
InterviewerAgent
EvaluatorAgent
RecommendationAgent
```

Responsibilities:

### InterviewerAgent

Generates interview questions using:

* topic
* difficulty
* previous questions
* resume context
* target role
* company context
* retrieved RAG context

### EvaluatorAgent

Evaluates candidate answers and produces structured scoring and feedback.

### RecommendationAgent

Produces personalized learning recommendations from subtopic performance.

---

# 13. Important Ownership Boundary

AI/ML Part 2 should consume Part 1 outputs but should not duplicate Part 1 responsibilities.

## Part 1 owns

```text
resume parsing
resume analysis
embeddings
vector database
RAG retrieval
company-specific information retrieval
candidate profile extraction
```

## Part 2 owns

```text
interview orchestration
question delivery
answer evaluation
adaptive difficulty
scoring
feedback
improved answers
session history
performance summaries
learning recommendations
analytics export
```

---

# 14. Automated Testing

Current test coverage includes:

* Gemini retry behavior
* mock question generation
* duplicate-question prevention
* answer evaluation
* adaptive difficulty
* learning recommendations
* interview session behavior
* Part 1 context acceptance
* integration schemas
* analytics exporter
* FastAPI endpoints
* analytics endpoint behavior
* missing-session handling

Current verified result:

```text
30 passed
```

Run all relevant tests with:

```bash
python3 -m pytest ai_ml/interview_intelligence/tests backend/test_main.py -v
```

For normal testing, use:

```env
LLM_MODE=mock
```

---

# 15. Recommended Team Integration Flow

The intended full-system flow is:

```text
Resume / Candidate Data
          ↓
AI/ML Part 1
Resume Analysis + RAG
          ↓
InterviewContext
          ↓
AI/ML Part 2
Interview Intelligence
          ↓
Question-Level Evaluation
          ↓
Adaptive Interview
          ↓
Final Performance Report
          ↓
Analytics Exporter
          ↓
Backend / Database
          ↓
Analytics + BI Dashboard
```

The cleanest integration point between modules is the structured schemas in:

```text
ai_ml/interview_intelligence/integration_schemas.py
```

These schemas should be treated as the contract between team components.
